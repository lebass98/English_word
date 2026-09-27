import { useLocalSearchParams, useRouter } from "expo-router";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  Animated,
  Easing,
  Pressable,
  ScrollView,
  Text,
  useWindowDimensions,
  View,
} from "react-native";
import { Image } from "expo-image";
import { BackButton } from "../../src/components/BackButton";
import {
  BookIcon,
  CheckIcon,
  CloseIcon,
  EditNoteIcon,
  HeadphonesIcon,
  LightbulbIcon,
  ShuffleIcon,
  SpeakerIcon,
  SpellcheckIcon,
  StarIcon,
  TextFieldsIcon,
  type IconProps,
} from "../../src/components/icons";
import { PillButton } from "../../src/components/PillButton";
import {
  MAX_CONTENT_WIDTH,
  SCREEN_PADDING_X,
  Screen,
  ScreenHeader,
} from "../../src/components/Screen";
import { useGrade } from "../../src/constants/grades";
import {
  studyLanguageOf,
  studyLangOfWordId,
} from "../../src/constants/languages";
import { useVocab, type Word } from "../../src/constants/words";
import { useT, type StringKey } from "../../src/i18n";
import {
  buildQuiz,
  imageOf,
  imageUrlsOf,
  isQuizKind,
  QUIZ_KINDS,
  QUIZ_SIZE,
  scoreOf,
  SPELLING_LIVES,
  type QuizKind,
  type QuizQuestion,
} from "../../src/lib/quiz";
import { speakWord, stopSpeaking } from "../../src/lib/speech";
import { useAppStore } from "../../src/stores/useAppStore";

const MINT = "#0EB582";
/** 오답 표시에 쓰는 빨강 */
const CORAL = "#ef4444";

/** 보기 그림 한 칸의 테두리 여백 (p-1.5) */
const CELL_PAD = 6;

/** 보기 그림 사이 간격. 좌우·세로를 같은 값으로 둔다 */
const GRID_GAP = 12;

/** 유형 선택 카드 2열 간격. 학년 화면의 유닛 카드와 같은 값 */
const GRID_GAP_LG = 16;

/** 보기 네 줄이 쓰는 세로 자리 (버튼 52 + 사이 간격 10) */
const CHOICE_LIST_H = 52 * 4 + 10 * 3;

/** 안내 문구 한 줄과 위아래 간격 */
const PROMPT_H = 42;

/** 제시부와 보기 사이 간격 (gap-6) */
const SECTION_GAP = 24;

/** 좌우로 나눠 놓을 만큼 넓은지 보는 기준 (px) */
const TWO_PANE_MIN = 600;

/** 넓은 화면에서 쓰는 내용 최대 폭 */
const WIDE_MAX_WIDTH = 960;

/** 그림 열 너비의 최소·최대. 작은 폰에서 뭉개지거나 큰 화면에서 과해지는 걸 막는다 */
const MIN_COLUMN = 200;
const MAX_COLUMN = 460;

/** 정답을 맞혔을 때 다음 문제로 넘어가기까지 기다리는 시간 (ms) */
const REVEAL_MS = 700;

/** 틀렸을 때는 정답을 확인할 시간이 필요해 더 오래 보여 준다 */
const REVEAL_WRONG_MS = 1500;

/** 한 문제의 채점 결과 */
interface Answered {
  question: QuizQuestion;
  /** 사용자가 고른 단어. 시간이 다 돼서 못 골랐으면 null */
  picked: Word | null;
  correct: boolean;
}

