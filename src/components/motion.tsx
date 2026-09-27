import {
  Children,
  isValidElement,
  type ReactNode,
  useEffect,
  useState,
} from "react";
import {
  Animated,
  Easing,
  Platform,
  Pressable,
  type PressableProps,
  StyleSheet,
  type StyleProp,
  View,
  type ViewStyle,
} from "react-native";

/**
 * 화면 곳곳의 움직임을 한곳에 모은다.
 *
 * 값이 "팍" 바뀌지 않고 흘러가듯 바뀌게 하는 것이 목표다.
 * - 누르면 살짝 눌렸다가 튕기듯 돌아온다 (PressableScale)
 * - 켜짐·선택처럼 모양이 바뀌면 두 모양을 겹쳐 두고 서서히 바꿔 낀다 (NeuStateLayer)
 * - 화면이 뜰 때 칸들이 아래에서 차례로 떠오른다 (FadeInUp)
 *
 * NativeWind 의 className 은 Animated.View 에 걸리지 않는다. 그래서 움직임은
 * Animated.View 의 style 로만 주고, 모양(className)은 그 안의 View 가 맡는다.
 */

/** 웹에는 네이티브 드라이버가 없다. 켜 두면 경고만 쌓인다 */
export const NATIVE_DRIVER = Platform.OS !== "web";

/** 앱 전체가 같은 박자로 움직이게 쓰는 시간 (ms) */
export const DURATION = {
  fast: 160,
  base: 240,
  slow: 450,
};

export const EASE_OUT = Easing.out(Easing.cubic);

/**
 * target 이 바뀔 때마다 그 값까지 부드럽게 따라가는 Animated.Value.
 * 처음 그릴 때는 from 에서 출발한다 (없으면 곧바로 target 에 놓인다).
 */
export function useSmooth(
  target: number,
  {
    duration = DURATION.base,
    from,
    native = false,
  }: { duration?: number; from?: number; native?: boolean } = {},
) {
  const [value] = useState(() => new Animated.Value(from ?? target));
  useEffect(() => {
    const anim = Animated.timing(value, {
      toValue: target,
      duration,
      easing: EASE_OUT,
      useNativeDriver: native && NATIVE_DRIVER,
    });
    anim.start();
    return () => anim.stop();
  }, [target, duration, native, value]);
  return value;
}

type PressableScaleProps = PressableProps & {
  className?: string;
  /** 누르고 있는 동안 줄어드는 크기 */
  scaleTo?: number;
  /** 바깥 틀 스타일. 줄 안에서 flex 로 나눠 가질 때 여기에 flex: 1 을 준다 */
  containerStyle?: StyleProp<ViewStyle>;
};

/**
 * 누르면 살짝 작아졌다가 떼면 스프링으로 튕기며 돌아오는 Pressable.
 * 크기만 움직이므로 안쪽 모양과 누르는 영역은 그대로다.
 */
export function PressableScale({
  scaleTo = 0.96,
  containerStyle,
  onPressIn,
  onPressOut,
  children,
  ...rest
}: PressableScaleProps) {
  const [scale] = useState(() => new Animated.Value(1));
  const springTo = (toValue: number) =>
    Animated.spring(scale, {
      toValue,
      // 누를 때는 곧바로, 뗄 때는 한 번 튕기며
      speed: toValue === 1 ? 18 : 40,
      bounciness: toValue === 1 ? 10 : 0,
      useNativeDriver: NATIVE_DRIVER,
    }).start();

  return (
    <Animated.View style={[containerStyle, { transform: [{ scale }] }]}>
      <Pressable
        {...rest}
        onPressIn={(e) => {
          springTo(scaleTo);
          onPressIn?.(e);
        }}
        onPressOut={(e) => {
          springTo(1);
          onPressOut?.(e);
        }}
      >
        {children}
      </Pressable>
    </Animated.View>
  );
}

/**
 * 뉴모피즘의 두 모양(솟은 / 파인)을 겹쳐 두고 active 에 따라 서서히 바꿔 낀다.
 * 그림자는 애니메이션으로 이어 바꿀 수 없어서, 두 겹의 투명도를 엇갈려 바꾼다.
 * 부모는 자체 배경·그림자 없이 모서리 모양(radius)만 이 층에 넘긴다.
 */
export function NeuStateLayer({
  active,
  radiusClass,
  activeClass = "bg-canvas shadow-neu-inset",
  idleClass = "bg-surface shadow-neu-sm",
  duration = DURATION.base,
  appear = false,
}: {
  active: boolean;
  radiusClass: string;
  activeClass?: string;
  idleClass?: string;
  duration?: number;
  /** true 면 처음 그릴 때도 꺼진 모양에서 출발해 서서히 켜진다 (화면을 옮긴 직후 등) */
  appear?: boolean;
}) {
  const v = useSmooth(active ? 1 : 0, {
    duration,
    native: true,
    from: appear ? 0 : undefined,
  });
  return (
    <>
      <Animated.View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFill,
          { opacity: v.interpolate({ inputRange: [0, 1], outputRange: [1, 0] }) },
        ]}
      >
        <View className={`flex-1 ${radiusClass} ${idleClass}`} />
      </Animated.View>
      <Animated.View
        pointerEvents="none"
        style={[StyleSheet.absoluteFill, { opacity: v }]}
      >
        <View className={`flex-1 ${radiusClass} ${activeClass}`} />
      </Animated.View>
    </>
  );
}

/** 처음 그려질 때 아래에서 떠오르며 나타난다. delay 로 칸마다 차례를 준다 */
export function FadeInUp({
  children,
  delay = 0,
  distance = 14,
  style,
}: {
  children: ReactNode;
  delay?: number;
  distance?: number;
  style?: StyleProp<ViewStyle>;
}) {
  const [v] = useState(() => new Animated.Value(0));
  useEffect(() => {
    Animated.timing(v, {
      toValue: 1,
      duration: DURATION.slow,
      delay,
      easing: EASE_OUT,
      useNativeDriver: NATIVE_DRIVER,
    }).start();
  }, [v, delay]);
  return (
    <Animated.View
      style={[
        style,
        {
          opacity: v,
          transform: [
            {
              translateY: v.interpolate({
                inputRange: [0, 1],
                outputRange: [distance, 0],
              }),
            },
          ],
        },
      ]}
    >
      {children}
    </Animated.View>
  );
}

/**
 * 자식들을 위에서부터 차례로 떠오르게 한다.
 * 조건부로 빠진 자식(false·null)은 순서에서 건너뛴다.
 */
export function Stagger({
  children,
  step = 70,
  startDelay = 0,
}: {
  children: ReactNode;
  step?: number;
  startDelay?: number;
}) {
  return (
    <>
      {Children.toArray(children).map((child, i) => (
        <FadeInUp key={isValidElement(child) ? child.key : i} delay={startDelay + i * step}>
          {child}
        </FadeInUp>
      ))}
    </>
  );
}
