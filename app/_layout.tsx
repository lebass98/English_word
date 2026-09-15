import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useFonts } from "expo-font";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import { Platform } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import {
  NATIVE_FONTS,
  installAppFont,
  setAppFontFamily,
} from "../src/lib/appFont";
import { useAppStore } from "../src/stores/useAppStore";
import "../global.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1분
      retry: 1,
    },
  },
});

// 글자 요소마다 기본 글꼴을 깔아 준다 (네이티브 전용, 웹은 CSS 로 씌운다)
installAppFont();

export default function RootLayout() {
  const uiLang = useAppStore((s) => s.uiLang);

  // 웹은 @font-face 로 이미 걸려 있어 따로 불러올 게 없다
  const [fontsLoaded] = useFonts(Platform.OS === "web" ? {} : NATIVE_FONTS);

  // 표시 언어에 맞는 글꼴로 바꾼다 (일본어 → Noto Sans JP, 그 밖 → 프리텐다드 GOV)
  useEffect(() => {
    setAppFontFamily(uiLang);
  }, [uiLang]);

  // 글꼴을 불러오는 동안 화면을 비워 둔다. 시스템 글꼴로 먼저 그렸다가
  // 글꼴이 바뀌면 글자 크기가 한 번 출렁인다
  if (!fontsLoaded) return null;

  return (
    <QueryClientProvider client={queryClient}>
      <SafeAreaProvider>
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: "#ffffff" },
          }}
        />
        <StatusBar style="auto" />
      </SafeAreaProvider>
    </QueryClientProvider>
  );
}
