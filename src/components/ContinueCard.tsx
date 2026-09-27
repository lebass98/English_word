import { useRouter } from "expo-router";
import { ReactNode, useEffect, useMemo, useState } from "react";
import { Animated, Easing, Text, View } from "react-native";
import { Image } from "expo-image";
import Svg, { Defs, LinearGradient, Rect, Stop } from "react-native-svg";
import { PillButton } from "./PillButton";
import { SectionLabel } from "./SectionLabel";
import { GAUGE_FILL_STOPS } from "./GaugeBar";
import { EASE_OUT, NATIVE_DRIVER, PressableScale } from "./motion";
import { useGrades } from "../constants/grades";
import { studyLanguageOf, studyLangOfWordId } from "../constants/languages";
import { useVocab } from "../constants/words";
import { useT } from "../i18n";
import { wordImageSource } from "../constants/wordImages";
import { speakWord } from "../lib/speech";
import {
  availableGrades,
  continuePoint,
  knownCountInWords,
} from "../stores/selectors";
import { useAppStore } from "../stores/useAppStore";
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  PictureIcon,
  PlayIcon,
  RocketIcon,
  ShuffleIcon,
  SpeakerIcon,
} from "./icons";

/** 스켈레톤과 실제 카드의 높이를 맞춰 저장소 로드 직후 화면이 밀리지 않게 한다 */
const CARD_MIN_HEIGHT = "min-h-[272px]";

/** 파형 카드 높이와 왼쪽 그림 폭 (px) */
const WAVE_H = 92;
const WAVE_IMG_W = 130;
/** 카드 서피스 색. 그림이 이 색으로 흐려지며 사라진다 */
const SURFACE = "#f1f2f6";

/** 낱말마다 늘 같은 높이가 나오게 철자로 막대 높이(14~44px)를 정한다 */
function barHeight(seed: string): number {
  let h = 0;
  for (const ch of seed) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return 14 + (h % 31);
}

function Thumb({ children }: { children: ReactNode }) {
  return (
    <View className="h-[72px] w-[72px] items-center justify-center overflow-hidden rounded-2xl bg-canvas shadow-neu-inset">
      {children}
    </View>
  );
}

/** 볼록한 원형 버튼. 누르면 쏙 작아졌다 튕겨 돌아온다 */
function RoundButton({
  children,
  onPress,
  label,
  size = 52,
}: {
  children: ReactNode;
  onPress: () => void;
  label: string;
  size?: number;
}) {
  return (
    <PressableScale
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={label}
      scaleTo={0.88}
      style={{ width: size, height: size }}
      className="items-center justify-center rounded-full bg-surface shadow-neu-sm"
    >
      {children}
    </PressableScale>
  );
}

/**
 * 유닛 진행 막대들. 처음 뜰 때 왼쪽부터 차례로 솟아오르고,
 * 외운 단어가 늘어 색이 바뀌면 그 막대만 스르르 물든다.
 */
function WaveBars({
  words,
  currentId,
  knownIds,
}: {
  words: { id: string; word: string }[];
  currentId: string;
  knownIds: Set<string>;
}) {
  const [rise] = useState(() => new Animated.Value(0));
  useEffect(() => {
    Animated.timing(rise, {
      toValue: 1,
      duration: 900,
      delay: 200,
      easing: EASE_OUT,
      useNativeDriver: NATIVE_DRIVER,
    }).start();
  }, [rise]);
  const n = words.length;
  // 막대마다 조금씩 늦게 출발하도록 입력 구간을 밀어 둔다
  const lag = 6;
  return (
    <View className="flex-1 flex-row items-center justify-center gap-[3px]">
      {words.map((w, i) => {
        const current = w.id === currentId;
        const known = knownIds.has(w.id);
        return (
          <Animated.View
            key={w.id}
            style={{
              height: barHeight(w.word),
              transform: [
                {
                  scaleY: rise.interpolate({
                    inputRange: [i / (n + lag), (i + lag) / (n + lag)],
                    outputRange: [0.15, 1],
                    extrapolate: "clamp",
                  }),
                },
              ],
            }}
          >
            <View
              className={`h-full w-[3px] rounded-full ${
                current ? "bg-mint-dark" : known ? "bg-mint" : "bg-[#cfd3dc]"
              }`}
            />
          </Animated.View>
        );
      })}
    </View>
  );
}

