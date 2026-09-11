import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Platform,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { BackButton } from "../src/components/BackButton";
import { BottomNav } from "../src/components/BottomNav";
import { PillButton } from "../src/components/PillButton";
import { useAppStore } from "../src/stores/useAppStore";

/** 웹 2단계 확인이 눌린 채로 남아 있지 않도록 되돌리는 시간 (ms) */
const CONFIRM_TIMEOUT_MS = 4000;

export default function SettingsScreen() {
  const nickname = useAppStore((s) => s.nickname);
  const setNickname = useAppStore((s) => s.setNickname);
  const autoAdvance = useAppStore((s) => s.autoAdvance);
  const setAutoAdvance = useAppStore((s) => s.setAutoAdvance);
  const entries = useAppStore((s) => s.entries);
  const resetProgress = useAppStore((s) => s.resetProgress);

  /** 웹에는 Alert이 없어 버튼을 두 번 눌러 확인받는다 */
  const [confirming, setConfirming] = useState(false);

  const counts = useMemo(() => {
    let known = 0;
    let unsure = 0;
    for (const entry of Object.values(entries)) {
      if (entry.status === "known") known += 1;
      else if (entry.status === "unsure") unsure += 1;
    }
    return { known, unsure };
  }, [entries]);

  const hasRecord = counts.known > 0 || counts.unsure > 0;

  // 확인 상태로 방치된 버튼을 잘못 누르는 일이 없도록 잠시 뒤 되돌린다
  useEffect(() => {
    if (!confirming) return;
    const timer = setTimeout(() => setConfirming(false), CONFIRM_TIMEOUT_MS);
    return () => clearTimeout(timer);
  }, [confirming]);

  const handleReset = () => {
    if (Platform.OS === "web") {
      if (!confirming) {
        setConfirming(true);
        return;
      }
      setConfirming(false);
      resetProgress();
      return;
    }

    Alert.alert(
      "학습 기록 초기화",
      "외운 단어와 이어하기 지점이 모두 지워져요. 계속할까요?",
      [
        { text: "취소", style: "cancel" },
        { text: "지우기", style: "destructive", onPress: resetProgress },
      ],
    );
  };

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View className="w-full flex-1">
        <View className="flex-row items-center gap-4 px-6 pb-4 pt-8">
          <BackButton fallbackHref="/" />
          <Text className="text-2xl font-bold text-ink">설정</Text>
        </View>

        <ScrollView
          className="flex-1"
          contentContainerClassName="px-6 pb-32 pt-2"
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
            <Text className="text-[15px] font-bold text-ink">내 이름</Text>
            <TextInput
              value={nickname}
              onChangeText={setNickname}
              placeholder="이름을 입력하세요"
              placeholderTextColor="#94a3b8"
              maxLength={12}
              returnKeyType="done"
              className="mt-3 rounded-2xl bg-canvas px-4 py-3 text-[15px] text-ink shadow-neu-inset"
            />
          </View>

          <View className="mt-6 rounded-3xl bg-surface p-6 shadow-neu-card">
            <Text className="text-[15px] font-bold text-ink">학습 설정</Text>
            <View className="mt-4 flex-row items-center justify-between gap-4">
              <View className="flex-1">
                <Text className="text-[15px] text-slate-700">자동 넘김</Text>
                <Text className="mt-1 text-[13px] text-slate-400">
                  학습 화면에서 다음 단어로 저절로 넘어가요
                </Text>
              </View>
              <Pressable
                accessibilityRole="switch"
                accessibilityLabel="자동 넘김"
                accessibilityState={{ checked: autoAdvance }}
                onPress={() => setAutoAdvance(!autoAdvance)}
                className={`rounded-full px-4 py-2 active:opacity-70 ${
                  autoAdvance
                    ? "bg-surface shadow-neu-sm"
                    : "bg-canvas shadow-neu-inset"
                }`}
              >
                <Text
                  className={`text-[13px] font-bold ${
                    autoAdvance ? "text-mint-dark" : "text-slate-400"
                  }`}
                >
                  {autoAdvance ? "켜짐" : "꺼짐"}
                </Text>
              </Pressable>
            </View>
          </View>

          <View className="mt-6 rounded-3xl bg-surface p-6 shadow-neu-card">
            <Text className="text-[15px] font-bold text-ink">학습 기록</Text>
            {/* 기록이 없으면 "0개 · 0개" 대신 안내를 보여주고, 지울 것도 없으니 버튼을 감춘다 */}
            {hasRecord ? (
              <>
                <Text className="mt-3 text-[13px] text-slate-700">
                  외운 단어 {counts.known}개 · 헷갈리는 단어 {counts.unsure}개
                </Text>
                <PillButton
                  className="mt-5 self-start"
                  size="sm"
                  label={confirming ? "정말 지울까요?" : "학습 기록 초기화"}
                  onPress={handleReset}
                />
              </>
            ) : (
              <Text className="mt-3 text-[13px] text-slate-400">
                아직 학습 기록이 없어요
              </Text>
            )}
          </View>
        </ScrollView>
      </View>

      <BottomNav />
    </SafeAreaView>
  );
}
