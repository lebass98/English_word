import { ReactNode } from "react";
import { Text, View } from "react-native";

/**
 * 가운데 알약 라벨 아래에 내용을 두는 블록.
 * 예문·유의어·어원처럼 성격이 다른 보충 설명을 같은 모양으로 늘어놓는 데 쓴다.
 */
export function LabeledSection({
  label,
  children,
  className = "",
}: {
  label: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <View className={`items-center ${className}`}>
      <View className="rounded-full bg-canvas px-3.5 py-1 shadow-neu-inset">
        <Text className="text-[11px] font-bold tracking-wide text-lavender">
          {label}
        </Text>
      </View>
      <View className="mt-2.5 w-full items-center">{children}</View>
    </View>
  );
}
