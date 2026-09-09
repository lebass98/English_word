import { useLocalSearchParams, useRouter } from "expo-router";
import { useCallback, useEffect, useState } from "react";
import { Image, Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  AgainIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronUpIcon,
  ClockIcon,
  PauseIcon,
  PlayIcon,
  SpeakerIcon,
  StarIcon,
} from "../../src/components/icons";
import { PillButton } from "../../src/components/PillButton";
import { GRADES } from "../../src/constants/grades";
import { UNIT_SIZE, findWord, type Word } from "../../src/constants/words";
import { WORD_IMAGES } from "../../src/constants/wordImages";
import { speakWord, stopSpeaking } from "../../src/lib/speech";
import {
  STARS_BY_STATUS,
  useAppStore,
  type WordStatus,
} from "../../src/stores/useAppStore";

/** 자동 넘김 간격 (초) */
const AUTO_ADVANCE_SEC = 15;
/** 타이머 갱신 주기 (ms) — 진행 바를 부드럽게 채우기 위한 값 */
const TICK_MS = 200;

const mmss = (sec: number) =>
  `${String(Math.floor(sec / 60)).padStart(2, "0")}:${String(
    Math.floor(sec % 60),
  ).padStart(2, "0")}`;

export default function StudyScreen() {
  const { wordId } = useLocalSearchParams<{ wordId: string }>();
  const router = useRouter();

  const found = findWord(wordId ?? "");

  const goTo = useCallback(
    (id?: string) => {
      if (id) router.setParams({ wordId: id });
    },
    [router],
  );

  if (!found) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-canvas">
        <Text className="text-[14px] text-slate-500">
          단어를 찾을 수 없습니다
        </Text>
        <PillButton
          className="mt-6"
          label="← 돌아가기"
          onPress={() => router.back()}
        />
      </SafeAreaView>
    );
  }

  const { gradeId, words, index, word } = found;

  return (
    // key로 단어마다 새로 마운트해서 뜻 가리기·타이머 상태가 자동 초기화되게 한다.
    <StudyCard
      key={word.id}
      word={word}
      gradeId={gradeId}
      index={index}
      total={words.length}
      prevId={words[index - 1]?.id}
      nextId={words[index + 1]?.id}
      onNavigate={goTo}
      onBack={() => router.back()}
    />
  );
}

interface StudyCardProps {
  word: Word;
  gradeId: string;
  index: number;
  total: number;
  prevId?: string;
  nextId?: string;
  onNavigate: (id?: string) => void;
  onBack: () => void;
}

