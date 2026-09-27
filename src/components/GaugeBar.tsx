import { useEffect, useId, useMemo, useState } from "react";
import { Animated, PanResponder, Text, View } from "react-native";
import Svg, { Defs, LinearGradient, Rect, Stop } from "react-native-svg";
import { DURATION, EASE_OUT, useSmooth } from "./motion";

/** 게이지 전체 높이, 안쪽 여백, 손잡이 지름 (px) */
const GAUGE_HEIGHT = 64;
const GAUGE_PAD = 8;
const KNOB = GAUGE_HEIGHT - GAUGE_PAD * 2;

/** 채움 그라데이션 (민트 → 시안 → 옅은 시안) */
export const GAUGE_FILL_STOPS = [
  { offset: "0", color: "#8fe9d0" },
  { offset: "0.7", color: "#5fd6e8" },
  { offset: "1", color: "#bdf0f5" },
];
/** 꺼짐(음소거 등)일 때 채움색 */
const DIMMED_FILL = "#d5d9e1";
/** 끄는 동안에는 손가락을 바짝 따라가도록 짧게 움직인다 */
const DRAG_DURATION = 90;

type GaugeBarProps = {
  /** 현재 값 (min~max 사이의 정수 단계) */
  value: number;
  min: number;
  max: number;
  /** 끌거나 누르는 동안 값이 바뀔 때마다 부른다. 없으면 보기 전용 게이지가 된다 */
  onChange?: (value: number) => void;
  /** 손을 뗐을 때 한 번 부른다 (견본 소리 재생 등) */
  onRelease?: (value: number) => void;
  /** 0 단계 등 값이 "꺼짐"처럼 보여야 할 때 채움색을 흐리게 한다 */
  dimmed?: boolean;
  /** 채움 안쪽 왼쪽에 쓰는 현재 값 (예: 60%, 10초) */
  valueLabel?: string;
  /** 오른쪽 끝에 쓰는 최댓값 (예: 20, 100%) */
  maxLabel?: string;
  accessibilityLabel: string;
  accessibilityValueText: string;
};

/**
 * 뉴모피즘 알약 게이지.
 * 파인 홈 안에 그라데이션 채움이 차오르고, 채움 끝에 볼록한 손잡이가 붙는다.
 * 홈의 오늘 목표(보기 전용)와 설정의 소리 크기·넘김 간격(끌어서 조절)이 같은 모양을 쓴다.
 * 조절할 때는 막대 아무 곳이나 누르거나 좌우로 끌면 가장 가까운 단계로 맞춰진다.
 *
 * 값은 순간이동하지 않는다. 처음 뜰 때는 0 에서 차오르고, 값이 바뀌면 손잡이가 미끄러져 간다.
 * 그라데이션은 게이지 전체 폭에 깔아 두고 채움 폭만큼만 드러내 차오르는 느낌을 낸다.
 */
