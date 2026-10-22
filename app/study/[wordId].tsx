import { useLocalSearchParams, useRouter } from "expo-router";
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";
import {
  Animated,
  Easing,
  PanResponder,
  Pressable,
  ScrollView,
  Text,
  useWindowDimensions,
  View,
  Platform,
} from "react-native";
import { Image } from "expo-image";
import { BlurView } from "expo-blur";
import {
  PictureIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronUpIcon,
  CloseIcon,
  MicIcon,
  PauseIcon,
  PlayIcon,
  SpeakerIcon,
} from "../../src/components/icons";
import { BackButton } from "../../src/components/BackButton";
import { LabeledSection } from "../../src/components/LabeledSection";
import { PillButton } from "../../src/components/PillButton";
import {
  MAX_CONTENT_WIDTH,
  Screen,
  ScreenHeader,
} from "../../src/components/Screen";
import { SynonymList } from "../../src/components/SynonymList";
import { gradesOf } from "../../src/constants/grades";
import {
  UNIT_SIZE,
  useVocabForWordId,
  type Word,
} from "../../src/constants/words";
import { UNIT_QUIZ_SIZE } from "../../src/lib/quiz";
import {
  studyLangOfWordId,
  studyLanguageOf,
} from "../../src/constants/languages";
import { useT } from "../../src/i18n";
import { wordImageSource } from "../../src/constants/wordImages";
import { playFeedback } from "../../src/lib/feedbackSound";
import { speakWord, stopSpeaking } from "../../src/lib/speech";
import {
  isListenSupported,
  judge,
  listenOnce,
  watchMicLevel,
  type ListenError,
  type Verdict,
} from "../../src/lib/listen";
import { useAppStore, type WordStatus } from "../../src/stores/useAppStore";

/** 앱 기본 초록 (tailwind 의 mint). Animated.View 처럼 className 이 안 먹는 곳에 쓴다 */
const MINT = "#0EB582";

/** 따라 말하기 진행 상태. 단어 id 를 붙여 두어 넘어가면 이전 결과가 남지 않는다 */
type ListenState = { wordId: string } & (
  | { phase: "listening" }
  | { phase: "result"; verdict: Verdict; heard: string }
  | { phase: "error"; error: ListenError }
);

/** 음성 인식 지원 여부는 바뀌지 않으므로 구독할 것이 없다 */
const subscribeNothing = () => () => {};

export default function StudyScreen() {
  const { wordId } = useLocalSearchParams<{ wordId: string }>();
  const router = useRouter();

  const t = useT();
  // 지금 설정이 아니라 단어 id 에 적힌 언어에서 찾는다
  const vocab = useVocabForWordId(wordId ?? "");
  const found = vocab.find(wordId ?? "");

  const goTo = useCallback(
    (id?: string) => {
      if (id) router.setParams({ wordId: id });
    },
    [router],
  );

  if (!found) {
    return (
      <Screen className="items-center justify-center">
        <Text className="text-[14px] text-slate-500">
          {t("study.notFound")}
        </Text>
        <PillButton
          className="mt-6"
          label={t("common.backArrow")}
          onPress={() => router.back()}
        />
      </Screen>
    );
  }

  const { levelId: gradeId, words, index, word } = found;

  return (
    // 화면 틀(안전 영역 포함)은 한 번만 만들고 단어가 바뀌어도 그대로 둔다.
    // 예전에는 key 로 단어마다 화면 전체를 새로 만들어서, 폰에서 안전 영역 여백이
    // 한 박자 늦게 붙으며 화면이 위에서 내려오듯 꿀렁이고 그림도 깜빡였다.
    <Screen>
      <StudyCard
        word={word}
        gradeId={gradeId}
        index={index}
        total={words.length}
        prev={words[index - 1]}
        next={words[index + 1]}
        onNavigate={goTo}
        onUnitEnd={() => {
          // 유닛 마지막 단어를 넘기면 그 유닛만 놓고 확인 퀴즈를 낸다.
          // replace 를 쓰면 퀴즈에서 뒤로 갈 때 방금 푼 단어로 돌아오지 않는다
          const unitNo = Math.floor(index / UNIT_SIZE) + 1;
          router.replace(
            `/quiz/${gradeId}?unit=${unitNo}&size=${UNIT_QUIZ_SIZE}`,
          );
        }}
        onBack={() => {
          // 주소로 바로 들어오거나 새로고침한 경우엔 되돌아갈 기록이 없다.
          // 그때는 해당 학년의 유닛 목록으로 보낸다.
          if (router.canGoBack()) router.back();
          else router.replace(`/grade/${gradeId}`);
        }}
      />
    </Screen>
  );
}

/**
 * 이미지 패널 한 칸. offset 만큼 좌우로 떨어뜨려 두면
 * 스와이프할 때 옆 그림이 자연스럽게 따라 들어온다.
 */
function WordImage({ word, offset = 0 }: { word: Word; offset?: number }) {
  const t = useT();
  const source = wordImageSource(word);
  return (
    <View
      style={{
        position: "absolute",
        top: 0,
        bottom: 0,
        left: offset,
        right: -offset,
      }}
    >
      {source ? (
        <Image
          source={source}
          contentFit="cover"
          style={{ width: "100%", height: "100%" }}
        />
      ) : (
        <View className="flex-1 items-center justify-center gap-3 bg-canvas">
          <PictureIcon size={40} color="#cbd5e1" />
          <Text className="text-[13px] text-slate-400">
            {t("study.imagePreparing")}
          </Text>
        </View>
      )}
    </View>
  );
}

interface StudyCardProps {
  word: Word;
  gradeId: string;
  index: number;
  total: number;
  /** 앞·뒤 단어. 스와이프할 때 옆 그림을 미리 보여주는 데 쓴다 */
  prev?: Word;
  next?: Word;
  onNavigate: (id?: string) => void;
  /** 유닛 마지막 단어에서 다음으로 넘어갈 때 부른다 */
  onUnitEnd: () => void;
  onBack: () => void;
}

