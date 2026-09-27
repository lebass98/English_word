import type { ReactNode } from "react";
import { Animated, View } from "react-native";
import { NeuStateLayer, PressableScale, useSmooth } from "./motion";

/**
 * 여럿 중 하나를 고르는 버튼 (학습 언어, 표시 언어).
 * 고른 쪽은 안으로 파이고 글씨가 민트로 바뀐다. 모양과 색이 서서히 바뀌어
 * 선택이 옆 버튼으로 스르르 옮겨 가는 것처럼 보인다.
 */
export function SegmentButton({
  selected,
  onPress,
  label,
  left,
}: {
  selected: boolean;
  onPress: () => void;
  label: string;
  left?: ReactNode;
}) {
  const v = useSmooth(selected ? 1 : 0);
  return (
    <PressableScale
      onPress={onPress}
      accessibilityRole="button"
      accessibilityState={{ selected }}
      accessibilityLabel={label}
      containerStyle={{ flex: 1 }}
    >
      <NeuStateLayer active={selected} radiusClass="rounded-2xl" />
      <View className="flex-row items-center gap-2.5 px-3 py-3">
        {left}
        <Animated.Text
          numberOfLines={1}
          style={{
            flexShrink: 1,
            fontSize: 14,
            fontWeight: "700",
            color: v.interpolate({
              inputRange: [0, 1],
              outputRange: ["#64748b", "#006C4C"],
            }),
          }}
        >
          {label}
        </Animated.Text>
      </View>
    </PressableScale>
  );
}
