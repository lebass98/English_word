import { useRouter } from "expo-router";
import { useMemo, useState } from "react";
import { FlatList, Image, Pressable, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { BackButton } from "../src/components/BackButton";
import { BottomNav } from "../src/components/BottomNav";
import { PillButton } from "../src/components/PillButton";
import { StarIcon } from "../src/components/icons";
import { useVocab, type Word } from "../src/constants/words";
import { WORD_IMAGES } from "../src/constants/wordImages";
import { useT, type StringKey } from "../src/i18n";
import {
  STARS_BY_STATUS,
  useAppStore,
  type WordStatus,
} from "../src/stores/useAppStore";

type Filter = "known" | "unsure" | "saved" | "all";

const FILTERS: { key: Filter; labelKey: StringKey }[] = [
  { key: "known", labelKey: "wordbook.known" },
  { key: "unsure", labelKey: "wordbook.unsure" },
  { key: "saved", labelKey: "wordbook.saved" },
  { key: "all", labelKey: "wordbook.all" },
];

/** 기록은 있는데 이 분류만 비었을 때 보여줄 안내 */
const EMPTY_BY_FILTER: Record<Filter, StringKey> = {
  known: "wordbook.noKnown",
  unsure: "wordbook.noUnsure",
  saved: "wordbook.noSaved",
  all: "wordbook.noRecords",
};

/** 숙련도 별은 항상 3칸. 채운 개수만 상태에 따라 달라진다 */
const STAR_SLOTS = [0, 1, 2];

interface Row {
  word: Word;
  status: WordStatus;
}

export default function WordbookScreen() {
  const router = useRouter();
  const hydrated = useAppStore((s) => s.hydrated);
  const entries = useAppStore((s) => s.entries);
  const saved = useAppStore((s) => s.saved);
  const vocab = useVocab();
  const t = useT();

  // 헷갈리는 단어가 다시 볼 이유가 가장 큰 목록이라 기본값으로 둔다
  const [filter, setFilter] = useState<Filter>("unsure");

  // entries는 수천 개까지 늘 수 있어 필터·정렬을 매 렌더마다 돌리지 않는다
  const rows = useMemo<Row[]>(() => {
    // "저장한 단어"는 학습 판정과 별개라 담은 시각 기준으로 따로 모은다.
    // "전체"에서는 판정한 단어와 담아 둔 단어를 한데 놓고 최근 순으로 섞는다.
    const at: [string, string][] =
      filter === "saved"
        ? Object.entries(saved)
        : filter === "all"
          ? Object.entries({
              ...saved,
              ...Object.fromEntries(
                Object.entries(entries).map(([id, e]) => [id, e.updatedAt]),
              ),
            })
          : Object.entries(entries)
              .filter(([, e]) => e.status === filter)
              .map(([id, e]) => [id, e.updatedAt]);

    const out: Row[] = [];
    for (const [wordId] of at.sort((a, b) => b[1].localeCompare(a[1]))) {
      const found = vocab.find(wordId);
      // 단어 데이터가 바뀌어 사라진 id는 조용히 건너뛴다
      if (!found) continue;
      out.push({
        word: found.word,
        // 담기만 하고 아직 판정하지 않은 단어는 별이 비어 있다
        status: entries[wordId]?.status ?? "unseen",
      });
    }
    return out;
  }, [entries, saved, filter, vocab]);

  // 기록이 아예 없는 것과 이 분류만 빈 것은 안내가 달라야 한다
  const hasAnyEntry = useMemo(
    () => Object.keys(entries).length > 0 || Object.keys(saved).length > 0,
    [entries, saved],
  );

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View className="w-full flex-1">
        <View className="flex-row items-center gap-4 px-6 pb-4 pt-8">
          <BackButton fallbackHref="/" />
          <Text className="text-2xl font-bold text-ink">{t("wordbook.title")}</Text>
        </View>

        {/* 기록이 하나도 없으면 고를 것이 없으므로 분류 버튼을 감춘다 */}
        {(!hydrated || hasAnyEntry) && (
          <View className="flex-row flex-wrap gap-2 px-6 pb-2">
            {FILTERS.map((f) => (
              <PillButton
                key={f.key}
                label={t(f.labelKey)}
                size="lg"
                variant={filter === f.key ? "inset" : "default"}
                onPress={() => setFilter(f.key)}
              />
            ))}
          </View>
        )}

        {rows.length > 0 ? (
          <FlatList
            data={rows}
            keyExtractor={(row) => row.word.id}
            contentContainerClassName="gap-3 px-6 pb-32 pt-4"
            showsVerticalScrollIndicator={false}
            renderItem={({ item }) => (
              <WordRow
                row={item}
                onPress={() => router.push(`/study/${item.word.id}`)}
              />
            )}
          />
        ) : (
          <View className="flex-1 items-center justify-center px-6 pb-32">
            {/* 저장소를 읽는 중에는 "기록 없음"이 잘못 보이므로 비워 둔다 */}
            {hydrated &&
              (hasAnyEntry ? (
                <Text className="text-[13px] text-slate-400">
                  {t(EMPTY_BY_FILTER[filter])}
                </Text>
              ) : (
                <View className="w-full max-w-[320px] items-center rounded-3xl bg-surface px-6 py-8 shadow-neu-card">
                  <Text className="text-[32px]">📖</Text>
                  <Text className="mt-3 text-[15px] font-bold text-ink">
                    {t("wordbook.emptyTitle")}
                  </Text>
                  <Text className="mt-1 text-center text-[13px] text-slate-500">
                    {t("wordbook.emptyDesc")}
                  </Text>
                  <PillButton
                    className="mt-5"
                    label={t("wordbook.goStudy")}
                    variant="primary"
                    onPress={() => router.replace("/")}
                  />
                </View>
              ))}
          </View>
        )}
      </View>

      <BottomNav />
    </SafeAreaView>
  );
}

function WordRow({ row, onPress }: { row: Row; onPress: () => void }) {
  const t = useT();
  const { word, status } = row;
  const source = WORD_IMAGES[word.conceptId] ?? WORD_IMAGES[word.word];
  const filled = STARS_BY_STATUS[status];

  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={t("a11y.studyWord", { word: word.word })}
      className="flex-row items-center gap-4 rounded-3xl bg-surface p-4 shadow-neu-card active:shadow-neu-pressed"
    >
      <View className="h-14 w-14 items-center justify-center overflow-hidden rounded-2xl bg-canvas shadow-neu-inset">
        {source ? (
          <Image
            source={source}
            resizeMode="cover"
            style={{ width: "100%", height: "100%" }}
          />
        ) : (
          <Text className="text-[20px]">🖼️</Text>
        )}
      </View>

      <View className="flex-1">
        <Text className="text-[16px] font-bold text-ink">{word.word}</Text>
        <Text numberOfLines={1} className="mt-0.5 text-[13px] text-slate-500">
          {word.meaning}
        </Text>
      </View>

      <View className="flex-row items-center gap-0.5">
        {STAR_SLOTS.map((i) => (
          <StarIcon
            key={i}
            size={14}
            color={i < filled ? "#fbbf24" : "#cbd5e1"}
          />
        ))}
      </View>
    </Pressable>
  );
}
