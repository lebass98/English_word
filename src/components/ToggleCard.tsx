import { Pressable, Text, View } from "react-native";
import Svg, { Defs, LinearGradient, Rect, Stop } from "react-native-svg";
import { useT } from "../i18n";
import { GAUGE_FILL_STOPS } from "./GaugeBar";

/** 스위치 크기 (px) */
const SW_W = 46;
const SW_H = 24;
const SW_THUMB = 18;

/**
 * 뉴모피즘 스위치. 꺼지면 파인 홈만, 켜지면 게이지와 같은 그라데이션이 찬다.
 * 누르는 자리는 카드 전체라 여기서는 모양만 그린다.
 */
function NeuSwitch({ on }: { on: boolean }) {
  return (
    <View
      style={{ width: SW_W, height: SW_H }}
      className="overflow-hidden rounded-full bg-canvas shadow-neu-inset"
    >
      {on && (
        <Svg width={SW_W} height={SW_H} style={{ position: "absolute" }}>
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
      )}
      <View
        style={{
          width: SW_THUMB,
          height: SW_THUMB,
          top: (SW_H - SW_THUMB) / 2,
          left: on ? SW_W - SW_THUMB - 3 : 3,
        }}
        className="absolute rounded-full bg-surface shadow-neu-sm"
      />
    </View>
  );
}

/**
 * 홈의 작은 설정 카드. 제목·설명 아래 오른쪽에 켜짐/꺼짐 스위치가 있다.
 * 설정 화면과 같은 값을 바로 켜고 끈다.
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
  return (
    <Pressable
      onPress={onToggle}
      accessibilityRole="switch"
      accessibilityLabel={title}
      accessibilityState={{ checked: on }}
      className="flex-1 justify-between rounded-3xl bg-surface p-4 shadow-neu-card active:shadow-neu-pressed"
    >
      <View>
        <Text numberOfLines={1} className="text-[15px] font-extrabold text-ink">
          {title}
        </Text>
        <Text numberOfLines={2} className="mt-0.5 text-[11px] text-slate-400">
          {desc}
        </Text>
      </View>
      <View className="mt-3 flex-row items-center justify-end gap-2">
        <Text className="text-[12px] text-slate-400">
          {on ? t("common.on") : t("common.off")}
        </Text>
        <NeuSwitch on={on} />
      </View>
    </Pressable>
  );
}