/** 발음이 나오는 동안 버튼 둘레로 퍼져 나가는 물결 */
function SpeakPulse({ active }: { active: boolean }) {
  const [v] = useState(() => new Animated.Value(0));
  useEffect(() => {
    if (!active) {
      v.stopAnimation();
      v.setValue(0);
      return;
    }
    const loop = Animated.loop(
      Animated.timing(v, {
        toValue: 1,
        duration: 900,
        easing: Easing.out(Easing.quad),
        useNativeDriver: NATIVE_DRIVER,
      }),
    );
    loop.start();
    return () => loop.stop();
  }, [active, v]);
  return (
    <Animated.View
      pointerEvents="none"
      style={{
        position: "absolute",
        width: 56,
        height: 56,
        borderRadius: 28,
        borderWidth: 2,
        borderColor: "#5fd6e8",
        opacity: v.interpolate({ inputRange: [0, 1], outputRange: [active ? 0.7 : 0, 0] }),
        transform: [
          { scale: v.interpolate({ inputRange: [0, 1], outputRange: [1, 1.45] }) },
        ],
      }}
    />
  );
}

/**
 * 홈 화면의 이어하기 칸.
 * 음악 플레이어처럼 두 층으로 그린다.
 * - 위: 단어 그림이 흐려지는 파형 카드. 막대 하나가 유닛의 단어 하나이고 외운 단어는 민트로 찬다
 * - 아래: 이전 단어 · 발음 듣기 · 다음 단어 · 유닛에서 아무 단어
 * 마지막으로 보던 단어가 없으면 첫 단어부터 시작하는 카드를 보여준다.
 */
