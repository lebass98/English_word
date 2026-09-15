import { useMemo, useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { BackButton } from "../src/components/BackButton";
import { BottomNav } from "../src/components/BottomNav";
import { Screen, ScreenHeader } from "../src/components/Screen";
import {
  imageBoard,
  registeredImageCount,
  type BoardCourse,
  type QuickWin,
} from "../src/lib/imageDebug";
import { useAppStore } from "../src/stores/useAppStore";

/**
 * 단어 연상 그림 현황판 (임시).
 *
 * 아직 그리지 않은 그림을 코스와 유닛 단위로 본다.
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

  const today = new Date();
  const stamp = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  return (
    <Screen>
      <ScreenHeader>
        <BackButton fallbackHref="/" />
        <View className="flex-1">
          <Text className="text-xl font-bold text-ink">
            단어 연상 그림 현황판
          </Text>
          <Text className="mt-1 text-[12px] text-slate-500">
            {board.courses.length}개 코스 · {stamp} 기준
          </Text>
        </View>
      </ScreenHeader>

      {/* 하단 독바에 가리지 않게 넉넉히 띄운다 */}
      <ScrollView className="flex-1" contentContainerClassName="px-6 pb-32 pt-6">
        <SummaryCard board={board} />

        {board.quickWins.length > 0 && (
          <>
            <SectionTitle>바로 끝낼 수 있는 유닛</SectionTitle>
            <View className="gap-3">
              {board.quickWins.map((q) => (
                <QuickWinCard key={`${q.courseKey}#${q.unitNo}`} win={q} />
              ))}
            </View>
          </>
        )}

        <SectionTitle>코스별 현황</SectionTitle>
        <View className="gap-4">
          {board.courses.map((course) => (
            <CourseCard key={course.key} course={course} />
          ))}
        </View>
      </ScrollView>

      <BottomNav />
    </Screen>
  );
}

function SectionTitle({ children }: { children: string }) {
  return (
    <Text className="mb-3 mt-8 text-[12px] font-bold tracking-widest text-slate-400">
      {children}
    </Text>
  );
}

/** 요약 칸 하나. 눌러 들어가는 곳이 아니라 파인 모양(inset)으로 둔다 */
function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <View className="min-w-[46%] flex-1 rounded-2xl bg-canvas px-4 py-3 shadow-neu-inset">
      <Text className="text-[11px] text-slate-400">{label}</Text>
      <Text className="mt-1 text-[17px] font-bold text-ink">{value}</Text>
    </View>
  );
}

function SummaryCard({ board }: { board: ReturnType<typeof imageBoard> }) {
  return (
    <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
      <Text className="text-[12px] font-bold text-slate-400">
        앞으로 그려야 할 그림
      </Text>
      <View className="mt-1 flex-row items-baseline gap-1">
        <Text className="text-[40px] font-bold leading-[46px] text-ink">
          {board.toDraw.toLocaleString()}
        </Text>
        <Text className="text-[16px] font-semibold text-slate-500">장</Text>
      </View>
      {/* 빈 자리보다 그릴 그림이 적은 까닭을 적어 둔다 */}
      <Text className="mt-2 text-[12px] leading-[18px] text-slate-500">
        빈 자리는 {board.emptySlots.toLocaleString()}칸이지만, 같은 뜻을 가리키는
        낱말은 그림 한 장을 함께 쓴다. 실제로 새로 그릴 그림은{" "}
        {board.toDraw.toLocaleString()}장이다.
      </Text>

      <View className="mt-5 flex-row flex-wrap gap-3">
        <MiniStat label="이미 그린 그림" value={board.drawn.toLocaleString()} />
        <MiniStat label="전체 단어 자리" value={board.slots.toLocaleString()} />
        <MiniStat label="빈 자리" value={board.emptySlots.toLocaleString()} />
        <MiniStat label="채움" value={`${(board.fill * 100).toFixed(1)}%`} />
      </View>
    </View>
  );
}

