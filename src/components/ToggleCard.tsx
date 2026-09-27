import { Animated, View } from "react-native";
import Svg, { Defs, LinearGradient, Rect, Stop } from "react-native-svg";
import { useT } from "../i18n";
import { GAUGE_FILL_STOPS } from "./GaugeBar";
import { PressableScale, useSmooth } from "./motion";

/** 스위치 크기 (px) */
const SW_W = 46;
const SW_H = 24;
const SW_THUMB = 18;
const THUMB_TRAVEL = SW_W - SW_THUMB - 6;

/** 켜짐 / 꺼짐 색 */
const COLOR = {
  titleOn: "#121826",
  titleOff: "#94a3b8",
  labelOn: "#006C4C",
  labelOff: "#94a3b8",
  thumbOn: "#ffffff",
  thumbOff: "#dfe2e8",
};

/**
 * 뉴모피즘 스위치. 꺼지면 파인 홈만, 켜지면 게이지와 같은 그라데이션이 찬다.
 * 손잡이는 미끄러지고 그라데이션은 서서히 번진다.
 * 누르는 자리는 카드 전체라 여기서는 모양만 그린다.
 */
function NeuSwitch({ v }: { v: Animated.Value }) {
  return (
    <View
      style={{ width: SW_W, height: SW_H }}
      className="overflow-hidden rounded-full bg-canvas shadow-neu-inset"
    >
      <Animated.View style={{ position: "absolute", opacity: v }}>
        <Svg width={SW_W} height={SW_H}>
          <Defs>
            <LinearGradient id="neuSwitchOn" x1="0" y1="0" x2="1" y2="0">
              {GAUGE_FILL_STOPS.slice(0, 2).map((s) => (
                <Stop key={s.offset} offset={s.offset} stopColor={s.color} />
              ))}
            </LinearGradient>
          </Defs>
          <Rect
            width={SW_W}
            height={SW_H}
            rx={SW_H / 2}
            fill="url(#neuSwitchOn)"
          />
        </Svg>
      </Animated.View>
      <Animated.View
        style={{
          position: "absolute",
          width: SW_THUMB,
          height: SW_THUMB,
          top: (SW_H - SW_THUMB) / 2,
          left: 3,
          borderRadius: SW_THUMB / 2,
          backgroundColor: v.interpolate({
            inputRange: [0, 1],
            outputRange: [COLOR.thumbOff, COLOR.thumbOn],
          }),
          transform: [
            {
              translateX: v.interpolate({
                inputRange: [0, 1],
                outputRange: [0, THUMB_TRAVEL],
              }),
            },
          ],
          shadowColor: "#aeaec0",
          shadowOffset: { width: 2, height: 2 },
          shadowOpacity: 0.6,
          shadowRadius: 3,
        }}
      />
    </View>
  );
}

/**
 * 홈의 작은 설정 카드. 제목·설명 아래 오른쪽에 켜짐/꺼짐 스위치가 있다.
 * 설정 화면과 같은 값을 바로 켜고 끈다.
 * 켜지면 제목은 진하게, 켜짐 글씨는 민트로, 스위치는 그라데이션으로 차고
 * 꺼지면 제목·글씨·손잡이가 모두 회색으로 가라앉아 한눈에 구분된다.
 * 색은 한 번에 바뀌지 않고 스위치가 미끄러지는 동안 함께 번진다.
 */
export function ToggleCard({
  title,
  desc,
  on,
  onToggle,
}: {
  title: string;
  desc: string;
  on: boolean;
  onToggle: () => void;
}) {
  const t = useT();
  // 색(color)은 네이티브 드라이버로 바꿀 수 없어 JS 로 움직인다
  const v = useSmooth(on ? 1 : 0);
  const color = (off: string, onColor: string) =>
    v.interpolate({ inputRange: [0, 1], outputRange: [off, onColor] });

  return (
    <PressableScale
      onPress={onToggle}
      accessibilityRole="switch"
      accessibilityLabel={title}
      accessibilityState={{ checked: on }}
      containerStyle={{ flex: 1 }}
      className="flex-1 justify-between rounded-3xl bg-surface p-4 shadow-neu-card"
    >
      <View>
        <Animated.Text
          numberOfLines={1}
          style={{
            fontSize: 15,
            fontWeight: "800",
            color: color(COLOR.titleOff, COLOR.titleOn),
          }}
        >
          {title}
        </Animated.Text>
        <Animated.Text
          numberOfLines={2}
          style={{ marginTop: 2, fontSize: 11, color: COLOR.titleOff }}
        >
          {desc}
        </Animated.Text>
      </View>
      <View className="mt-3 flex-row items-center justify-end gap-2">
        <Animated.Text
          style={{
            fontSize: 12,
            fontWeight: on ? "700" : "400",
            color: color(COLOR.labelOff, COLOR.labelOn),
          }}
        >
          {on ? t("common.on") : t("common.off")}
        </Animated.Text>
        <NeuSwitch v={v} />
      </View>
    </PressableScale>
  );
}
