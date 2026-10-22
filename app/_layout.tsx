import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useFonts } from "expo-font";
import { activateKeepAwakeAsync, deactivateKeepAwake } from "expo-keep-awake";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import { Platform } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { UpdateDialog } from "../src/components/UpdateDialog";
import { checkForUpdate, updateAvailable } from "../src/lib/appUpdate";
import { startCloudSync } from "../src/lib/cloudSync";
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

  // 앱을 쓰는 동안은 화면이 꺼지거나 잠기지 않게 한다.
  // 앱을 닫거나 다른 앱으로 가면 기기 설정대로 다시 꺼진다.
  // 웹은 브라우저가 화면 켜짐을 막을 수 있어, 켜기·끄기 실패는 조용히 넘긴다
  // (useKeepAwake 는 켜지기 전에 끄려 하면 오류를 던진다)
  useEffect(() => {
    const tag = "wordpic-app";
    activateKeepAwakeAsync(tag).catch(() => {});
    return () => {
      Promise.resolve()
        .then(() => deactivateKeepAwake(tag))
        .catch(() => {});
    };
  }, []);

  // 웹은 @font-face 로 이미 걸려 있어 따로 불러올 게 없다
  const [fontsLoaded] = useFonts(Platform.OS === "web" ? {} : NATIVE_FONTS);

  // 표시 언어에 맞는 글꼴로 바꾼다 (일본어 → Noto Sans JP, 그 밖 → 프리텐다드 GOV)
  useEffect(() => {
    setAppFontFamily(uiLang);
  }, [uiLang]);

  // 로그인하면 학습 기록을 Firestore 와 맞춘다 (웹 전용, 로그인 전에는 아무것도 안 한다)
  useEffect(() => startCloudSync(), []);

  // 앱을 켤 때 한 번 새 버전을 확인해, 있으면 업데이트 창을 띄운다 (안드로이드 APK 전용)
  useEffect(() => {
    checkForUpdate({ quiet: true });
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
        {updateAvailable ? <UpdateDialog /> : null}
        <StatusBar style="auto" />
      </SafeAreaProvider>
    </QueryClientProvider>
  );
}
