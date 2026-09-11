import { usePathname, useRouter } from "expo-router";
import { Pressable, Text, View } from "react-native";

interface Tab {
  href: string;
  label: string;
  emoji: string;
}

const TABS: Tab[] = [
  { href: "/", label: "홈", emoji: "🏠" },
  { href: "/wordbook", label: "단어장", emoji: "📋" },
  { href: "/settings", label: "설정", emoji: "⚙️" },
];

/**
 * 홈 · 단어장 · 설정 3탭 하단 네비게이션.
 * 활성 탭은 현재 경로에서 직접 계산해 화면마다 따로 알려줄 필요가 없다.
 */
export function BottomNav() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <View className="absolute inset-x-0 bottom-0 bg-canvas px-6 pb-6 pt-2">
      <View className="flex-row items-center justify-around rounded-full bg-surface px-4 py-3 shadow-neu-card">
        {TABS.map((tab) => {
          const active = pathname === tab.href;

          return (
            <Pressable
              key={tab.href}
              accessibilityRole="button"
              accessibilityLabel={tab.label}
              accessibilityState={{ selected: active }}
              // 같은 탭을 다시 누르면 스택만 쌓이므로 아무것도 하지 않는다
              onPress={() => {
                if (!active) router.push(tab.href as any);
              }}
              className={`items-center gap-0.5 rounded-full px-5 py-2 ${
                active ? "bg-canvas shadow-neu-inset" : "active:opacity-60"
              }`}
            >
              <Text className="text-[18px]">{tab.emoji}</Text>
              <Text
                className={`text-[12px] ${
                  active ? "font-bold text-mint-dark" : "text-slate-400"
                }`}
              >
                {tab.label}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}