function StudyCard({
  word,
  gradeId,
  index,
  total,
  prevId,
  nextId,
  onNavigate,
  onBack,
}: StudyCardProps) {
  const autoAdvance = useAppStore((s) => s.autoAdvance);
  const setAutoAdvance = useAppStore((s) => s.setAutoAdvance);
  const status = useAppStore((s) => s.wordStatus[word.id] ?? "unseen");
  const setWordStatus = useAppStore((s) => s.setWordStatus);

  const [showMeaning, setShowMeaning] = useState(true);
  const [speaking, setSpeaking] = useState(false);
  /** 현재 단어를 본 지 경과한 시간 (ms) */
  const [elapsed, setElapsed] = useState(0);

  const advance = useCallback(() => onNavigate(nextId), [onNavigate, nextId]);

  // 자동 넘김 타이머: 켜져 있는 동안만 돌고, 다 채우면 다음 단어로 넘어간다.
  useEffect(() => {
    if (!autoAdvance) return;

    const startedAt = Date.now();
    const timer = setInterval(() => {
      const ms = Date.now() - startedAt;
      if (ms >= AUTO_ADVANCE_SEC * 1000) {
        clearInterval(timer);
        setElapsed(AUTO_ADVANCE_SEC * 1000);
        advance();
      } else {
        setElapsed(ms);
      }
    }, TICK_MS);

    return () => clearInterval(timer);
  }, [autoAdvance, advance]);

  // 화면을 벗어나거나 단어가 바뀌면 재생 중인 음성을 멈춘다.
  useEffect(() => stopSpeaking, []);

  const gradeLabel = GRADES.find((g) => g.id === gradeId)?.label ?? "";
  const unitNo = Math.floor(index / UNIT_SIZE) + 1;
  const posInUnit = (index % UNIT_SIZE) + 1;
  // 마지막 유닛은 20개보다 적을 수 있다.
  const unitLen = Math.min(UNIT_SIZE, total - (unitNo - 1) * UNIT_SIZE);
  const localImage = WORD_IMAGES[word.id] || WORD_IMAGES[word.word];

  const filledStars = STARS_BY_STATUS[status];
  /** 이미지 위 힌트는 앞의 물결표를 뺀 짧은 형태로 보여준다 */
  const shortMeaning = word.meaning.replace(/^~\s*/, "");

  const elapsedSec = Math.min(AUTO_ADVANCE_SEC, Math.floor(elapsed / 1000));
  const timerPct = Math.min(100, (elapsed / (AUTO_ADVANCE_SEC * 1000)) * 100);

  const handleSpeak = () => {
    setSpeaking(true);
    speakWord(word.word, () => setSpeaking(false));
  };

  const decide = (next: WordStatus) => {
    setWordStatus(word.id, next);
    onNavigate(nextId);
  };

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View className="mx-auto w-full max-w-[430px] flex-1 px-4">
        {/* ── 상단 바: 뒤로 · 유닛 · 진행 카운터 ───────────────── */}
        <View className="flex-row items-center justify-between pt-2">
          <Pressable
            onPress={onBack}
            accessibilityLabel="뒤로 가기"
            className="h-11 w-11 items-center justify-center rounded-full bg-surface shadow-neu-sm active:scale-95 active:shadow-neu-pressed"
          >
            <ChevronLeftIcon />
          </Pressable>

          <View className="rounded-full bg-surface px-5 py-2 shadow-neu-sm">
            <Text className="text-[14px] font-bold tracking-tight text-slate-700">
              {gradeLabel} UNIT {unitNo}
            </Text>
          </View>

          <View className="flex-row items-center gap-1 rounded-full bg-surface px-4 py-2 shadow-neu-sm">
            <Text className="text-[15px] font-extrabold text-emerald-500">
              {posInUnit}
            </Text>
            <Text className="text-[14px] font-medium text-slate-400">
              / {unitLen}
            </Text>
          </View>
        </View>

        {/* 유닛 진행률 */}
        <View className="mt-4 px-1">
          <View className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
            <View
              className="h-full rounded-full bg-emerald-500"
              style={{ width: `${(posInUnit / unitLen) * 100}%` }}
            />
          </View>
        </View>

        {/* ── 메인 플래시카드 ──────────────────────────────── */}
        <ScrollView
          className="flex-1"
          contentContainerClassName="py-4"
          showsVerticalScrollIndicator={false}
        >
          <View className="rounded-[32px] bg-surface p-6 shadow-neu">
            {/* 단어 + 발음 듣기 */}
            <View className="mb-5 mt-1 flex-row items-center justify-between">
              <Text className="text-[34px] font-black leading-tight tracking-tight text-slate-900">
                {word.word}
              </Text>
              <Pressable
                accessibilityLabel={`${word.word} 발음 듣기`}
                onPress={handleSpeak}
                className={`h-11 w-11 items-center justify-center rounded-full active:scale-95 ${
                  speaking
                    ? "bg-canvas shadow-neu-inset"
                    : "bg-surface shadow-neu-sm"
                }`}
              >
                <SpeakerIcon color={speaking ? "#0eb582" : "#334155"} />
              </Pressable>
            </View>

            {/* 연상 이미지 패널 */}
            <View
              className="w-full rounded-2xl bg-canvas p-4 shadow-neu-inset"
              style={{ minHeight: 270 }}
            >
              <View className="flex-row items-start justify-between">
                <View className="items-start gap-1">
                  <View className="flex-row items-center gap-0.5 px-0.5">
                    {[0, 1, 2].map((i) => (
                      <StarIcon
                        key={i}
                        color={i < filledStars ? "#fbbf24" : "#cbd5e1"}
                      />
                    ))}
                  </View>
                  <View className="rounded bg-amber-400 px-1.5 py-0.5">
                    <Text className="text-[14px] font-black tracking-tight text-slate-950">
                      {word.word}
                    </Text>
                  </View>
                </View>

                {showMeaning && (
                  <Text className="max-w-[45%] text-right text-[13px] font-medium tracking-tight text-slate-600">
                    {shortMeaning}
                  </Text>
                )}
              </View>

              <View className="w-full flex-1 items-center justify-center py-2">
                {localImage ? (
                  <Image
                    source={localImage}
                    resizeMode="contain"
                    style={{ width: "100%", height: 190 }}
                  />
                ) : (
                  <View className="items-center gap-3">
                    <Text className="text-[40px]">🖼️</Text>
                    <Text className="text-[13px] text-slate-400">
                      연상 이미지 준비 중
                    </Text>
                  </View>
                )}
              </View>
            </View>

            {/* 한국어 뜻풀이 */}
            <View className="mt-4 rounded-2xl bg-surface p-4 shadow-neu-sm">
              <View className="flex-row items-center justify-between">
                <View className="flex-row items-center gap-1.5">
                  <View className="h-2 w-2 rounded-full bg-emerald-500" />
                  <Text className="text-[13px] font-bold text-slate-700">
                    한국어 뜻풀이
                  </Text>
                </View>
                <Pressable
                  onPress={() => setShowMeaning((v) => !v)}
                  className="flex-row items-center gap-1 active:opacity-70"
                >
                  <Text className="text-[12px] font-bold text-emerald-500">
                    {showMeaning ? "가리기" : "뜻 보기"}
                  </Text>
                  {showMeaning ? <ChevronUpIcon /> : <ChevronDownIcon />}
                </Pressable>
              </View>

              <Text
                className={`mt-2.5 text-[20px] font-black tracking-tight ${
                  showMeaning ? "text-slate-950" : "text-slate-300"
                }`}
              >
                {showMeaning ? word.meaning : "• • • • • •"}
              </Text>
            </View>
          </View>
        </ScrollView>

        {/* ── 자동 넘김 타이머 ─────────────────────────────── */}
        <View className="mb-2.5 gap-1.5 rounded-2xl bg-surface px-3.5 py-2.5 shadow-neu-sm">
          <View className="flex-row items-center justify-between px-0.5">
            <ClockIcon color={autoAdvance ? "#10b981" : "#94a3b8"} />
            <View className="flex-row items-baseline">
              <Text
                className={`text-[12px] font-extrabold tracking-tight ${
                  autoAdvance ? "text-emerald-600" : "text-slate-400"
                }`}
              >
                {mmss(elapsedSec)}
              </Text>
              <Text className="text-[12px] font-medium text-slate-400">
                {` / ${mmss(AUTO_ADVANCE_SEC)}`}
              </Text>
            </View>
          </View>
          <View className="h-2 w-full overflow-hidden rounded-full bg-canvas p-0.5 shadow-neu-inset">
            <View
              className={`h-full rounded-full ${
                autoAdvance ? "bg-emerald-500" : "bg-slate-300"
              }`}
              style={{ width: `${autoAdvance ? timerPct : 0}%` }}
            />
          </View>
        </View>

        {/* ── 이전 · 자동 넘김 토글 · 다음 ──────────────────── */}
        <View className="my-1 flex-row items-center justify-between gap-2.5 px-1">
          <Pressable
            onPress={() => onNavigate(prevId)}
            style={{ flex: 1 }}
            className="flex-row items-center justify-center gap-1.5 rounded-full bg-surface px-4 py-3 shadow-neu-sm active:scale-95 active:shadow-neu-pressed"
          >
            <ArrowLeftIcon />
            <Text className="text-[14px] font-bold text-slate-700">이전</Text>
          </Pressable>

          <Pressable
            accessibilityLabel="자동 넘김 켜기 끄기"
            onPress={() => setAutoAdvance(!autoAdvance)}
            style={{ flex: 1.4 }}
            className={`flex-row items-center justify-center gap-1.5 rounded-full px-3 py-3 active:scale-95 ${
              autoAdvance
                ? "bg-surface shadow-neu-sm"
                : "bg-canvas shadow-neu-inset"
            }`}
          >
            {autoAdvance ? <PlayIcon /> : <PauseIcon />}
            <Text className="text-[14px] font-bold text-slate-800">
              자동 넘김
            </Text>
            <View
              className={`ml-0.5 rounded-full px-1.5 py-0.5 ${
                autoAdvance ? "bg-emerald-500" : "bg-slate-400"
              }`}
            >
              <Text className="text-[11px] font-black text-white">
                {autoAdvance ? "ON" : "OFF"}
              </Text>
            </View>
          </Pressable>

          <Pressable
            onPress={() => onNavigate(nextId)}
            style={{ flex: 1 }}
            className="flex-row items-center justify-center gap-1.5 rounded-full bg-surface px-4 py-3 shadow-neu-sm active:scale-95 active:shadow-neu-pressed"
          >
            <Text className="text-[14px] font-bold text-slate-700">다음</Text>
            <ArrowRightIcon />
          </Pressable>
        </View>

        {/* ── 학습 평가 버튼 ───────────────────────────────── */}
        <View className="flex-row items-stretch gap-3 px-1 pb-4 pt-3">
          <Pressable
            onPress={() => decide("unsure")}
            style={{ flex: 1 }}
            className="flex-row items-center justify-center gap-2 rounded-[28px] bg-surface px-3 py-4 shadow-neu-sm active:scale-[0.98] active:shadow-neu-pressed"
          >
            <View className="h-7 w-7 items-center justify-center rounded-lg bg-slate-300">
              <AgainIcon />
            </View>
            <Text className="text-[14px] font-extrabold tracking-tight text-slate-800">
              아직 헷갈려요
            </Text>
          </Pressable>

          <Pressable
            onPress={() => decide("known")}
            style={{ flex: 1 }}
            className="flex-row items-center justify-center gap-2 rounded-[28px] bg-[#dff5ea] px-3 py-4 shadow-neu-sm active:scale-[0.98] active:shadow-neu-pressed"
          >
            <View className="h-6 w-6 items-center justify-center rounded-md bg-emerald-500">
              <CheckIcon />
            </View>
            <Text className="text-[15px] font-black tracking-tight text-emerald-800">
              외웠어요!
            </Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}