function QuickWinCard({ win }: { win: QuickWin }) {
  return (
    <View className="rounded-2xl bg-surface p-4 shadow-neu-card">
      <View className="flex-row items-center gap-2">
        <Text className="flex-1 text-[14px] font-bold text-ink">
          {win.title}{" "}
          <Text className="font-bold text-slate-400">U{win.unitNo}</Text>
        </Text>
        <Text className="text-[13px] font-bold text-amber-600">
          {win.missing}장
        </Text>
      </View>
      <View className="mt-2.5 flex-row flex-wrap gap-1.5">
        {win.words.map((w) => (
          <View
            key={w}
            className="rounded-full bg-canvas px-2.5 py-1 shadow-neu-inset"
          >
            <Text className="text-[12px] text-slate-500">{w}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

/** 진행 정도를 한 낱말로 (완성 / 진행 중 / 초기) */
function stageOf(fill: number, missing: number) {
  if (missing === 0) return { label: "완성", tone: "text-mint-dark bg-[#dcf2ea]" };
  if (fill >= 0.25) return { label: "진행 중", tone: "text-amber-600 bg-[#fdf0dc]" };
  return { label: "초기", tone: "text-rose-500 bg-[#fbe3e6]" };
}

function CourseCard({ course }: { course: BoardCourse }) {
  /** 눌러 둔 유닛. 그 유닛에 남은 낱말을 펼쳐 보여준다 */
  const [openUnit, setOpenUnit] = useState<number | null>(null);

  const fill = course.total > 0 ? course.made / course.total : 0;
  const stage = stageOf(fill, course.missing);
  const open = course.units.find((u) => u.no === openUnit);

  return (
    <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
      <View className="flex-row items-center gap-2">
        <View className="rounded-full bg-canvas px-2.5 py-1 shadow-neu-inset">
          <Text className="text-[11px] text-slate-500">{course.langName}</Text>
        </View>
        <Text className="text-[17px] font-bold text-ink">{course.short}</Text>
        <View className={`rounded-full px-2.5 py-0.5 ${stage.tone}`}>
          <Text className={`text-[11px] font-bold ${stage.tone.split(" ")[0]}`}>
            {stage.label}
          </Text>
        </View>
      </View>

      <Text className="mt-2 text-[12px] text-slate-500">
        남은{" "}
        <Text className="font-bold text-slate-700">
          {course.missing.toLocaleString()}
        </Text>
        장 · 완성 유닛{" "}
        <Text className="font-bold text-slate-700">
          {course.doneUnits}/{course.units.length}
        </Text>
      </Text>

      <View className="mt-3 h-2 overflow-hidden rounded-full bg-canvas shadow-neu-inset">
        <View
          className="h-full rounded-full bg-mint"
          style={{ width: `${Math.round(fill * 100)}%` }}
        />
      </View>
      <View className="mt-1.5 flex-row justify-between">
        <Text className="text-[11px] text-slate-400">
          {course.made.toLocaleString()} / {course.total.toLocaleString()}
        </Text>
        <Text className="text-[11px] text-slate-400">
          {(fill * 100).toFixed(1)}%
        </Text>
      </View>

      {/* 유닛 칸. 다 그린 유닛은 초록으로 채우고, 그리는 중인 유닛은
          아래쪽에 채운 만큼 초록 띠를 둔다 */}
      <View className="mt-4 flex-row flex-wrap gap-1.5">
        {course.units.map((u) => {
          const done = u.missing === 0;
          const selected = u.no === openUnit;
          const unitFill = u.total > 0 ? u.made / u.total : 0;

          return (
            <Pressable
              key={u.no}
              onPress={() => setOpenUnit(selected ? null : u.no)}
              accessibilityRole="button"
              accessibilityState={{ selected }}
              accessibilityLabel={`유닛 ${u.no} — ${
                done ? "그림 완료" : `${u.missing}장 남음`
              }`}
              className={`h-8 w-8 items-center justify-center overflow-hidden rounded-xl ${
                done
                  ? "bg-mint"
                  : selected
                    ? "bg-canvas shadow-neu-inset"
                    : "bg-surface shadow-neu-sm active:shadow-neu-pressed"
              }`}
            >
              <Text
                className={`text-[11px] font-bold ${
                  done
                    ? "text-white"
                    : selected
                      ? "text-mint-dark"
                      : "text-slate-400"
                }`}
              >
                {u.no}
              </Text>
              {!done && unitFill > 0 && (
                <View className="absolute inset-x-0 bottom-0 h-[3px] bg-canvas">
                  <View
                    className="h-full bg-mint"
                    style={{ width: `${Math.round(unitFill * 100)}%` }}
                  />
                </View>
              )}
            </Pressable>
          );
        })}
      </View>

      {/* 누른 유닛에 남은 낱말 */}
      {open && (
        <View className="mt-4 rounded-2xl bg-canvas p-4 shadow-neu-inset">
          <Text className="text-[12px] font-bold text-slate-500">
            U{open.no} · 남은 {open.missing}장
          </Text>
          {open.missing === 0 ? (
            <Text className="mt-2 text-[12px] text-mint-dark">
              이 유닛은 그림을 다 그렸다
            </Text>
          ) : (
            <View className="mt-2.5 flex-row flex-wrap gap-1.5">
              {open.words.map((w) => (
                <View
                  key={w}
                  className="rounded-full bg-surface px-2.5 py-1 shadow-neu-sm"
                >
                  <Text className="text-[12px] text-slate-600">{w}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      )}
    </View>
  );
}
