import { ReactNode } from "react";
import { Text, View } from "react-native";

/**
 * 알약 라벨 아래에 내용을 두는 블록.
 * 예문·유의어·어원처럼 성격이 다른 보충 설명을 같은 모양으로 늘어놓는 데 쓴다.
 * 읽는 흐름이 끊기지 않도록 왼쪽 정렬한다.
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
    <View className={`items-start ${className}`}>
      <View className="rounded-full bg-canvas px-3.5 py-1 shadow-neu-inset">
        <Text className="text-[11px] font-bold tracking-wide text-lavender">
          {label}
        </Text>
      </View>
      <View className="mt-2.5 w-full">{children}</View>
    </View>
  );
}
