import { useLocalSearchParams, useRouter } from "expo-router";
import { Pressable, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { PillButton } from "../../src/components/PillButton";
import { GRADES } from "../../src/constants/grades";

export default function GradeScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const grade = GRADES.find((g) => g.id === id);

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View className="w-full flex-1 px-5 lg:mx-auto lg:max-w-3xl">
        <View className="flex-row items-center gap-3 py-5">
          <Pressable onPress={() => router.back()} className="active:opacity-60">
            <Text className="text-2xl text-gray-700">‹</Text>
          </Pressable>
          <Text className="text-2xl font-bold text-gray-900">
            {grade?.label ?? "학년"}
          </Text>
        </View>
        <View className="flex-1 items-center justify-center gap-4">
          <Text className="text-gray-400">
            단어 목록 화면 — 다음 단계에서 만듭니다
          </Text>
          <PillButton
            variant="primary"
            size="lg"
            label="학습 시작 (샘플)"
            onPress={() => router.push("/study/innocent")}
          />
        </View>
      </View>
    </SafeAreaView>
  );
}
