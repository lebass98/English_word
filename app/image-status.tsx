import { useMemo, useState } from "react";
import { ScrollView, Pressable, Text, View } from "react-native";
import { BackButton } from "../src/components/BackButton";
import { ChevronDownIcon, ChevronRightIcon } from "../src/components/icons";
import { Screen, ScreenHeader } from "../src/components/Screen";
import {
  imageBoard,
  registeredImageCount,
  type BoardCourse,
} from "../src/lib/imageDebug";
import { useAppStore } from "../src/stores/useAppStore";

/**
 * 그림 현황판 (임시).
 *
 * 아직 연상 그림이 없는 낱말을 코스 → 유닛 → 낱말 순으로 좁혀 가며 본다.
 * 낱말은 한 줄에 하나씩 적어 어떤 낱말이 남았는지 눈으로 훑기 쉽게 한다.
 * 그림을 전부 채우면 이 화면과 src/lib/imageDebug.ts 를 함께 지운다.
 */
export default function ImageStatusScreen() {
  const uiLang = useAppStore((s) => s.uiLang);
  // 그림이 새로 등록되면 숫자가 곧바로 줄어든다
  const imageCount = registeredImageCount();
  const board = useMemo(
    () => imageBoard(uiLang),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [uiLang, imageCount],
  );

  /** 펼쳐 둔 코스 (en:high-1) */
  const [openCourses, setOpenCourses] = useState<Record<string, boolean>>({});
  /** 펼쳐 둔 유닛 (en:high-1#8) */
  const [openUnits, setOpenUnits] = useState<Record<string, boolean>>({});

  const percent = board.total > 0 ? board.made / board.total : 0;

  return (
    <Screen>
      <ScreenHeader>
        <BackButton fallbackHref="/" />
        <View className="flex-1">
          <Text className="text-2xl font-bold text-ink">그림 현황판</Text>
          <Text className="mt-1 text-[13px] text-slate-500">
            {board.courses.length}개 코스 · 아직 그리지 않은 그림
          </Text>
        </View>
      </ScreenHeader>

      <ScrollView className="flex-1" contentContainerClassName="px-6 pb-16 pt-6">
        {/* 전체 요약 */}
        <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
          <View className="flex-row items-end justify-between">
            <View>
              <Text className="text-[12px] font-bold text-slate-400">
                남은 그림
              </Text>
              <View className="mt-1 flex-row items-baseline gap-1">
                <Text className="text-[34px] font-bold leading-[40px] text-ink">
                  {board.missing.toLocaleString()}
                </Text>
                <Text className="text-[15px] font-semibold text-slate-500">
                  장
                </Text>
              </View>
            </View>
            <Text className="text-[15px] font-bold text-mint-dark">
              {Math.floor(percent * 100)}%
            </Text>
          </View>

          <View className="mt-4 h-2.5 overflow-hidden rounded-full bg-canvas shadow-neu-inset">
            <View
              className="h-full rounded-full bg-mint"
              style={{ width: `${Math.round(percent * 100)}%` }}
            />
          </View>
          <Text className="mt-2 text-[12px] font-bold text-slate-500">
            {board.made.toLocaleString()} / {board.total.toLocaleString()}장
            완료
          </Text>
        </View>

        {/* 코스별 */}
        <View className="mt-6 gap-4">
          {board.courses.map((course) => (
            <CourseCard
              key={course.key}
              course={course}
              open={Boolean(openCourses[course.key])}
              onToggle={() =>
                setOpenCourses((prev) => ({
                  ...prev,
                  [course.key]: !prev[course.key],
                }))
              }
              openUnits={openUnits}
              onToggleUnit={(unitKey) =>
                setOpenUnits((prev) => ({ ...prev, [unitKey]: !prev[unitKey] }))
              }
            />
          ))}
        </View>
      </ScrollView>
    </Screen>
  );
}

interface CourseCardProps {
  course: BoardCourse;
  open: boolean;
  onToggle: () => void;
  openUnits: Record<string, boolean>;
  onToggleUnit: (unitKey: string) => void;
}

