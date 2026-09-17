import type { ReactNode } from "react";
import { View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

/**
 * 화면 내용의 최대 폭.
 * 넓은 웹 창이나 태블릿에서도 카드·그림이 끝없이 늘어나지 않고
 * 폰 화면 폭으로 가운데 모이게 한다.
 */
export const MAX_CONTENT_WIDTH = 480;

/** 화면 좌우 여백 (px-6) */
export const SCREEN_PADDING_X = 24;

/** 2열 카드 사이 간격 (gap-4) */
export const GRID_GAP = 16;

/**
 * 모든 화면의 바깥 틀.
 * 배경색과 안전 영역, 최대 폭 가운데 정렬을 한 곳에서 정한다.
 * 하단 탭(BottomNav)도 이 안에 두면 같은 폭으로 모인다.
 */
export function Screen({
  children,
  className = "",
  maxWidth = MAX_CONTENT_WIDTH,
}: {
  children: ReactNode;
  className?: string;
  /**
   * 내용 최대 폭. 기본은 폰 폭이다.
   * 퀴즈처럼 넓은 화면에서 좌우로 펼쳐야 하는 화면만 더 큰 값을 넘긴다.
   */
  maxWidth?: number;
}) {
  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View
        className={`w-full flex-1 self-center ${className}`}
        style={{ maxWidth }}
      >
        {children}
      </View>
    </SafeAreaView>
  );
}

/**
 * 화면 머리줄. 위 여백과 최소 높이(뒤로가기 버튼 48px)를 모든 화면에서 같게 둔다.
 * 뒤로가기 버튼이 없는 화면도 제목이 같은 높이에 온다.
 * 머리줄 아래 첫 내용과의 간격은 내용 쪽에서 HEADER_GAP 클래스(pt-6 / mt-6)로 준다.
 */
export function ScreenHeader({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <View className={`min-h-12 flex-row items-center gap-4 px-6 pt-8 ${className}`}>
      {children}
    </View>
  );
}