export default function QuizScreen() {
  const {
    gradeId: raw,
    unit,
    size,
    kind: kindParam,
  } = useLocalSearchParams<{
    gradeId: string;
    unit?: string;
    size?: string;
    kind?: string;
  }>();
  const gradeId = raw ?? "";
  /** 유닛을 끝내고 바로 들어온 확인 퀴즈면 그 유닛 번호가 들어온다 */
  const unitNo = unit ? Number(unit) : null;
  const quizSize = size ? Number(size) : QUIZ_SIZE;

  /*
   * 낼 문제 유형.
   *
   * 유닛 확인 퀴즈는 고르는 자리 없이 바로 시작하므로 늘 섞어서 낸다.
   * 단어 퀴즈로 들어오면 먼저 유형을 고르게 하고, 고른 값이 주소에 실려 돌아온다.
   */
  const chosen = isQuizKind(kindParam) ? kindParam : null;
  const kinds: readonly QuizKind[] = useMemo(
    () => (chosen ? [chosen] : QUIZ_KINDS),
    [chosen],
  );
  /** 유닛 퀴즈가 아니고 유형도 안 골랐으면 고르는 화면을 먼저 보여 준다 */
  const needsKind = !unitNo && !chosen && kindParam !== "mix";
  const t = useT();
  const { width: screenWidth } = useWindowDimensions();
  /*
   * 좁은 화면은 다른 화면과 같은 폰 폭을 쓰고,
   * 좌우로 나눠 놓을 만큼 넓을 때만 내용 폭을 키운다.
   */
  const screenMaxWidth =
    screenWidth >= TWO_PANE_MIN + SCREEN_PADDING_X * 2
      ? WIDE_MAX_WIDTH
      : MAX_CONTENT_WIDTH;
  const vocab = useVocab();
  const grade = useGrade(gradeId);

  const recordStudy = useAppStore((s) => s.recordStudy);
  const recordQuiz = useAppStore((s) => s.recordQuiz);
  const speechVolume = useAppStore((s) => s.speechVolume);
  /** 유닛 확인 퀴즈는 8문제짜리라 학년 전체 기록과 섞지 않는다 */
  const recordKey = unitNo
    ? `${gradeId}:u${unitNo}`
    : chosen
      ? `${gradeId}:k-${chosen}`
      : gradeId;
  const best = useAppStore((s) => s.quizRecords[recordKey]?.best ?? 0);

  // 학년 단어 목록. 없는 학년이면 빈 배열이 매번 새로 생기므로 메모해 둔다
  const gradeWords = useMemo(
    () => vocab.byLevel[gradeId] ?? [],
    [vocab, gradeId],
  );
  // 유닛 확인 퀴즈는 그 유닛 단어에서만 낸다. 오답 보기는 학년 전체에서 가져온다
  const words = useMemo(
    () =>
      unitNo ? (vocab.unitsOf(gradeId)[unitNo - 1]?.words ?? []) : gradeWords,
    [vocab, gradeId, unitNo, gradeWords],
  );

  /**
   * 한 판은 시작할 때 한 번만 만든다.
   * entries 는 문제를 풀 때마다 바뀌는데, 그때마다 다시 만들면
   * 풀던 문제가 통째로 갈린다. 그래서 의존성에 넣지 않고 판 번호로만 새로 뽑는다.
   */
  const [round, setRound] = useState(0);
  const [questions, setQuestions] = useState<QuizQuestion[]>(() =>
    buildQuiz(
      words,
      useAppStore.getState().entries,
      quizSize,
      kinds,
      gradeWords,
    ),
  );

  const [index, setIndex] = useState(0);
  const [picked, setPicked] = useState<Word | null>(null);
  /** 정답이 공개됐는지. 철자 맞추기처럼 보기를 안 고르는 유형도 있어 따로 둔다 */
  const [revealed, setRevealed] = useState(false);
  const [log, setLog] = useState<Answered[]>([]);

  const question = questions[index];
  const done = questions.length > 0 && index >= questions.length;

  const speechCode = useMemo(
    () =>
      question
        ? studyLanguageOf(studyLangOfWordId(question.answer.id)).speechCode
        : "en-US",
    [question],
  );

  // 판이 끝나면 소리를 멈춘다. 결과 화면에서 발음이 이어 나오면 어수선하다
  useEffect(() => stopSpeaking, []);

  /*
   * 다음 두 문제의 그림을 미리 받아 둔다.
   * 그림은 CDN 에서 오므로 미리 받지 않으면 문제를 넘길 때마다 빈 칸을 보게 된다.
   */
  useEffect(() => {
    const urls = questions
      .slice(index, index + 3)
      .flatMap((q) => imageUrlsOf(q));
    if (urls.length) Image.prefetch(urls, { cachePolicy: "disk" });
  }, [questions, index]);

  /** 새 판을 뽑는다. 기록이 쌓였으면 헷갈린 단어가 더 자주 나온다 */
  const restart = useCallback(() => {
    setQuestions(
      buildQuiz(
        words,
        useAppStore.getState().entries,
        quizSize,
        kinds,
        gradeWords,
      ),
    );
    setIndex(0);
    setPicked(null);
    setRevealed(false);
    setLog([]);
    setRound((r) => r + 1);
  }, [words, gradeWords, quizSize, kinds]);

  // 학년을 바꿔 들어오면 판을 다시 뽑는다.
  // effect 가 아니라 렌더 중에 맞춰야 이전 학년 문제가 한 번 스쳐 지나가지 않는다
  const scope = `${gradeId}:${unitNo ?? "all"}:${chosen ?? "mix"}`;
  const [builtFor, setBuiltFor] = useState(scope);
  if (builtFor !== scope) {
    setBuiltFor(scope);
    restart();
  }

  if (needsKind) {
    return (
      <KindPicker
        gradeId={gradeId}
        gradeLabel={grade?.label ?? t("quiz.title")}
      />
    );
  }

  if (questions.length === 0) {
    return (
      <Screen>
        <ScreenHeader>
          <BackButton fallbackHref="/" />
          <Text className="text-2xl font-bold text-ink">{t("quiz.title")}</Text>
        </ScreenHeader>
        <View className="flex-1 items-center justify-center px-8">
          <Text className="text-center text-[14px] text-slate-400">
            {t("quiz.notEnough")}
          </Text>
        </View>
      </Screen>
    );
  }

  if (done) {
    return (
      <QuizResult
        gradeId={gradeId}
        recordKey={recordKey}
        gradeLabel={grade?.label ?? ""}
        log={log}
        previousBest={best}
        onRestart={restart}
        onRecord={recordQuiz}
      />
    );
  }

  const correctCount = log.filter((a) => a.correct).length;
  const combo = comboOf(log);

  /**
   * 한 문제를 채점한다.
   * 보기를 고르는 유형은 고른 단어가 들어오고, 철자 맞추기는 null 이 들어온다.
   */
  const submit = (choice: Word | null, correct: boolean) => {
    // 정답이 드러난 동안 두 번째로 누른 건 무시한다
    if (revealed) return;
    setPicked(choice);
    setRevealed(true);

    // 맞히면 외운 것으로, 틀리면 헷갈리는 것으로 기록한다.
    // 이 기록이 다음 판의 출제 가중치가 된다
    recordStudy(question.answer.id, correct ? "known" : "unsure");
    speakWord(question.answer.word, {
      lang: speechCode,
      volume: speechVolume,
    });

    setTimeout(
      () => {
        setLog((prev) => [...prev, { question, picked: choice, correct }]);
        setPicked(null);
        setRevealed(false);
        setIndex((i) => i + 1);
      },
      correct ? REVEAL_MS : REVEAL_WRONG_MS,
    );
  };

  return (
    <Screen maxWidth={screenMaxWidth}>
      <ScreenHeader>
        <BackButton fallbackHref={`/grade/${gradeId}`} />
        <View className="flex-1">
          <Text className="text-[15px] font-bold text-ink">
            {unitNo
              ? t("quiz.unitTitle", { unit: unitNo })
              : (grade?.label ?? t("quiz.title"))}
          </Text>
          <Text className="mt-0.5 text-[12px] text-slate-500">
            {index + 1} / {questions.length}
          </Text>
        </View>
        {/* 연속 정답은 3개부터 보여 준다. 1~2개에 띄우면 늘 켜져 있어 밋밋해진다 */}
        {combo >= 3 && <ComboBadge label={t("quiz.combo", { count: combo })} />}
        <View className="rounded-full bg-surface px-3 py-1 shadow-neu-sm">
          <Text className="text-[12px] font-bold text-slate-600">
            {correctCount}
          </Text>
        </View>
      </ScreenHeader>

      <ProgressBar current={index} total={questions.length} />

      <QuizBody
        key={`${round}-${index}`}
        question={question}
        picked={picked}
        revealed={revealed}
        onSubmit={submit}
        speechCode={speechCode}
        speechVolume={speechVolume}
      />
    </Screen>
  );
}

/** 고를 수 있는 문제 유형. "섞어서"가 맨 앞이다 */
const KIND_OPTIONS: {
  value: QuizKind | "mix";
  Icon: (props: IconProps) => React.ReactElement;
}[] = [
  { value: "mix", Icon: ShuffleIcon },
  { value: "wordToImage", Icon: TextFieldsIcon },
  { value: "wordToMeaning", Icon: BookIcon },
  { value: "meaningToWord", Icon: LightbulbIcon },
  { value: "listenToWord", Icon: HeadphonesIcon },
  { value: "cloze", Icon: EditNoteIcon },
  { value: "spelling", Icon: SpellcheckIcon },
];

/**
 * 문제 유형 고르는 화면.
 * 단어 퀴즈로 들어오면 먼저 이 화면이 뜬다.
 * 유닛을 끝내고 자동으로 이어지는 확인 퀴즈는 이 화면 없이 섞어서 바로 시작한다.
 */
