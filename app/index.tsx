import { useRouter } from "expo-router";
import { type ReactNode, useMemo, useState } from "react";
import { ScrollView, Text, View } from "react-native";
import { Image } from "expo-image";
import { BottomNav } from "../src/components/BottomNav";
import { ContinueCard } from "../src/components/ContinueCard";
import { GaugeBar } from "../src/components/GaugeBar";
import { GradeCard } from "../src/components/GradeCard";
import { LanguageFlag } from "../src/components/flags";
import { PillButton } from "../src/components/PillButton";
import { Screen, ScreenHeader } from "../src/components/Screen";
import { SectionLabel } from "../src/components/SectionLabel";
import { SegmentButton } from "../src/components/SegmentButton";
import {
  DURATION,
  NeuStateLayer,
  PressableScale,
  Stagger,
} from "../src/components/motion";
import { TodayWordCard } from "../src/components/TodayWordCard";
import { ToggleCard } from "../src/components/ToggleCard";
import {
  AgainIcon,
  BookIcon,
  QuizIcon,
  ShuffleIcon,
} from "../src/components/icons";
import { useGrades } from "../src/constants/grades";
import { STUDY_LANGS } from "../src/constants/languages";
import { useVocab } from "../src/constants/words";
import { hasWordImage, wordImageSource } from "../src/constants/wordImages";
import { useT } from "../src/i18n";
import type { UiLangId } from "../src/i18n/strings";
import {
  DAILY_GOAL,
  availableGrades,
  knownCountByGrade,
  streakDays,
  todayStats,
  todayWord,
  unsureWords,
  upcomingGrades,
} from "../src/stores/selectors";
import { useAppStore } from "../src/stores/useAppStore";

/** 머리줄 요일 이름. 달 이름은 장식이라 영문 약자로 통일한다 */
const WEEKDAYS: Record<UiLangId, string[]> = {
  ko: ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"],
  ja: ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"],
};
const MONTHS = [
  "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
  "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
];

/** 발음 소리를 다시 켤 때 쓰는 크기. 음소거 전 크기는 따로 기억하지 않는다 */
const DEFAULT_VOLUME = 1;

/** 오늘 목표 게이지 아래의 작은 숫자 하나 */
function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <Text className="text-[12px] text-slate-500">
      {label} <Text className="font-extrabold text-ink">{value}</Text>
    </Text>
  );
}

/** 원형 빠른 실행 버튼. 누르면 작아지며 안으로 스르르 파인다 */
function QuickButton({
  icon,
  label,
  onPress,
}: {
  icon: ReactNode;
  label: string;
  onPress: () => void;
}) {
  const [pressed, setPressed] = useState(false);
  return (
    <PressableScale
      onPress={onPress}
      onPressIn={() => setPressed(true)}
      onPressOut={() => setPressed(false)}
      accessibilityRole="button"
      accessibilityLabel={label}
      scaleTo={0.92}
      className="items-center gap-2"
    >
      <View className="h-[60px] w-[60px] items-center justify-center">
        <NeuStateLayer
          active={pressed}
          radiusClass="rounded-full"
          duration={DURATION.fast}
        />
        {/* 웹에서는 absolute 인 모양 층이 그냥 놓인 svg 아이콘을 덮는다. View 로 감싸 위로 올린다 */}
        <View>{icon}</View>
      </View>
      <Text className="text-[11px] font-bold text-slate-500">{label}</Text>
    </PressableScale>
  );
}

