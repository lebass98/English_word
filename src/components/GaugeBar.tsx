import { useMemo, useState } from "react";
import { PanResponder, View } from "react-native";

type GaugeBarProps = {
  /** 현재 값 (min~max 사이의 정수 단계) */
  value: number;
  min: number;
  max: number;
  /** 끌거나 누르는 동안 값이 바뀔 때마다 부른다 */
  onChange: (value: number) => void;
  /** 손을 뗐을 때 한 번 부른다 (견본 소리 재생 등) */
  onRelease?: (value: number) => void;
  /** 0 단계 등 값이 "꺼짐"처럼 보여야 할 때 채움색을 흐리게 한다 */
  dimmed?: boolean;
  accessibilityLabel: string;
  accessibilityValueText: string;
};

/**
 * 가로 막대 게이지.
 * 슬라이더 라이브러리 없이 앱의 뉴모피즘 모양(파인 홈 + 민트 채움 + 둥근 손잡이)으로 그린다.
 * 막대 아무 곳이나 누르거나 좌우로 끌면 가장 가까운 단계로 맞춰진다.
 */
export function GaugeBar({
  value,
  min,
  max,
  onChange,
  onRelease,
  dimmed,
  accessibilityLabel,
  accessibilityValueText,
}: GaugeBarProps) {
  const [width, setWidth] = useState(0);
  /** 막대 왼쪽 끝의 화면 가로 좌표. 누를 때 구해 두고, 끄는 동안은
      손가락의 화면 좌표에서 빼서 막대 안 위치를 얻는다 */
  const [barLeft, setBarLeft] = useState(0);

  const pan = useMemo(() => {
    const valueAt = (x: number) => {
      if (width <= 0) return value;
      const ratio = Math.min(1, Math.max(0, x / width));
      return Math.round(min + ratio * (max - min));
    };
    const update = (x: number) => {
      const next = valueAt(x);
      if (next !== value) onChange(next);
    };
    return PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      // 가로로 끄는 동안 스크롤이 제스처를 빼앗지 않게 한다
      onPanResponderTerminationRequest: () => false,
      onPanResponderGrant: (e) => {
        const { locationX, pageX } = e.nativeEvent;
        setBarLeft(pageX - locationX);
        update(locationX);
      },
      onPanResponderMove: (e) => update(e.nativeEvent.pageX - barLeft),
      onPanResponderRelease: (e) =>
        onRelease?.(valueAt(e.nativeEvent.pageX - barLeft)),
    });
  }, [barLeft, width, value, min, max, onChange, onRelease]);

  const ratio = max > min ? (value - min) / (max - min) : 0;
  const steps = max - min;

  return (
    <View
      accessible
      accessibilityRole="adjustable"
      accessibilityLabel={accessibilityLabel}
      accessibilityValue={{
        min,
        max,
        now: value,
        text: accessibilityValueText,
      }}
      onAccessibilityAction={(e) => {
        const next =
          e.nativeEvent.actionName === "increment"
            ? Math.min(max, value + 1)
            : Math.max(min, value - 1);
        if (next !== value) {
          onChange(next);
          onRelease?.(next);
        }
      }}
      accessibilityActions={[{ name: "increment" }, { name: "decrement" }]}
      // 막대는 얇아도 누르는 자리는 44px 로 넉넉히 잡는다
      className="h-11 justify-center"
      onLayout={(e) => setWidth(e.nativeEvent.layout.width)}
      {...pan.panHandlers}
    >
      <View
        pointerEvents="none"
        className="h-3 rounded-full bg-canvas shadow-neu-inset"
      >
        <View
          style={{ width: `${ratio * 100}%` }}
          className={`h-full rounded-full ${dimmed ? "bg-slate-300" : "bg-mint"}`}
        />
        {/* 단계 눈금 */}
        <View className="absolute inset-0 flex-row justify-between px-1.5">
          {Array.from({ length: steps + 1 }, (_, i) => (
            <View
              key={i}
              className="my-auto h-1 w-1 rounded-full bg-white/60"
            />
          ))}
        </View>
      </View>
      {width > 0 && (
        <View
          pointerEvents="none"
          style={{ left: ratio * width - 12 }}
          className="absolute h-6 w-6 rounded-full bg-surface shadow-neu-sm"
        />
      )}
    </View>
  );
}
