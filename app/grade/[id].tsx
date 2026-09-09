import { useLocalSearchParams, useRouter } from "expo-router";
import { FlatList, Pressable, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { BackButton } from "../../src/components/BackButton";
import { GRADES } from "../../src/constants/grades";
import { unitsOf } from "../../src/constants/words";

export default function GradeScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const grade = GRADES.find((g) => g.id === id);
  const units = unitsOf(id ?? "");

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View className="w-full flex-1">
        <View className="flex-row items-center gap-4 px-6 pt-8 pb-4">
          <BackButton fallbackHref="/" />
          <View>
            <Text className="text-2xl font-bold text-ink">
              {grade?.label ?? "학년"}
            </Text>
            <Text className="mt-1 text-sm text-slate-500">
              전체 {grade?.totalWords ?? 0}개 단어 · {units.length}개 유닛
            </Text>
          </View>
        </View>

        {units.length === 0 ? (
          <View className="flex-1 items-center justify-center px-6">
            <Text className="text-sm text-slate-400">
              단어 데이터 준비 중입니다
            </Text>
          </View>
        ) : (
          <FlatList
            data={units}
            keyExtractor={(u) => String(u.unitNo)}
            numColumns={2}
            columnWrapperClassName="gap-6"
            contentContainerClassName="gap-6 px-6 pb-10 pt-6"
            renderItem={({ item }) => (
              <Pressable
                onPress={() => router.push(`/study/${item.words[0].id}`)}
                className="flex-1 rounded-3xl bg-surface p-6 shadow-neu-card active:shadow-neu-pressed"
              >
                <Text className="text-xs font-bold text-mint">UNIT</Text>
                <Text className="mt-1 text-3xl font-bold text-ink">
                  {item.unitNo}
                </Text>
                <Text className="mt-3 text-sm text-slate-500">
                  0 / {item.words.length}
                </Text>
              </Pressable>
            )}
          />
        )}
      </View>
    </SafeAreaView>
  );
}
