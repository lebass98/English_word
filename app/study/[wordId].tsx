import { useLocalSearchParams, useRouter } from "expo-router";
import { useCallback, useEffect, useState } from "react";
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
import { SafeAreaView } from "react-native-safe-area-context";
import {
  AgainIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronUpIcon,
  PauseIcon,
  PlayIcon,
  SpeakerIcon,
} from "../../src/components/icons";
import { PillButton } from "../../src/components/PillButton";
import { GRADES } from "../../src/constants/grades";
import { UNIT_SIZE, findWord, type Word } from "../../src/constants/words";
import { WORD_IMAGES } from "../../src/constants/wordImages";
import { speakWord, stopSpeaking } from "../../src/lib/speech";
import { useAppStore, type WordStatus } from "../../src/stores/useAppStore";

/** 자동 넘김 간격 (초) */
const AUTO_ADVANCE_SEC = 15;

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
      onBack={() => {
        // 주소로 바로 들어오거나 새로고침한 경우엔 되돌아갈 기록이 없다.
        // 그때는 해당 학년의 유닛 목록으로 보낸다.
        if (router.canGoBack()) router.back();
        else router.replace(`/grade/${gradeId}`);
      }}
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
  const setWordStatus = useAppStore((s) => s.setWordStatus);

  const { width: screenWidth } = useWindowDimensions();

  /** 예문을 보여줄지 여부. 끄면 뜻만 남고 예문은 통째로 가려진다 */
  const [showExample, setShowExample] = useState(true);
  const [speaking, setSpeaking] = useState(false);
  /** 자동 넘김 진행도 0 → 1. 애니메이션 값이라 매 프레임 부드럽게 움직인다.
      한 번만 만들어 두고 계속 같은 값을 쓴다 */
  const [progress] = useState(() => new Animated.Value(0));

  const advance = useCallback(() => onNavigate(nextId), [onNavigate, nextId]);

  // 자동 넘김 타이머.
  // 예전에는 200ms마다 상태를 바꿔 바를 다시 그렸는데, 그 간격만큼 계단처럼 끊겨 보였다.
  // 지금은 15초 동안 0에서 1까지 일정한 속도로 흐르는 애니메이션 하나로 처리해
  // 왼쪽에서 오른쪽으로 끊김 없이 채워진다.
  useEffect(() => {
    progress.setValue(0);
    if (!autoAdvance) return;

    const animation = Animated.timing(progress, {
      toValue: 1,
      duration: AUTO_ADVANCE_SEC * 1000,
      easing: Easing.linear,
      // 너비는 레이아웃 속성이라 네이티브 드라이버를 쓸 수 없다
      useNativeDriver: false,
    });
    animation.start(({ finished }) => {
      if (finished) advance();
    });

    return () => animation.stop();
  }, [autoAdvance, advance, progress]);

  // 단어가 바뀌면 발음을 자동으로 한 번 들려준다.
  // (단어마다 key로 새로 마운트되므로 단어당 정확히 한 번 실행된다)
  // 화면을 벗어날 때는 재생 중인 음성을 멈춘다.
  useEffect(() => {
    speakWord(word.word, {
      onStart: () => setSpeaking(true),
      onDone: () => setSpeaking(false),
    });
    return stopSpeaking;
  }, [word.word]);

  // 헤더는 자리가 좁으므로 짧은 이름을 쓴다 (중학 2학년 → 중2)
  const gradeLabel = GRADES.find((g) => g.id === gradeId)?.short ?? "";
  const unitNo = Math.floor(index / UNIT_SIZE) + 1;
  const posInUnit = (index % UNIT_SIZE) + 1;
  // 마지막 유닛은 20개보다 적을 수 있다.
  const unitLen = Math.min(UNIT_SIZE, total - (unitNo - 1) * UNIT_SIZE);
  const localImage = WORD_IMAGES[word.id] || WORD_IMAGES[word.word];

  // 단어가 길어도 두 줄로 넘기지 않고 글자 크기를 줄여 한 줄에 담는다.
  // 단어는 이미지 패널 위에 얹히므로 그 안쪽 폭을 기준으로 계산한다.
  // 화면 좌우 여백(48) + 카드 안쪽 여백(48) + 겹침 영역 좌우 여백(32)
  //   + 스피커 버튼(44) + 버튼과의 간격(12)
  const wordAreaWidth = Math.max(110, screenWidth - 184);
  // 굵은 글씨는 한 글자가 글자 크기의 약 0.58배 너비를 차지한다
  // 최대 크기는 24px (이미지 위에 얹히므로 기존 34px에서 약 30% 줄였다)
  const wordFontSize = Math.max(
    10,
    Math.min(24, Math.floor(wordAreaWidth / (word.word.length * 0.58))),
  );


  const handleSpeak = () => {
    speakWord(word.word, {
      onStart: () => setSpeaking(true),
      onDone: () => setSpeaking(false),
    });
  };

  const decide = (next: WordStatus) => {
    setWordStatus(word.id, next);
    onNavigate(nextId);
  };

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View className="w-full flex-1">
        {/* ── 상단 바: 뒤로 · 유닛/진행 · 자동 넘김 ──────────── */}
        <View className="flex-row items-center justify-between px-6 pt-2">
          <Pressable
            onPress={onBack}
            accessibilityLabel="뒤로 가기"
            className="h-11 w-11 items-center justify-center rounded-full bg-surface shadow-neu-sm active:scale-95 active:shadow-neu-pressed"
          >
            <ChevronLeftIcon />
          </Pressable>

          {/* 유닛과 진행 개수를 하나의 알약에 담는다 */}
          <View className="relative mx-2 h-11 flex-1 flex-row items-center justify-center gap-2 overflow-hidden rounded-full bg-surface px-4 shadow-neu-sm">
            <Text
              numberOfLines={1}
              className="text-[14px] font-bold leading-[15px] tracking-tight text-slate-700"
            >
              {gradeLabel} UNIT {unitNo}
            </Text>
            <Text className="text-[14px] leading-[15px] text-slate-300">·</Text>
            <View className="flex-row items-center">
              <Text className="text-[13px] font-extrabold leading-[15px] text-emerald-500">
                {posInUnit}
              </Text>
              <Text className="text-[13px] font-medium leading-[15px] text-slate-400">
                /{unitLen}
              </Text>
            </View>

            {/* 유닛 진행률: 알약 안쪽 하단에 겹쳐서 표시한다 (높이 3px) */}
            <View className="absolute inset-x-0 bottom-0 h-[3px] bg-slate-200">
              <View
                className="h-full bg-emerald-500"
                style={{ width: `${(posInUnit / unitLen) * 100}%` }}
              />
            </View>
          </View>

          {/* 자동 넘김 켜기/끄기 (중간 버튼 줄에서 헤더로 옮김) */}
          <Pressable
            accessibilityLabel="자동 넘김 켜기 끄기"
            onPress={() => setAutoAdvance(!autoAdvance)}
            className={`h-11 flex-row items-center justify-center gap-1 rounded-full px-3.5 active:scale-95 ${
              autoAdvance
                ? "bg-surface shadow-neu-sm"
                : "bg-canvas shadow-neu-inset"
            }`}
          >
            {autoAdvance ? <PlayIcon size={14} /> : <PauseIcon size={14} />}
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
        </View>

        {/* ── 메인 플래시카드 ──────────────────────────────── */}
        <ScrollView
          className="flex-1"
          contentContainerClassName="px-6 pb-10 pt-8"
          showsVerticalScrollIndicator={false}
        >
          <View className="rounded-[32px] bg-surface p-6 shadow-neu-card">
            {/* 연상 이미지 + 좌우 이동 버튼.
                바깥 View는 잘라내지 않아야 화살표가 패널 밖으로 걸쳐 보인다.
                이미지가 1024x1024 정사각형이라 패널도 정사각형으로 꽉 채운다 */}
            <View className="relative w-full">
              <View className="aspect-square w-full overflow-hidden rounded-2xl bg-canvas shadow-neu-inset">
                {localImage ? (
                  <Image
                    source={localImage}
                    resizeMode="cover"
                    style={{ width: "100%", height: "100%" }}
                  />
                ) : (
                  <View className="flex-1 items-center justify-center gap-3">
                    <Text className="text-[40px]">🖼️</Text>
                    <Text className="text-[13px] text-slate-400">
                      연상 이미지 준비 중
                    </Text>
                  </View>
                )}

                {/* 단어 · 발음기호 · 발음 듣기: 이미지 위쪽에 겹쳐서 표시한다 */}
                <View className="absolute inset-x-0 top-0 flex-row items-start justify-between px-4 pb-3 pt-4">
                  <View className="flex-1 pr-3">
                    <Text
                      numberOfLines={1}
                      adjustsFontSizeToFit
                      style={{
                        fontSize: wordFontSize,
                        lineHeight: Math.round(wordFontSize * 1.15),
                      }}
                      className="font-black tracking-tight text-slate-900"
                    >
                      {word.word}
                    </Text>
                    {word.phonetic && (
                      <Text className="mt-1 text-[13px] tracking-wide text-slate-500">
                        {word.phonetic}
                      </Text>
                    )}
                  </View>
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

                {/* 자동 넘김 초시계: 이미지 카드 안쪽 하단에 겹쳐서 표시한다 */}
                <View className="absolute inset-x-0 bottom-0 h-1.5 bg-slate-200">
                  {/* Animated.View 에는 className 이 적용되지 않아
                      높이와 색을 인라인 스타일로 지정한다 */}
                  <Animated.View
                    style={{
                      height: "100%",
                      backgroundColor: autoAdvance ? "#10b981" : "#cbd5e1",
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
                accessibilityLabel="이전 단어"
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
                accessibilityLabel="다음 단어"
                disabled={!nextId}
                onPress={() => onNavigate(nextId)}
                style={{ top: "50%", marginTop: -18, right: -16 }}
                className={`absolute h-9 w-9 items-center justify-center rounded-full bg-surface shadow-neu-sm active:scale-95 active:shadow-neu-pressed ${
                  nextId ? "" : "opacity-40"
                }`}
              >
                <ChevronRightIcon size={14} />
              </Pressable>
            </View>

            {/* 한국어 뜻풀이 */}
            <View className="mt-4 rounded-2xl bg-surface p-4 shadow-neu-sm">
              {/* 한글 뜻과 가리기 버튼을 한 줄에 둔다 (제목 없이) */}
              <View className="flex-row items-center justify-between gap-3">
                <Text className="flex-1 text-[20px] font-black tracking-tight text-slate-950">
                  {word.meaning}
                </Text>
                <Pressable
                  onPress={() => setShowExample((v) => !v)}
                  className="flex-row items-center gap-1 active:opacity-70"
                >
                  <Text className="text-[12px] font-bold text-emerald-500">
                    {showExample ? "가리기" : "보기"}
                  </Text>
                  {showExample ? <ChevronUpIcon /> : <ChevronDownIcon />}
                </Pressable>
              </View>

              {/* 예문: 가리기를 누르면 영어와 한글 해석을 통째로 감춘다.
                  뜻만 남아서 스스로 확인해 보기 좋다 */}
              {showExample && word.example && (
                <View className="mt-3 gap-1 border-t border-slate-200 pt-3">
                  <Text className="text-[13px] font-semibold leading-snug text-slate-800">
                    <Text className="font-bold text-emerald-600">예문 </Text>
                    {word.example}
                  </Text>
                  {word.exampleKo && (
                    <Text className="text-[12px] font-medium leading-snug text-slate-500">
                      {word.exampleKo}
                    </Text>
                  )}
                </View>
              )}
            </View>
          </View>
        </ScrollView>

        {/* ── 학습 평가 버튼 ───────────────────────────────── */}
        <View className="mx-6 flex-row items-stretch gap-3 px-1 pb-4 pt-3">
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
