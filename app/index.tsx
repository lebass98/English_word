import { useRouter } from "expo-router";
import { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { GradeCard } from "../src/components/GradeCard";
import { PillButton } from "../src/components/PillButton";
import { StatCard } from "../src/components/StatCard";
import { GRADES } from "../src/constants/grades";
import { useAppStore } from "../src/stores/useAppStore";

const TABS = ["오늘의 학습", "성장기록", "커리큘럼"] as const;

export default function HomeScreen() {
  const router = useRouter();
  const setActiveGradeId = useAppStore((s) => s.setActiveGradeId);
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]>(TABS[0]);

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <ScrollView
        className="flex-1"
        contentContainerClassName="w-full px-6 pb-28"
      >
        {/* 헤더: 브랜드 + 알림 */}
        <View className="flex-row items-center justify-between pt-4">
          <Text className="text-2xl font-bold tracking-tight text-ink">
            Word<Text className="text-mint">Pic</Text>
          </Text>
          <Pressable className="h-12 w-12 items-center justify-center rounded-full bg-surface shadow-neu-sm active:shadow-neu-pressed">
            <Text className="text-lg">🔔</Text>
          </Pressable>
        </View>

        {/* 프로필 카드 */}
        <View className="mt-6 flex-row items-center gap-4 rounded-3xl bg-surface p-6 shadow-neu-card">
          <View className="h-16 w-16 items-center justify-center rounded-full bg-canvas shadow-neu-inset">
            <Text className="text-3xl">🧑‍🎓</Text>
          </View>
          <View className="flex-1">
            <Text className="text-xl font-bold text-ink">우리 학습자 ⌄</Text>
            <Text className="mt-1 text-sm text-slate-500">2026.09.09</Text>
          </View>
          <View className="rounded-full bg-[#dcf2ea] px-3.5 py-1.5 shadow-neu-sm">
            <Text className="text-sm font-bold text-mint-dark">
              출석 완료
            </Text>
          </View>
        </View>

        {/* 탭 칩 */}
        <View className="mt-6 flex-row gap-3">
          {TABS.map((tab) => (
            <PillButton
              key={tab}
              size="sm"
              label={tab}
              variant={activeTab === tab ? "inset" : "default"}
              onPress={() => setActiveTab(tab)}
            />
          ))}
        </View>

        {/* 오늘의 성취 기록 */}
        <Text className="mt-8 text-xl font-bold text-ink">
          오늘의 성취 기록
        </Text>
        <View className="mt-4 flex-row flex-wrap gap-4">
          <StatCard value="9시 23분" label="학습 시간" emoji="⏰" />
          <StatCard value="62" label="학습한 단어 수" emoji="🔤" />
          <StatCard value="75" label="학습한 레슨 수" emoji="📜" />
          <StatCard value="21" label="말한 문장 수" emoji="🔊" />
        </View>

        {/* 오늘의 학습 내용: 학년 선택 */}
        <Text className="mt-8 text-xl font-bold text-ink">
          오늘의 학습 내용
        </Text>
        <Text className="mt-1.5 text-sm text-slate-500">
          학년을 선택하고 학습을 시작하세요
        </Text>
        <View className="mt-4 gap-8 md:flex-row md:flex-wrap">
          {GRADES.map((grade) => (
            <View key={grade.id} className="md:w-[48%]">
              <GradeCard
                label={grade.label}
                learnedWords={0}
                totalWords={grade.totalWords}
                onPress={() => {
                  setActiveGradeId(grade.id);
                  router.push(`/grade/${grade.id}`);
                }}
              />
            </View>
          ))}
        </View>
      </ScrollView>

      {/* 하단 네비게이션 */}
      <View className="absolute inset-x-0 bottom-0 bg-canvas px-6 pb-6 pt-2">
        <View className="flex-row items-center justify-around rounded-full bg-surface px-4 py-3 shadow-neu-card">
          <Pressable className="items-center rounded-full bg-canvas px-6 py-2 shadow-neu-inset">
            <Text className="text-lg">🏠</Text>
            <Text className="text-base font-bold text-mint-dark">홈</Text>
          </Pressable>
          <Pressable className="items-center px-6 py-2 active:opacity-60">
            <Text className="text-lg">📋</Text>
            <Text className="text-base text-slate-400">단어장</Text>
          </Pressable>
          <Pressable className="items-center px-6 py-2 active:opacity-60">
            <Text className="text-lg">⚙️</Text>
            <Text className="text-base text-slate-400">설정</Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}
