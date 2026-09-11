import { Text, View } from "react-native";
import type { Synonym } from "../constants/words";

/**
 * 유의어를 "영단어 + 한글 뜻" 쌍으로 늘어놓는다.
 * 한 쌍이 줄 중간에서 끊기지 않도록 쌍마다 감싸고, 줄이 넘치면 다음 줄로 접힌다.
 */
export function SynonymList({ items }: { items: Synonym[] }) {
  return (
    <View className="flex-row flex-wrap items-baseline">
      {items.map((s) => (
        <View key={s.word} className="mr-3 flex-row items-baseline">
          <Text className="text-[15px] font-semibold leading-snug text-lavender">
            {s.word}
          </Text>
          <Text className="ml-1 text-[13px] leading-snug text-slate-500">
            {s.meaning}
          </Text>
        </View>
      ))}
    </View>
  );
}
