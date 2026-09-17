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
import { useT } from "../../src/i18n";
import {
  buildQuiz,
  imageOf,
  QUIZ_SIZE,
  scoreOf,
  type QuizQuestion,
} from "../../src/lib/quiz";
import { speakWord, stopSpeaking } from "../../src/lib/speech";
import { useAppStore } from "../../src/stores/useAppStore";

const MINT = "#0EB582";

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

  const pick = (choice: Word) => {
    // 정답이 드러난 동안 두 번째로 누른 건 무시한다
    if (picked) return;
    const correct = choice.conceptId === question.answer.conceptId;
    setPicked(choice);

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
        onPick={pick}
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

/**
 * 문제 본문.
 * 그림을 보고 단어를 고르거나, 단어를 보고 그림을 고른다.
 */
function QuizBody({
  question,
  picked,
  onPick,
  speechCode,
  speechVolume,
}: {
  question: QuizQuestion;
  picked: Word | null;
  onPick: (w: Word) => void;
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
  // 문제 그림 한 장 (보기 단어 4줄이 함께 들어가야 한다)
  const heroSize = Math.round(
    Math.min(contentWidth - 24, screenHeight * 0.3, 280),
  );
  // 보기 그림 네 장 (2열). gap-3(12px) 과 카드 안쪽 여백(8px)을 뺀다
  const cellSize = Math.round(
    Math.min((contentWidth - 12) / 2 - 8, screenHeight * 0.19, 150),
  );

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

  return (
    <ScrollView
      contentContainerClassName="gap-4 px-6 pb-8 pt-4"
      keyboardShouldPersistTaps="handled"
    >
      <Text className="text-center text-[13px] text-slate-500">
        {kind === "imageToWord" ? t("quiz.pickWord") : t("quiz.pickImage")}
      </Text>

      <Animated.View style={style} className="gap-4">
        {kind === "imageToWord" ? (
          <>
            <View className="items-center rounded-3xl bg-surface p-3 shadow-neu-card">
              <View
                style={{ width: heroSize, height: heroSize }}
                className="overflow-hidden rounded-2xl bg-canvas shadow-neu-inset"
              >
                <Image
                  source={imageOf(answer)}
                  resizeMode="cover"
                  style={{ width: "100%", height: "100%" }}
                />
              </View>
            </View>
            <View className="gap-2.5">
              {choices.map((choice) => (
                <WordChoice
                  key={choice.id}
                  choice={choice}
                  answer={answer}
                  picked={picked}
                  onPress={() => onPick(choice)}
                />
              ))}
            </View>
          </>
        ) : (
          <>
            <View className="items-center gap-2 rounded-3xl bg-surface px-4 py-5 shadow-neu-card">
              <Text className="text-[28px] font-black text-slate-900">
                {answer.word}
              </Text>
              <Pressable
                onPress={() =>
                  speakWord(answer.word, {
                    lang: speechCode,
                    volume: speechVolume,
                  })
                }
                className="rounded-full bg-canvas p-2.5 shadow-neu-sm active:opacity-70"
                accessibilityRole="button"
                accessibilityLabel={answer.word}
              >
                <SpeakerIcon size={18} color="#64748b" />
              </Pressable>
            </View>
            <View className="flex-row flex-wrap justify-center gap-3">
              {choices.map((choice) => (
                <ImageChoice
                  key={choice.id}
                  choice={choice}
                  answer={answer}
                  picked={picked}
                  size={cellSize}
                  onPress={() => onPick(choice)}
                />
              ))}
            </View>
          </>
        )}
      </Animated.View>

      {/* 정답이 드러난 뒤에만 뜻을 보여 준다. 먼저 보이면 문제가 안 된다 */}
      {picked && (
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

/**
 * 고른 보기의 표시 상태.
 * 아직 안 골랐으면 기본, 고른 뒤에는 정답을 초록으로, 내가 틀리게 고른 것만 빨갛게 한다.
 */
function markOf(
  choice: Word,
  answer: Word,
  picked: Word | null,
): "idle" | "correct" | "wrong" {
  if (!picked) return "idle";
  if (choice.conceptId === answer.conceptId) return "correct";
  if (choice.id === picked.id) return "wrong";
  return "idle";
}

function WordChoice({
  choice,
  answer,
  picked,
  onPress,
}: {
  choice: Word;
  answer: Word;
  picked: Word | null;
  onPress: () => void;
}) {
  const mark = markOf(choice, answer, picked);
  const tone =
    mark === "correct"
      ? "bg-[#dcf2ea]"
      : mark === "wrong"
        ? "bg-[#fde8e8]"
        : "bg-surface";

  return (
    <Pressable
      onPress={onPress}
      disabled={Boolean(picked)}
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
  size,
  onPress,
}: {
  choice: Word;
  answer: Word;
  picked: Word | null;
  /** 그림 한 변의 길이 (px). 화면 크기에 맞춰 위에서 정한다 */
  size: number;
  onPress: () => void;
}) {
  const mark = markOf(choice, answer, picked);
  const tone =
    mark === "correct"
      ? "bg-[#dcf2ea]"
      : mark === "wrong"
        ? "bg-[#fde8e8]"
        : "bg-surface";

  return (
    <Pressable
      onPress={onPress}
      disabled={Boolean(picked)}
      className={`rounded-2xl ${tone} p-1.5 shadow-neu-sm active:opacity-80`}
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