function StudyCard({
  word,
  gradeId,
  index,
  total,
  prev,
  next,
  onNavigate,
  onUnitEnd,
  onBack,
}: StudyCardProps) {
  const prevId = prev?.id;
  const nextId = next?.id;
  /** 이 단어가 유닛의 마지막인지. 학년 마지막 단어도 유닛의 끝이다 */
  const isUnitEnd = index % UNIT_SIZE === UNIT_SIZE - 1 || index === total - 1;
  const autoAdvance = useAppStore((s) => s.autoAdvance);
  const setAutoAdvance = useAppStore((s) => s.setAutoAdvance);
  const autoAdvanceSec = useAppStore((s) => s.autoAdvanceSec);
  const recordStudy = useAppStore((s) => s.recordStudy);
  const markSeen = useAppStore((s) => s.markSeen);
  const toggleSaved = useAppStore((s) => s.toggleSaved);
  const speechVolume = useAppStore((s) => s.speechVolume);
  // 이 단어가 단어장에 담겨 있는지. saved 전체를 구독하면 다른 단어를 담을 때도 다시 그려진다
  const isSaved = useAppStore((s) => Boolean(s.saved[word.id]));
  const t = useT();
  const router = useRouter();
  const uiLang = useAppStore((s) => s.uiLang);
  const speechCode = studyLanguageOf(studyLangOfWordId(word.id)).speechCode;

  const { width: screenWidth } = useWindowDimensions();

  /** 뜻·예문을 가려 둔 단어. 다음 단어로 넘어가면 따로 되돌리지 않아도 다시 보인다 */
  const [answerHiddenFor, setAnswerHiddenFor] = useState<string | null>(null);
  const showAnswer = answerHiddenFor !== word.id;
  /** 발음 중인 단어. 넘어가면 이전 단어의 재생 표시가 남지 않는다 */
  const [speakingFor, setSpeakingFor] = useState<string | null>(null);
  const speaking = speakingFor === word.id;

  /** 따라 말하기. 웹 정적 빌드는 서버에서 먼저 그려지므로
      지원 여부는 브라우저에서만 확인하고 서버에서는 없는 것으로 친다 */
  const canListen = useSyncExternalStore(
    subscribeNothing,
    isListenSupported,
    () => false,
  );
  const [listen, setListen] = useState<ListenState | null>(null);
  const listenNow = listen?.wordId === word.id ? listen : null;
  const listening = listenNow?.phase === "listening";
  /** 듣기를 그만두는 함수. 단어를 넘기거나 화면을 떠나면 부른다 */
  const stopListenRef = useRef<(() => void) | null>(null);
  /** 발음 재생 순번. 새로 읽거나 듣기를 시작하면 올라가서
      이전 재생의 "끝났다" 알림이 엉뚱하게 듣기를 켜지 않는다 */
  const speakSeq = useRef(0);
  const followTimer = useRef<ReturnType<typeof setTimeout>>(undefined);
  /** 렌더마다 새로 만들어지는 startListen 을 재생 콜백에서 최신 것으로 부르려고 담아 둔다 */
  const startListenRef = useRef<() => void>(() => {});

  /**
   * 단어 발음을 들려준다. 소리가 실제로 나고 끝까지 재생되면
   * (설정에서 켜 둔 경우) 바로 마이크를 켜서 따라 말한 것을 듣는다.
   * 음소거·자동 재생 차단으로 소리가 안 났으면 마이크를 켜지 않는다.
   */
  const playWord = () => {
    const seq = ++speakSeq.current;
    const id = word.id;
    let played = false;
    clearTimeout(followTimer.current);
    speakWord(word.word, {
      lang: speechCode,
      volume: speechVolume,
      onStart: () => {
        played = true;
        setSpeakingFor(id);
      },
      onDone: () => {
        setSpeakingFor((cur) => (cur === id ? null : cur));
        if (!played || seq !== speakSeq.current) return;
        if (!useAppStore.getState().autoListen || !isListenSupported()) return;
        // 스피커 소리의 꼬리가 마이크에 섞이지 않게 아주 잠깐 쉬고 켠다
        followTimer.current = setTimeout(() => {
          if (seq === speakSeq.current) startListenRef.current();
        }, 250);
      },
    });
  };
  /** 자동 넘김 진행도 0 → 1. 애니메이션 값이라 매 프레임 부드럽게 움직인다.
      한 번만 만들어 두고 계속 같은 값을 쓴다 */
  const [progress] = useState(() => new Animated.Value(0));

  /**
   * 다음으로 넘어간다.
   * 유닛의 마지막 단어였다면 다음 단어 대신 확인 퀴즈로 간다.
   * 자동 넘김·판정·스와이프·다음 버튼이 모두 이 길을 쓴다.
   */
  const advance = useCallback(() => {
    if (isUnitEnd) onUnitEnd();
    else onNavigate(nextId);
  }, [isUnitEnd, onUnitEnd, onNavigate, nextId]);

  /** 이미지를 좌우로 밀어서 단어를 넘기는 스와이프.
      그림만 손가락을 따라 흐르고, 충분히 밀면 옆 그림이 자리를 넘겨받으며 단어가 바뀐다 */
  const [panelW, setPanelW] = useState(0);
  const [dragX] = useState(() => new Animated.Value(0));
  const scrollRef = useRef<ScrollView>(null);

  // 단어가 바뀌면 그림 위치와 스크롤을 처음 자리로 돌린다.
  // 새 단어가 화면에 그려지기 전에 맞춰야 한 프레임 어긋나 보이지 않는다
  useLayoutEffect(() => {
    dragX.setValue(0);
    scrollRef.current?.scrollTo({ y: 0, animated: false });
  }, [word.id, dragX]);

  const swipe = useMemo(() => {
    // 웹에서는 네이티브 드라이버를 쓸 수 없다
    const useNativeDriver = Platform.OS !== "web";
    const springBack = () =>
      Animated.spring(dragX, {
        toValue: 0,
        bounciness: 6,
        useNativeDriver,
      }).start();

    return PanResponder.create({
      // 세로 스크롤을 방해하지 않도록 가로로 확실히 움직였을 때만 잡는다
      onMoveShouldSetPanResponder: (_, g) =>
        Math.abs(g.dx) > 12 && Math.abs(g.dx) > Math.abs(g.dy) * 1.5,
      onPanResponderMove: (_, g) => {
        // 첫 단어/마지막 단어 쪽으로는 조금만 끌리게 해 더 갈 곳이 없음을 알린다
        const blocked = (g.dx > 0 && !prevId) || (g.dx < 0 && !nextId);
        dragX.setValue(blocked ? g.dx * 0.18 : g.dx);
      },
      onPanResponderRelease: (_, g) => {
        // 패널 너비의 4분의 1쯤 밀었거나 빠르게 튕겼으면 넘긴다
        const enough =
          Math.abs(g.dx) > (panelW || 200) * 0.26 || Math.abs(g.vx) > 0.35;
        const forward = g.dx < 0;
        // 유닛 마지막 단어에서는 다음 단어가 아니라 확인 퀴즈로 간다
        const target = forward ? (isUnitEnd ? word.id : nextId) : prevId;
        if (!enough || !target) return springBack();

        // 옆 그림이 자리를 다 채운 다음에 단어를 바꾼다.
        // 위치는 단어가 바뀔 때 위의 useLayoutEffect 가 0 으로 돌린다
        Animated.timing(dragX, {
          toValue: g.dx < 0 ? -panelW : panelW,
          duration: 180,
          easing: Easing.out(Easing.quad),
          useNativeDriver,
        }).start(({ finished }) => {
          if (finished) {
            if (forward) advance();
            else onNavigate(target);
          } else springBack();
        });
      },
      onPanResponderTerminate: springBack,
    });
  }, [dragX, panelW, prevId, nextId, onNavigate, advance, isUnitEnd, word.id]);

  /** 자동 넘김 바가 지금 어느 단어의 것인지. 단어가 바뀔 때만 처음부터 다시 채운다 */
  const progressWord = useRef(word.id);

  // 자동 넘김 타이머.
  // 예전에는 200ms마다 상태를 바꿔 바를 다시 그렸는데, 그 간격만큼 계단처럼 끊겨 보였다.
  // 지금은 설정한 간격(5~15초) 동안 0에서 1까지 일정한 속도로 흐르는 애니메이션 하나로 처리해
  // 왼쪽에서 오른쪽으로 끊김 없이 채워진다.
  useEffect(() => {
    if (progressWord.current !== word.id) {
      progressWord.current = word.id;
      progress.setValue(0);
    }
    if (!autoAdvance) {
      progress.setValue(0);
      return;
    }
    // 말하는 도중에 다음 단어로 넘어가 버리지 않게 듣는 동안은 멈춘다.
    // 바는 멈춘 자리에 그대로 두고, 듣기가 끝나면 거기서부터 남은 시간만큼 이어 간다
    if (listening) return;

    let animation: Animated.CompositeAnimation | undefined;
    progress.stopAnimation((value) => {
      const from = value >= 1 ? 0 : value;
      progress.setValue(from);
      animation = Animated.timing(progress, {
        toValue: 1,
        duration: (1 - from) * autoAdvanceSec * 1000,
        easing: Easing.linear,
        // 너비는 레이아웃 속성이라 네이티브 드라이버를 쓸 수 없다
        useNativeDriver: false,
      });
      animation.start(({ finished }) => {
        if (finished) advance();
      });
    });

    return () => animation?.stop();
  }, [word.id, autoAdvance, autoAdvanceSec, advance, progress, listening]);

  // 단어가 바뀌면 발음을 자동으로 한 번 들려준다.
  // (단어가 바뀔 때마다 정확히 한 번 실행된다)
  // 화면을 벗어날 때는 재생 중인 음성을 멈춘다.
  useEffect(() => {
    playWord();
    return () => {
      // 멈추면서 오는 "끝났다" 알림이 따라 말하기를 켜지 않게 순번을 올린다.
      // 화면 요소가 아니라 숫자 세는 ref 라 지금 값을 올리는 게 맞다
      // eslint-disable-next-line react-hooks/exhaustive-deps
      speakSeq.current++;
      clearTimeout(followTimer.current);
      stopSpeaking();
    };
    // 소리 크기를 바꿨다고 발음을 다시 들려줄 필요는 없어 의존성에서 뺀다
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [word.word, speechCode]);

  // 단어를 넘기거나 화면을 떠나면 듣던 것을 그만둔다
  useEffect(
    () => () => {
      stopListenRef.current?.();
      stopListenRef.current = null;
    },
    [word.id],
  );

  // 이어하기 지점과 "오늘 본 단어"는 화면에 뜬 시점에 기록한다.
  // 판정 버튼에서 기록하면 보다 만 단어와 자동 넘김으로 지나간 단어가 빠진다.
  useEffect(() => {
    markSeen(word.id, gradeId);
  }, [word.id, gradeId, markSeen]);

  // 헤더는 자리가 좁으므로 짧은 이름을 쓴다 (중학 2학년 → 중2)
  // 단계 이름도 지금 설정이 아니라 이 단어가 속한 언어에서 가져온다
  const gradeLabel =
    gradesOf(studyLangOfWordId(word.id), uiLang).find((g) => g.id === gradeId)
      ?.short ?? "";
  const unitNo = Math.floor(index / UNIT_SIZE) + 1;
  const posInUnit = (index % UNIT_SIZE) + 1;
  // 마지막 유닛은 20개보다 적을 수 있다.
  const unitLen = Math.min(UNIT_SIZE, total - (unitNo - 1) * UNIT_SIZE);
  const hasSynonyms = (word.synonyms?.length ?? 0) > 0;

  // 단어가 길어도 두 줄로 넘기지 않고 글자 크기를 줄여 한 줄에 담는다.
  // 단어는 이미지 패널 위에 얹히므로 그 안쪽 폭을 기준으로 계산한다.
  // 화면 내용은 최대 480px 로 모이므로 넓은 창에서도 그 폭을 기준으로 잡는다.
  // 화면 좌우 여백(48) + 카드 안쪽 여백(48) + 겹침 영역 좌우 여백(32)
  //   + 스피커 버튼(44) + 버튼과의 간격(12)
  //   + 마이크 버튼(44) + 버튼 사이 간격(8) (따라 말하기를 쓸 수 있을 때만)
  const contentWidth = Math.min(screenWidth, MAX_CONTENT_WIDTH);
  const wordAreaWidth = Math.max(
    110,
    contentWidth - 184 - (canListen ? 52 : 0),
  );
  // 굵은 글씨는 한 글자가 글자 크기의 약 0.58배 너비를 차지한다
  // 최대 크기는 25px (31px 이 너무 커서 20% 줄였다)
  const wordFontSize = Math.max(
    10,
    Math.min(25, Math.floor(wordAreaWidth / (word.word.length * 0.58))),
  );

  /** 듣기를 그만두고 패널도 닫는다 */
  const stopListen = () => {
    stopListenRef.current?.();
    stopListenRef.current = null;
    setListen(null);
  };

  /** 마이크를 켜고 한 번 듣는다. 끝나면 판정 결과를 패널에 보여 준다 */
  const startListen = () => {
    stopListenRef.current?.();
    // 앱이 읽어 주는 소리가 마이크로 들어가 정답으로 잡히지 않게 먼저 끈다.
    // 순번을 올려 두어야 멈추면서 오는 "끝났다" 알림이 듣기를 다시 켜지 않는다
    speakSeq.current++;
    clearTimeout(followTimer.current);
    stopSpeaking();
    const id = word.id;
    // 일본어는 엔진이 한자로 적을지 가나로 적을지 몰라 읽기 가나도 정답으로 친다.
    // 영어의 phonetic 은 발음기호라 견주지 않는다
    const targets =
      studyLangOfWordId(id) === "ja"
        ? [word.word, word.phonetic ?? ""]
        : [word.word];
    setListen({ wordId: id, phase: "listening" });
    stopListenRef.current = listenOnce(speechCode, {
      onResult: (alternatives) => {
        stopListenRef.current = null;
        const result = judge(targets, alternatives);
        // 똑같이 말했으면 "띵동", 아니면 틀렸다는 소리를 낸다 (발음 소리 크기를 따른다)
        playFeedback(
          result.verdict === "correct" ? "correct" : "wrong",
          useAppStore.getState().speechVolume,
        );
        setListen({ wordId: id, phase: "result", ...result });
      },
      onError: (error) => {
        stopListenRef.current = null;
        setListen({ wordId: id, phase: "error", error });
      },
    });
  };

  // 렌더 중에는 ref 를 바꿀 수 없어 그린 뒤에 최신 함수로 바꿔 둔다
  useEffect(() => {
    startListenRef.current = startListen;
  });

  /** 마이크 버튼. 듣는 중이면 그만두고, 아니면 듣기 시작한다 */
  const handleListen = () => (listening ? stopListen() : startListen());

  const handleSpeak = () => {
    if (listening) stopListen();
    playWord();
  };

  const decide = (next: WordStatus) => {
    recordStudy(word.id, next);
    advance();
  };

  return (
    <>
      {/* ── 상단 바: 뒤로 · 유닛/진행 · 자동 넘김 ──────────── */}
      <ScreenHeader>
        <BackButton onPress={onBack} />

        {/* 유닛과 진행 개수를 하나의 알약에 담는다 */}
        <View className="relative h-12 flex-1 flex-row items-center justify-center gap-1.5 overflow-hidden rounded-full bg-surface px-3 shadow-neu-sm">
          <Text
            numberOfLines={1}
            className="text-[14px] font-bold leading-[15px] tracking-tight text-slate-700"
          >
            {gradeLabel} UNIT {unitNo}
          </Text>
          <Text className="text-[14px] leading-[15px] text-slate-300">·</Text>
          <View className="flex-row items-center">
            <Text className="text-[13px] font-extrabold leading-[15px] text-mint">
              {posInUnit}
            </Text>
            <Text className="text-[13px] font-medium leading-[15px] text-slate-400">
              /{unitLen}
            </Text>
          </View>

          {/* 유닛 진행률: 알약 안쪽 하단에 겹쳐서 표시한다 (높이 3px).
              홈·유닛 목록의 진행 막대와 같은 트랙·채움 색을 쓴다 */}
          <View className="absolute inset-x-0 bottom-0 h-[3px] bg-canvas">
            <View
              className="h-full bg-mint"
              style={{ width: `${(posInUnit / unitLen) * 100}%` }}
            />
          </View>
        </View>

        {/* 자동 넘김 켜기/끄기. 앱 전체에서 파인 모양은 "켜짐·선택됨"을 뜻한다 */}
        <Pressable
          accessibilityLabel={t("study.autoAdvanceToggle")}
          accessibilityState={{ checked: autoAdvance }}
          onPress={() => setAutoAdvance(!autoAdvance)}
          className={`h-12 flex-row items-center justify-center gap-1 rounded-full px-3.5 active:scale-95 ${
            autoAdvance
              ? "bg-canvas shadow-neu-inset"
              : "bg-surface shadow-neu-sm"
          }`}
        >
          {autoAdvance ? <PlayIcon size={14} /> : <PauseIcon size={14} />}
          <View
            className={`ml-0.5 rounded-full px-1.5 py-0.5 ${
              autoAdvance ? "bg-mint" : "bg-slate-400"
            }`}
          >
            <Text className="text-[11px] font-black text-white">
              {autoAdvance ? "ON" : "OFF"}
            </Text>
          </View>
        </Pressable>
      </ScreenHeader>

      {/* ── 메인 플래시카드 ──────────────────────────────── */}
      <ScrollView
        ref={scrollRef}
        className="flex-1"
        contentContainerClassName="px-6 pb-10 pt-6"
        // 따라 말하기 패널이 떠 있으면 마지막 내용이 그 밑에 가리지 않게 띄운다
        contentContainerStyle={listenNow ? { paddingBottom: 120 } : undefined}
        showsVerticalScrollIndicator={false}
      >
        <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
          {/* 연상 이미지 + 좌우 이동 버튼.
              바깥 View는 잘라내지 않아야 화살표가 패널 밖으로 걸쳐 보인다.
              이미지가 1024x1024 정사각형이라 패널도 정사각형으로 꽉 채운다 */}
          <View className="relative w-full" {...swipe.panHandlers}>
            <View
              onLayout={(e) => setPanelW(e.nativeEvent.layout.width)}
              className="aspect-square w-full overflow-hidden rounded-2xl bg-canvas shadow-neu-inset"
            >
              {/* 그림만 손가락을 따라 흐른다. 위에 얹힌 단어·발음 영역은 제자리에 둔다.
                  앞·뒤 그림을 양옆에 붙여 놓아 밀면 옆 그림이 따라 들어온다 */}
              <Animated.View
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  transform: [{ translateX: dragX }],
                }}
              >
                {/* 앞·현재·뒤 그림을 단어 id 로 묶어 둔다. 다음 단어로 넘어가면
                    옆에 미리 그려 둔 그림이 그대로 가운데 자리로 옮겨 와서
                    새로 불러오며 깜빡이지 않는다 */}
                {[
                  { w: prev, offset: -panelW },
                  { w: word, offset: 0 },
                  { w: next, offset: panelW },
                ].map(({ w, offset }) =>
                  w && (offset === 0 || panelW > 0) ? (
                    <WordImage key={w.id} word={w} offset={offset} />
                  ) : null,
                )}
              </Animated.View>

              {/* 단어 · 발음기호 · 발음 듣기: 이미지 위쪽에 반투명 블러(Glassmorphism) 배경으로 표시 */}
              <View
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  borderTopLeftRadius: 16,
                  borderTopRightRadius: 16,
                  overflow: "hidden",
                  borderBottomWidth: 1,
                  borderBottomColor: "rgba(255, 255, 255, 0.45)",
                }}
              >
                <BlurView
                  intensity={65}
                  tint="light"
                  style={{
                    width: "100%",
                    ...(Platform.OS === "web"
                      ? {
                          backdropFilter: "saturate(180%) blur(7px)",
                          WebkitBackdropFilter: "saturate(180%) blur(7px)",
                        }
                      : {}),
                  }}
                >
                  <View
                    style={{
                      backgroundColor: "rgba(241, 242, 246, 0.05)",
                    }}
                    className="flex-row items-start justify-between px-4 pb-3 pt-4"
                  >
                    <View className="flex-1 pr-3">
                      <Text
                        numberOfLines={1}
                        adjustsFontSizeToFit
                        style={{
                          fontSize: wordFontSize,
                          lineHeight: Math.round(wordFontSize * 1.15),
                        }}
                        className="font-black tracking-normal text-slate-900"
                      >
                        {word.word}
                      </Text>
                      {(word.phonetic || word.reading || word.pos?.length) && (
                        <View className="mt-1 flex-row flex-wrap items-center gap-2">
                          {word.phonetic && (
                            <Text className="text-[13px] tracking-wide text-slate-500">
                              {word.phonetic}
                            </Text>
                          )}
                          {/* 가나 옆에 한국어로 읽는 법을 붙인다 (わたし 와타시) */}
                          {word.reading && (
                            <Text className="text-[13px] tracking-wide text-mint">
                              {word.reading}
                            </Text>
                          )}
                          {/* 품사 표시. 뜻이 여럿이면 여러 개가 붙는다 */}
                          {word.pos?.map((code) => (
                            <View
                              key={code}
                              className="rounded-md bg-canvas px-1.5 py-0.5 shadow-neu-sm"
                            >
                              <Text className="text-[11px] font-bold text-mint-dark">
                                {t(`pos.${code}` as never)}
                              </Text>
                            </View>
                          ))}
                        </View>
                      )}
                    </View>
                    <View className="flex-row gap-2">
                      {/* 따라 말하기: 단어를 말하면 맞게 들렸는지 알려 준다 */}
                      {canListen && (
                        <Pressable
                          accessibilityLabel={
                            listening
                              ? t("study.listenStop")
                              : t("study.listen")
                          }
                          accessibilityState={{ busy: listening }}
                          onPress={handleListen}
                          className={`h-11 w-11 items-center justify-center rounded-full active:scale-95 ${
                            listening
                              ? "bg-canvas shadow-neu-inset"
                              : "bg-surface shadow-neu-sm"
                          }`}
                        >
                          <MicIcon color={listening ? MINT : "#334155"} />
                        </Pressable>
                      )}
                      {/* 설정에서 음소거해 두면 눌러도 소리가 안 난다.
                        왜 조용한지 알 수 있게 버튼을 흐리게 보여 준다 */}
                      <Pressable
                        accessibilityLabel={
                          speechVolume === 0
                            ? t("settings.speechMuted")
                            : t("study.speak", { word: word.word })
                        }
                        onPress={handleSpeak}
                        className={`h-11 w-11 items-center justify-center rounded-full active:scale-95 ${
                          speechVolume === 0
                            ? "bg-surface opacity-40 shadow-neu-sm"
                            : speaking
                              ? "bg-canvas shadow-neu-inset"
                              : "bg-surface shadow-neu-sm"
                        }`}
                      >
                        <SpeakerIcon
                          color={
                            speechVolume === 0
                              ? "#94a3b8"
                              : speaking
                                ? MINT
                                : "#334155"
                          }
                        />
                      </Pressable>
                    </View>
                  </View>
                </BlurView>
              </View>

              {/* 자동 넘김 초시계: 이미지 카드 안쪽 하단에 겹쳐서 표시한다 */}
              <View className="absolute inset-x-0 bottom-0 h-1.5 bg-canvas">
                {/* Animated.View 에는 className 이 적용되지 않아
                    높이와 색을 인라인 스타일로 지정한다 */}
                <Animated.View
                  style={{
                    height: "100%",
                    backgroundColor: autoAdvance ? MINT : "#cbd5e1",
                    width: progress.interpolate({
                      inputRange: [0, 1],
                      outputRange: ["0%", "100%"],
                    }),
                  }}
                />
              </View>
            </View>

            {/* 이전 단어 (버튼 높이 36px의 절반만큼 올려 세로 중앙에 둔다) */}
            <Pressable
              accessibilityLabel={t("study.prevWord")}
              disabled={!prevId}
              onPress={() => onNavigate(prevId)}
              style={{ top: "50%", marginTop: -18, left: -16 }}
              className={`absolute h-9 w-9 items-center justify-center rounded-full bg-surface shadow-neu-sm active:scale-95 active:shadow-neu-pressed ${
                prevId ? "" : "opacity-40"
              }`}
            >
              <ChevronLeftIcon size={14} />
            </Pressable>

            {/* 다음 단어 */}
            <Pressable
              accessibilityLabel={t("study.nextWord")}
              disabled={!nextId && !isUnitEnd}
              onPress={advance}
              style={{ top: "50%", marginTop: -18, right: -16 }}
              className={`absolute h-9 w-9 items-center justify-center rounded-full bg-surface shadow-neu-sm active:scale-95 active:shadow-neu-pressed ${
                nextId || isUnitEnd ? "" : "opacity-40"
              }`}
            >
              <ChevronRightIcon size={14} />
            </Pressable>
          </View>

          {/* 한국어 뜻풀이 */}
          <View className="mt-4 rounded-2xl bg-surface p-4 shadow-neu-sm">
            {/* 한글 뜻과 가리기 버튼을 한 줄에 둔다 (제목 없이) */}
            <View className="flex-row items-center justify-between gap-3">
              {showAnswer ? (
                <Text className="flex-1 text-[20px] font-black tracking-tight text-slate-950">
                  {word.meaning}
                </Text>
              ) : (
                /* 가려진 자리. 눌러도 바로 뜻이 나오게 해 둔다 */
                <Pressable
                  onPress={() => setAnswerHiddenFor(null)}
                  className="h-[26px] flex-1 items-center justify-center rounded-xl bg-canvas shadow-neu-inset active:opacity-70"
                >
                  <Text className="text-[13px] font-bold tracking-[3px] text-slate-400">
                    ● ● ● ●
                  </Text>
                </Pressable>
              )}
              <Pressable
                onPress={() => setAnswerHiddenFor(showAnswer ? word.id : null)}
                className="flex-row items-center gap-1 active:opacity-70"
              >
                <Text className="text-[12px] font-bold text-mint">
                  {showAnswer ? t("study.hide") : t("study.show")}
                </Text>
                {showAnswer ? <ChevronUpIcon /> : <ChevronDownIcon />}
              </Pressable>
            </View>

            {/* 예문·유의어·어원. 뜻과 함께 가려진다 —
                단어만 보고 스스로 떠올려 보기 좋다.
                반의어·어근 풀이·같은 어근 단어·의미 비교는 토플 코스에만 있다 */}
            {showAnswer &&
              (word.example ||
                hasSynonyms ||
                word.etymology ||
                word.antonyms ||
                word.roots ||
                word.senseFlow ||
                word.family ||
                word.compare) && (
                <View className="mt-4 gap-5 border-t border-slate-200 pt-4">
                  {word.example && (
                    <LabeledSection label={t("study.example")}>
                      <Text className="text-[15px] font-semibold leading-snug text-slate-800">
                        {word.example}
                      </Text>
                      {word.exampleTr && (
                        <Text className="mt-1 text-[14px] font-medium leading-snug text-slate-500">
                          {word.exampleTr}
                        </Text>
                      )}
                    </LabeledSection>
                  )}

                  {hasSynonyms && (
                    <LabeledSection label={t("study.synonyms")}>
                      <SynonymList items={word.synonyms!} />
                    </LabeledSection>
                  )}

                  {word.antonyms && (
                    <LabeledSection label={t("study.antonyms")}>
                      <SynonymList items={word.antonyms} />
                    </LabeledSection>
                  )}

                  {word.etymology && (
                    <LabeledSection label={t("study.etymology")}>
                      <Text className="text-[14px] leading-relaxed text-slate-600">
                        {word.etymology}
                      </Text>
                    </LabeledSection>
                  )}

                  {/* 어근 공식 아래에 글자 그대로의 뜻부터 지금 뜻까지 이어 보여 준다.
                    어근 공식이 없는 낱말은 뜻이 넓어진 순서만 보여 준다 */}
                  {(word.roots || word.senseFlow) && (
                    <LabeledSection label={t("study.roots")}>
                      {word.roots && (
                        <Text className="mb-1 text-[15px] font-semibold leading-snug text-lavender">
                          {word.roots.formula}
                        </Text>
                      )}
                      <Text className="text-[14px] leading-relaxed text-slate-600">
                        {[
                          ...(word.roots ? [`“${word.roots.literal}”`] : []),
                          ...(word.senseFlow ?? []),
                        ].join(" → ")}
                      </Text>
                    </LabeledSection>
                  )}

                  {/* 같은 어근 단어는 풀이가 길어 한 줄에 한 단어씩 두고 줄바꿈되게 한다 */}
                  {word.family && (
                    <LabeledSection label={t("study.family")}>
                      <View className="gap-1.5">
                        {word.family.map((item) => (
                          <Text
                            key={item.word}
                            className="text-[14px] leading-snug text-slate-600"
                          >
                            <Text className="text-[15px] font-semibold text-lavender">
                              {item.word}
                            </Text>
                            {"  "}
                            {item.meaning}
                          </Text>
                        ))}
                      </View>
                    </LabeledSection>
                  )}

                  {word.compare && (
                    <LabeledSection label={t("study.compare")}>
                      <Text className="text-[13px] font-bold text-slate-500">
                        {word.compare.title}
                      </Text>
                      <View className="mt-1.5 gap-1.5">
                        {word.compare.items.map((item) => (
                          <Text
                            key={item.word}
                            className="text-[14px] leading-snug text-slate-600"
                          >
                            <Text className="font-semibold text-lavender">
                              {item.word}
                            </Text>
                            {"  "}
                            {item.note}
                          </Text>
                        ))}
                      </View>
                    </LabeledSection>
                  )}
                </View>
              )}
          </View>
        </View>
      </ScrollView>

      {/* ── 학습 평가 버튼 (가운데는 단어장에 담기) ────────── */}
      <View className="relative">
        {/* 따라 말하기 패널: 독 바로 위에 떠서 파형과 판정을 보여 준다 */}
        {listenNow && (
          <FollowAlongDock
            word={word.word}
            state={listenNow}
            onMic={handleListen}
            onClose={stopListen}
          />
        )}
        <View className="mx-6 flex-row items-stretch gap-2 pb-4 pt-3">
          {/* 홈으로 이동 버튼 */}
          <Pressable
            onPress={() => router.replace("/")}
            accessibilityRole="button"
            accessibilityLabel={t("nav.home")}
            className="h-[52px] w-[52px] shrink-0 self-center items-center justify-center rounded-full bg-surface shadow-neu-sm active:scale-[0.98] active:shadow-neu-pressed"
          >
            <Text
              numberOfLines={1}
              className="text-[13px] font-bold tracking-tight text-slate-600"
            >
              {t("nav.home")}
            </Text>
          </Pressable>

          {/* 판정 버튼 둘이 남는 자리를 똑같이 나눠 가진다 */}
          <Pressable
            onPress={() => decide("unsure")}
            style={{ flex: 1 }}
            className="flex-row items-center justify-center rounded-full bg-surface px-1 py-4 shadow-neu-sm active:scale-[0.98] active:shadow-neu-pressed"
          >
            <Text
              numberOfLines={1}
              className="text-[13px] font-bold tracking-tight text-slate-800"
            >
              {t("study.unsure")}
            </Text>
          </Pressable>

          {/* 저장 버튼도 가로는 글씨('저장됨')에 맞춰 못 박는다(shrink-0).
            늘었다 줄었다 하는 것은 '헷갈려요'·'외웠어요' 둘뿐이다 */}
          <Pressable
            onPress={() => toggleSaved(word.id)}
            accessibilityRole="button"
            accessibilityState={{ selected: isSaved }}
            accessibilityLabel={t("study.saveToggle")}
            className={`w-[64px] shrink-0 flex-row items-center justify-center rounded-full px-1 active:scale-[0.98] ${
              isSaved
                ? "bg-canvas shadow-neu-inset"
                : "bg-surface shadow-neu-sm active:shadow-neu-pressed"
            }`}
          >
            <Text
              numberOfLines={1}
              className={`text-[13px] font-bold tracking-tight ${
                isSaved ? "text-mint-dark" : "text-slate-500"
              }`}
            >
              {t(isSaved ? "study.saved" : "study.save")}
            </Text>
          </Pressable>

          {/* 외웠어요는 앱의 주요 동작 버튼(PillButton primary)과 같은 연민트 */}
          <Pressable
            onPress={() => decide("known")}
            style={{ flex: 1 }}
            className="flex-row items-center justify-center rounded-full bg-[#dcf2ea] px-1 py-4 shadow-neu-sm active:scale-[0.98] active:shadow-neu-pressed"
          >
            <Text
              numberOfLines={1}
              className="text-[13px] font-bold tracking-tight text-mint-dark"
            >
              {t("study.known")}
            </Text>
          </Pressable>
        </View>
      </View>
    </>
  );
}

