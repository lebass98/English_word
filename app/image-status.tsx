import { Image } from "expo-image";
import { useEffect, useMemo, useRef, useState } from "react";
import { Platform, Pressable, ScrollView, Text, View } from "react-native";
import { BottomNav } from "../src/components/BottomNav";
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  PauseIcon,
  PictureIcon,
  PlayIcon,
} from "../src/components/icons";
import { PressableScale } from "../src/components/motion";
import { Screen, ScreenHeader } from "../src/components/Screen";
import { ImageBoard } from "../src/components/ImageBoard";
import { SegmentButton } from "../src/components/SegmentButton";
import {
  REPLACED_IMAGES,
  wordImageCount,
  wordImageSource,
} from "../src/constants/wordImages";
import { buildSlides, type Slide } from "../src/lib/imageSlides";
import replacedData from "../src/data/images/replaced.json";
import { useAppStore } from "../src/stores/useAppStore";

/**
 * 그림 현황 (디버그용). 탭 두 개로 나뉜다.
 *
 * - 순차 보기: 아래 설명
 * - 제작 현황표: 코스·유닛별로 어디까지 그렸는지 한눈에 본다 (ImageBoard)
 *
 * 모든 코스의 단어 그림을 뜻과 함께 하나씩 차례로 넘겨 본다. 퀴즈·학습과 달리
 * 유닛이 끝나도 멈추지 않고 다음 유닛·다음 코스로 이어지며, 끝에 닿으면
 * 처음으로 돌아간다. 교체한 그림에는 "교체됨" 표시가 붙는다.
 *
 * 교체 기록은 scripts/image_replacements.py 가 그림 저장소 기록에서 세어 둔다.
 */

type Tab = "viewer" | "board";
type Mode = "all" | "replaced" | "missing";

const MODES: { id: Mode; label: string }[] = [
  { id: "all", label: "전체" },
  { id: "replaced", label: "교체됨" },
  { id: "missing", label: "그림 없음" },
];

/** 자동 넘김 간격 (초) */
const SPEEDS = [0.7, 1.5, 3];

/** 다른 탭에 다녀와도 보던 자리에서 이어 보게 화면 밖에 기억해 둔다 */
const memory = {
  tab: "viewer" as Tab,
  scope: "all",
  mode: "all" as Mode,
  slideId: "",
  speed: 1.5,
};

