import { Pressable, Text, View } from "react-native";
import { ChevronRightIcon } from "./icons";

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
      accessibilityRole="button"
      accessibilityLabel={
        started
          ? `${label} 학습중, ${totalWords}개 중 ${learnedWords}개 외움`
          : `${label} 아직 학습 전`
      }
      className="rounded-3xl bg-surface p-6 shadow-neu-card active:shadow-neu-pressed"
    >
      <Text
        className={`text-[12px] font-bold ${
          started ? "text-mint" : "text-slate-400"
        }`}
      >
        {started ? "학습중" : "학습 전"}
      </Text>

      <View className="mt-2 flex-row items-center justify-between">
        <Text className="text-[20px] font-bold text-ink">{label}</Text>
        <ChevronRightIcon size={18} color="#94a3b8" strokeWidth={2.5} />
      </View>

      <View className="mt-4 flex-row items-center gap-3">
        <View className="h-2 flex-1 overflow-hidden rounded-full bg-canvas shadow-neu-inset">
          <View
            className="h-full rounded-full bg-mint"
            style={{ width: `${Math.round(progress * 100)}%` }}
          />
        </View>
        {/* 아직 한 개도 못 외운 학년은 "0 / 700" 대신 전체 개수만 알려준다 */}
        <Text className="text-[13px] font-bold text-slate-500">
          {started ? `${learnedWords} / ${totalWords}` : `${totalWords}개 단어`}
        </Text>
      </View>
    </Pressable>
  );
}
