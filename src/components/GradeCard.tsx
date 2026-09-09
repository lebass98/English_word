import { Pressable, Text, View } from "react-native";

interface GradeCardProps {
  label: string;
  learnedWords: number;
  totalWords: number;
  onPress: () => void;
}

export function GradeCard({
  label,
  learnedWords,
  totalWords,
  onPress,
}: GradeCardProps) {
  const progress = totalWords > 0 ? learnedWords / totalWords : 0;
  const started = learnedWords > 0;

  return (
    <Pressable
      onPress={onPress}
      className="rounded-3xl bg-surface p-6 shadow-neu active:shadow-neu-pressed"
    >
      <Text
        className={`text-base font-semibold ${started ? "text-emerald-500" : "text-sky-500"}`}
      >
        {started ? "학습중" : "미학습"}
      </Text>

      <View className="mt-2 flex-row items-center justify-between">
        <Text className="text-2xl font-bold text-gray-800">{label}</Text>
        <Text className="text-xl text-gray-400">›</Text>
      </View>

      <View className="mt-4 flex-row items-center gap-3">
        <View className="h-2.5 flex-1 overflow-hidden rounded-full border border-sky-300 bg-white">
          <View
            className="h-full rounded-full bg-sky-400"
            style={{ width: `${Math.round(progress * 100)}%` }}
          />
        </View>
        <Text className="text-base text-gray-500">
          학습률: {learnedWords} / {totalWords}
        </Text>
      </View>
    </Pressable>
  );
}