/** 파형 칸 수. 왼쪽부터 막대가 쌓이고, 다 차면 왼쪽으로 밀려난다 */
const WAVE_SLOTS = 44;
/** 막대 하나가 쌓이는 간격 (ms) */
const WAVE_STEP_MS = 100;
/** 녹음 카드의 글자. 숫자 폭이 같아야 시간이 흔들리지 않는다 */
const MONO = Platform.select({
  ios: "Menlo",
  android: "monospace",
  default: "ui-monospace, SFMono-Regular, Menlo, monospace",
});
const WAVE_INK = "#2b2b2b";
const WAVE_CURSOR = "#ef4136";

/** 0:07 처럼 흐른 시간을 "00:07" 로 */
function formatElapsed(ms: number) {
  const sec = Math.floor(ms / 1000);
  const mm = String(Math.floor(sec / 60)).padStart(2, "0");
  const ss = String(sec % 60).padStart(2, "0");
  return `${mm}:${ss}`;
}

/**
 * 녹음기 화면처럼 내 목소리를 그린다.
 * 위아래로 대칭인 검은 막대가 왼쪽부터 쌓이고, 지금 위치에 빨간 세로선,
 * 그 오른쪽 남은 자리는 점선으로 보여 준다.
 * 마이크 크기를 읽지 못하는 환경이면 잔잔하게 출렁이는 모양으로 대신한다.
 */