function KindPicker({
  gradeId,
  gradeLabel,
}: {
  gradeId: string;
  gradeLabel: string;
}) {
  const t = useT();
  const router = useRouter();
  const records = useAppStore((s) => s.quizRecords);
  const { width: screenWidth } = useWindowDimensions();

  // 학년 화면의 유닛 카드와 같은 2열·16px 간격으로 맞춘다
  const contentWidth =
    Math.min(screenWidth, MAX_CONTENT_WIDTH) - SCREEN_PADDING_X * 2;
  const cardWidth = Math.floor((contentWidth - GRID_GAP_LG) / 2);

  return (
    <Screen>
      <ScreenHeader>
        <BackButton fallbackHref={`/grade/${gradeId}`} />
        <View className="flex-1">
          <Text className="text-2xl font-bold text-ink">{t("quiz.title")}</Text>
          <Text className="mt-0.5 text-[13px] text-slate-500">
            {gradeLabel}
          </Text>
        </View>
      </ScreenHeader>

      <ScrollView contentContainerClassName="gap-4 px-6 pb-10 pt-6">
        <Text className="text-[13px] text-slate-500">
          {t("quiz.chooseKind")}
        </Text>

        <View
          style={{ gap: GRID_GAP_LG }}
          className="flex-row flex-wrap justify-center"
        >
          {KIND_OPTIONS.map(({ value, Icon }) => {
            // 섞어서는 예전 기록을 그대로 쓰고, 유형별은 따로 쌓는다
            const best =
              records[value === "mix" ? gradeId : `${gradeId}:k-${value}`]
                ?.best;
            return (
              <Pressable
                key={value}
                onPress={() => router.push(`/quiz/${gradeId}?kind=${value}`)}
                accessibilityRole="button"
                // 섞어서는 한 줄을 통째로 쓰고, 나머지 여섯 개가 2열 3줄로 맞아떨어진다
                style={{ width: value === "mix" ? contentWidth : cardWidth }}
                className="items-center gap-1.5 rounded-3xl bg-surface px-3 py-5 shadow-neu-card active:shadow-neu-pressed"
              >
                {/* 아이콘 자리는 그림자 없이 둔다. 카드 자체 그림자만 남긴다 */}
                <View className="h-12 w-12 items-center justify-center">
                  <Icon size={28} color="#0EB582" />
                </View>
                <Text
                  numberOfLines={1}
                  className="mt-1 text-[14px] font-bold text-ink"
                >
                  {t(`quiz.kind.${value}` as StringKey)}
                </Text>
                <Text
                  numberOfLines={2}
                  className="text-center text-[11px] leading-[15px] text-slate-500"
                >
                  {t(`quiz.kind.${value}Desc` as StringKey)}
                </Text>
                {/* 한 번이라도 풀었으면 최고점을 보여 준다. 자리를 늘 차지해 카드 높이가 흔들리지 않는다 */}
                <Text
                  className={`mt-0.5 text-[11px] font-bold ${
                    best ? "text-mint" : "text-transparent"
                  }`}
                >
                  {best ? t("quiz.best", { score: best }) : "-"}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </ScrollView>
    </Screen>
  );
}

/** 맨 뒤에서부터 이어 맞힌 개수 */
function comboOf(log: Answered[]): number {
  let n = 0;
  for (let i = log.length - 1; i >= 0; i--) {
    if (!log[i].correct) break;
    n++;
  }
  return n;
}

/** 한 판에서 나온 최대 연속 정답 */
function bestComboOf(log: Answered[]): number {
  let best = 0;
  let run = 0;
  for (const a of log) {
    run = a.correct ? run + 1 : 0;
    if (run > best) best = run;
  }
  return best;
}

/**
 * 듣기 문제의 스피커 버튼.
 * 문제를 푸는 동안 은은하게 고동쳐서 "여길 눌러 다시 들으라"는 신호를 준다.
 */
function PulseButton({
  onPress,
  label,
  active,
}: {
  onPress: () => void;
  label: string;
  active: boolean;
}) {
  const [ring] = useState(() => new Animated.Value(0));
  useEffect(() => {
    if (!active) {
      ring.stopAnimation();
      ring.setValue(0);
      return;
    }
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(ring, {
          toValue: 1,
          duration: 1400,
          easing: Easing.out(Easing.quad),
          useNativeDriver: true,
        }),
        Animated.timing(ring, {
          toValue: 0,
          duration: 0,
          useNativeDriver: true,
        }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [active, ring]);

  return (
    <View className="items-center justify-center">
      {/* 버튼 뒤에서 퍼져 나가는 물결 */}
      <Animated.View
        pointerEvents="none"
        style={{
          position: "absolute",
          width: 80,
          height: 80,
          borderRadius: 40,
          backgroundColor: "#0EB582",
          opacity: ring.interpolate({
            inputRange: [0, 1],
            outputRange: [0.25, 0],
          }),
          transform: [
            {
              scale: ring.interpolate({
                inputRange: [0, 1],
                outputRange: [1, 1.55],
              }),
            },
          ],
        }}
      />
      <Pressable
        onPress={onPress}
        className="h-20 w-20 items-center justify-center rounded-full bg-[#dcf2ea] shadow-neu-sm active:shadow-neu-pressed"
        accessibilityRole="button"
        accessibilityLabel={label}
      >
        <SpeakerIcon size={34} color="#0EB582" />
      </Pressable>
    </View>
  );
}

/**
 * 연속 정답 배지.
 * 개수가 늘 때마다 통통 튀어야 "이어지고 있다"는 느낌이 산다.
 */
function ComboBadge({ label }: { label: string }) {
  const [pop] = useState(() => new Animated.Value(0.4));
  useEffect(() => {
    pop.setValue(0.55);
    Animated.spring(pop, {
      toValue: 1,
      friction: 4,
      tension: 260,
      useNativeDriver: true,
    }).start();
    // label 이 바뀔 때(콤보가 늘 때)마다 다시 튄다
  }, [label, pop]);

  return (
    <Animated.View
      style={{ transform: [{ scale: pop }] }}
      className="rounded-full bg-[#dcf2ea] px-3 py-1 shadow-neu-sm"
    >
      <Text className="text-[12px] font-bold text-mint-dark">{label}</Text>
    </Animated.View>
  );
}

function ProgressBar({ current, total }: { current: number; total: number }) {
  const ratio = total > 0 ? current / total : 0;
  // 문제를 넘길 때 눈금이 뚝 뛰지 않고 스르륵 차오르게 한다
  const [anim] = useState(() => new Animated.Value(ratio));
  useEffect(() => {
    Animated.timing(anim, {
      toValue: ratio,
      duration: 350,
      easing: Easing.out(Easing.cubic),
      // 너비는 레이아웃 속성이라 네이티브 드라이버를 쓸 수 없다
      useNativeDriver: false,
    }).start();
  }, [ratio, anim]);

  return (
    <View className="mx-6 mt-4 h-2 overflow-hidden rounded-full bg-canvas shadow-neu-inset">
      <Animated.View
        className="h-full rounded-full bg-mint"
        style={{
          width: anim.interpolate({
            inputRange: [0, 1],
            outputRange: ["0%", "100%"],
          }),
        }}
      />
    </View>
  );
}

/** 문제 유형별 안내 문구 */
const PROMPT_KEY: Record<QuizKind, StringKey> = {
  wordToImage: "quiz.pickImage",
  wordToMeaning: "quiz.pickMeaning",
  meaningToWord: "quiz.pickWordByMeaning",
  listenToWord: "quiz.listen",
  cloze: "quiz.cloze",
  spelling: "quiz.spell",
};

/**
 * 문제 본문.
 * 여섯 가지 유형을 한 자리에서 그린다. 제시부(위)와 보기부(아래)만 유형에 따라 갈린다.
 */
function QuizBody({
  question,
  picked,
  revealed,
  onSubmit,
  speechCode,
  speechVolume,
}: {
  question: QuizQuestion;
  picked: Word | null;
  revealed: boolean;
  onSubmit: (choice: Word | null, correct: boolean) => void;
  speechCode: string;
  speechVolume: number;
}) {
  const t = useT();
  const { answer, choices, kind } = question;
  const { width: screenWidth, height: screenHeight } = useWindowDimensions();

  /**
   * 그림 칸 크기.
   *
   * 학습 화면처럼 정사각형으로 두되, 높이가 화면을 넘지 않게 잘라 준다.
   * 폭에만 맞추면 작은 폰에서 그림이 화면을 다 먹어 보기 버튼이 안 보인다.
   */
  /*
   * 문제 영역의 실제 크기를 재서 배치를 정한다.
   *
   * 화면 높이에서 머리줄 높이를 어림잡아 빼면 가로 모드나 창 크기를 줄인
   * 웹에서 어긋난다. 그래서 스크롤 영역이 실제로 차지한 자리를 받아 쓴다.
   * 아직 못 쟀을 때만 화면 크기로 어림한다.
   */
  const [box, setBox] = useState({ width: 0, height: 0 });
  const availWidth =
    (box.width || Math.min(screenWidth, WIDE_MAX_WIDTH)) - SCREEN_PADDING_X * 2;
  const availHeight = box.height || screenHeight * 0.72;

  /** 넓으면 제시부와 보기를 좌우로 나눈다. 가로 모드에서 세로로 쌓으면 다 안 들어간다 */
  const twoPane = availWidth >= TWO_PANE_MIN;

  /*
   * 그림 열 너비.
   *
   * 그림은 정사각형이라 열 너비가 곧 높이가 되고, 보기 그림 2x2 도 두 줄을 합치면
   * 같은 높이가 나온다. 그래서 한 값만 정하면 두 배치가 같이 맞는다.
   */
  const paneWidth = twoPane
    ? Math.floor((availWidth - SECTION_GAP) / 2)
    : availWidth;
  const heightBudget = twoPane
    ? availHeight - PROMPT_H
    : availHeight - PROMPT_H - SECTION_GAP - CHOICE_LIST_H;
  const columnWidth = Math.round(
    Math.max(MIN_COLUMN, Math.min(paneWidth, heightBudget, MAX_COLUMN)),
  );

  /** 보기 그림 한 변. 열 너비에서 간격과 테두리 여백을 빼면 딱 떨어진다 */
  const cellSize = Math.floor((columnWidth - GRID_GAP) / 2) - CELL_PAD * 2;

  /**
   * 철자 맞추기는 보기 목록이 없으니 높이 예산에 묶지 않고 폭을 그대로 쓴다.
   * 그림이 카드 좌우를 꽉 채우고, 자판은 아래로 스크롤해 닿는다.
   */
  const spellWidth = Math.round(
    Math.max(MIN_COLUMN, Math.min(availWidth, MAX_COLUMN)),
  );

  const speak = useCallback(() => {
    speakWord(answer.word, { lang: speechCode, volume: speechVolume });
  }, [answer.word, speechCode, speechVolume]);

  // 듣기 문제는 화면에 뜨자마자 한 번 읽어 준다
  useEffect(() => {
    if (kind === "listenToWord") speak();
  }, [kind, speak]);

  // 문제가 바뀔 때 살짝 떠오르게 한다
  const [enter] = useState(() => new Animated.Value(0));
  useEffect(() => {
    enter.setValue(0);
    Animated.timing(enter, {
      toValue: 1,
      duration: 220,
      easing: Easing.out(Easing.quad),
      useNativeDriver: true,
    }).start();
  }, [enter]);

  const style = {
    opacity: enter,
    transform: [
      {
        translateY: enter.interpolate({
          inputRange: [0, 1],
          outputRange: [12, 0],
        }),
      },
    ],
  };

  /** 보기를 골랐을 때. 뜻이 같으면 정답으로 본다 */
  const pick = (choice: Word) =>
    onSubmit(choice, choice.conceptId === answer.conceptId);

  /** 단어 네 개를 세로로 늘어놓는 보기부. 여러 유형이 함께 쓴다 */
  const wordChoices = (
    <View className="gap-2.5">
      {choices.map((choice) => (
        <WordChoice
          key={choice.id}
          choice={choice}
          answer={answer}
          picked={picked}
          revealed={revealed}
          onPress={() => pick(choice)}
        />
      ))}
    </View>
  );

  /** 뜻 네 개를 세로로 늘어놓는 보기부 */
  const meaningChoices = (
    <View className="gap-2.5">
      {choices.map((choice) => (
        <MeaningChoice
          key={choice.id}
          choice={choice}
          answer={answer}
          picked={picked}
          revealed={revealed}
          onPress={() => pick(choice)}
        />
      ))}
    </View>
  );

  /** 유형별 제시부(위/왼쪽)와 보기부(아래/오른쪽) */
  let prompt: ReactNode = null;
  let answers: ReactNode = null;

  switch (kind) {
    case "wordToImage":
      prompt = <WordPrompt word={answer} onSpeak={speak} />;
      answers = (
        <View style={{ gap: GRID_GAP }} className="flex-row flex-wrap">
          {choices.map((choice) => (
            <ImageChoice
              key={choice.id}
              choice={choice}
              answer={answer}
              picked={picked}
              revealed={revealed}
              size={cellSize}
              onPress={() => pick(choice)}
            />
          ))}
        </View>
      );
      break;

    case "wordToMeaning":
      prompt = <WordPrompt word={answer} onSpeak={speak} />;
      answers = meaningChoices;
      break;

    case "meaningToWord":
      prompt = (
        <View className="items-center rounded-3xl bg-surface px-5 py-5 shadow-neu-card">
          <Text className="text-center text-[20px] font-bold text-slate-800">
            {answer.meaning}
          </Text>
        </View>
      );
      answers = wordChoices;
      break;

    case "listenToWord":
      // 소리만으로 푸는 문제라 단어는 숨긴다
      prompt = (
        <View className="items-center gap-3 rounded-3xl bg-surface px-5 py-8 shadow-neu-card">
          <PulseButton
            onPress={speak}
            label={t("quiz.replay")}
            active={!revealed}
          />
          <Text className="text-[12px] text-slate-400">{t("quiz.replay")}</Text>
        </View>
      );
      answers = wordChoices;
      break;

    case "cloze":
      prompt = question.cloze ? (
        <View className="rounded-3xl bg-surface px-5 py-6 shadow-neu-card">
          <Text className="text-[17px] leading-[28px] text-slate-800">
            {question.cloze.before}
            <Text className="font-black text-mint">
              {revealed ? question.cloze.surface : "______"}
            </Text>
            {question.cloze.after}
          </Text>
          {/* 해석은 정답이 드러난 뒤에만. 먼저 보이면 답이 새어 나간다 */}
          {revealed && answer.exampleTr ? (
            <Text className="mt-2 text-[13px] text-slate-500">
              {answer.exampleTr}
            </Text>
          ) : null}
        </View>
      ) : null;
      answers = wordChoices;
      break;

    case "spelling":
      // 힌트와 글자판이 한 덩어리라 좌우로 나누지 않는다
      prompt = (
        <SpellingBoard
          key={answer.id}
          answer={answer}
          revealed={revealed}
          width={spellWidth}
          onSpeak={speak}
          onDone={(correct) => onSubmit(null, correct)}
        />
      );
      break;
  }

  // 철자 맞추기는 한 덩어리라 좌우로 나누지 않는다
  const splitPanes = twoPane && answers !== null;
  /** 좌우로 나누지 않을 때 한 줄의 폭 */
  const singleWidth = kind === "spelling" ? spellWidth : columnWidth;

  return (
    <ScrollView
      onLayout={(e) => {
        const { width, height } = e.nativeEvent.layout;
        setBox((prev) =>
          prev.width === width && prev.height === height
            ? prev
            : { width, height },
        );
      }}
      contentContainerClassName="gap-4 px-6 pb-8 pt-4"
      keyboardShouldPersistTaps="handled"
    >
      {/* 철자 맞추기는 그림과 뜻만으로 충분해 안내 문구를 뺀다 */}
      {kind !== "spelling" && (
        <Text
          style={{ width: splitPanes ? availWidth : singleWidth }}
          className="self-center text-center text-[13px] text-slate-500"
        >
          {t(PROMPT_KEY[kind])}
        </Text>
      )}

      <Animated.View
        style={[
          style,
          splitPanes
            ? { width: availWidth, gap: SECTION_GAP }
            : { width: singleWidth, gap: SECTION_GAP },
        ]}
        className={`self-center ${splitPanes ? "flex-row items-start" : ""}`}
      >
        <View style={{ width: singleWidth }}>{prompt}</View>
        {answers && (
          <View style={splitPanes ? { flex: 1 } : { width: columnWidth }}>
            {answers}
          </View>
        )}
      </Animated.View>

      {/* 정답이 드러난 뒤에만 뜻을 보여 준다. 먼저 보이면 문제가 안 된다 */}
      {revealed && (
        <View
          style={{ width: splitPanes ? availWidth : singleWidth }}
          className="items-center gap-0.5 self-center rounded-2xl bg-surface px-4 py-2.5 shadow-neu-sm"
        >
          <Text className="text-[15px] font-bold text-slate-800">
            {answer.word}
          </Text>
          <Text className="text-center text-[13px] text-slate-500">
            {answer.meaning}
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

/** 단어를 크게 보여 주는 제시부. 발음도 들을 수 있다 */
function WordPrompt({ word, onSpeak }: { word: Word; onSpeak: () => void }) {
  return (
    <View className="items-center gap-1.5 rounded-3xl bg-surface px-4 py-4 shadow-neu-card">
      <Text className="text-[26px] font-black text-slate-900">{word.word}</Text>
      <Pressable
        onPress={onSpeak}
        className="rounded-full bg-canvas p-2.5 shadow-neu-sm active:opacity-70"
        accessibilityRole="button"
        accessibilityLabel={word.word}
      >
        <SpeakerIcon size={18} color="#64748b" />
      </Pressable>
    </View>
  );
}

/**
 * 철자 맞추기.
 *
 * 그림과 뜻을 힌트로 주고 글자를 하나씩 고른다.
 * 처음부터 전부 비우면 너무 어려워서 약 30%는 채워 둔 채 시작한다.
 * 틀릴 수 있는 횟수는 하트로 보여 준다. 다 쓰면 정답을 펼쳐 보여 주고 넘어간다.
 */
function SpellingBoard({
  answer,
  revealed,
  width,
  onSpeak,
  onDone,
}: {
  answer: Word;
  revealed: boolean;
  /** 보드 전체 폭 (px). 그림과 자판이 이 폭을 꽉 채운다 */
  width: number;
  onSpeak: () => void;
  onDone: (correct: boolean) => void;
}) {
  const t = useT();
  const target = answer.word.toUpperCase();
  const chars = useMemo(() => target.split(""), [target]);

  /** 미리 채워 둔 칸 번호. 문제마다 한 번만 뽑는다 */
  const [given] = useState(() => givenSlotsOf(chars.length));

  /** 사용자가 맞혀야 하는 글자 (비워 둔 칸의 글자) */
  const letters = useMemo(
    () => new Set(chars.filter((_, i) => !given.has(i))),
    [chars, given],
  );
  /** 판에 들어 있는 모든 글자. 오답 판정에 쓴다 */
  const inWord = useMemo(() => new Set(chars), [chars]);

  const [tried, setTried] = useState<Set<string>>(() => new Set());
  /** 힌트는 한 문제에 한 번, 글자 하나만 알려 준다 */
  const [hintUsed, setHintUsed] = useState(false);
  const misses = useMemo(
    () => [...tried].filter((c) => !inWord.has(c)).length,
    [tried, inWord],
  );
  const lives = SPELLING_LIVES - misses;
  const solved = useMemo(
    () => [...letters].every((c) => tried.has(c)),
    [letters, tried],
  );

  // 다 맞히거나 하트를 다 쓰면 한 번만 넘긴다
  const finished = useRef(false);
  useEffect(() => {
    if (finished.current) return;
    if (solved || lives <= 0) {
      finished.current = true;
      onDone(solved);
    }
  }, [solved, lives, onDone]);

  const tap = (letter: string) => {
    if (revealed || finished.current) return;
    setTried((prev) => new Set(prev).add(letter));
  };

  /** 아직 안 나온 글자 중 하나를 채워 준다 */
  const useHint = () => {
    if (hintUsed || revealed || finished.current) return;
    const left = [...letters].filter((c) => !tried.has(c));
    if (left.length === 0) return;
    const pickOne = left[Math.floor(Math.random() * left.length)];
    setHintUsed(true);
    setTried((prev) => new Set(prev).add(pickOne));
  };

  /*
   * 빈칸 크기. 긴 단어(10자)도 한 줄에 들어가도록 폭에서 계산한다.
   * 줄이 바뀌면 단어가 중간에 끊겨 보여서 읽기 어렵다.
   */
  const slotGap = 6;
  const slotW = Math.min(
    40,
    Math.floor((width - slotGap * (chars.length - 1)) / chars.length),
  );

  /** 자판 한 칸 폭. 가장 긴 첫 줄(10칸)이 폭을 꽉 채운다 */
  const keyW = Math.floor(
    (width - KEY_GAP * (KEY_ROWS[0].length - 1)) / KEY_ROWS[0].length,
  );
  const keyH = Math.round(Math.min(52, keyW * 1.35));

  const image = imageOf(answer);

  return (
    <View style={{ width }} className="gap-4">
      <View className="overflow-hidden rounded-3xl bg-surface shadow-neu-card">
        {/* 그림이 있으면 카드 좌우를 꽉 채워 보여 주고, 없으면 뜻만 힌트로 준다 */}
        {image ? (
          <View style={{ width, aspectRatio: 1 }} className="bg-canvas">
            <Image
              source={image}
              contentFit="cover"
              transition={150}
              cachePolicy="disk"
              style={{ width: "100%", height: "100%" }}
            />
          </View>
        ) : null}
        {/* 뜻 옆에 발음 듣기와 힌트 버튼을 나란히 둔다 */}
        <View className="flex-row flex-wrap items-center justify-center gap-2 px-4 py-3">
          <Text className="shrink text-center text-[15px] font-bold text-slate-700">
            {answer.meaning}
          </Text>
          <Pressable
            onPress={onSpeak}
            className="rounded-full bg-surface p-2 shadow-neu-sm active:opacity-70"
            accessibilityRole="button"
            accessibilityLabel={t("quiz.replay")}
          >
            <SpeakerIcon size={15} color="#64748b" />
          </Pressable>
          {/* 힌트는 한 번만. 다 쓰면 눌리지 않는다 */}
          <Pressable
            onPress={useHint}
            disabled={hintUsed || revealed}
            accessibilityRole="button"
            accessibilityLabel={t("quiz.hint")}
            className={`flex-row items-center gap-1 rounded-full px-3 py-1.5 ${
              hintUsed || revealed
                ? "bg-canvas shadow-neu-inset"
                : "bg-[#e9e6f8] shadow-neu-sm active:opacity-70"
            }`}
          >
            <LightbulbIcon
              size={14}
              color={hintUsed || revealed ? "#cbd5e1" : "#4338ca"}
            />
            <Text
              className={`text-[12px] font-bold ${
                hintUsed || revealed ? "text-slate-300" : "text-indigo-700"
              }`}
            >
              {t("quiz.hint")}
            </Text>
          </Pressable>
        </View>
      </View>

      {/* 빈칸. 미리 준 칸과 맞힌 글자만 채워진다 */}
      <View style={{ gap: slotGap }} className="flex-row justify-center">
        {chars.map((ch, i) => {
          const pre = given.has(i);
          const open = pre || tried.has(ch) || revealed || lives <= 0;
          return (
            <View
              key={`${ch}-${i}`}
              style={{ width: slotW, height: Math.round(slotW * 1.3) }}
              className={`items-center justify-center rounded-lg ${
                pre
                  ? "bg-surface shadow-neu-sm"
                  : open
                    ? "bg-[#dcf2ea]"
                    : "bg-canvas shadow-neu-inset"
              }`}
            >
              <Text
                style={{ fontSize: Math.min(20, Math.round(slotW * 0.55)) }}
                className={`font-black ${
                  !open
                    ? "text-transparent"
                    : pre
                      ? "text-slate-500"
                      : "text-mint-dark"
                }`}
              >
                {ch}
              </Text>
            </View>
          );
        })}
      </View>

      {/* 키보드 자판 (QWERTY). 줄마다 가운데 정렬해 실제 자판처럼 엇갈리게 둔다 */}
      <View style={{ gap: KEY_GAP }}>
        {KEY_ROWS.map((row) => (
          <View
            key={row.join("")}
            style={{ gap: KEY_GAP }}
            className="flex-row justify-center"
          >
            {row.map((ch) => {
              const used = tried.has(ch);
              const good = used && inWord.has(ch);
              return (
                <Pressable
                  key={ch}
                  onPress={() => tap(ch)}
                  disabled={used || revealed}
                  style={{ width: keyW, height: keyH }}
                  className={`items-center justify-center rounded-lg ${
                    !used
                      ? "bg-surface shadow-neu-sm active:opacity-70"
                      : good
                        ? "bg-[#dcf2ea]"
                        : "bg-canvas shadow-neu-inset"
                  }`}
                  accessibilityRole="button"
                  accessibilityLabel={ch}
                >
                  <Text
                    className={`text-[15px] font-bold ${
                      !used
                        ? "text-slate-700"
                        : good
                          ? "text-mint-dark"
                          : "text-slate-300"
                    }`}
                  >
                    {ch}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        ))}
      </View>
    </View>
  );
}

/** 자판 배열 (QWERTY) */
const KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"].map((r) => r.split(""));

/** 자판 칸 사이 간격 */
const KEY_GAP = 5;

/** 처음부터 채워 두는 칸의 비율. 나머지 70%를 사용자가 채운다 */
const GIVEN_RATIO = 0.3;

/**
 * 미리 채워 둘 칸 번호를 뽑는다.
 * 최소 한 칸은 채우고, 최소 두 칸은 비워 둬서 풀 거리가 남게 한다.
 */
function givenSlotsOf(length: number): Set<number> {
  const count = Math.min(
    Math.max(1, Math.round(length * GIVEN_RATIO)),
    Math.max(0, length - 2),
  );
  const slots = Array.from({ length }, (_, i) => i);
  for (let i = slots.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [slots[i], slots[j]] = [slots[j], slots[i]];
  }
  return new Set(slots.slice(0, count));
}

/**
 * 채점 순간의 몸짓.
 * 정답 보기는 살짝 부풀었다 돌아오고, 잘못 고른 보기는 좌우로 떨린다.
 * 색만 바뀌면 아이 눈에 안 들어와서 움직임을 함께 준다.
 */
function useMarkFeedback(mark: "idle" | "correct" | "wrong") {
  const [scale] = useState(() => new Animated.Value(1));
  const [shake] = useState(() => new Animated.Value(0));

  useEffect(() => {
    if (mark === "correct") {
      Animated.sequence([
        Animated.spring(scale, {
          toValue: 1.06,
          friction: 4,
          tension: 220,
          useNativeDriver: true,
        }),
        Animated.spring(scale, {
          toValue: 1,
          friction: 5,
          tension: 160,
          useNativeDriver: true,
        }),
      ]).start();
    } else if (mark === "wrong") {
      Animated.sequence(
        [10, -8, 6, -4, 0].map((x) =>
          Animated.timing(shake, {
            toValue: x,
            duration: 55,
            easing: Easing.linear,
            useNativeDriver: true,
          }),
        ),
      ).start();
    } else {
      scale.setValue(1);
      shake.setValue(0);
    }
  }, [mark, scale, shake]);

  return { transform: [{ scale }, { translateX: shake }] };
}

/**
 * 고른 보기의 표시 상태.
 * 아직 안 골랐으면 기본, 고른 뒤에는 정답을 초록으로, 내가 틀리게 고른 것만 빨갛게 한다.
 */
function markOf(
  choice: Word,
  answer: Word,
  picked: Word | null,
  revealed: boolean,
): "idle" | "correct" | "wrong" {
  if (!revealed) return "idle";
  if (choice.conceptId === answer.conceptId) return "correct";
  if (picked && choice.id === picked.id) return "wrong";
  return "idle";
}

/** 뜻을 보기로 늘어놓는다. 단어 보기와 표시 규칙은 같다 */
function MeaningChoice({
  choice,
  answer,
  picked,
  revealed,
  onPress,
}: {
  choice: Word;
  answer: Word;
  picked: Word | null;
  revealed: boolean;
  onPress: () => void;
}) {
  const mark = markOf(choice, answer, picked, revealed);
  const feedback = useMarkFeedback(mark);
  const tone =
    mark === "correct"
      ? "bg-[#dcf2ea]"
      : mark === "wrong"
        ? "bg-[#fde8e8]"
        : "bg-surface";

  return (
    <Animated.View style={feedback}>
    <Pressable
      onPress={onPress}
      disabled={revealed}
      className={`flex-row items-center justify-between gap-3 rounded-2xl ${tone} px-5 py-3.5 shadow-neu-sm active:shadow-neu-pressed`}
      accessibilityRole="button"
      accessibilityLabel={choice.meaning}
    >
      <Text
        className={`flex-1 text-[15px] font-bold ${
          mark === "correct"
            ? "text-mint-dark"
            : mark === "wrong"
              ? "text-red-600"
              : "text-slate-800"
        }`}
      >
        {choice.meaning}
      </Text>
      {mark === "correct" && <CheckIcon size={18} color={MINT} />}
      {mark === "wrong" && <CloseIcon size={18} color={CORAL} />}
    </Pressable>
    </Animated.View>
  );
}

function WordChoice({
  choice,
  answer,
  picked,
  revealed,
  onPress,
}: {
  choice: Word;
  answer: Word;
  picked: Word | null;
  revealed: boolean;
  onPress: () => void;
}) {
  const mark = markOf(choice, answer, picked, revealed);
  const feedback = useMarkFeedback(mark);
  const tone =
    mark === "correct"
      ? "bg-[#dcf2ea]"
      : mark === "wrong"
        ? "bg-[#fde8e8]"
        : "bg-surface";

  return (
    <Animated.View style={feedback}>
    <Pressable
      onPress={onPress}
      disabled={revealed}
      className={`flex-row items-center justify-between rounded-2xl ${tone} px-5 py-3.5 shadow-neu-sm active:shadow-neu-pressed`}
      accessibilityRole="button"
      accessibilityLabel={choice.word}
    >
      <Text
        className={`text-[17px] font-bold ${
          mark === "correct"
            ? "text-mint-dark"
            : mark === "wrong"
              ? "text-red-600"
              : "text-slate-800"
        }`}
      >
        {choice.word}
      </Text>
      {mark === "correct" && <CheckIcon size={18} color={MINT} />}
      {mark === "wrong" && <CloseIcon size={18} color={CORAL} />}
    </Pressable>
    </Animated.View>
  );
}

function ImageChoice({
  choice,
  answer,
  picked,
  revealed,
  size,
  onPress,
}: {
  choice: Word;
  answer: Word;
  picked: Word | null;
  revealed: boolean;
  /** 그림 한 변의 길이 (px). 화면 크기에 맞춰 위에서 정한다 */
  size: number;
  onPress: () => void;
}) {
  const mark = markOf(choice, answer, picked, revealed);
  const feedback = useMarkFeedback(mark);
  const tone =
    mark === "correct"
      ? "bg-[#dcf2ea]"
      : mark === "wrong"
        ? "bg-[#fde8e8]"
        : "bg-surface";

  return (
    <Animated.View style={feedback}>
    <Pressable
      onPress={onPress}
      disabled={revealed}
      style={{ width: size + CELL_PAD * 2, padding: CELL_PAD }}
      className={`rounded-2xl ${tone} shadow-neu-sm active:shadow-neu-pressed`}
      accessibilityRole="button"
      accessibilityLabel={choice.word}
    >
      <View
        style={{ width: size, height: size }}
        className="overflow-hidden rounded-xl bg-canvas shadow-neu-inset"
      >
        <Image
          source={imageOf(choice)}
          contentFit="cover"
          transition={150}
          cachePolicy="disk"
          style={{ width: "100%", height: "100%" }}
        />
      </View>
      {mark === "correct" && (
        <View className="absolute right-2 top-2">
          <CheckIcon size={18} color={MINT} />
        </View>
      )}
      {mark === "wrong" && (
        <View className="absolute right-2 top-2">
          <CloseIcon size={18} color={CORAL} />
        </View>
      )}
    </Pressable>
    </Animated.View>
  );
}

/** 한 판이 끝나고 보여 주는 점수 화면 */
function QuizResult({
  gradeId,
  recordKey,
  gradeLabel,
  log,
  previousBest,
  onRestart,
  onRecord,
}: {
  gradeId: string;
  /** 최고 기록을 남길 열쇠. 유닛 확인 퀴즈는 학년 기록과 따로 쌓는다 */
  recordKey: string;
  gradeLabel: string;
  log: Answered[];
  previousBest: number;
  onRestart: () => void;
  onRecord: (key: string, score: number, combo: number) => void;
}) {
  const t = useT();
  const router = useRouter();

  const correct = log.filter((a) => a.correct).length;
  const total = log.length;
  const score = scoreOf(correct, total);
  const combo = bestComboOf(log);
  const wrong = log.filter((a) => !a.correct);

  // 최고 기록은 화면에 들어온 순간 딱 한 번만 남긴다
  const saved = useRef(false);
  const [beat] = useState(() => score > previousBest && previousBest > 0);
  useEffect(() => {
    if (saved.current) return;
    saved.current = true;
    onRecord(recordKey, score, combo);
  }, [recordKey, score, combo, onRecord]);

  const praise =
    score === 100
      ? t("quiz.result.perfect")
      : score >= 80
        ? t("quiz.result.great")
        : score >= 50
          ? t("quiz.result.good")
          : t("quiz.result.keep");

  // 점수판이 살짝 커지며 나타난다
  const [pop] = useState(() => new Animated.Value(0.85));
  useEffect(() => {
    Animated.spring(pop, {
      toValue: 1,
      friction: 5,
      tension: 90,
      useNativeDriver: true,
    }).start();
  }, [pop]);

  /*
   * 점수는 0에서 차오르며 보여 준다.
   * 아이에게는 "결과가 계산되는" 짧은 기다림이 점수 자체보다 재미있다.
   */
  const [shown, setShown] = useState(0);
  useEffect(() => {
    if (score <= 0) return;
    const start = Date.now();
    const tick = setInterval(() => {
      const gone = (Date.now() - start) / 900;
      if (gone >= 1) {
        setShown(score);
        clearInterval(tick);
      } else {
        // 끝에 갈수록 느려지게 (easeOut)
        setShown(Math.round(score * (1 - Math.pow(1 - gone, 3))));
      }
    }, 40);
    return () => clearInterval(tick);
  }, [score]);

  /** 점수를 별 셋으로 요약한다. 숫자보다 별이 한눈에 들어온다 */
  const stars = score >= 90 ? 3 : score >= 60 ? 2 : score >= 30 ? 1 : 0;

  return (
    <Screen>
      <ScreenHeader>
        <BackButton fallbackHref={`/grade/${gradeId}`} />
        <Text numberOfLines={1} className="flex-1 text-2xl font-bold text-ink">
          {t("quiz.result.title")}
        </Text>
      </ScreenHeader>

      <ScrollView
        className="flex-1"
        contentContainerClassName="gap-5 px-6 pb-10 pt-6"
      >
        <Animated.View
          style={{ transform: [{ scale: pop }] }}
          className="w-full items-center gap-2 rounded-3xl bg-surface px-6 py-8 shadow-neu-card"
        >
          {/* 별 셋: 채워진 별과 빈 별로 이번 판을 한눈에 보여 준다 */}
          <View className="flex-row gap-1.5">
            {[0, 1, 2].map((i) => (
              <StarIcon
                key={i}
                size={26}
                color={i < stars ? "#fbbf24" : "#e2e8f0"}
              />
            ))}
          </View>
          <Text className="text-center text-[52px] font-black leading-[60px] text-mint">
            {shown}
          </Text>
          <Text className="text-center text-[14px] text-slate-500">
            {t("quiz.result.correct", { correct, total })}
          </Text>
          <Text className="mt-1 text-center text-[15px] font-bold text-slate-700">
            {praise}
          </Text>
          {beat && (
            <View className="mt-2 rounded-full bg-[#dcf2ea] px-4 py-1.5 shadow-neu-sm">
              <Text className="text-[13px] font-bold text-mint-dark">
                {t("quiz.result.newBest")}
              </Text>
            </View>
          )}
          {combo >= 3 && (
            <Text className="mt-1 text-center text-[12px] text-slate-400">
              {t("quiz.result.bestCombo", { count: combo })}
            </Text>
          )}
        </Animated.View>

        <View className="w-full flex-row items-stretch gap-3">
          <PillButton
            label={t("quiz.startAgain")}
            variant="primary"
            size="lg"
            className="flex-1"
            onPress={onRestart}
          />
          <PillButton
            label={t("quiz.result.home")}
            size="lg"
            className="flex-1"
            onPress={() => router.replace(`/grade/${gradeId}`)}
          />
        </View>

        {wrong.length > 0 && (
          <View className="gap-3">
            <View className="flex-row flex-wrap items-baseline gap-x-2 gap-y-0.5">
              <Text className="text-[15px] font-bold text-ink">
                {t("quiz.result.wrongTitle")}
              </Text>
              <Text className="shrink text-[12px] text-slate-400">
                {t("quiz.result.wrongHint")}
              </Text>
            </View>
            {wrong.map((a, i) => {
              const image = imageOf(a.question.answer);
              return (
                <Pressable
                  key={`${a.question.answer.id}-${i}`}
                  onPress={() => router.push(`/study/${a.question.answer.id}`)}
                  className="w-full flex-row items-center gap-3 rounded-2xl bg-surface px-4 py-3 shadow-neu-sm active:opacity-80"
                >
                  {/* 그림이 없는 단어도 같은 자리를 차지해 글자 줄이 어긋나지 않게 한다 */}
                  <View
                    style={{ width: 48, height: 48 }}
                    className="overflow-hidden rounded-xl bg-canvas"
                  >
                    {image ? (
                      <Image
                        transition={150}
                        cachePolicy="disk"
                        source={image}
                        contentFit="cover"
                        style={{ width: 48, height: 48 }}
                      />
                    ) : null}
                  </View>
                  <View className="min-w-0 flex-1">
                    <Text
                      numberOfLines={1}
                      className="text-[15px] font-bold text-slate-800"
                    >
                      {a.question.answer.word}
                    </Text>
                    <Text
                      numberOfLines={1}
                      className="text-[12px] text-slate-500"
                    >
                      {a.question.answer.meaning}
                    </Text>
                  </View>
                  {/* 내가 잘못 고른 단어도 같이 보여 줘야 왜 틀렸는지 안다 */}
                  {a.picked && (
                    <Text
                      numberOfLines={1}
                      style={{ maxWidth: 110 }}
                      className="shrink-0 text-right text-[12px] text-red-400 line-through"
                    >
                      {a.picked.word}
                    </Text>
                  )}
                </Pressable>
              );
            })}
          </View>
        )}

        {gradeLabel ? (
          <Text className="text-center text-[12px] text-slate-400">
            {gradeLabel}
          </Text>
        ) : null}
      </ScrollView>
    </Screen>
  );
}
