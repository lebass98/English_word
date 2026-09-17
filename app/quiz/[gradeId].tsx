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
  Image,
  Pressable,
  ScrollView,
  Text,
  useWindowDimensions,
  View,
} from "react-native";
import { BackButton } from "../../src/components/BackButton";
import { CheckIcon, SpeakerIcon } from "../../src/components/icons";
import { PillButton } from "../../src/components/PillButton";
import {
  MAX_CONTENT_WIDTH,
  SCREEN_PADDING_X,
  Screen,
  ScreenHeader,
} from "../../src/components/Screen";
import { useGrade } from "../../src/constants/grades";
import { studyLanguageOf, studyLangOfWordId } from "../../src/constants/languages";
import { useVocab, type Word } from "../../src/constants/words";
import { useT, type StringKey } from "../../src/i18n";
import {
  buildQuiz,
  imageOf,
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

/** 그림 카드 안쪽 여백 (p-3). 프레임이 그림에 딱 붙도록 계산에 쓴다 */
const CARD_PAD = 12;

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

/** 정답·오답을 보여 주고 다음 문제로 넘어가기까지 기다리는 시간 (ms) */
const REVEAL_MS = 900;

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
      unitNo
        ? (vocab.unitsOf(gradeId)[unitNo - 1]?.words ?? [])
        : gradeWords,
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

    setTimeout(() => {
      setLog((prev) => [...prev, { question, picked: choice, correct }]);
      setPicked(null);
      setRevealed(false);
      setIndex((i) => i + 1);
    }, REVEAL_MS);
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
        {combo >= 3 && (
          <View className="rounded-full bg-[#dcf2ea] px-3 py-1 shadow-neu-sm">
            <Text className="text-[12px] font-bold text-mint-dark">
              {t("quiz.combo", { count: combo })}
            </Text>
          </View>
        )}
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
const KIND_OPTIONS: { value: QuizKind | "mix"; emoji: string }[] = [
  { value: "mix", emoji: "🎲" },
  { value: "imageToWord", emoji: "🖼️" },
  { value: "wordToImage", emoji: "🔤" },
  { value: "wordToMeaning", emoji: "📖" },
  { value: "meaningToWord", emoji: "💡" },
  { value: "listenToWord", emoji: "🎧" },
  { value: "cloze", emoji: "📝" },
  { value: "spelling", emoji: "✏️" },
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
          <Text className="mt-0.5 text-[13px] text-slate-500">{gradeLabel}</Text>
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
          {KIND_OPTIONS.map(({ value, emoji }) => {
            // 섞어서는 예전 기록을 그대로 쓰고, 유형별은 따로 쌓는다
            const best =
              records[value === "mix" ? gradeId : `${gradeId}:k-${value}`]?.best;
            return (
              <Pressable
                key={value}
                onPress={() => router.push(`/quiz/${gradeId}?kind=${value}`)}
                accessibilityRole="button"
                style={{ width: cardWidth }}
                className="items-center gap-1.5 rounded-3xl bg-surface px-3 py-5 shadow-neu-card active:shadow-neu-pressed"
              >
                {/* 아이콘 자리는 그림자 없이 둔다. 카드 자체 그림자만 남긴다 */}
                <View className="h-12 w-12 items-center justify-center">
                  <Text className="text-[22px]">{emoji}</Text>
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

function ProgressBar({ current, total }: { current: number; total: number }) {
  const ratio = total > 0 ? current / total : 0;
  return (
    <View className="mx-6 mt-4 h-2 overflow-hidden rounded-full bg-canvas shadow-neu-inset">
      <View
        className="h-full rounded-full bg-mint"
        style={{ width: `${Math.round(ratio * 100)}%` }}
      />
    </View>
  );
}

/** 문제 유형별 안내 문구 */
const PROMPT_KEY: Record<QuizKind, StringKey> = {
  imageToWord: "quiz.pickWord",
  wordToImage: "quiz.pickImage",
  wordToMeaning: "quiz.pickMeaning",
  meaningToWord: "quiz.pickWordByMeaning",
  listenToWord: "quiz.listen",
  cloze: "quiz.cloze",
  spelling: "quiz.spell",
};

/**
 * 문제 본문.
 * 일곱 가지 유형을 한 자리에서 그린다. 제시부(위)와 보기부(아래)만 유형에 따라 갈린다.
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

  /** 문제 그림 한 장. 카드 좌우 여백 없이 열을 그대로 채운다 */
  const heroSize = columnWidth;

  /** 보기 그림 한 변. 열 너비에서 간격과 테두리 여백을 빼면 딱 떨어진다 */
  const cellSize = Math.floor((columnWidth - GRID_GAP) / 2) - CELL_PAD * 2;

  /** 철자 맞추기의 힌트 그림은 자판이 들어갈 자리를 남겨야 해서 더 작다 */
  const hintSize = Math.round(
    Math.min(columnWidth - CARD_PAD * 2, availHeight * 0.3, 200),
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
    case "imageToWord":
      prompt = <HeroImage word={answer} size={heroSize} />;
      answers = wordChoices;
      break;

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
          <Pressable
            onPress={speak}
            className="h-20 w-20 items-center justify-center rounded-full bg-[#dcf2ea] shadow-neu-sm active:opacity-70"
            accessibilityRole="button"
            accessibilityLabel={t("quiz.replay")}
          >
            <SpeakerIcon size={34} color="#0EB582" />
          </Pressable>
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
          hintSize={hintSize}
          onSpeak={speak}
          onDone={(correct) => onSubmit(null, correct)}
        />
      );
      break;
  }

  // 철자 맞추기는 한 덩어리라 좌우로 나누지 않는다
  const splitPanes = twoPane && answers !== null;

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
      <Text
        style={{ width: splitPanes ? availWidth : columnWidth }}
        className="self-center text-center text-[13px] text-slate-500"
      >
        {t(PROMPT_KEY[kind])}
      </Text>

      <Animated.View
        style={[
          style,
          splitPanes
            ? { width: availWidth, gap: SECTION_GAP }
            : { width: columnWidth, gap: SECTION_GAP },
        ]}
        className={`self-center ${splitPanes ? "flex-row items-start" : ""}`}
      >
        <View style={{ width: columnWidth }}>{prompt}</View>
        {answers && (
          <View style={splitPanes ? { flex: 1 } : { width: columnWidth }}>
            {answers}
          </View>
        )}
      </Animated.View>

      {/* 정답이 드러난 뒤에만 뜻을 보여 준다. 먼저 보이면 문제가 안 된다 */}
      {revealed && (
        <View
          style={{ width: splitPanes ? availWidth : columnWidth }}
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

/** 문제로 내는 큰 그림 한 장 */
function HeroImage({ word, size }: { word: Word; size: number }) {
  return (
    // 좌우 여백 없이 그림이 카드를 그대로 채운다
    <View
      style={{ width: size, height: size }}
      className="overflow-hidden rounded-3xl bg-canvas shadow-neu-card"
    >
      <Image
        source={imageOf(word)}
        resizeMode="cover"
        style={{ width: "100%", height: "100%" }}
      />
    </View>
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
 * 틀릴 수 있는 횟수는 하트로 보여 준다. 다 쓰면 정답을 펼쳐 보여 주고 넘어간다.
 */
function SpellingBoard({
  answer,
  revealed,
  hintSize,
  onSpeak,
  onDone,
}: {
  answer: Word;
  revealed: boolean;
  hintSize: number;
  onSpeak: () => void;
  onDone: (correct: boolean) => void;
}) {
  const t = useT();
  const target = answer.word.toUpperCase();
  const letters = useMemo(() => new Set(target.split("")), [target]);

  const [tried, setTried] = useState<Set<string>>(() => new Set());
  /** 힌트는 한 문제에 한 번, 글자 하나만 알려 준다 */
  const [hintUsed, setHintUsed] = useState(false);
  const misses = useMemo(
    () => [...tried].filter((c) => !letters.has(c)).length,
    [tried, letters],
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

  return (
    <View className="gap-4">
      <View
        style={{ padding: CARD_PAD }}
        className="items-center gap-3 rounded-3xl bg-surface shadow-neu-card"
      >
        {/* 그림이 있으면 그림을, 없으면 뜻만 힌트로 준다 */}
        {imageOf(answer) ? (
          <View
            style={{ width: hintSize, height: hintSize }}
            className="overflow-hidden rounded-2xl bg-canvas shadow-neu-inset"
          >
            <Image
              source={imageOf(answer)}
              resizeMode="cover"
              style={{ width: "100%", height: "100%" }}
            />
          </View>
        ) : null}
        <Text className="px-3 text-center text-[15px] font-bold text-slate-700">
          {answer.meaning}
        </Text>

        {/* 남은 기회 */}
        <View className="flex-row gap-1.5">
          {Array.from({ length: SPELLING_LIVES }).map((_, i) => (
            <Text
              key={i}
              className={`text-[15px] ${i < lives ? "" : "opacity-25"}`}
            >
              {i < lives ? "💚" : "🤍"}
            </Text>
          ))}
        </View>
      </View>

      {/* 빈칸. 맞힌 글자만 채워진다 */}
      <View className="flex-row flex-wrap justify-center gap-1.5">
        {target.split("").map((ch, i) => {
          const open = tried.has(ch) || revealed || lives <= 0;
          return (
            <View
              key={`${ch}-${i}`}
              className={`h-11 w-8 items-center justify-center rounded-lg ${
                open ? "bg-[#dcf2ea]" : "bg-canvas shadow-neu-inset"
              }`}
            >
              <Text
                className={`text-[19px] font-black ${
                  open ? "text-mint-dark" : "text-transparent"
                }`}
              >
                {ch}
              </Text>
            </View>
          );
        })}
      </View>

      <View className="flex-row items-center justify-center gap-2">
        <Text className="text-[12px] text-slate-400">{t("quiz.spellHint")}</Text>
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
          <Text className="text-[12px]">💡</Text>
          <Text
            className={`text-[12px] font-bold ${
              hintUsed || revealed ? "text-slate-300" : "text-indigo-700"
            }`}
          >
            {t("quiz.hint")}
          </Text>
        </Pressable>
      </View>

      {/* 글자판 */}
      <View className="flex-row flex-wrap justify-center gap-1.5">
        {ALPHABET.map((ch) => {
          const used = tried.has(ch);
          const good = used && letters.has(ch);
          return (
            <Pressable
              key={ch}
              onPress={() => tap(ch)}
              disabled={used || revealed}
              className={`h-9 w-9 items-center justify-center rounded-lg ${
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
                className={`text-[14px] font-bold ${
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
    </View>
  );
}

/** 글자판에 쓰는 알파벳 */
const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");


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
  const tone =
    mark === "correct"
      ? "bg-[#dcf2ea]"
      : mark === "wrong"
        ? "bg-[#fde8e8]"
        : "bg-surface";

  return (
    <Pressable
      onPress={onPress}
      disabled={revealed}
      className={`flex-row items-center justify-between gap-3 rounded-2xl ${tone} px-5 py-3.5 shadow-neu-sm active:opacity-80`}
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
      {mark === "wrong" && (
        <Text className="text-[16px] font-bold text-red-500">✕</Text>
      )}
    </Pressable>
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
  const tone =
    mark === "correct"
      ? "bg-[#dcf2ea]"
      : mark === "wrong"
        ? "bg-[#fde8e8]"
        : "bg-surface";

  return (
    <Pressable
      onPress={onPress}
      disabled={revealed}
      className={`flex-row items-center justify-between rounded-2xl ${tone} px-5 py-3.5 shadow-neu-sm active:opacity-80`}
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
      {mark === "wrong" && (
        <Text className="text-[16px] font-bold text-red-500">✕</Text>
      )}
    </Pressable>
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
  const tone =
    mark === "correct"
      ? "bg-[#dcf2ea]"
      : mark === "wrong"
        ? "bg-[#fde8e8]"
        : "bg-surface";

  return (
    <Pressable
      onPress={onPress}
      disabled={revealed}
      style={{ width: size + CELL_PAD * 2, padding: CELL_PAD }}
      className={`rounded-2xl ${tone} shadow-neu-sm active:opacity-80`}
      accessibilityRole="button"
      accessibilityLabel={choice.word}
    >
      <View
        style={{ width: size, height: size }}
        className="overflow-hidden rounded-xl bg-canvas shadow-neu-inset"
      >
        <Image
          source={imageOf(choice)}
          resizeMode="cover"
          style={{ width: "100%", height: "100%" }}
        />
      </View>
      {mark === "correct" && (
        <View className="absolute right-2 top-2">
          <CheckIcon size={18} color={MINT} />
        </View>
      )}
      {mark === "wrong" && (
        <Text className="absolute right-2 top-1 text-[16px] font-bold text-red-500">
          ✕
        </Text>
      )}
    </Pressable>
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

  return (
    <Screen>
      <ScreenHeader>
        <BackButton fallbackHref={`/grade/${gradeId}`} />
        <Text className="flex-1 text-2xl font-bold text-ink">
          {t("quiz.result.title")}
        </Text>
      </ScreenHeader>

      <ScrollView contentContainerClassName="gap-5 px-6 pb-10 pt-6">
        <Animated.View
          style={{ transform: [{ scale: pop }] }}
          className="items-center gap-2 rounded-3xl bg-surface px-6 py-8 shadow-neu-card"
        >
          <Text className="text-[52px] font-black text-mint">{score}</Text>
          <Text className="text-[14px] text-slate-500">
            {t("quiz.result.correct", { correct, total })}
          </Text>
          <Text className="mt-1 text-[15px] font-bold text-slate-700">
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
            <Text className="mt-1 text-[12px] text-slate-400">
              {t("quiz.result.bestCombo", { count: combo })}
            </Text>
          )}
        </Animated.View>

        <View className="flex-row gap-3">
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
            <View className="flex-row items-baseline gap-2">
              <Text className="text-[15px] font-bold text-ink">
                {t("quiz.result.wrongTitle")}
              </Text>
              <Text className="text-[12px] text-slate-400">
                {t("quiz.result.wrongHint")}
              </Text>
            </View>
            {wrong.map((a) => (
              <Pressable
                key={a.question.answer.id}
                onPress={() => router.push(`/study/${a.question.answer.id}`)}
                className="flex-row items-center gap-3 rounded-2xl bg-surface px-4 py-3 shadow-neu-sm active:opacity-80"
              >
                <Image
                  source={imageOf(a.question.answer)}
                  resizeMode="contain"
                  className="h-12 w-12"
                />
                <View className="flex-1">
                  <Text className="text-[15px] font-bold text-slate-800">
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
                  <Text className="text-[12px] text-red-400">
                    {a.picked.word}
                  </Text>
                )}
              </Pressable>
            ))}
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
