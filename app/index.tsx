import { useRouter } from "expo-router";
import { useMemo } from "react";
import { Image, Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { BottomNav } from "../src/components/BottomNav";
import { ContinueCard } from "../src/components/ContinueCard";
import { GradeCard } from "../src/components/GradeCard";
import { PillButton } from "../src/components/PillButton";
import { WORD_IMAGES } from "../src/constants/wordImages";
import {
  availableGrades,
  knownCountByGrade,
  streakDays,
  todayStats,
  unsureWords,
  upcomingGrades,
} from "../src/stores/selectors";
import { useAppStore } from "../src/stores/useAppStore";

// 학년 목록은 상수에서 나오므로 렌더마다 다시 만들 필요가 없다
const AVAILABLE_GRADES = availableGrades();
const UPCOMING_LABEL = upcomingGrades()
  .map((g) => g.short)
  .join(" · ");

/**
 * 오늘의 기록 칸. 한 줄에 셋이 들어가야 해서
 * StatCard(최소 45% 폭) 대신 홈 전용으로 좁게 만든다.
 */
function TodayStat({
  emoji,
  value,
  unit,
  label,
}: {
  emoji: string;
  value: number;
  unit?: string;
  label: string;
}) {
  return (
    <View className="flex-1 items-center rounded-3xl bg-surface px-2 py-5 shadow-neu-card">
      <Text className="text-[18px]">{emoji}</Text>
      <View className="mt-2 flex-row items-baseline gap-0.5">
        <Text className="text-[22px] font-bold text-ink">{value}</Text>
        {unit && (
          <Text className="text-[12px] font-semibold text-slate-500">
            {unit}
          </Text>
        )}
      </View>
      <Text numberOfLines={1} className="mt-1 text-[12px] text-slate-500">
        {label}
      </Text>
    </View>
  );
}

export default function HomeScreen() {
  const router = useRouter();
  const entries = useAppStore((s) => s.entries);
  const dailyLog = useAppStore((s) => s.dailyLog);
  const setActiveGradeId = useAppStore((s) => s.setActiveGradeId);

  // 아래 셋은 모두 기록 전체(단어 수천 개)를 훑으므로 원본이 바뀔 때만 다시 센다
  const streak = useMemo(() => streakDays(dailyLog), [dailyLog]);
  const today = useMemo(() => todayStats(dailyLog), [dailyLog]);
  const unsure = useMemo(() => unsureWords(entries, 10), [entries]);
  const knownByGrade = useMemo(
    () =>
      AVAILABLE_GRADES.map((grade) => ({
        grade,
        known: knownCountByGrade(entries, grade.id),
      })),
    [entries],
  );

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <ScrollView
        className="flex-1"
        contentContainerClassName="w-full px-6 pb-32"
      >
        {/* 헤더: 브랜드 + 연속 학습 (0일은 아예 감춘다) */}
        <View className="flex-row items-center justify-between pb-2 pt-8">
          <Text className="text-2xl font-bold tracking-tight text-ink">
            Word<Text className="text-mint">Pic</Text>
          </Text>
          {streak > 0 && (
            <View className="flex-row items-center gap-1 rounded-full bg-surface px-4 py-2 shadow-neu-sm">
              <Text className="text-[13px]">🔥</Text>
              <Text className="text-[13px] font-bold text-mint-dark">
                {streak}일
              </Text>
            </View>
          )}
        </View>

        {/* 이어하기 히어로 */}
        <View className="mt-6">
          <ContinueCard />
        </View>

        {/* 오늘의 복습: 헷갈린다고 표시한 단어가 있을 때만 */}
        {unsure.length > 0 && (
          <View className="mt-8">
            <View className="flex-row items-center justify-between gap-3">
              <Text className="flex-1 text-[17px] font-bold text-ink">
                헷갈리는 단어 {unsure.length}개
              </Text>
              <PillButton
                label="복습 시작"
                size="sm"
                variant="primary"
                onPress={() => router.push(`/study/${unsure[0].id}`)}
              />
            </View>

            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              className="mt-4"
              contentContainerClassName="gap-3 pr-6"
            >
              {unsure.map((w) => {
                const source = WORD_IMAGES[w.id] || WORD_IMAGES[w.word];
                return (
                  <Pressable
                    key={w.id}
                    onPress={() => router.push(`/study/${w.id}`)}
                    accessibilityRole="button"
                    accessibilityLabel={`${w.word} 복습하기`}
                    className="w-[92px] active:opacity-70"
                  >
                    <View className="h-[92px] w-[92px] items-center justify-center overflow-hidden rounded-2xl bg-canvas shadow-neu-inset">
                      {source ? (
                        <Image
                          source={source}
                          resizeMode="cover"
                          style={{ width: "100%", height: "100%" }}
                        />
                      ) : (
                        <Text className="text-[26px]">🖼️</Text>
                      )}
                    </View>
                    <Text
                      numberOfLines={1}
                      className="mt-2 text-[13px] font-bold text-ink"
                    >
                      {w.word}
                    </Text>
                  </Pressable>
                );
              })}
            </ScrollView>
          </View>
        )}

        {/* 오늘의 기록 */}
        <Text className="mt-8 text-[17px] font-bold text-ink">오늘의 기록</Text>
        {today.seen === 0 && today.known === 0 ? (
          <View className="mt-4 rounded-3xl bg-surface px-6 py-5 shadow-neu-card">
            <Text className="text-[13px] text-slate-500">
              오늘 첫 단어를 시작해 보세요
            </Text>
          </View>
        ) : (
          <View className="mt-4 flex-row gap-4">
            <TodayStat emoji="👀" value={today.seen} label="오늘 본 단어" />
            <TodayStat emoji="✅" value={today.known} label="오늘 외운 단어" />
            <TodayStat emoji="🔥" value={streak} unit="일" label="연속 학습" />
          </View>
        )}

        {/* 내 코스 */}
        <Text className="mt-8 text-[17px] font-bold text-ink">내 코스</Text>
        <View className="mt-4 gap-6 md:flex-row md:flex-wrap">
          {knownByGrade.map(({ grade, known }) => (
            <View key={grade.id} className="md:w-[48%]">
              <GradeCard
                label={grade.label}
                learnedWords={known}
                totalWords={grade.totalWords}
                onPress={() => {
                  setActiveGradeId(grade.id);
                  router.push(`/grade/${grade.id}`);
                }}
              />
            </View>
          ))}
        </View>
        {UPCOMING_LABEL.length > 0 && (
          <Text className="mt-4 text-[12px] text-slate-400">
            {UPCOMING_LABEL} 코스 준비 중
          </Text>
        )}
      </ScrollView>

      <BottomNav />
    </SafeAreaView>
  );
}