export default function HomeScreen() {
  const router = useRouter();
  const entries = useAppStore((s) => s.entries);
  const dailyLog = useAppStore((s) => s.dailyLog);
  const activeGradeId = useAppStore((s) => s.activeGradeId);
  const setActiveGradeId = useAppStore((s) => s.setActiveGradeId);
  const studyLang = useAppStore((s) => s.studyLang);
  const setStudyLang = useAppStore((s) => s.setStudyLang);
  const uiLang = useAppStore((s) => s.uiLang);
  const speechVolume = useAppStore((s) => s.speechVolume);
  const setSpeechVolume = useAppStore((s) => s.setSpeechVolume);
  const autoAdvance = useAppStore((s) => s.autoAdvance);
  const setAutoAdvance = useAppStore((s) => s.setAutoAdvance);
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

  /** 빠른 실행·오늘의 단어가 기준으로 삼는 코스. 고른 코스가 없으면 첫 코스 */
  const baseGradeId =
    activeGradeId && vocab.byLevel[activeGradeId]
      ? activeGradeId
      : availableList[0]?.id;

  // 아래 셋은 모두 기록 전체(단어 수천 개)를 훑으므로 원본이 바뀔 때만 다시 센다
  const streak = useMemo(() => streakDays(dailyLog), [dailyLog]);
  const today = useMemo(() => todayStats(dailyLog), [dailyLog]);
  const unsure = useMemo(
    () => unsureWords(entries, vocab, 10),
    [entries, vocab],
  );
  // 그림이 있는 단어 중에서 고른다. 오늘의 단어 카드는 그림이 주인공이다
  const wordOfDay = useMemo(
    () =>
      todayWord(
        baseGradeId ? (vocab.byLevel[baseGradeId] ?? []) : [],
        hasWordImage,
      ),
    [vocab, baseGradeId],
  );
  const knownByGrade = useMemo(
    () =>
      availableList.map((grade) => ({
        grade,
        known: knownCountByGrade(entries, vocab, grade.id),
      })),
    [entries, vocab, availableList],
  );

  // 코스 카드는 한 줄에 두 개. 창 폭으로 카드 폭을 계산하면 웹에서 처음 그릴 때
  // 창 폭이 실제와 달라 카드가 좁아졌다. 두 개씩 줄로 묶어 반씩 나눠 갖게 한다
  const courseRows = useMemo(() => {
    const rows: (typeof knownByGrade)[] = [];
    for (let i = 0; i < knownByGrade.length; i += 2) {
      rows.push(knownByGrade.slice(i, i + 2));
    }
    return rows;
  }, [knownByGrade]);

  const now = new Date();
  const goalSeen = Math.min(today.seen, DAILY_GOAL);
  const goalPercent = Math.round((goalSeen / DAILY_GOAL) * 100);
  const goalLeft = DAILY_GOAL - goalSeen;

  const openWord = (gradeId: string, wordId: string) => {
    setActiveGradeId(gradeId);
    router.push(`/study/${wordId}`);
  };
  const openRandom = () => {
    const words = baseGradeId ? vocab.byLevel[baseGradeId] : undefined;
    if (!baseGradeId || !words?.length) return;
    openWord(baseGradeId, words[Math.floor(Math.random() * words.length)].id);
  };
  const openQuiz = () => {
    if (!baseGradeId) return;
    setActiveGradeId(baseGradeId);
    router.push(`/quiz/${baseGradeId}`);
  };

  return (
    <Screen>
      <ScrollView className="flex-1" contentContainerClassName="pb-32">
        {/* 헤더: 브랜드 · 오늘 날짜 · 연속 학습 (0일은 아예 감춘다) */}
        <ScreenHeader>
          <View className="flex-1">
            <Text className="text-[20px] font-extrabold tracking-tight text-ink">
              Word<Text className="text-mint">Pic</Text>
            </Text>
          </View>
          <View className="items-center">
            <Text className="text-[17px] font-bold text-ink">
              {WEEKDAYS[uiLang][now.getDay()]}
            </Text>
            <Text className="text-[11px] font-extrabold tracking-[2px] text-slate-500">
              {MONTHS[now.getMonth()]} {now.getDate()}
            </Text>
          </View>
          <View className="flex-1 items-end">
            {streak > 0 && (
              <View className="rounded-full bg-surface px-3 py-2 shadow-neu-sm">
                <Text className="text-[13px] font-extrabold text-mint-dark">
                  {streak}
                  {t("home.days")}
                </Text>
              </View>
            )}
          </View>
        </ScreenHeader>

        <View className="px-6 pt-6">
          {/* 칸들이 위에서부터 차례로 떠오른다 */}
          <Stagger>
          {/* 학습 언어 고르기. 무엇을 배울지가 화면의 출발점이라 맨 위에 둔다 */}
          <View className="flex-row gap-3">
            {STUDY_LANGS.map((id) => (
              <SegmentButton
                key={id}
                selected={studyLang === id}
                onPress={() => setStudyLang(id)}
                label={t(`studyLang.${id}` as never)}
                left={<LanguageFlag lang={id} size={26} />}
              />
            ))}
          </View>

          {/* 오늘 목표: 오늘 본 단어로 하루치(20단어)를 채운다 */}
          <View className="mt-8">
            <SectionLabel
              label="TODAY GOAL"
              sub={
                goalLeft > 0
                  ? t("home.goalRemaining", { count: goalLeft })
                  : t("home.goalDone")
              }
              right={
                <Text className="text-[13px] text-slate-500">
                  <Text className="text-[20px] font-extrabold text-ink">
                    {today.seen}
                  </Text>{" "}
                  / {DAILY_GOAL}
                </Text>
              }
            />
            <View className="mt-3.5">
              <GaugeBar
                value={goalSeen}
                min={0}
                max={DAILY_GOAL}
                valueLabel={`${goalPercent}%`}
                maxLabel={String(DAILY_GOAL)}
                accessibilityLabel={t("home.todayRecord")}
                accessibilityValueText={t("home.goalA11y", {
                  goal: DAILY_GOAL,
                  seen: today.seen,
                })}
              />
            </View>
            <View className="mt-3 flex-row justify-between px-1.5">
              <MiniStat label={t("home.seenToday")} value={String(today.seen)} />
              <MiniStat label={t("home.knownToday")} value={String(today.known)} />
              <MiniStat
                label={t("home.streak")}
                value={`${streak}${t("home.days")}`}
              />
            </View>
          </View>

          {/* 오늘의 단어(큰 카드) + 설정 토글 둘(작은 카드) */}
          <View className="mt-8 flex-row gap-4">
            {wordOfDay && baseGradeId ? (
              <TodayWordCard
                word={wordOfDay}
                onPress={() => openWord(baseGradeId, wordOfDay.id)}
              />
            ) : (
              <View className="flex-1" />
            )}
            <View className="flex-1 gap-4">
              <ToggleCard
                title={t("home.soundToggle")}
                desc={t("home.soundToggleDesc")}
                on={speechVolume > 0}
                onToggle={() =>
                  setSpeechVolume(speechVolume > 0 ? 0 : DEFAULT_VOLUME)
                }
              />
              <ToggleCard
                title={t("settings.autoAdvance")}
                desc={t("home.autoToggleDesc")}
                on={autoAdvance}
                onToggle={() => setAutoAdvance(!autoAdvance)}
              />
            </View>
          </View>

          {/* 이어하기 플레이어 */}
          <View className="mt-8">
            <ContinueCard />
          </View>

          {/* 오늘의 복습: 헷갈린다고 표시한 단어가 있을 때만 */}
          {unsure.length > 0 && (
            <View className="mt-8">
              <SectionLabel
                label="REVIEW"
                sub={t("home.reviewCount", { count: unsure.length })}
                right={
                  <PillButton
                    label={t("home.reviewStart")}
                    size="sm"
                    variant="primary"
                    onPress={() => router.push(`/study/${unsure[0].id}`)}
                  />
                }
              />

              {/* 가로 목록은 화면 좌우 여백을 넘어 끝까지 이어지게 한다 */}
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                className="-mx-6 mt-4"
                contentContainerClassName="gap-3 px-6 pb-2"
              >
                {unsure.map((w) => {
                  const source =
                    wordImageSource(w);
                  return (
                    <PressableScale
                      key={w.id}
                      onPress={() => router.push(`/study/${w.id}`)}
                      accessibilityRole="button"
                      accessibilityLabel={t("a11y.reviewWord", { word: w.word })}
                      className="w-[88px]"
                    >
                      <View className="h-[88px] w-[88px] items-center justify-center overflow-hidden rounded-2xl bg-canvas shadow-neu-inset">
                        {source ? (
                          <Image
                            source={source}
                            contentFit="cover"
                            style={{ width: "100%", height: "100%" }}
                          />
                        ) : (
                          <Text className="text-[11px] text-slate-400">준비 중</Text>
                        )}
                      </View>
                      <Text
                        numberOfLines={1}
                        className="mt-2 text-[13px] font-bold text-ink"
                      >
                        {w.word}
                      </Text>
                    </PressableScale>
                  );
                })}
              </ScrollView>
            </View>
          )}

          {/* 빠른 실행: 아래 탭에 없는 동작 위주로 */}
          <View className="mt-8">
            <SectionLabel label="QUICK START" center />
            <View className="mt-4 flex-row justify-around">
              {unsure.length > 0 && (
                <QuickButton
                  icon={<AgainIcon size={24} color="#475569" />}
                  label={t("home.quickReview")}
                  onPress={() => router.push(`/study/${unsure[0].id}`)}
                />
              )}
              <QuickButton
                icon={<ShuffleIcon size={24} color="#475569" />}
                label={t("home.quickRandom")}
                onPress={openRandom}
              />
              <QuickButton
                icon={<QuizIcon size={26} color="#475569" />}
                label={t("nav.quiz")}
                onPress={openQuiz}
              />
              <QuickButton
                icon={<BookIcon size={24} color="#475569" />}
                label={t("nav.wordbook")}
                onPress={() => router.push("/wordbook")}
              />
            </View>
          </View>

          {/* 내 코스 */}
          <View className="mt-8">
            <SectionLabel label="MY COURSE" sub={t("home.myCourse")} />
          </View>
          <View className="mt-4 gap-4">
            {courseRows.map((row) => (
              <View key={row[0].grade.id} className="flex-row gap-4">
                {row.map(({ grade, known }) => (
                  <View key={grade.id} className="flex-1">
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
                {/* 홀수 개일 때 마지막 카드가 한 줄을 다 차지하지 않게 빈 칸을 둔다 */}
                {row.length === 1 && <View className="flex-1" />}
              </View>
            ))}
          </View>
          {upcomingLabel.length > 0 && (
            <Text className="mt-4 text-[12px] text-slate-400">
              {upcomingLabel} · {t("level.preparing")}
            </Text>
          )}
          </Stagger>
        </View>
      </ScrollView>

      <BottomNav />
    </Screen>
  );
}
