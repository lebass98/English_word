import { useEffect, useState } from "react";
import { Animated, Text, View } from "react-native";
import Svg, { Circle } from "react-native-svg";
import { EASE_OUT, PressableScale } from "./motion";
import { useT } from "../i18n";
import { ChevronRightIcon } from "./icons";

interface GradeCardProps {
  label: string;
  learnedWords: number;
  totalWords: number;
  onPress: () => void;
}

/** 진행 고리 크기 (px) */
const RING = 44;
const RING_STROKE = 6;

/** 외운 비율만큼 민트로 차는 원형 고리. 처음 뜰 때 0 에서 빙 돌며 차오른다 */
function ProgressRing({ progress }: { progress: number }) {
  const r = (RING - RING_STROKE) / 2;
  const circumference = 2 * Math.PI * r;
  // 1% 처럼 아주 작아도 점 하나는 보이게 최소 길이를 둔다
  const target = progress > 0 ? Math.max(progress, 0.02) : 0;
  const [shown] = useState(() => new Animated.Value(0));
  /** 지금 그려진 비율. Animated 로 SVG 를 직접 움직이면 웹에서 쓸모없는 속성이
      DOM 에 새어 경고가 나서, 값이 흐를 때마다 상태로 옮겨 다시 그린다 */
  const [drawn, setDrawn] = useState(0);
  useEffect(() => {
    const id = shown.addListener(({ value }) => setDrawn(value));
    return () => shown.removeListener(id);
  }, [shown]);
  useEffect(() => {
    Animated.timing(shown, {
      toValue: target,
      duration: 900,
      delay: 250,
      easing: EASE_OUT,
      // SVG 속성은 네이티브 드라이버로 움직일 수 없다
      useNativeDriver: false,
    }).start();
  }, [target, shown]);
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
      {drawn > 0 && (
        <Circle
          cx={RING / 2}
          cy={RING / 2}
          r={r}
          fill="none"
          stroke="#0EB582"
          strokeWidth={RING_STROKE}
          strokeLinecap="round"
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={circumference * (1 - drawn)}
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
  onPress,
}: GradeCardProps) {
  const t = useT();
  const progress = totalWords > 0 ? learnedWords / totalWords : 0;
  const started = learnedWords > 0;

  return (
    <PressableScale
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={
        started
          ? t("a11y.courseProgress", { label, total: totalWords, known: learnedWords })
          : t("a11y.courseNotStarted", { label })
      }
      className="rounded-3xl bg-surface p-5 shadow-neu-card"
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

    </PressableScale>
  );
}
