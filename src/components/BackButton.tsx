import { useRouter } from "expo-router";
import { Pressable } from "react-native";
import { ChevronLeftIcon } from "./icons";

export interface BackButtonProps {
  onPress?: () => void;
  fallbackHref?: string;
  className?: string;
  iconSize?: number;
}

/**
 * 앱 전체에서 일관되게 사용하는 뒤로가기 원형 버튼.
 * 유닛 뷰 화면의 스타일과 동작을 기준으로 통일되어 있다.
 */
export function BackButton({
  onPress,
  fallbackHref = "/",
  className = "",
  iconSize = 24,
}: BackButtonProps) {
  const router = useRouter();

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else if (router.canGoBack()) {
      router.back();
    } else {
      router.replace(fallbackHref as any);
    }
  };

  return (
    <Pressable
      onPress={handlePress}
      accessibilityLabel="뒤로 가기"
      className={`h-12 w-12 items-center justify-center rounded-full bg-surface shadow-neu-sm active:shadow-neu-pressed ${className}`}
    >
      <ChevronLeftIcon size={iconSize} strokeWidth={2.8} color="#334155" />
    </Pressable>
  );
}
