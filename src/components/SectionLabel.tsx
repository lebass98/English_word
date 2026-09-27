import type { ReactNode } from "react";
import { Text, View } from "react-native";

/**
 * 홈 화면 칸 제목.
 * 자간을 넓힌 작은 영문 대문자(TODAY GOAL, REVIEW …)를 위에, 표시 언어로 쓴 부제를 아래에 둔다.
 * 영문 제목은 장식이라 번역하지 않는다. 오른쪽에 버튼 하나를 붙일 수 있다.
 */
export function SectionLabel({
  label,
  sub,
  right,
  center = false,
}: {
  label: string;
  sub?: string;
  right?: ReactNode;
  /** 제목만 가운데 둘 때 (부제·버튼 없이) */
  center?: boolean;
}) {
  return (
    <View className="flex-row items-center justify-between gap-3">
      <View className="flex-1">
        <Text
          accessibilityRole="header"
          className={`text-[11px] font-bold tracking-[3px] text-slate-400 ${
            center ? "text-center" : ""
          }`}
        >
          {label}
        </Text>
        {sub && (
          <Text numberOfLines={1} className="mt-0.5 text-[13px] text-slate-500">
            {sub}
          </Text>
        )}
      </View>
      {right}
    </View>
  );
}
