import { usePathname, useRouter } from "expo-router";
import { useEffect, useState } from "react";
import { Animated, Platform, Text, View } from "react-native";
import {
  BookFilledIcon,
  BookIcon,
  GearFilledIcon,
  GearIcon,
  HomeFilledIcon,
  HomeIcon,
  PictureFilledIcon,
  PictureIcon,
  QuizFilledIcon,
  QuizIcon,
} from "./icons";
import { MAX_CONTENT_WIDTH } from "./Screen";
import {
  DURATION,
  NATIVE_DRIVER,
  NeuStateLayer,
  PressableScale,
} from "./motion";
import { useT, type StringKey } from "../i18n";
import { useAppStore } from "../stores/useAppStore";

/** 독 탭 하나. 기본은 선 아이콘, 활성 탭은 꽉 찬 아이콘을 쓴다 */
interface Tab {
  /** 고정 경로. 퀴즈처럼 학년에 따라 달라지는 탭은 비워 두고 아래에서 정한다 */
  href: string;
  labelKey: StringKey;
  Icon: (props: {
    size?: number;
    color?: string;
    strokeWidth?: number;
  }) => React.ReactElement;
  IconFilled: (props: { size?: number; color?: string }) => React.ReactElement;
}

const TABS: Tab[] = [
  { href: "/", labelKey: "nav.home", Icon: HomeIcon, IconFilled: HomeFilledIcon },
  {
    href: "/wordbook",
    labelKey: "nav.wordbook",
    Icon: BookIcon,
    IconFilled: BookFilledIcon,
  },
  {
    href: "/quiz",
    labelKey: "nav.quiz",
    Icon: QuizIcon,
    IconFilled: QuizFilledIcon,
  },
  // 그림 현황 (디버그용). 그림을 하나씩 차례로 넘겨 보며 확인한다
  {
    href: "/image-status",
    labelKey: "nav.imageStatus",
    Icon: PictureIcon,
    IconFilled: PictureFilledIcon,
  },
  {
    href: "/settings",
    labelKey: "nav.settings",
    Icon: GearIcon,
    IconFilled: GearFilledIcon,
  },
];

/**
 * 독 탭 하나. 화면마다 독바를 새로 그리므로, 화면을 옮기면 켜진 탭의 파인 자리가
 * 스르르 나타나고 꽉 찬 아이콘이 톡 튀어 오른다. 누르면 살짝 눌렸다 돌아온다.
 */
function TabItem({
  tab,
  active,
  label,
  onPress,
}: {
  tab: Tab;
  active: boolean;
  label: string;
  onPress: () => void;
}) {
  const [pop] = useState(() => new Animated.Value(active ? 0.85 : 1));
  useEffect(() => {
    if (!active) return;
    Animated.spring(pop, {
      toValue: 1,
      speed: 16,
      bounciness: 10,
      useNativeDriver: NATIVE_DRIVER,
    }).start();
  }, [active, pop]);

  return (
    <PressableScale
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityState={{ selected: active }}
      onPress={onPress}
      scaleTo={0.92}
      containerStyle={{ flex: 1 }}
      // 아이콘을 위, 제목을 아래에 둔다 (슬림한 54px 높이)
      className="h-[54px] items-center justify-center gap-0.5 px-1"
    >
      <NeuStateLayer
        active={active}
        appear
        radiusClass="rounded-full"
        idleClass="bg-transparent"
        duration={DURATION.slow}
      />
      <Animated.View style={{ transform: [{ scale: pop }] }}>
        {active ? (
          <tab.IconFilled size={24} color="#006C4C" />
        ) : (
          <tab.Icon size={24} color="#94a3b8" />
        )}
      </Animated.View>
      <Text
        numberOfLines={1}
        className={`text-[11px] tracking-tight ${
          active ? "font-bold text-mint-dark" : "font-medium text-slate-400"
        }`}
      >
        {label}
      </Text>
    </PressableScale>
  );
}

/**
 * 홈 · 단어장 · 퀴즈 · 현황 · 설정 독바. 아이콘을 위에, 제목을 아래에 둔다.
 * 활성 탭은 현재 경로에서 직접 계산해 화면마다 따로 알려줄 필요가 없다.
 *
 * 웹에서는 position:fixed 로 창 아래에 붙여 둔다. absolute 로 두면 모바일
 * 브라우저에서 주소창이 들고 나며 페이지가 늘어날 때 독바가 같이 밀려 올라간다.
 * 대신 화면 폭 전체를 차지하게 되므로, 안쪽 내용은 다른 화면과 같은
 * 최대 폭으로 가운데 모은다.
 */
export function BottomNav() {
  const pathname = usePathname();
  const router = useRouter();
  const t = useT();
  // 퀴즈는 학년마다 다른 화면이다. 고른 학년이 없으면 홈에서 먼저 고르게 한다
  const activeGradeId = useAppStore((s) => s.activeGradeId);

  const hrefOf = (tab: Tab) =>
    tab.href === "/quiz"
      ? activeGradeId
        ? `/quiz/${activeGradeId}`
        : "/"
      : tab.href;

  const web = Platform.OS === "web";

  return (
    <View
      className={web ? "" : "absolute inset-x-0 bottom-0"}
      style={
        web
          ? // RN 웹에서만 쓰는 값이라 타입 단언으로 넘긴다
            ({ position: "fixed", left: 0, right: 0, bottom: 0 } as never)
          : undefined
      }
    >
      <View
        className="w-full self-center px-6 pb-5 pt-1"
        style={{ maxWidth: MAX_CONTENT_WIDTH }}
      >
        <View className="flex-row items-center gap-1 rounded-full bg-surface px-2 py-1.5 shadow-neu-card">
          {TABS.map((tab) => {
            const href = hrefOf(tab);
            // 퀴즈 탭은 어느 학년이든 /quiz 로 시작하면 켜진 것으로 본다
            const active =
              tab.href === "/quiz"
                ? pathname.startsWith("/quiz")
                : pathname === tab.href;

            return (
              <TabItem
                key={tab.href}
                tab={tab}
                active={active}
                label={t(tab.labelKey)}
                // 같은 탭을 다시 누르면 스택만 쌓이므로 아무것도 하지 않는다
                onPress={() => {
                  if (!active) router.push(href as any);
                }}
              />
            );
          })}
        </View>
      </View>
    </View>
  );
}
