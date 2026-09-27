import { Pressable, Text, View } from "react-native";
import Svg, { Circle } from "react-native-svg";
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

/** 진행 고리 크기 (px) */
const RING = 44;
const RING_STROKE = 6;

/** 외운 비율만큼 민트로 차는 원형 고리 */
function ProgressRing({ progress }: { progress: number }) {
  const r = (RING - RING_STROKE) / 2;
  const circumference = 2 * Math.PI * r;
  return (
    <Svg width={RING} height={RING}>
      <Circle
        cx={RING / 2}
        cy={RING / 2}
        r={r}
        fill="none"
        stroke="#e1e3ea"
        strokeWidth={RING_STROKE}
      />
      {progress > 0 && (
        <Circle
          cx={RING / 2}
          cy={RING / 2}
          r={r}
          fill="none"
          stroke="#0EB582"
          strokeWidth={RING_STROKE}
          strokeLinecap="round"
          strokeDasharray={`${circumference} ${circumference}`}
          // 1% 처럼 아주 작아도 점 하나는 보이게 최소 길이를 둔다
          strokeDashoffset={circumference * (1 - Math.max(progress, 0.02))}
          // 12시 방향에서 시작한다
          transform={`rotate(-90 ${RING / 2} ${RING / 2})`}
        />
      )}
    </Svg>
  );
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
      className="rounded-3xl bg-surface p-5 shadow-neu-card active:shadow-neu-pressed"
    >
      <Text
        className={`text-[11px] font-bold ${
          started ? "text-mint" : "text-slate-400"
        }`}
      >
        {started ? t("course.studying") : t("course.notStarted")}
      </Text>

      <View className="mt-1 flex-row items-center justify-between gap-1">
        <Text
          className="flex-1 text-[16px] font-extrabold text-ink"
          numberOfLines={1}
        >
          {label}
        </Text>
        <ChevronRightIcon size={16} color="#94a3b8" strokeWidth={2.5} />
      </View>

      {/* 카드가 한 줄에 두 개 들어가 좁아서, 막대 대신 고리와 숫자를 나란히 둔다 */}
      <View className="mt-3 flex-row items-center gap-2.5">
        <ProgressRing progress={progress} />
        <View className="flex-1">
          {/* 아직 한 개도 못 외운 학년은 "0 / 700" 대신 전체 개수만 알려준다 */}
          <Text numberOfLines={1} className="text-[12px] font-bold text-slate-500">
            {started
              ? `${learnedWords} / ${totalWords}`
              : t("course.wordCount", { count: totalWords })}
          </Text>
          {started && (
            <Text className="text-[11px] text-slate-400">
              {Math.round(progress * 100)}%
            </Text>
          )}
        </View>
      </View>

      {/* 그림 제작 현황(임시). 카드가 좁아 단어 수와 한 줄에 두면 줄이 접혀서
          아래 줄에 따로 둔다. 그림을 전부 채우면 이 블록과 missingImages prop 을 지운다 */}
      {missingImages !== undefined && (
        <View
          className={`mt-2 self-start rounded-full px-2 py-0.5 ${
            missingImages > 0 ? "bg-canvas shadow-neu-inset" : "bg-[#dcf2ea]"
          }`}
        >
          <Text
            className={`text-[10px] font-bold ${
              missingImages > 0 ? "text-amber-600" : "text-mint-dark"
            }`}
          >
            {missingImages > 0 ? `${missingImages}개 미완료` : "그림 완료"}
          </Text>
        </View>
      )}
    </Pressable>
  );
}