export default function ImageStatusScreen() {
  const uiLang = useAppStore((s) => s.uiLang);
  // 그림 등록표가 바뀌면(Fast Refresh) 다시 센다
  const imageCount = wordImageCount();
  const { slides, courses } = useMemo(
    () => buildSlides(uiLang),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [uiLang, imageCount],
  );

  const [tab, setTab] = useState<Tab>(memory.tab);
  const scrollRef = useRef<ScrollView>(null);
  const [scope, setScope] = useState(memory.scope);
  const [mode, setMode] = useState<Mode>(memory.mode);
  const [speed, setSpeed] = useState(memory.speed);
  const [playing, setPlaying] = useState(false);

  /** 고른 범위와 보기에 맞는 칸들 */
  const list = useMemo(() => {
    let out: Slide[];
    if (scope === "all") {
      // 전체로 볼 때는 같은 그림을 한 번만 보여 준다
      const seen = new Set<string>();
      out = slides.filter((s) => {
        if (seen.has(s.imageKey)) return false;
        seen.add(s.imageKey);
        return true;
      });
    } else {
      out = slides.filter((s) => s.courseKey === scope);
    }
    if (mode === "replaced") out = out.filter((s) => s.replaced);
    if (mode === "missing") out = out.filter((s) => !s.has);
    return out;
  }, [slides, scope, mode]);

  // 보던 칸을 키로 기억한다. 범위를 바꿔도 같은 그림이 있으면 그 자리에서 잇는다
  const [slideId, setSlideId] = useState(memory.slideId);
  const found = list.findIndex((s) => s.id === slideId);
  const sameImage =
    found >= 0
      ? found
      : list.findIndex(
          (s) => s.imageKey === slides.find((o) => o.id === slideId)?.imageKey,
        );
  const index = Math.max(0, sameImage);
  const slide = list[index];

  useEffect(() => {
    Object.assign(memory, {
      tab,
      scope,
      mode,
      speed,
      slideId: slide?.id ?? "",
    });
  }, [tab, scope, mode, speed, slide]);

  /** n 칸 옮긴다. 끝을 넘으면 반대쪽 끝에서 이어진다 */
  const step = (n: number) => {
    if (list.length === 0) return;
    const next = (((index + n) % list.length) + list.length) % list.length;
    setSlideId(list[next].id);
  };

  /** 이전·다음 유닛의 첫 칸으로 */
  const stepUnit = (dir: 1 | -1) => {
    if (!slide || list.length === 0) return;
    const unitOf = (s: Slide) => `${s.courseKey}#${s.unitNo}`;
    const here = unitOf(slide);
    let i = index;
    // 지금 유닛을 벗어날 때까지 간다
    for (let n = 0; n < list.length && unitOf(list[i]) === here; n++) {
      i = (i + dir + list.length) % list.length;
    }
    if (dir === -1) {
      // 앞 유닛의 첫 칸까지 거슬러 올라간다
      const target = unitOf(list[i]);
      while (unitOf(list[(i - 1 + list.length) % list.length]) === target) {
        i = (i - 1 + list.length) % list.length;
        if (i === index) break;
      }
    }
    setSlideId(list[i].id);
  };

  // 자동 넘김. 끝에 닿아도 처음으로 돌아가 멈추지 않는다
  useEffect(() => {
    if (!playing || tab !== "viewer" || list.length === 0) return;
    const timer = setTimeout(() => step(1), speed * 1000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playing, tab, speed, slide, list]);

  // 다음 몇 장을 미리 받아 둬서 넘길 때 빈 칸이 뜨지 않게 한다
  useEffect(() => {
    const urls = [1, 2, 3]
      .map((n) => list[(index + n) % Math.max(1, list.length)])
      .map((s) => s && wordImageSource(s.word)?.uri)
      .filter((u): u is string => Boolean(u));
    if (urls.length) Image.prefetch(urls, { cachePolicy: "disk" });
  }, [index, list]);

  // 웹에서는 ← → 로 넘기고, 스페이스로 자동 넘김을 켜고 끈다
  useEffect(() => {
    if (Platform.OS !== "web" || typeof window === "undefined") return;
    if (tab !== "viewer") return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") step(1);
      else if (e.key === "ArrowLeft") step(-1);
      else if (e.key === "ArrowDown") stepUnit(1);
      else if (e.key === "ArrowUp") stepUnit(-1);
      else if (e.key === " ") setPlaying((p) => !p);
      else return;
      e.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const missingCount = useMemo(
    () => new Set(slides.filter((s) => !s.has).map((s) => s.imageKey)).size,
    [slides],
  );

  return (
    <Screen>
      <ScreenHeader>
        <View className="flex-1">
          <Text className="text-xl font-bold text-ink">그림 현황</Text>
          <Text className="mt-1 text-[12px] text-slate-500">
            그림 {imageCount.toLocaleString()}장 · 없음{" "}
            {missingCount.toLocaleString()} · 교체 {replacedData.total}장 ·{" "}
            {replacedData.generatedAt} 기준
          </Text>
        </View>
      </ScreenHeader>

      {/* 하단 독바에 가리지 않게 넉넉히 띄운다 */}
      <ScrollView
        ref={scrollRef}
        className="flex-1"
        contentContainerClassName="px-6 pb-32 pt-5"
      >
        <View className="flex-row gap-3">
          <SegmentButton
            label="순차 보기"
            selected={tab === "viewer"}
            onPress={() => setTab("viewer")}
          />
          <SegmentButton
            label="제작 현황표"
            selected={tab === "board"}
            onPress={() => setTab("board")}
          />
        </View>

        {tab === "board" ? (
          <ImageBoard
            slides={slides}
            courses={courses}
            onOpen={(target) => {
              // 누른 그림을 그 코스 안에서 이어 볼 수 있게 연다
              setMode("all");
              setScope(target.courseKey);
              setSlideId(target.id);
              setPlaying(false);
              setTab("viewer");
              scrollRef.current?.scrollTo({ y: 0, animated: false });
            }}
          />
        ) : (
          <>
            {/* 범위: 전체 또는 코스 하나 */}
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerClassName="gap-2 px-1 py-2"
            >
              <Chip
                label="전체"
                active={scope === "all"}
                onPress={() => setScope("all")}
              />
              {courses.map((c) => (
                <Chip
                  key={c.key}
                  label={c.label}
                  active={scope === c.key}
                  onPress={() => setScope(c.key)}
                />
              ))}
            </ScrollView>

            <View className="mt-1 flex-row gap-2 px-1">
              {MODES.map((m) => (
                <Chip
                  key={m.id}
                  label={m.label}
                  active={mode === m.id}
                  onPress={() => setMode(m.id)}
                />
              ))}
            </View>

            {slide ? (
              <SlideCard slide={slide} />
            ) : (
              <View className="mt-5 items-center rounded-3xl bg-surface p-10 shadow-neu-card">
                <Text className="text-[13px] text-slate-400">
                  보여 줄 그림이 없다
                </Text>
              </View>
            )}

            {/* 넘김 조작 */}
            <View className="mt-5 flex-row items-center justify-between">
              <RoundButton label="이전 유닛" onPress={() => stepUnit(-1)}>
                <Text
                  style={{ fontSize: 12, fontWeight: "700", color: "#64748b" }}
                >
                  U-
                </Text>
              </RoundButton>
              <RoundButton label="이전" onPress={() => step(-1)}>
                <ChevronLeftIcon size={26} color="#475569" />
              </RoundButton>
              <RoundButton
                label={playing ? "멈춤" : "자동 넘김"}
                big
                active={playing}
                onPress={() => setPlaying((p) => !p)}
              >
                {playing ? (
                  <PauseIcon size={26} color="#006C4C" />
                ) : (
                  <PlayIcon size={26} color="#006C4C" />
                )}
              </RoundButton>
              <RoundButton label="다음" onPress={() => step(1)}>
                <ChevronRightIcon size={26} color="#475569" />
              </RoundButton>
              <RoundButton label="다음 유닛" onPress={() => stepUnit(1)}>
                <Text
                  style={{ fontSize: 12, fontWeight: "700", color: "#64748b" }}
                >
                  U+
                </Text>
              </RoundButton>
            </View>

            <View className="mt-4 flex-row items-center justify-between px-1">
              <Text className="text-[12px] font-bold text-slate-500">
                {list.length ? index + 1 : 0} / {list.length.toLocaleString()}
              </Text>
              <View className="flex-row gap-2">
                {SPEEDS.map((s) => (
                  <Chip
                    key={s}
                    label={`${s}초`}
                    active={speed === s}
                    onPress={() => setSpeed(s)}
                  />
                ))}
              </View>
            </View>

            {/* 전체 중 어디쯤인지 */}
            <View className="mt-3 h-2 overflow-hidden rounded-full bg-canvas shadow-neu-inset">
              <View
                className="h-full rounded-full bg-mint"
                style={{
                  width: `${list.length ? ((index + 1) / list.length) * 100 : 0}%`,
                }}
              />
            </View>

            {Platform.OS === "web" && (
              <Text className="mt-2 text-[11px] text-slate-400">
                ← → 넘김 · ↑ ↓ 유닛 이동 · 스페이스 자동 넘김
              </Text>
            )}

            <ReplacedList
              onPick={(key) => {
                const target = slides.find((s) => s.imageKey === key);
                if (!target) return;
                setMode("replaced");
                if (scope !== "all" && scope !== target.courseKey)
                  setScope("all");
                setSlideId(target.id);
              }}
            />
          </>
        )}
      </ScrollView>

      <BottomNav />
    </Screen>
  );
}

/** 그림 한 장과 낱말·뜻 */
function SlideCard({ slide }: { slide: Slide }) {
  const source = wordImageSource(slide.word);
  const { word, replaced } = slide;

  return (
    <View className="mt-5 overflow-hidden rounded-3xl bg-surface shadow-neu-card">
      <View style={{ width: "100%", aspectRatio: 1 }} className="bg-canvas">
        {source ? (
          <Image
            source={source}
            contentFit="cover"
            transition={120}
            cachePolicy="disk"
            style={{ width: "100%", height: "100%" }}
          />
        ) : (
          <View className="flex-1 items-center justify-center gap-3">
            <PictureIcon size={44} color="#cbd5e1" />
            <Text className="text-[13px] font-bold text-rose-400">
              그림 없음
            </Text>
          </View>
        )}

        {/* 교체한 그림 표시 */}
        {replaced && (
          <View
            style={{
              position: "absolute",
              left: 12,
              top: 12,
              backgroundColor: "#f59e0b",
              borderRadius: 999,
              paddingHorizontal: 12,
              paddingVertical: 4,
            }}
          >
            <Text style={{ color: "#ffffff", fontSize: 12, fontWeight: "700" }}>
              교체됨 · {replaced.date.slice(5).replace("-", "/")}
              {replaced.count > 1 ? ` (${replaced.count}회)` : ""}
            </Text>
          </View>
        )}
      </View>

      <View className="p-5">
        <Text className="text-[11px] font-bold tracking-wider text-slate-400">
          {slide.course} · U{slide.unitNo} · {slide.noInUnit}/{slide.unitSize}
          {"  "}
          <Text className="font-normal">{word.id}</Text>
        </Text>
        <View className="mt-1.5 flex-row flex-wrap items-baseline gap-x-2">
          <Text
            className="font-bold text-ink"
            style={{ fontSize: 28, lineHeight: 36 }}
          >
            {word.word}
          </Text>
          {word.phonetic ? (
            <Text className="text-[13px] text-slate-400">{word.phonetic}</Text>
          ) : null}
        </View>
        <Text className="mt-1 text-[16px] leading-[24px] text-slate-700">
          {word.meaning}
        </Text>
        {/* 그림을 낱말과 다른 이름으로 찾는 경우 (같은 뜻끼리 그림 공유) */}
        {slide.imageKey !== word.word && (
          <Text className="mt-2 text-[11px] text-slate-400">
            그림 열쇠: {slide.imageKey}
          </Text>
        )}
      </View>
    </View>
  );
}

/** 교체한 그림 목록. 누르면 그 그림으로 간다 */
function ReplacedList({ onPick }: { onPick: (key: string) => void }) {
  const items = Object.entries(REPLACED_IMAGES);

  return (
    <View className="mt-8 rounded-3xl bg-surface p-5 shadow-neu-card">
      <Text className="text-[12px] font-bold tracking-widest text-slate-400">
        교체한 그림 {items.length}장
      </Text>
      {items.length === 0 ? (
        <Text className="mt-2 text-[12px] text-slate-400">
          아직 교체한 그림이 없다
        </Text>
      ) : (
        <View className="mt-3 flex-row flex-wrap gap-1.5">
          {items.map(([key, r]) => (
            <Pressable
              key={key}
              onPress={() => onPick(key)}
              className="rounded-full bg-canvas px-2.5 py-1 shadow-neu-inset active:opacity-60"
            >
              <Text className="text-[12px] text-slate-600">
                {key}{" "}
                <Text className="text-[11px] text-amber-600">
                  {r.date.slice(5).replace("-", "/")}
                </Text>
              </Text>
            </Pressable>
          ))}
        </View>
      )}
      <Text className="mt-3 text-[11px] text-slate-400">
        그림 저장소 기록에서 셈 · 교체 후 scripts/image_replacements.py 로 갱신
      </Text>
    </View>
  );
}

function Chip({
  label,
  active,
  onPress,
}: {
  label: string;
  active: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityState={{ selected: active }}
      // 칩도 높이를 고정해 줄마다 들쭉날쭉하지 않게 한다
      style={{ height: 32, justifyContent: "center" }}
      className={`rounded-full px-3.5 ${
        active
          ? "bg-canvas shadow-neu-inset"
          : "bg-surface shadow-neu-sm active:shadow-neu-pressed"
      }`}
    >
      <Text
        className={`text-[12px] font-bold ${
          active ? "text-mint-dark" : "text-slate-500"
        }`}
      >
        {label}
      </Text>
    </Pressable>
  );
}

function RoundButton({
  label,
  big,
  active,
  onPress,
  children,
}: {
  label: string;
  big?: boolean;
  active?: boolean;
  onPress: () => void;
  children: React.ReactNode;
}) {
  return (
    <PressableScale
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={label}
      // 크기는 인라인으로 고정한다. 클래스로 두면 CSS 가 새로 만들어지기 전까지 무너진다
      style={{
        // 높이는 모두 같게 두고, 재생 버튼만 폭을 넓혀 구분한다
        width: big ? 76 : 52,
        height: 52,
        borderRadius: 999,
        alignItems: "center",
        justifyContent: "center",
      }}
      className={
        active ? "bg-canvas shadow-neu-inset" : "bg-surface shadow-neu-sm"
      }
    >
      {children}
    </PressableScale>
  );
}
