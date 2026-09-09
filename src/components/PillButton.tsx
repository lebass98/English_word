import { ReactNode } from "react";
import { ActivityIndicator, Pressable, Text } from "react-native";

export type PillButtonVariant = "default" | "primary" | "accent" | "inset";

interface PillButtonProps {
  label: string;
  onPress?: () => void;
  /**
   * 뉴모피즘 필 버튼. 모든 variant가 배경에서 솟아오른(또는 파인) 형태를 유지한다.
   * default: 기본 서피스 필
   * primary: 민트 틴트 서피스 (주요 액션)
   * accent: 라벤더 틴트 서피스 (보조 강조)
   * inset: 안쪽으로 파인 상태 (토글 ON, 선택됨)
   */
  variant?: PillButtonVariant;
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  left?: ReactNode;
  right?: ReactNode;
  className?: string;
}

const VARIANT = {
  default: { bg: "bg-surface", text: "text-slate-800", shadow: "shadow-neu-sm" },
  primary: {
    bg: "bg-[#dcf2ea]",
    text: "text-mint-dark",
    shadow: "shadow-neu-sm",
  },
  accent: {
    bg: "bg-[#e9e6f8]",
    text: "text-indigo-700",
    shadow: "shadow-neu-sm",
  },
  inset: {
    bg: "bg-canvas",
    text: "text-mint-dark",
    shadow: "shadow-neu-inset",
  },
};

// 최소 폰트 16px(text-base) 유지
const SIZE = {
  sm: { pad: "px-5 py-2.5", text: "text-base" },
  md: { pad: "px-6 py-3", text: "text-base" },
  lg: { pad: "px-7 py-4", text: "text-lg" },
};

export function PillButton({
  label,
  onPress,
  variant = "default",
  size = "md",
  loading = false,
  left,
  right,
  className = "",
}: PillButtonProps) {
  const v = VARIANT[variant];
  const s = SIZE[size];

  return (
    <Pressable
      onPress={onPress}
      disabled={loading}
      className={`flex-row items-center justify-center gap-2 rounded-full ${v.bg} ${v.shadow} ${s.pad} active:shadow-neu-pressed active:scale-[0.97] ${className}`}
    >
      {left}
      <Text className={`font-bold ${s.text} ${v.text}`}>{label}</Text>
      {loading ? <ActivityIndicator size="small" color="#0eb582" /> : right}
    </Pressable>
  );
}
