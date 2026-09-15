import { useRouter } from "expo-router";
import { useMemo } from "react";
import { Pressable, Text, View } from "react-native";
import { imageBoard, registeredImageCount } from "../lib/imageDebug";
import { useAppStore } from "../stores/useAppStore";

/**
 * 그림 현황판으로 가는 떠 있는 버튼 (임시).
 *
 * 아직 그리지 않은 그림 수를 곧바로 보여주고, 누르면 현황판으로 간다.
 * 하단 탭에 가리지 않게 탭 높이만큼 띄워 둔다.
 * 그림을 전부 채우면 이 파일과 쓰는 곳을 함께 지운다.
 */
export function ImageStatusFab() {
  const router = useRouter();
  const uiLang = useAppStore((s) => s.uiLang);
  // 그림이 새로 등록되면 숫자가 곧바로 줄어들도록 등록 수를 조건에 넣는다
  const imageCount = registeredImageCount();
  const missing = useMemo(
    () => imageBoard(uiLang).missing,
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [uiLang, imageCount],
  );

  const done = missing === 0;

  return (
    <View className="absolute bottom-28 right-6">
      <Pressable
        onPress={() => router.push("/image-status")}
        accessibilityRole="button"
        accessibilityLabel={
          done ? "그림 현황판 — 모두 완료" : `그림 현황판 — ${missing}장 남음`
        }
        className="h-14 flex-row items-center gap-2 rounded-full bg-surface px-5 shadow-neu-card active:shadow-neu-pressed"
      >
        <Text className="text-[20px]">🖼</Text>
        <Text
          className={`text-[15px] font-bold ${
            done ? "text-mint-dark" : "text-ink"
          }`}
        >
          {done ? "완료" : missing.toLocaleString()}
        </Text>
      </Pressable>
    </View>
  );
}