function Waveform({ word }: { word: string }) {
  const [bars, setBars] = useState<number[]>([]);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    let peak = 0;
    let fake = false;
    const stop = watchMicLevel(
      (level) => {
        peak = Math.max(peak, level);
      },
      () => {
        fake = true;
      },
    );
    const startedAt = Date.now();
    let n = 0;
    const timer = setInterval(() => {
      n++;
      const value = fake ? 0.3 + 0.35 * Math.abs(Math.sin(n / 2.5)) : peak;
      peak = 0;
      setBars((prev) => [...prev, value].slice(-WAVE_SLOTS));
      setElapsed(Date.now() - startedAt);
    }, WAVE_STEP_MS);
    return () => {
      clearInterval(timer);
      stop();
    };
  }, []);

  const dots = Math.max(0, WAVE_SLOTS - bars.length);

  return (
    <View>
      {/* 오른쪽 위 닫기 버튼과 겹치지 않게 시간 옆을 비워 둔다 */}
      <View className="flex-row items-center justify-between pr-6">
        <Text
          numberOfLines={1}
          style={{ fontFamily: MONO, letterSpacing: 0.5 }}
          className="flex-1 text-[12px] text-slate-400"
        >
          LISTENING #{word.toUpperCase()}
        </Text>
        <Text
          style={{ fontFamily: MONO }}
          className="ml-2 text-[12px] text-slate-400"
        >
          {formatElapsed(elapsed)}
        </Text>
      </View>
      <View className="mt-2 h-14 flex-row items-center">
        {bars.map((v, i) => (
          <View
            key={i}
            style={{
              flex: 1,
              alignItems: "center",
            }}
          >
            <View
              style={{
                width: 2.5,
                height: 4 + Math.min(1, v) * 48,
                backgroundColor: WAVE_INK,
              }}
            />
          </View>
        ))}
        {/* 지금 듣고 있는 자리 */}
        <View
          style={{
            width: 2,
            height: 56,
            marginHorizontal: 3,
            backgroundColor: WAVE_CURSOR,
          }}
        />
        {Array.from({ length: dots }, (_, i) => (
          <View key={`dot-${i}`} style={{ flex: 1, alignItems: "center" }}>
            <View
              style={{
                width: 2,
                height: 2,
                borderRadius: 1,
                backgroundColor: "#cbd5e1",
              }}
            />
          </View>
        ))}
      </View>
    </View>
  );
}