function CourseCard({
  course,
  open,
  onToggle,
  openUnits,
  onToggleUnit,
}: CourseCardProps) {
  const done = course.missing === 0;
  const percent = course.total > 0 ? course.made / course.total : 0;
  // 다 그린 유닛은 목록에서 빼서 남은 것만 눈에 들어오게 한다
  const remaining = course.units.filter((u) => u.missing > 0);

  return (
    <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
      <Pressable
        onPress={onToggle}
        accessibilityRole="button"
        accessibilityState={{ expanded: open }}
        accessibilityLabel={`${course.label} — ${
          done ? "그림 완료" : `${course.missing}장 남음`
        }`}
        className="active:opacity-70"
      >
        <View className="flex-row items-center gap-3">
          <View className="flex-1">
            <Text className="text-[11px] font-bold text-slate-400">
              {course.langName}
            </Text>
            <Text className="mt-1 text-[17px] font-bold text-ink">
              {course.label}
            </Text>
          </View>
          <View
            className={`rounded-full px-3 py-1 ${
              done ? "bg-[#dcf2ea]" : "bg-canvas shadow-neu-inset"
            }`}
          >
            <Text
              className={`text-[12px] font-bold ${
                done ? "text-mint-dark" : "text-amber-600"
              }`}
            >
              {done ? "완료" : `${course.missing.toLocaleString()}장`}
            </Text>
          </View>
          {!done &&
            (open ? (
              <ChevronDownIcon size={16} color="#94a3b8" strokeWidth={2.5} />
            ) : (
              <ChevronRightIcon size={16} color="#94a3b8" strokeWidth={2.5} />
            ))}
        </View>

        <View className="mt-4 h-2 overflow-hidden rounded-full bg-canvas shadow-neu-inset">
          <View
            className="h-full rounded-full bg-mint"
            style={{ width: `${Math.round(percent * 100)}%` }}
          />
        </View>
        <Text className="mt-2 text-[12px] font-bold text-slate-500">
          {course.made.toLocaleString()} / {course.total.toLocaleString()}
        </Text>
      </Pressable>

      {/* 유닛별. 코스를 펼쳤을 때만 그린다 (단어 수천 개를 한 번에 그리지 않게) */}
      {open && !done && (
        <View className="mt-4 gap-2">
          {remaining.map((unit) => {
            const unitKey = `${course.key}#${unit.no}`;
            const unitOpen = Boolean(openUnits[unitKey]);

            return (
              <View key={unitKey}>
                <Pressable
                  onPress={() => onToggleUnit(unitKey)}
                  accessibilityRole="button"
                  accessibilityState={{ expanded: unitOpen }}
                  accessibilityLabel={`유닛 ${unit.no} — ${unit.missing}장 남음`}
                  className={`h-11 flex-row items-center gap-2 rounded-2xl px-4 ${
                    unitOpen
                      ? "bg-canvas shadow-neu-inset"
                      : "bg-surface shadow-neu-sm active:shadow-neu-pressed"
                  }`}
                >
                  <Text className="flex-1 text-[13px] font-bold text-slate-600">
                    UNIT {unit.no}
                  </Text>
                  <Text className="text-[13px] font-bold text-amber-600">
                    {unit.missing}
                  </Text>
                  <Text className="text-[12px] text-slate-400">
                    / {unit.total}
                  </Text>
                  {unitOpen ? (
                    <ChevronDownIcon
                      size={14}
                      color="#94a3b8"
                      strokeWidth={2.5}
                    />
                  ) : (
                    <ChevronRightIcon
                      size={14}
                      color="#94a3b8"
                      strokeWidth={2.5}
                    />
                  )}
                </Pressable>

                {/* 남은 낱말. 유닛당 스무 개 안쪽이라 줄바꿈하며 채운다 */}
                {unitOpen && (
                  <View className="mt-2 flex-row flex-wrap gap-1.5 px-1">
                    {unit.words.map((w) => (
                      <View
                        key={w}
                        className="rounded-full bg-surface px-3 py-1 shadow-neu-sm"
                      >
                        <Text className="text-[13px] text-slate-700">{w}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            );
          })}
        </View>
      )}
    </View>
  );
}
