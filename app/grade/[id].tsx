import { useLocalSearchParams, useRouter } from "expo-router";
import { FlatList, Pressable, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { GRADES } from "../../src/constants/grades";
import { UNIT_SIZE, unitsOf } from "../../src/constants/words";

export default function GradeScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const grade = GRADES.find((g) => g.id === id);
  const units = unitsOf(id ?? "");

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View className="w-full flex-1 px-6 lg:mx-auto lg:max-w-3xl">
        <View className="flex-row items-center gap-4 py-5">
          <Pressable
            onPress={() => router.back()}
            className="h-12 w-12 items-center justify-center rounded-full bg-surface shadow-neu-sm active:shadow-neu-pressed"
          >
            <Text className="text-xl text-slate-700">‹</Text>
          </Pressable>
          <View>
            <Text className="text-2xl font-bold text-ink">
              {grade?.label ?? "학년"}
            </Text>
            <Text className="mt-1 text-base text-slate-500">
              전체 {grade?.totalWords ?? 0}개 단어 · {units.length}개 유닛
            </Text>
          </View>
        </View>

        {units.length === 0 ? (
          <View className="flex-1 items-center justify-center">
            <Text className="text-base text-slate-400">
              단어 데이터 준비 중입니다
            </Text>
          </View>
        ) : (
          <FlatList
            data={units}
            keyExtractor={(u) => String(u.unitNo)}
            numColumns={2}
            columnWrapperClassName="gap-6"
            contentContainerClassName="gap-6 pb-10 pt-2"
            renderItem={({ item }) => (
              <Pressable
                onPress={() => router.push(`/study/${item.words[0].id}`)}
                className="flex-1 rounded-3xl bg-surface p-6 shadow-neu active:shadow-neu-pressed"
              >
                <Text className="text-base font-bold text-mint">UNIT</Text>
                <Text className="mt-1 text-3xl font-bold text-ink">
                  {item.unitNo}
                </Text>
                <Text className="mt-3 text-base text-slate-500">
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