/**
 * 따라 말하기 패널. 하단 독 바로 위에 떠 있다.
 * 듣는 동안은 내 목소리 파형을, 끝나면 판정과 들린 말을 보여 준다.
 */
function FollowAlongDock({
  word,
  state,
  onMic,
  onClose,
}: {
  word: string;
  state: ListenState;
  onMic: () => void;
  onClose: () => void;
}) {
  const t = useT();
  const listening = state.phase === "listening";

  const look =
    state.phase === "result"
      ? {
          correct: {
            box: "bg-[#dcf2ea]",
            title: "text-mint-dark",
            label: `✓ ${t("study.listenCorrect")}`,
          },
          close: {
            box: "bg-amber-50",
            title: "text-amber-700",
            label: t("study.listenAlmost"),
          },
          wrong: {
            box: "bg-rose-50",
            title: "text-rose-600",
            label: t("study.listenWrong"),
          },
        }[state.verdict]
      : null;

  const errorMessage =
    state.phase === "error"
      ? {
          "no-speech": t("study.listenNoSpeech"),
          "not-allowed": t("study.listenDenied"),
          unsupported: t("study.listenUnsupported"),
          failed: t("study.listenFailed"),
        }[state.error]
      : null;

  if (listening) {
    return (
      <View
        accessibilityLiveRegion="polite"
        accessibilityLabel={t("study.listening")}
        style={{
          position: "absolute",
          left: 24,
          right: 24,
          bottom: "100%",
          zIndex: 10,
          backgroundColor: "#f7f7f7",
        }}
        className="mb-1 rounded-3xl px-5 pb-4 pt-4 shadow-neu"
      >
        <Waveform word={word} />
        {/* 듣기 멈추기 */}
        <Pressable
          accessibilityLabel={t("study.listenStop")}
          onPress={onClose}
          hitSlop={8}
          style={{ position: "absolute", top: 6, right: 6 }}
          className="h-7 w-7 items-center justify-center rounded-full active:opacity-60"
        >
          <CloseIcon size={14} />
        </Pressable>
      </View>
    );
  }

  return (
    <View
      accessibilityLiveRegion="polite"
      style={{
        position: "absolute",
        left: 24,
        right: 24,
        bottom: "100%",
        zIndex: 10,
      }}
      className={`mb-1 flex-row items-center gap-3 rounded-3xl px-3 py-3 shadow-neu ${
        look?.box ?? "bg-surface"
      }`}
    >
      {/* 마이크: 눌러서 다시 말한다 */}
      <Pressable
        accessibilityLabel={t("study.listen")}
        onPress={onMic}
        className="h-11 w-11 items-center justify-center rounded-full bg-surface shadow-neu-sm active:scale-95"
      >
        <MicIcon color="#334155" />
      </Pressable>

      <View className="flex-1">
        {look && state.phase === "result" ? (
          <>
            <Text className={`text-[16px] font-black ${look.title}`}>
              {look.label}
            </Text>
            <Text
              numberOfLines={1}
              className="mt-0.5 text-[13px] font-medium text-slate-500"
            >
              {t("study.listenHeard", { text: state.heard })}
            </Text>
          </>
        ) : (
          <Text className="text-[13px] font-semibold text-slate-500">
            {errorMessage}
          </Text>
        )}
      </View>

      <Pressable
        accessibilityLabel={t("study.listenClose")}
        onPress={onClose}
        hitSlop={8}
        className="h-8 w-8 items-center justify-center rounded-full active:opacity-60"
      >
        <CloseIcon size={18} />
      </Pressable>
    </View>
  );
}
