import { Image } from "expo-image";
import { useMemo, useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { PictureIcon } from "./icons";
import { wordImageCount, wordImageSource } from "../constants/wordImages";
import type { Slide, SlideCourse } from "../lib/imageSlides";
import dailyCounts from "../data/images/dailyCounts.json";
import type { LiveReplaced } from "../lib/liveReplaced";

/**
 * 그림 제작 현황표 (디버그용). 예전 그림 현황판을 다시 살린 것이다.
 *
 * 코스마다 유닛 칸을 늘어놓아 어디까지 그렸는지 한눈에 보고, 칸을 누르면
 * 그 유닛 그림 20장을 작게 펼친다. 교체한 그림이 든 곳은 주황으로 칠해
 * 처음 그린 것(초록)과 구분한다. 작은 그림을 누르면 순차 보기로 넘어간다.
 *
 * 색은 인라인으로 둔다. 클래스로 두면 CSS 가 새로 만들어지기 전까지 빠진다.
 */

/** 처음 그린 그림 */
const MADE = "#0EB582";
/** 교체한 그림 */
const REPLACED = "#f59e0b";
/** 아직 없는 그림 */
const EMPTY = "#cbd5e1";

interface BoardUnit {
  no: number;
  slides: Slide[];
  made: number;
  replaced: number;
}

interface BoardCourse extends SlideCourse {
  total: number;
  made: number;
  replaced: number;
  doneUnits: number;
  units: BoardUnit[];
}

function buildBoard(slides: Slide[], courses: SlideCourse[]) {
  const byCourse = new Map<string, BoardCourse>();
  for (const c of courses) {
    byCourse.set(c.key, {
      ...c,
      total: 0,
      made: 0,
      replaced: 0,
      doneUnits: 0,
      units: [],
    });
  }
  for (const s of slides) {
    const c = byCourse.get(s.courseKey)!;
    let unit = c.units[c.units.length - 1];
    if (!unit || unit.no !== s.unitNo) {
      unit = { no: s.unitNo, slides: [], made: 0, replaced: 0 };
      c.units.push(unit);
    }
    unit.slides.push(s);
    c.total += 1;
    if (s.has) {
      unit.made += 1;
      c.made += 1;
    }
    if (s.replaced) {
      unit.replaced += 1;
      c.replaced += 1;
    }
  }
  for (const c of byCourse.values()) {
    c.doneUnits = c.units.filter((u) => u.made === u.slides.length).length;
  }

  // 같은 뜻을 가리키는 낱말은 그림 한 장을 함께 쓰므로 그림 단위로도 센다
  const missing = new Set(slides.filter((s) => !s.has).map((s) => s.imageKey));
  return {
    courses: [...byCourse.values()],
    slots: slides.length,
    filledSlots: slides.filter((s) => s.has).length,
    replacedSlots: slides.filter((s) => s.replaced).length,
    toDraw: missing.size,
  };
}

export function ImageBoard({
  slides,
  courses,
  live,
  onOpen,
}: {
  slides: Slide[];
  courses: SlideCourse[];
  /** 교체 기록. 화면을 열 때마다 그림 저장소에서 다시 확인한다 */
  live: LiveReplaced;
  /** 그림 하나를 순차 보기로 연다 */
  onOpen: (slide: Slide) => void;
}) {
  const board = useMemo(() => buildBoard(slides, courses), [slides, courses]);

  /** 교체한 그림. 같은 그림이 여러 코스에 있으면 처음 것 하나만 둔다 */
  const replacedSlides = useMemo(() => {
    const seen = new Set<string>();
    return slides.filter((s) => {
      if (!s.replaced || seen.has(s.imageKey)) return false;
      seen.add(s.imageKey);
      return true;
    });
  }, [slides]);

  return (
    <View>
      <SummaryCard board={board} replacedCount={Object.keys(live.map).length} />
      <Legend />

      <SectionTitle>교체한 그림 {replacedSlides.length}장</SectionTitle>
      <View className="rounded-3xl bg-surface p-5 shadow-neu-card">
        {replacedSlides.length === 0 ? (
          <Text className="text-[12px] text-slate-400">
            아직 교체한 그림이 없다
          </Text>
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View className="flex-row gap-3">
              {replacedSlides.map((s) => (
                <Thumb key={s.id} slide={s} size={84} onPress={onOpen} />
              ))}
            </View>
          </ScrollView>
        )}
        <Text className="mt-3 text-[11px] text-slate-400">
          {live.status === "loading"
            ? "그림 저장소에서 교체 기록 확인 중…"
            : live.status === "live"
              ? `${live.checkedAt} 그림 저장소에서 확인`
              : `${live.checkedAt} 기록 · 지금은 저장소를 확인하지 못함`}
        </Text>
      </View>

      <SectionTitle>일자별 제작</SectionTitle>
      <DailyCard replaced={live.map} />

      <SectionTitle>코스별 현황</SectionTitle>
      <View className="gap-4">
        {board.courses.map((c) => (
          <CourseCard key={c.key} course={c} onOpen={onOpen} />
        ))}
      </View>
    </View>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <Text className="mb-3 mt-8 text-[12px] font-bold tracking-widest text-slate-400">
      {children}
    </Text>
  );
}

/** 요약 칸 하나. 눌러 들어가는 곳이 아니라 파인 모양(inset)으로 둔다 */
function MiniStat({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <View className="min-w-[46%] flex-1 rounded-2xl bg-canvas px-4 py-3 shadow-neu-inset">
      <Text className="text-[11px] text-slate-400">{label}</Text>
      <Text className="mt-1 font-bold text-ink" style={{ fontSize: 17, color }}>
        {value}
      </Text>
    </View>
  );
}

/** 초록(처음 그림)과 주황(교체) 두 겹 진행 막대 */
function StackBar({
  total,
  made,
  replaced,
  height = 8,
}: {
  total: number;
  made: number;
  replaced: number;
  height?: number;
}) {
  const pct = (n: number) => `${total > 0 ? (n / total) * 100 : 0}%` as const;
  return (
    <View
      className="flex-row overflow-hidden rounded-full bg-canvas shadow-neu-inset"
      style={{ height }}
    >
      <View style={{ width: pct(made - replaced), backgroundColor: MADE }} />
      <View style={{ width: pct(replaced), backgroundColor: REPLACED }} />
    </View>
  );
}

function SummaryCard({
  board,
  replacedCount,
}: {
  board: ReturnType<typeof buildBoard>;
  replacedCount: number;
}) {
  const fill = board.slots > 0 ? board.filledSlots / board.slots : 0;
  return (
    <View className="mt-5 rounded-3xl bg-surface p-6 shadow-neu-card">
      <Text className="text-[12px] font-bold text-slate-400">제작된 그림</Text>
      <View className="mt-1 flex-row items-baseline gap-1">
        <Text
          className="font-bold text-ink"
          style={{ fontSize: 40, lineHeight: 46 }}
        >
          {wordImageCount().toLocaleString()}
        </Text>
        <Text className="text-[16px] font-semibold text-slate-500">장</Text>
      </View>

      <View className="mt-4">
        <StackBar
          total={board.slots}
          made={board.filledSlots}
          replaced={board.replacedSlots}
          height={10}
        />
      </View>

      <View className="mt-5 flex-row flex-wrap gap-3">
        <MiniStat
          label="교체한 그림"
          value={`${replacedCount.toLocaleString()}장`}
          color={REPLACED}
        />
        <MiniStat
          label="남은 그림"
          value={`${board.toDraw.toLocaleString()}장`}
        />
        <MiniStat label="전체 단어 자리" value={board.slots.toLocaleString()} />
        <MiniStat label="채움" value={`${(fill * 100).toFixed(1)}%`} />
      </View>
    </View>
  );
}

/** 색 설명 */
function Legend() {
  const item = (color: string, label: string, hollow?: boolean) => (
    <View className="flex-row items-center gap-1.5">
      <View
        style={{
          width: 12,
          height: 12,
          borderRadius: 4,
          backgroundColor: hollow ? "transparent" : color,
          borderWidth: hollow ? 1.5 : 0,
          borderColor: color,
        }}
      />
      <Text className="text-[11px] text-slate-500">{label}</Text>
    </View>
  );
  return (
    <View className="mt-4 flex-row flex-wrap gap-x-4 gap-y-2 px-1">
      {item(MADE, "다 그린 유닛")}
      {item(REPLACED, "교체한 그림이 든 유닛")}
      {item(EMPTY, "덜 그린 유닛", true)}
    </View>
  );
}

/** 작은 그림 하나. 교체한 그림은 주황 테두리를 두른다 */
function Thumb({
  slide,
  size,
  onPress,
}: {
  slide: Slide;
  size: number;
  onPress: (slide: Slide) => void;
}) {
  const source = wordImageSource(
    slide.word,
    slide.replaced
      ? { [slide.imageKey]: slide.replaced, [slide.word.word]: slide.replaced }
      : {},
  );
  const border = slide.replaced ? REPLACED : slide.has ? "transparent" : EMPTY;
  return (
    <Pressable
      onPress={() => onPress(slide)}
      accessibilityRole="button"
      accessibilityLabel={`${slide.word.word} 크게 보기`}
      className="active:opacity-60"
      style={{ width: size }}
    >
      <View
        style={{
          width: size,
          height: size,
          borderRadius: 12,
          overflow: "hidden",
          borderWidth: 2,
          borderColor: border,
          backgroundColor: "#f5f6f8",
        }}
      >
        {source ? (
          <Image
            source={source}
            contentFit="cover"
            cachePolicy="disk"
            style={{ width: "100%", height: "100%" }}
          />
        ) : (
          <View className="flex-1 items-center justify-center">
            <PictureIcon size={20} color={EMPTY} />
          </View>
        )}
        {slide.replaced && (
          <View
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: REPLACED,
              paddingVertical: 1,
            }}
          >
            <Text
              style={{
                color: "#ffffff",
                fontSize: 9,
                fontWeight: "700",
                textAlign: "center",
              }}
            >
              교체 {slide.replaced.date.slice(5).replace("-", "/")}
            </Text>
          </View>
        )}
      </View>
      <Text
        numberOfLines={1}
        className="mt-1 text-center text-slate-600"
        style={{ fontSize: 10 }}
      >
        {slide.word.word}
      </Text>
    </Pressable>
  );
}