export function ContinueCard() {
  const router = useRouter();
  const hydrated = useAppStore((s) => s.hydrated);
  const lastStudied = useAppStore((s) => s.lastStudied);
  const entries = useAppStore((s) => s.entries);
  const speechVolume = useAppStore((s) => s.speechVolume);
  const setActiveGradeId = useAppStore((s) => s.setActiveGradeId);
  const vocab = useVocab();
  const grades = useGrades();
  const t = useT();
  /** 지금 발음이 나오는 중인지. 버튼 둘레 물결을 그린다 */
  const [speaking, setSpeaking] = useState(false);

  // 아래 계산들은 훅이라 hydrated 분기보다 먼저, 그리고 항상 실행되어야 한다.

  // 단어 색인 조회와 유닛 슬라이스를 렌더마다 돌리지 않는다
  const point = useMemo(
    () => continuePoint(lastStudied, vocab, grades),
    [lastStudied, vocab, grades],
  );

  // 기록이 없을 때 보여줄 첫 단어. 상수에서 나오므로 한 번만 계산한다
  const startPoint = useMemo(() => {
    const grade = availableGrades(grades)[0];
    const first = grade ? vocab.byLevel[grade.id]?.[0] : undefined;
    return grade && first ? { grade, first } : null;
  }, [grades, vocab]);

  /** 이어할 단어가 든 유닛의 단어들과, 학년 전체에서 앞뒤 단어 */
  const around = useMemo(() => {
    if (!point) return null;
    const unitWords =
      vocab.unitsOf(point.gradeId).find((u) => u.unitNo === point.unitNo)
        ?.words ?? [];
    const found = vocab.find(point.word.id);
    return {
      unitWords,
      prev: found ? found.words[found.index - 1] : undefined,
      next: found ? found.words[found.index + 1] : undefined,
    };
  }, [point, vocab]);

  // selectors의 continuePoint는 unitKnown을 0으로 주므로 여기서 직접 센다
  const unitKnown = useMemo(
    () => (around ? knownCountInWords(entries, around.unitWords) : 0),
    [entries, around],
  );

  // 저장소를 읽기 전에 "시작" 카드를 잠깐 보여주면 이어하기 카드로 바뀌며 깜빡인다
  if (!hydrated) {
    return <View className={CARD_MIN_HEIGHT} />;
  }

  if (!point || !around) {
    if (!startPoint) return null;
    const { grade, first } = startPoint;

    const start = () => {
      setActiveGradeId(grade.id);
      router.push(`/study/${first.id}`);
    };

    return (
      <View>
        <SectionLabel label="START" sub={`${grade.short} · UNIT 1`} />
        <View className="mt-4 rounded-3xl bg-surface p-6 shadow-neu-card">
          <PressableScale
            onPress={start}
            accessibilityRole="button"
            accessibilityLabel={`${grade.short} UNIT 1 ${t("continue.start")}`}
            className="flex-row items-center gap-4"
          >
            <Thumb>
              <RocketIcon size={32} color="#0EB582" />
            </Thumb>
            <View className="flex-1">
              <Text className="text-[12px] font-bold text-mint">
                {t("continue.start")}
              </Text>
              <Text className="mt-1 text-[20px] font-bold text-ink">
                {grade.short} UNIT 1
              </Text>
              <Text className="mt-1 text-[14px] text-slate-500">
                {first.word}
              </Text>
            </View>
          </PressableScale>

          <PillButton
            className="mt-6"
            label={t("continue.start")}
            variant="primary"
            size="lg"
            onPress={start}
          />
        </View>
      </View>
    );
  }

  const { word } = point;
  const source = wordImageSource(word);

  const open = (wordId: string) => {
    setActiveGradeId(point.gradeId);
    router.push(`/study/${wordId}`);
  };
  const resume = () => open(word.id);
  const speak = () =>
    speakWord(word.word, {
      lang: studyLanguageOf(studyLangOfWordId(word.id)).speechCode,
      volume: speechVolume,
      onStart: () => setSpeaking(true),
      onDone: () => setSpeaking(false),
    });
  const shuffle = () => {
    const others = around.unitWords.filter((w) => w.id !== word.id);
    const pool = others.length > 0 ? others : around.unitWords;
    open(pool[Math.floor(Math.random() * pool.length)].id);
  };

  return (
    <View>
      <SectionLabel
        label="CONTINUE"
        sub={t("home.continueSub", {
          grade: point.gradeShort,
          unit: point.unitNo,
        })}
        right={
          <RoundButton onPress={resume} label={t("continue.resume")}>
            <PlayIcon size={22} color="#0EB582" />
          </RoundButton>
        }
      />

      {/* 파형 카드: 그림이 오른쪽으로 흐려지고, 그 옆에 유닛 진행 막대가 선다 */}
      <PressableScale
        onPress={resume}
        accessibilityRole="button"
        accessibilityLabel={t("a11y.unitProgress", {
          unit: point.unitNo,
          total: point.unitLen,
          known: unitKnown,
        })}
        style={{ height: WAVE_H }}
        className="mt-4 flex-row items-center overflow-hidden rounded-3xl bg-surface shadow-neu-card"
      >
        <View
          style={{ width: WAVE_IMG_W, height: WAVE_H }}
          className="absolute left-0 top-0 items-center justify-center"
        >
          {source ? (
            <Image
              source={source}
              contentFit="cover"
              style={{ width: "100%", height: "100%" }}
            />
          ) : (
            <PictureIcon size={28} color="#cbd5e1" />
          )}
          <Svg
            width={WAVE_IMG_W}
            height={WAVE_H}
            style={{ position: "absolute", left: 0, top: 0 }}
          >
            <Defs>
              <LinearGradient id="continueFade" x1="0" y1="0" x2="1" y2="0">
                <Stop offset="0.3" stopColor={SURFACE} stopOpacity={0} />
                <Stop offset="1" stopColor={SURFACE} stopOpacity={1} />
              </LinearGradient>
            </Defs>
            <Rect width={WAVE_IMG_W} height={WAVE_H} fill="url(#continueFade)" />
          </Svg>
        </View>

        <View
          style={{ marginLeft: WAVE_IMG_W - 20 }}
          className="flex-1 flex-row items-center gap-2 pr-4"
        >
          <Text className="text-[12px] font-bold text-slate-500">
            {unitKnown}
          </Text>
          <WaveBars
            words={around.unitWords}
            currentId={word.id}
            knownIds={
              new Set(
                around.unitWords
                  .filter((w) => entries[w.id]?.status === "known")
                  .map((w) => w.id),
              )
            }
          />
          <Text className="text-[12px] font-bold text-slate-500">
            {point.unitLen}
          </Text>
        </View>
      </PressableScale>

      {/* 플레이어 카드 */}
      <View className="mt-4 flex-row items-center justify-between gap-3 rounded-3xl bg-surface py-4 pl-5 pr-4 shadow-neu-card">
        <View className="flex-1">
          <Text numberOfLines={1} className="text-[17px] font-extrabold text-ink">
            {word.word}
          </Text>
          <Text numberOfLines={1} className="text-[12px] text-slate-500">
            {word.meaning}
          </Text>
        </View>
        <View className="flex-row items-center gap-1">
          <PressableScale
            onPress={() => around.prev && open(around.prev.id)}
            disabled={!around.prev}
            accessibilityRole="button"
            accessibilityLabel={t("study.prevWord")}
            className="h-11 w-9 items-center justify-center"
          >
            <ChevronLeftIcon
              size={26}
              color={around.prev ? "#94a3b8" : "#dde1e8"}
            />
          </PressableScale>
          <PressableScale
            onPress={speak}
            accessibilityRole="button"
            accessibilityLabel={t("study.speak", { word: word.word })}
            scaleTo={0.9}
            className="h-14 w-14 items-center justify-center rounded-full bg-surface shadow-neu-sm"
          >
            <SpeakPulse active={speaking} />
            <View className="h-10 w-10 items-center justify-center overflow-hidden rounded-full">
              <Svg width={40} height={40} style={{ position: "absolute" }}>
                <Defs>
                  <LinearGradient id="continuePlay" x1="0" y1="0" x2="1" y2="1">
                    {GAUGE_FILL_STOPS.slice(0, 2).map((s) => (
                      <Stop key={s.offset} offset={s.offset} stopColor={s.color} />
                    ))}
                  </LinearGradient>
                </Defs>
                <Rect width={40} height={40} fill="url(#continuePlay)" />
              </Svg>
              {/* 웹에서 absolute 인 그라데이션이 정적 배치된 svg 아이콘을 덮지 않게 View 로 감싼다 */}
              <View>
                <SpeakerIcon size={20} color="#ffffff" />
              </View>
            </View>
          </PressableScale>
          <PressableScale
            onPress={() => around.next && open(around.next.id)}
            disabled={!around.next}
            accessibilityRole="button"
            accessibilityLabel={t("study.nextWord")}
            className="h-11 w-9 items-center justify-center"
          >
            <ChevronRightIcon
              size={26}
              color={around.next ? "#94a3b8" : "#dde1e8"}
            />
          </PressableScale>
          <PressableScale
            onPress={shuffle}
            accessibilityRole="button"
            accessibilityLabel={t("home.randomWord")}
            className="h-11 w-9 items-center justify-center"
          >
            <ShuffleIcon size={20} color="#94a3b8" />
          </PressableScale>
        </View>
      </View>
    </View>
  );
}
