import { useRouter } from "expo-router";
import { useMemo } from "react";
import { Image, Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { BottomNav } from "../src/components/BottomNav";
import { ContinueCard } from "../src/components/ContinueCard";
import { GradeCard } from "../src/components/GradeCard";
import { LanguageFlag } from "../src/components/flags";
import { PillButton } from "../src/components/PillButton";
import { useGrades } from "../src/constants/grades";
import { STUDY_LANGS } from "../src/constants/languages";
import { useVocab } from "../src/constants/words";
import { WORD_IMAGES } from "../src/constants/wordImages";
import { useT } from "../src/i18n";
import {
  availableGrades,
  knownCountByGrade,
  streakDays,
  todayStats,
  unsureWords,
  upcomingGrades,
} from "../src/stores/selectors";
import { useAppStore } from "../src/stores/useAppStore";

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
  const studyLang = useAppStore((s) => s.studyLang);
  const setStudyLang = useAppStore((s) => s.setStudyLang);
  const t = useT();
  const vocab = useVocab();
  const grades = useGrades();

  // 단계 목록은 언어가 바뀔 때만 다시 만든다
  const availableList = useMemo(() => availableGrades(grades), [grades]);
  const upcomingLabel = useMemo(
    () =>
      upcomingGrades(grades)
        .map((g) => g.short)
        .join(" · "),
    [grades],
  );

  // 아래 셋은 모두 기록 전체(단어 수천 개)를 훑으므로 원본이 바뀔 때만 다시 센다
  const streak = useMemo(() => streakDays(dailyLog), [dailyLog]);
  const today = useMemo(() => todayStats(dailyLog), [dailyLog]);
  const unsure = useMemo(
    () => unsureWords(entries, vocab, 10),
    [entries, vocab],
  );
  const knownByGrade = useMemo(
    () =>
      availableList.map((grade) => ({
        grade,
        known: knownCountByGrade(entries, vocab, grade.id),
      })),
    [entries, vocab, availableList],
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

        {/* 학습 언어 고르기. 무엇을 배울지가 화면의 출발점이라 맨 위에 둔다 */}
        <View className="mt-5 flex-row gap-3">
          {STUDY_LANGS.map((id) => {
            const on = studyLang === id;
            return (
              <Pressable
                key={id}
                onPress={() => setStudyLang(id)}
                accessibilityRole="button"
                accessibilityState={{ selected: on }}
                accessibilityLabel={t(`studyLang.${id}` as never)}
                style={{ flex: 1 }}
                className={`flex-row items-center gap-2.5 rounded-2xl px-3 py-3 active:scale-[0.98] ${
                  on ? "bg-canvas shadow-neu-inset" : "bg-surface shadow-neu-sm"
                }`}
              >
                <LanguageFlag lang={id} size={26} />
                <Text
                  numberOfLines={1}
                  className={`text-[14px] font-bold ${
                    on ? "text-mint-dark" : "text-slate-500"
                  }`}
                >
                  {t(`studyLang.${id}` as never)}
                </Text>
              </Pressable>
            );
          })}
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
                label={t("home.reviewStart")}
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
                const source = WORD_IMAGES[w.conceptId] ?? WORD_IMAGES[w.word];
                return (
                  <Pressable
                    key={w.id}
                    onPress={() => router.push(`/study/${w.id}`)}
                    accessibilityRole="button"
                    accessibilityLabel={t("a11y.reviewWord", { word: w.word })}
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
        <Text className="mt-8 text-[17px] font-bold text-ink">
          {t("home.todayRecord")}
        </Text>
        {today.seen === 0 && today.known === 0 ? (
          <View className="mt-4 rounded-3xl bg-surface px-6 py-5 shadow-neu-card">
            <Text className="text-[13px] text-slate-500">
              {t("home.firstWordPrompt")}
            </Text>
          </View>
        ) : (
          <View className="mt-4 flex-row gap-4">
            <TodayStat
              emoji="👀"
              value={today.seen}
              label={t("home.seenToday")}
            />
            <TodayStat
              emoji="✅"
              value={today.known}
              label={t("home.knownToday")}
            />
            <TodayStat
              emoji="🔥"
              value={streak}
              unit={t("home.days")}
              label={t("home.streak")}
            />
          </View>
        )}

        {/* 내 코스 */}
        <Text className="mt-8 text-[17px] font-bold text-ink">
          {t("home.myCourse")}
        </Text>
        {/* 한 줄에 두 개씩. 폭을 47%로 잡아 좁은 화면에서도 두 칸이 확실히 들어간다 */}
        <View className="mt-4 flex-row flex-wrap gap-4">
          {knownByGrade.map(({ grade, known }) => (
            <View key={grade.id} className="w-[47%]">
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
        {upcomingLabel.length > 0 && (
          <Text className="mt-4 text-[12px] text-slate-400">
            {upcomingLabel} · {t("level.preparing")}
          </Text>
        )}
      </ScrollView>

      <BottomNav />
    </SafeAreaView>
  );
}
