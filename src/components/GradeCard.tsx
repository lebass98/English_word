import { Pressable, Text, View } from "react-native";
import { useT } from "../i18n";
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
  const t = useT();
  const progress = totalWords > 0 ? learnedWords / totalWords : 0;
  const started = learnedWords > 0;

  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={
        started
          ? t("a11y.courseProgress", { label, total: totalWords, known: learnedWords })
          : t("a11y.courseNotStarted", { label })
      }
      className="rounded-3xl bg-surface p-5 shadow-neu-card active:shadow-neu-pressed"
    >
      <Text
        className={`text-[11px] font-bold ${
          started ? "text-mint" : "text-slate-400"
        }`}
      >
        {started ? t("course.studying") : t("course.notStarted")}
      </Text>

      <View className="mt-1.5 flex-row items-center justify-between gap-1">
        <Text
          className="flex-1 text-[17px] font-bold text-ink"
          numberOfLines={1}
        >
          {label}
        </Text>
        <ChevronRightIcon size={16} color="#94a3b8" strokeWidth={2.5} />
      </View>

      {/* 카드가 한 줄에 두 개 들어가느라 좁아서, 막대와 개수를 옆이 아니라 위아래로 놓는다 */}
      <View className="mt-4 h-2 overflow-hidden rounded-full bg-canvas shadow-neu-inset">
        <View
          className="h-full rounded-full bg-mint"
          style={{ width: `${Math.round(progress * 100)}%` }}
        />
      </View>
      {/* 아직 한 개도 못 외운 학년은 "0 / 700" 대신 전체 개수만 알려준다 */}
      <Text className="mt-2 text-[12px] font-bold text-slate-500">
        {started ? `${learnedWords} / ${totalWords}` : t("course.wordCount", { count: totalWords })}
      </Text>
    </Pressable>
  );
}
