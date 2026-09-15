import { usePathname, useRouter } from "expo-router";
import { Platform, Pressable, Text, View } from "react-native";
import {
  BookFilledIcon,
  BookIcon,
  GearFilledIcon,
  GearIcon,
  HomeFilledIcon,
  HomeIcon,
  PictureFilledIcon,
  PictureIcon,
} from "./icons";
import { MAX_CONTENT_WIDTH } from "./Screen";
import { useT, type StringKey } from "../i18n";

/** 독 탭 하나. 기본은 선 아이콘, 활성 탭은 꽉 찬 아이콘을 쓴다 */
interface Tab {
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
  // 그림 제작 현황(임시). 그림을 전부 채우면 이 줄과 현황판을 함께 지운다
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
 * 홈 · 단어장 · 현황 · 설정 독바. 아이콘을 위에, 제목을 아래에 둔다.
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
        className="w-full self-center px-6 pb-6 pt-2"
        style={{ maxWidth: MAX_CONTENT_WIDTH }}
      >
        <View className="flex-row items-center gap-1 rounded-full bg-surface px-2 py-2 shadow-neu-card">
          {TABS.map((tab) => {
            const active = pathname === tab.href;

            return (
              <Pressable
                key={tab.href}
                accessibilityRole="button"
                accessibilityLabel={t(tab.labelKey)}
                accessibilityState={{ selected: active }}
                // 같은 탭을 다시 누르면 스택만 쌓이므로 아무것도 하지 않는다
                onPress={() => {
                  if (!active) router.push(tab.href as any);
                }}
                // 아이콘을 위, 제목을 아래에 둔다
                className={`h-[64px] flex-1 items-center justify-center gap-1 rounded-2xl px-1 ${
                  active ? "bg-canvas shadow-neu-inset" : "active:opacity-60"
                }`}
              >
                {active ? (
                  <tab.IconFilled size={34} color="#006C4C" />
                ) : (
                  <tab.Icon size={34} color="#94a3b8" strokeWidth={0.55} />
                )}
                <Text
                  numberOfLines={1}
                  className={`text-[11px] ${
                    active ? "font-bold text-mint-dark" : "font-semibold text-slate-400"
                  }`}
                >
                  {t(tab.labelKey)}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </View>
    </View>
  );
}
