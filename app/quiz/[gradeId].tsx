import { useLocalSearchParams, useRouter } from "expo-router";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
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
  const { gradeId: raw } = useLocalSearchParams<{ gradeId: string }>();
  const gradeId = raw ?? "";
  const t = useT();
  const vocab = useVocab();
  const grade = useGrade(gradeId);

  const recordStudy = useAppStore((s) => s.recordStudy);
  const recordQuiz = useAppStore((s) => s.recordQuiz);
  const speechVolume = useAppStore((s) => s.speechVolume);
  const best = useAppStore((s) => s.quizRecords[gradeId]?.best ?? 0);

  // 학년 단어 목록. 없는 학년이면 빈 배열이 매번 새로 생기므로 메모해 둔다
  const words = useMemo(() => vocab.byLevel[gradeId] ?? [], [vocab, gradeId]);

  /**
   * 한 판은 시작할 때 한 번만 만든다.
   * entries 는 문제를 풀 때마다 바뀌는데, 그때마다 다시 만들면
   * 풀던 문제가 통째로 갈린다. 그래서 의존성에 넣지 않고 판 번호로만 새로 뽑는다.
   */
  const [round, setRound] = useState(0);
  const [questions, setQuestions] = useState<QuizQuestion[]>(() =>
    buildQuiz(words, useAppStore.getState().entries, QUIZ_SIZE),
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
    setQuestions(buildQuiz(words, useAppStore.getState().entries, QUIZ_SIZE));
    setIndex(0);
    setPicked(null);
    setRevealed(false);
    setLog([]);
    setRound((r) => r + 1);
  }, [words]);

  // 학년을 바꿔 들어오면 판을 다시 뽑는다.
  // effect 가 아니라 렌더 중에 맞춰야 이전 학년 문제가 한 번 스쳐 지나가지 않는다
  const [builtFor, setBuiltFor] = useState(gradeId);
  if (builtFor !== gradeId) {
    setBuiltFor(gradeId);
    restart();
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
    <Screen>
      <ScreenHeader>
        <BackButton fallbackHref={`/grade/${gradeId}`} />
        <View className="flex-1">
          <Text className="text-[15px] font-bold text-ink">
            {grade?.label ?? t("quiz.title")}
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
  const contentWidth =
    Math.min(screenWidth, MAX_CONTENT_WIDTH) - SCREEN_PADDING_X * 2;

  // 문제 그림 한 장. 카드 안쪽 여백(p-3 = 12px) 을 뺀 만큼이 그림이 된다
  const heroSize = Math.round(
    Math.min(contentWidth - CARD_PAD * 2, screenHeight * 0.3, 280),
  );

  /*
   * 보기 그림 네 장 (2열 2행).
   *
   * 칸 하나의 바깥 너비는 그림 + 테두리 여백(p-1.5 = 6px)이다.
   * 두 칸과 사이 간격을 더한 값을 그리드 너비로 못 박아야
   * 좌우 간격과 세로 간격이 똑같이 떨어진다.
   */
  const cellSize = Math.round(
    Math.min(
      (contentWidth - GRID_GAP) / 2 - CELL_PAD * 2,
      screenHeight * 0.19,
      150,
    ),
  );
  const cellOuter = cellSize + CELL_PAD * 2;
  const gridWidth = cellOuter * 2 + GRID_GAP;

  // 철자 맞추기의 힌트 그림은 자판이 들어갈 자리를 남겨야 해서 더 작다
  const hintSize = Math.round(
    Math.min(contentWidth - CARD_PAD * 2, screenHeight * 0.2, 170),
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

  return (
    <ScrollView
      contentContainerClassName="gap-4 px-6 pb-8 pt-4"
      keyboardShouldPersistTaps="handled"
    >
      <Text className="text-center text-[13px] text-slate-500">
        {t(PROMPT_KEY[kind])}
      </Text>

      <Animated.View style={style} className="gap-4">
        {kind === "imageToWord" && (
          <>
            <HeroImage word={answer} size={heroSize} />
            {wordChoices}
          </>
        )}

        {kind === "wordToImage" && (
          <>
            <WordPrompt word={answer} onSpeak={speak} />
            <View
              style={{ width: gridWidth, gap: GRID_GAP }}
              className="flex-row flex-wrap self-center"
            >
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
          </>
        )}

        {kind === "wordToMeaning" && (
          <>
            <WordPrompt word={answer} onSpeak={speak} />
            {meaningChoices}
          </>
        )}

        {kind === "meaningToWord" && (
          <>
            <View className="items-center rounded-3xl bg-surface px-5 py-6 shadow-neu-card">
              <Text className="text-center text-[20px] font-bold text-slate-800">
                {answer.meaning}
              </Text>
            </View>
            {wordChoices}
          </>
        )}

        {kind === "listenToWord" && (
          <>
            {/* 소리만으로 푸는 문제라 단어는 숨긴다 */}
            <View className="items-center gap-3 rounded-3xl bg-surface px-5 py-8 shadow-neu-card">
              <Pressable
                onPress={speak}
                className="h-20 w-20 items-center justify-center rounded-full bg-[#dcf2ea] shadow-neu-sm active:opacity-70"
                accessibilityRole="button"
                accessibilityLabel={t("quiz.replay")}
              >
                <SpeakerIcon size={34} color="#0EB582" />
              </Pressable>
              <Text className="text-[12px] text-slate-400">
                {t("quiz.replay")}
              </Text>
            </View>
            {wordChoices}
          </>
        )}

        {kind === "cloze" && question.cloze && (
          <>
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
            {wordChoices}
          </>
        )}

        {kind === "spelling" && (
          <SpellingBoard
            key={answer.id}
            answer={answer}
            revealed={revealed}
            hintSize={hintSize}
            onSpeak={speak}
            onDone={(correct) => onSubmit(null, correct)}
          />
        )}
      </Animated.View>

      {/* 정답이 드러난 뒤에만 뜻을 보여 준다. 먼저 보이면 문제가 안 된다 */}
      {revealed && (
        <View className="items-center gap-0.5 rounded-2xl bg-surface px-4 py-2.5 shadow-neu-sm">
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
    // 카드 폭을 그림에 맞춰 못 박는다. 전체 폭으로 두면 그림 양옆에 빈 자리가 남는다
    <View
      style={{ width: size + CARD_PAD * 2, padding: CARD_PAD }}
      className="self-center rounded-3xl bg-surface shadow-neu-card"
    >
      <View
        style={{ width: size, height: size }}
        className="overflow-hidden rounded-2xl bg-canvas shadow-neu-inset"
      >
        <Image
          source={imageOf(word)}
          resizeMode="cover"
          style={{ width: "100%", height: "100%" }}
        />
      </View>
    </View>
  );
}

/** 단어를 크게 보여 주는 제시부. 발음도 들을 수 있다 */
function WordPrompt({ word, onSpeak }: { word: Word; onSpeak: () => void }) {
  return (
    <View className="items-center gap-2 rounded-3xl bg-surface px-4 py-5 shadow-neu-card">
      <Text className="text-[28px] font-black text-slate-900">{word.word}</Text>
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
  gradeLabel,
  log,
  previousBest,
  onRestart,
  onRecord,
}: {
  gradeId: string;
  gradeLabel: string;
  log: Answered[];
  previousBest: number;
  onRestart: () => void;
  onRecord: (gradeId: string, score: number, combo: number) => void;
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
    onRecord(gradeId, score, combo);
  }, [gradeId, score, combo, onRecord]);

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