function CourseCard({
  course,
  onOpen,
}: {
  course: BoardCourse;
  onOpen: (slide: Slide) => void;
}) {
  /** 눌러 둔 유닛. 그 유닛 그림을 작게 펼쳐 보여 준다 */
  const [openUnit, setOpenUnit] = useState<number | null>(null);
  const open = course.units.find((u) => u.no === openUnit);
  const missing = course.total - course.made;

  return (
    <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
      <View className="flex-row items-baseline gap-2">
        <Text className="text-[17px] font-bold text-ink">{course.label}</Text>
        <Text className="text-[12px] text-slate-400">{course.fullLabel}</Text>
      </View>

      <Text className="mt-2 text-[12px] text-slate-500">
        제작{" "}
        <Text className="font-bold text-slate-700">
          {course.made.toLocaleString()}/{course.total.toLocaleString()}
        </Text>
        {" · "}교체{" "}
        <Text style={{ color: REPLACED, fontWeight: "700" }}>
          {course.replaced}
        </Text>
        {" · "}남은 <Text className="font-bold text-slate-700">{missing}</Text>
        {" · "}완성 유닛{" "}
        <Text className="font-bold text-slate-700">
          {course.doneUnits}/{course.units.length}
        </Text>
      </Text>

      <View className="mt-3">
        <StackBar
          total={course.total}
          made={course.made}
          replaced={course.replaced}
        />
      </View>

      {/* 유닛 칸. 다 그린 유닛은 초록, 교체한 그림이 든 유닛은 주황으로 채우고
          덜 그린 유닛은 아래쪽에 채운 만큼 초록 띠를 둔다 */}
      <View className="mt-4 flex-row flex-wrap" style={{ gap: 6 }}>
        {course.units.map((u) => {
          const done = u.made === u.slides.length;
          const selected = u.no === openUnit;
          const fillColor = u.replaced > 0 ? REPLACED : done ? MADE : null;
          const unitFill = u.slides.length ? u.made / u.slides.length : 0;

          return (
            <Pressable
              key={u.no}
              onPress={() => setOpenUnit(selected ? null : u.no)}
              accessibilityRole="button"
              accessibilityState={{ selected }}
              accessibilityLabel={`유닛 ${u.no} — 제작 ${u.made}/${u.slides.length}${
                u.replaced ? `, 교체 ${u.replaced}` : ""
              }`}
              style={{
                width: 32,
                height: 32,
                borderRadius: 10,
                alignItems: "center",
                justifyContent: "center",
                overflow: "hidden",
                backgroundColor: fillColor ?? "#ffffff",
                borderWidth: selected ? 2 : fillColor ? 0 : 1,
                borderColor: selected ? "#334155" : EMPTY,
              }}
            >
              <Text
                style={{
                  fontSize: 11,
                  fontWeight: "700",
                  color: fillColor ? "#ffffff" : "#94a3b8",
                }}
              >
                {u.no}
              </Text>
              {!fillColor && unitFill > 0 && (
                <View
                  style={{
                    position: "absolute",
                    left: 0,
                    bottom: 0,
                    height: 3,
                    width: `${Math.round(unitFill * 100)}%`,
                    backgroundColor: MADE,
                  }}
                />
              )}
            </Pressable>
          );
        })}
      </View>

      {/* 누른 유닛의 그림 20장 */}
      {open && (
        <View className="mt-4 rounded-2xl bg-canvas p-3 shadow-neu-inset">
          <Text className="mb-2 px-1 text-[12px] font-bold text-slate-500">
            U{open.no} · 제작 {open.made}/{open.slides.length}
            {open.replaced ? ` · 교체 ${open.replaced}` : ""}
          </Text>
          <View className="flex-row flex-wrap" style={{ gap: 8 }}>
            {open.slides.map((s) => (
              <Thumb key={s.id} slide={s} size={72} onPress={onOpen} />
            ))}
          </View>
        </View>
      )}
    </View>
  );
}

const WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"];

/**
 * 날짜별로 그림을 몇 장 만들고 교체했는지.
 *
 * 앱은 번들 안에서 돌아가 git 기록을 볼 수 없으므로 미리 세어 둔 값을 읽는다.
 * 만든 수는 scripts/image_daily_counts.py, 교체 수는 scripts/image_replacements.py
 * 가 센다.
 */
function DailyCard({ replaced }: { replaced: LiveReplaced["map"] }) {
  const replacedByDay = new Map<string, number>();
  for (const r of Object.values(replaced)) {
    replacedByDay.set(r.date, (replacedByDay.get(r.date) ?? 0) + 1);
  }
  const byDay = new Map<string, number>(
    dailyCounts.days.map((d) => [d.date, d.count]),
  );
  const dates = [...new Set([...byDay.keys(), ...replacedByDay.keys()])].sort();
  // 최근 것이 위로 오게 뒤집는다
  const recent = dates.slice(-14).reverse();
  const most = Math.max(
    1,
    ...recent.map((d) => (byDay.get(d) ?? 0) + (replacedByDay.get(d) ?? 0)),
  );
  const days = dailyCounts.days;
  const average = days.length
    ? Math.round(days.reduce((sum, d) => sum + d.count, 0) / days.length)
    : 0;

  return (
    <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
      <View className="flex-row items-end justify-between">
        <View>
          <Text className="text-[12px] font-bold text-slate-400">
            하루 평균
          </Text>
          <View className="mt-1 flex-row items-baseline gap-1">
            <Text
              className="font-bold text-ink"
              style={{ fontSize: 26, lineHeight: 32 }}
            >
              {average.toLocaleString()}
            </Text>
            <Text className="text-[13px] font-semibold text-slate-500">장</Text>
          </View>
        </View>
        <Text className="text-[11px] text-slate-400">
          {days.length}일 · 모두 {dailyCounts.total.toLocaleString()}장
        </Text>
      </View>

      <View className="mt-4 gap-2">
        {recent.map((date) => {
          const [, month, day] = date.split("-");
          const weekday = WEEKDAYS[new Date(`${date}T00:00:00`).getDay()];
          const made = byDay.get(date) ?? 0;
          const replaced = replacedByDay.get(date) ?? 0;

          return (
            <View key={date} className="flex-row items-center gap-3">
              <Text className="w-[54px] text-[11px] text-slate-500">
                {month}/{day} ({weekday})
              </Text>
              {/* 가장 많이 그린 날을 꽉 찬 길이로 두고 견준다 */}
              <View
                className="flex-1 flex-row overflow-hidden rounded-full bg-canvas shadow-neu-inset"
                style={{ height: 10 }}
              >
                <View
                  style={{
                    width: `${(made / most) * 100}%`,
                    backgroundColor: MADE,
                  }}
                />
                <View
                  style={{
                    width: `${Math.max(replaced ? 2 : 0, (replaced / most) * 100)}%`,
                    backgroundColor: REPLACED,
                  }}
                />
              </View>
              <Text className="w-[52px] text-right text-[12px] font-bold text-slate-600">
                {made}
                {replaced ? (
                  <Text style={{ color: REPLACED }}> +{replaced}</Text>
                ) : null}
              </Text>
            </View>
          );
        })}
      </View>

      <Text className="mt-4 text-[11px] text-slate-400">
        초록 = 새로 그림 · 주황 = 교체 · {dailyCounts.generatedAt} 기준
      </Text>
    </View>
  );
}
