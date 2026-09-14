import { Pressable, Text, View } from "react-native";
import { useT } from "../i18n";
import { ChevronRightIcon } from "./icons";

interface GradeCardProps {
  label: string;
  learnedWords: number;
  totalWords: number;
  /** 연상 그림이 아직 없는 단어 수. 그림을 다 그릴 때까지만 띄우는 임시 표시 */
  missingImages?: number;
  onPress: () => void;
}

export function GradeCard({
  label,
  learnedWords,
  totalWords,
  missingImages,
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
      className="rounded-3xl bg-surface p-6 shadow-neu-card active:shadow-neu-pressed"
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
        {started
          ? `${learnedWords} / ${totalWords}`
          : t("course.wordCount", { count: totalWords })}
      </Text>

      {/* 그림 제작 현황(임시). 카드가 좁아 단어 수와 한 줄에 두면 줄이 접혀서
          아래 줄에 따로 둔다. 그림을 전부 채우면 이 블록과 missingImages prop 을 지운다 */}
      {missingImages !== undefined && (
        <View
          className={`mt-1.5 self-start rounded-full px-2 py-0.5 ${
            missingImages > 0 ? "bg-canvas shadow-neu-inset" : "bg-[#dcf2ea]"
          }`}
        >
          <Text
            className={`text-[10px] font-bold ${
              missingImages > 0 ? "text-amber-600" : "text-mint-dark"
            }`}
          >
            {missingImages > 0 ? `🖼 ${missingImages}개 미완료` : "🖼 그림 완료"}
          </Text>
        </View>
      )}
    </Pressable>
  );
}
