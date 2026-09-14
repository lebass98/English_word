import { useLocalSearchParams, useRouter } from "expo-router";
import { useMemo } from "react";
import { FlatList, Pressable, Text, View } from "react-native";
import { BackButton } from "../../src/components/BackButton";
import { CheckIcon } from "../../src/components/icons";
import { Screen, ScreenHeader } from "../../src/components/Screen";
import { useGrade } from "../../src/constants/grades";
import { useVocab } from "../../src/constants/words";
import { useT } from "../../src/i18n";
import { imageCoverageOfWords, registeredImageCount } from "../../src/lib/imageDebug";
import {
  knownCountByGrade,
  knownCountInWords,
} from "../../src/stores/selectors";
import { useAppStore } from "../../src/stores/useAppStore";

export default function GradeScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const gradeId = id ?? "";
  const t = useT();
  const vocab = useVocab();
  const grade = useGrade(gradeId);
  // 유닛 목록은 언어 조합마다 캐시되므로 여기서는 참조만 가져온다
  const units = vocab.unitsOf(gradeId);

  const entries = useAppStore((s) => s.entries);
  // 학년 전체 단어(수백~수천 개)를 세므로 기록이 바뀔 때만 다시 센다
  const gradeKnown = useMemo(
    () => knownCountByGrade(entries, vocab, gradeId),
    [entries, vocab, gradeId],
  );

  return (
    <Screen>
      <ScreenHeader>
        <BackButton fallbackHref="/" />
        <View className="flex-1">
          <Text className="text-2xl font-bold text-ink">
            {grade?.label ?? t("level.fallback")}
          </Text>
          {/* 데이터가 없는 학년에서 "0개 단어 · 0개 유닛"을 늘어놓지 않는다 */}
          {units.length > 0 && (
            <Text className="mt-1 text-[13px] text-slate-500">
              전체 {grade?.totalWords ?? 0}개 단어 · {units.length}개 유닛
            </Text>
          )}
          {/* 아직 한 개도 못 외웠으면 0을 보여주지 않는다 */}
          {gradeKnown > 0 ? (
            <Text className="mt-0.5 text-[13px] font-bold text-mint">
              외운 단어 {gradeKnown}개
            </Text>
          ) : null}
        </View>
      </ScreenHeader>

      {units.length === 0 ? (
        <View className="flex-1 items-center justify-center px-6">
          <Text className="text-[13px] text-slate-400">
            {t("level.preparing")}
          </Text>
        </View>
      ) : (
        <FlatList
          data={units}
          keyExtractor={(u) => String(u.unitNo)}
          numColumns={2}
          // 학습 기록이 바뀌면 셀을 다시 그려야 개수·진행바가 따라간다
          // 등록된 그림 수가 바뀌어도 셀을 다시 그려야 그림 미완료 배지가 따라간다
          extraData={[entries, registeredImageCount()]}
          // 2열 카드 간격은 홈 코스 카드와 같은 16px
          columnWrapperClassName="gap-4"
          contentContainerClassName="gap-4 px-6 pb-10 pt-6"
          renderItem={({ item }) => {
            const total = item.words.length;
            const known = knownCountInWords(entries, item.words);
            const done = total > 0 && known === total;
            // 그림 제작 현황(임시). 그림을 전부 채우면 이 줄과 아래 배지를 지운다
            const noImage = imageCoverageOfWords(item.words).missing;

            return (
              <Pressable
                onPress={() => router.push(`/study/${item.words[0].id}`)}
                accessibilityRole="button"
                accessibilityLabel={t("a11y.unitProgress", { unit: item.unitNo, total, known })}
                className="flex-1 rounded-3xl bg-surface p-6 shadow-neu-card active:shadow-neu-pressed"
              >
                <View className="flex-row items-start justify-between">
                  <View>
                    <Text className="text-[12px] font-bold text-mint">
                      UNIT
                    </Text>
                    <Text className="mt-1 text-[26px] font-bold leading-[32px] text-ink">
                      {item.unitNo}
                    </Text>
                  </View>
                  {done ? (
                    <View className="h-5 w-5 items-center justify-center rounded-full bg-canvas shadow-neu-inset">
                      <CheckIcon size={11} color="#0EB582" strokeWidth={3} />
                    </View>
                  ) : null}
                </View>

                <View className="mt-3 h-1.5 w-full rounded-full bg-canvas shadow-neu-inset">
                  <View
                    className="h-full rounded-full bg-mint"
                    style={{ width: `${total ? (known / total) * 100 : 0}%` }}
                  />
                </View>

                <View className="mt-2 flex-row items-baseline">
                  <Text
                    className={`text-[13px] font-bold ${
                      done ? "text-mint" : "text-slate-700"
                    }`}
                  >
                    {known}
                  </Text>
                  <Text className="text-[13px] text-slate-500">
                    {" "}
                    / {total}
                  </Text>
                </View>

                {/* 그림 제작 현황(임시). 다 그린 유닛은 초록 표시로 바뀐다 */}
                <View
                  className={`mt-1.5 self-start rounded-full px-2 py-0.5 ${
                    noImage > 0 ? "bg-canvas shadow-neu-inset" : "bg-[#dcf2ea]"
                  }`}
                >
                  <Text
                    className={`text-[10px] font-bold ${
                      noImage > 0 ? "text-amber-600" : "text-mint-dark"
                    }`}
                  >
                    {noImage > 0 ? `🖼 ${noImage}개 미완료` : "🖼 그림 완료"}
                  </Text>
                </View>
              </Pressable>
            );
          }}
        />
      )}
    </Screen>
  );
}
