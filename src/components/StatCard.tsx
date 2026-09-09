import { Text, View } from "react-native";

interface StatCardProps {
  value: string;
  unit?: string;
  label: string;
  emoji: string;
}

export function StatCard({ value, unit, label, emoji }: StatCardProps) {
  return (
    <View className="min-w-[45%] flex-1 flex-row items-center justify-between rounded-3xl bg-surface p-6 shadow-neu">
      <View>
        <View className="flex-row items-baseline gap-1">
          <Text className="text-2xl font-bold text-ink">{value}</Text>
          {unit && (
            <Text className="text-sm font-semibold text-slate-500">
              {unit}
            </Text>
          )}
        </View>
        <Text className="mt-1 text-sm text-slate-500">{label}</Text>
      </View>
      <Text className="text-3xl">{emoji}</Text>
    </View>
  );
}