export function GaugeBar({
  value,
  min,
  max,
  onChange,
  onRelease,
  dimmed,
  valueLabel,
  maxLabel,
  accessibilityLabel,
  accessibilityValueText,
}: GaugeBarProps) {
  const interactive = Boolean(onChange);
  // 웹 SVG 는 url(#id) 가 문서 전체에서 겹치면 엉뚱한 그라데이션을 집는다
  const gradientId = `gauge${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  /** 안쪽 여백을 뺀 채움 영역 폭 */
  const [width, setWidth] = useState(0);
  /** 게이지 왼쪽 끝의 화면 가로 좌표. 누를 때 구해 두고, 끄는 동안은
      손가락의 화면 좌표에서 빼서 게이지 안 위치를 얻는다 */
  const [barLeft, setBarLeft] = useState(0);
  /** 손가락으로 끄는 중인지. 끄는 동안에는 손잡이가 바짝 따라온다 */
  const [dragging, setDragging] = useState(false);

  const ratio =
    max > min ? Math.min(1, Math.max(0, (value - min) / (max - min))) : 0;

  /** 화면에 그려지는 비율. ratio 를 뒤따라 움직인다 (첫 그림은 0 에서 출발) */
  const [shown] = useState(() => new Animated.Value(0));
  useEffect(() => {
    // 폭을 재기 전에 움직이면 첫 차오름이 보이지 않는다
    if (width <= 0) return;
    const anim = Animated.timing(shown, {
      toValue: ratio,
      duration: dragging ? DRAG_DURATION : DURATION.slow + 250,
      easing: EASE_OUT,
      // 폭(width)은 네이티브 드라이버로 움직일 수 없다
      useNativeDriver: false,
    });
    anim.start();
    return () => anim.stop();
  }, [ratio, width, shown, dragging]);

  // 음소거로 바뀌면 채움색이 스르르 회색으로 덮인다
  const dim = useSmooth(dimmed ? 1 : 0, { native: true });

  const pan = useMemo(() => {
    // 손잡이 가운데가 손가락 아래에 오게, 손잡이 반지름만큼 안쪽을 0 으로 본다
    const valueAt = (x: number) => {
      const travel = width - KNOB;
      if (travel <= 0) return value;
      const r = Math.min(1, Math.max(0, (x - GAUGE_PAD - KNOB / 2) / travel));
      return Math.round(min + r * (max - min));
    };
    const update = (x: number) => {
      const next = valueAt(x);
      if (next !== value) onChange?.(next);
    };
    return PanResponder.create({
      onStartShouldSetPanResponder: () => interactive,
      // 가로로 끄는 동안 스크롤이 제스처를 빼앗지 않게 한다
      onPanResponderTerminationRequest: () => false,
      onPanResponderGrant: (e) => {
        const { locationX, pageX } = e.nativeEvent;
        setBarLeft(pageX - locationX);
        // 처음 누른 자리로는 부드럽게 미끄러져 가고, 그 뒤 끄는 동안은 바짝 따라간다
        setDragging(false);
        update(locationX);
      },
      onPanResponderMove: (e) => {
        if (!dragging) setDragging(true);
        update(e.nativeEvent.pageX - barLeft);
      },
      onPanResponderRelease: (e) => {
        setDragging(false);
        onRelease?.(valueAt(e.nativeEvent.pageX - barLeft));
      },
      onPanResponderTerminate: () => setDragging(false),
    });
  }, [interactive, barLeft, width, value, min, max, onChange, onRelease, dragging]);

  const travel = Math.max(0, width - KNOB);
  // 값이 0 이어도 손잡이가 들어갈 자리만큼은 채워 둔다
  const fillWidth = shown.interpolate({
    inputRange: [0, 1],
    outputRange: [KNOB, KNOB + travel],
  });
  const knobLeft = shown.interpolate({
    inputRange: [0, 1],
    outputRange: [0, travel],
  });
  // 채움이 좁으면 글자가 손잡이에 가려지므로 감춘다 (목표 값 기준)
  const showValueLabel =
    Boolean(valueLabel) && KNOB + ratio * travel >= KNOB + 56;

  return (
    <View
      accessible
      accessibilityRole={interactive ? "adjustable" : "progressbar"}
      accessibilityLabel={accessibilityLabel}
      accessibilityValue={{ min, max, now: value, text: accessibilityValueText }}
      onAccessibilityAction={
        interactive
          ? (e) => {
              const next =
                e.nativeEvent.actionName === "increment"
                  ? Math.min(max, value + 1)
                  : Math.max(min, value - 1);
              if (next !== value) {
                onChange?.(next);
                onRelease?.(next);
              }
            }
          : undefined
      }
      accessibilityActions={
        interactive ? [{ name: "increment" }, { name: "decrement" }] : undefined
      }
      style={{ height: GAUGE_HEIGHT, padding: GAUGE_PAD }}
      className="rounded-full bg-canvas shadow-neu-inset"
      {...pan.panHandlers}
    >
      <View
        pointerEvents="none"
        className="flex-1 justify-center"
        onLayout={(e) => setWidth(e.nativeEvent.layout.width)}
      >
        {/* 오른쪽 끝: 눈금 셋 + 최댓값. 채움이 차오르면 그 아래로 덮인다 */}
        <View className="absolute inset-y-0 right-3 flex-row items-center gap-3.5">
          {[0, 1, 2].map((i) => (
            <View key={i} className="h-3.5 w-0.5 rounded-full bg-[#cfd3dc]" />
          ))}
          {maxLabel && (
            <Text className="ml-1 text-[13px] font-bold text-slate-400">
              {maxLabel}
            </Text>
          )}
        </View>

        {width > 0 && (
          <Animated.View
            style={{
              width: fillWidth,
              height: KNOB,
              borderRadius: KNOB / 2,
              overflow: "hidden",
              justifyContent: "center",
            }}
          >
            <Svg
              width={width}
              height={KNOB}
              style={{ position: "absolute", left: 0, top: 0 }}
            >
              <Defs>
                <LinearGradient id={gradientId} x1="0" y1="0" x2="1" y2="0">
                  {GAUGE_FILL_STOPS.map((s) => (
                    <Stop key={s.offset} offset={s.offset} stopColor={s.color} />
                  ))}
                </LinearGradient>
              </Defs>
              <Rect width={width} height={KNOB} fill={`url(#${gradientId})`} />
            </Svg>
            <Animated.View
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                top: 0,
                bottom: 0,
                backgroundColor: DIMMED_FILL,
                opacity: dim,
              }}
            />
            {showValueLabel && (
              <Text
                numberOfLines={1}
                className={`ml-[18px] text-[13px] font-extrabold ${
                  dimmed ? "text-slate-500" : "text-[#0b5c55]"
                }`}
              >
                {valueLabel}
              </Text>
            )}
          </Animated.View>
        )}

        {/* 손잡이: 채움 끝에 붙은 볼록한 원, 가운데는 살짝 파여 있다 */}
        {width > 0 && (
          <Animated.View
            style={{
              position: "absolute",
              left: knobLeft,
              width: KNOB,
              height: KNOB,
            }}
          >
            <View className="flex-1 items-center justify-center rounded-full bg-surface shadow-neu-sm">
              <View className="h-[26px] w-[26px] rounded-full bg-canvas shadow-neu-inset" />
            </View>
          </Animated.View>
        )}
      </View>
    </View>
  );
}
