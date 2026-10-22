import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useFonts } from "expo-font";
import { useKeepAwake } from "expo-keep-awake";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import { Alert, Platform } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { checkForUpdate, openUpdate } from "../src/lib/appUpdate";
import { startCloudSync } from "../src/lib/cloudSync";
import {
  NATIVE_FONTS,
  installAppFont,
  setAppFontFamily,
} from "../src/lib/appFont";
import { translate } from "../src/i18n";
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

  // 앱을 쓰는 동안은 화면이 꺼지거나 잠기지 않게 한다.
  // 앱을 닫거나 다른 앱으로 가면 기기 설정대로 다시 꺼진다
  useKeepAwake();

  // 웹은 @font-face 로 이미 걸려 있어 따로 불러올 게 없다
  const [fontsLoaded] = useFonts(Platform.OS === "web" ? {} : NATIVE_FONTS);

  // 표시 언어에 맞는 글꼴로 바꾼다 (일본어 → Noto Sans JP, 그 밖 → 프리텐다드 GOV)
  useEffect(() => {
    setAppFontFamily(uiLang);
  }, [uiLang]);

  // 로그인하면 학습 기록을 Firestore 와 맞춘다 (웹 전용, 로그인 전에는 아무것도 안 한다)
  useEffect(() => startCloudSync(), []);

  // 앱을 켤 때 한 번 새 버전을 확인해 알려 준다 (안드로이드 APK 전용)
  useEffect(() => {
    checkForUpdate().then((release) => {
      if (!release) return;
      const lang = useAppStore.getState().uiLang;
      Alert.alert(
        translate(lang, "update.found", { version: release.version }),
        translate(lang, "update.installHint"),
        [
          { text: translate(lang, "update.later"), style: "cancel" },
          {
            text: translate(lang, "update.download"),
            onPress: () => openUpdate(release),
          },
        ],
      );
    });
  }, []);

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
