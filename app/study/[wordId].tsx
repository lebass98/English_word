import { useLocalSearchParams, useRouter } from "expo-router";
import { useState } from "react";
import { Image, Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { PillButton } from "../../src/components/PillButton";
import { GRADES } from "../../src/constants/grades";
import { UNIT_SIZE, findWord } from "../../src/constants/words";
import { WORD_IMAGES } from "../../src/constants/wordImages";

export default function StudyScreen() {
  const { wordId } = useLocalSearchParams<{ wordId: string }>();
  const router = useRouter();

  const [showMeaning, setShowMeaning] = useState(true);
  const [bookmarked, setBookmarked] = useState(false);
  const [reverseMode, setReverseMode] = useState(false);

  const found = findWord(wordId ?? "");
  if (!found) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-canvas">
        <Text className="text-base text-slate-500">
          단어를 찾을 수 없습니다
        </Text>
        <PillButton
          className="mt-6"
          label="← 돌아가기"
          onPress={() => router.back()}
        />
      </SafeAreaView>
    );
  }

  const { gradeId, words, index, word } = found;
  const gradeLabel = GRADES.find((g) => g.id === gradeId)?.label ?? "";
  const unitNo = Math.floor(index / UNIT_SIZE) + 1;
  const posInUnit = (index % UNIT_SIZE) + 1;
  const unitLen = Math.min(UNIT_SIZE, words.length - (unitNo - 1) * UNIT_SIZE);
  const localImage = WORD_IMAGES[word.id] || WORD_IMAGES[word.word];

  const goTo = (i: number) => {
    if (i >= 0 && i < words.length) {
      router.setParams({ wordId: words[i].id });
      setShowMeaning(true);
      setBookmarked(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <ScrollView
        className="flex-1"
        contentContainerClassName="w-full px-5 pb-14 lg:mx-auto lg:max-w-2xl"
      >
        {/* 상단 세션 바 */}
        <View className="flex-row items-center justify-between pt-3">
          <View className="flex-row items-center gap-2">
            <Pressable
              onPress={() => router.back()}
              className="h-11 w-11 items-center justify-center rounded-full bg-surface shadow-neu-sm active:shadow-neu-pressed"
            >
              <Text className="text-xl text-slate-700">‹</Text>
            </Pressable>
            <View className="rounded-full bg-surface px-4 py-1.5 shadow-neu-sm">
              <Text className="text-sm font-semibold text-slate-700">
                {gradeLabel} UNIT {unitNo}
              </Text>
            </View>
          </View>
          <View className="flex-row items-center gap-1 rounded-full bg-surface px-4 py-1.5 shadow-neu-sm">
            <Text className="text-sm font-bold text-mint">{posInUnit}</Text>
            <Text className="text-sm text-slate-400">/ {unitLen}</Text>
          </View>
        </View>

        {/* 진행률 바 */}
        <View className="mt-5 h-2 w-full overflow-hidden rounded-full bg-canvas shadow-neu-inset">
          <View
            className="h-full rounded-full bg-mint"
            style={{ width: `${(posInUnit / unitLen) * 100}%` }}
          />
        </View>

        {/* 메인 플래시카드 */}
        <View className="mt-5 rounded-3xl bg-surface p-6 shadow-neu">
          {/* 품사 · 발음기호 · 북마크 */}
          <View className="flex-row items-center justify-between">
            <View className="flex-row items-center gap-3">
              {word.pos && (
                <View className="rounded-full bg-[#e9e6f8] px-3 py-1 shadow-neu-sm">
                  <Text className="text-xs font-bold text-indigo-700">
                    {word.pos}
                  </Text>
                </View>
              )}
              {word.phonetic && (
                <Text className="text-sm font-medium text-slate-500">
                  {word.phonetic}
                </Text>
              )}
            </View>
            <Pressable
              onPress={() => setBookmarked((b) => !b)}
              className={`h-11 w-11 items-center justify-center rounded-full ${
                bookmarked
                  ? "bg-canvas shadow-neu-inset"
                  : "bg-surface shadow-neu-sm"
              } active:scale-90`}
            >
              <Text className="text-base">{bookmarked ? "🔖" : "📑"}</Text>
            </Pressable>
          </View>

          {/* 단어 + 발음 듣기 */}
          <View className="mt-5 flex-row items-center justify-between">
            <Text className="text-4xl font-bold tracking-tight text-ink">
              {word.word}
            </Text>
            <Pressable className="flex-row items-center gap-2 rounded-full bg-surface px-5 py-2 shadow-neu-sm active:shadow-neu-pressed">
              <Text className="text-base">🔊</Text>
              <View className="h-3 flex-row items-center gap-0.5">
                <View className="h-1.5 w-0.5 rounded-full bg-mint" />
                <View className="h-3 w-0.5 rounded-full bg-mint" />
                <View className="h-2 w-0.5 rounded-full bg-mint" />
              </View>
            </Pressable>
          </View>

          {/* 연상 이미지 (준비 전엔 자리만) */}
          <View className="mt-6 aspect-square w-full items-center justify-center overflow-hidden rounded-2xl bg-canvas shadow-neu-inset">
            {localImage ? (
              <Image
                source={localImage}
                style={{ width: "100%", height: "100%", resizeMode: "contain" }}
              />
            ) : (
              <View className="items-center gap-3">
                <Text className="text-5xl">🖼️</Text>
                <Text className="text-base text-slate-400">
                  연상 이미지 준비 중
                </Text>
              </View>
            )}
          </View>

          {/* 한국어 뜻풀이 (가리기/보기 토글) */}
          <View className="mt-6 rounded-2xl bg-canvas p-5 shadow-neu-inset">
            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center gap-2">
                <View className="h-2 w-2 rounded-full bg-mint" />
                <Text className="text-sm font-semibold text-slate-600">
                  한국어 뜻풀이
                </Text>
              </View>
              <Pressable onPress={() => setShowMeaning((v) => !v)}>
                <Text className="text-sm font-bold text-mint">
                  {showMeaning ? "가리기 ⌃" : "뜻 보기 ⌄"}
                </Text>
              </Pressable>
            </View>

            {showMeaning && (
              <View className="mt-4 gap-3">
                <Text className="text-xl font-bold text-slate-900">
                  {word.meaning}
                </Text>
                {word.example && (
                  <View className="rounded-xl bg-surface p-4 shadow-neu-sm">
                    <Text className="text-base font-medium leading-relaxed text-slate-800">
                      &ldquo;{word.example}&rdquo;
                    </Text>
                    {word.exampleKo && (
                      <Text className="mt-2 text-base leading-snug text-slate-500">
                        {word.exampleKo}
                      </Text>
                    )}
                  </View>
                )}
              </View>
            )}
          </View>

          {/* 연상 암기 팁 */}
          {word.mnemonic && (
            <View className="mt-6 flex-row items-start gap-3 rounded-xl bg-[#dcf2ea] px-5 py-4 shadow-neu-sm">
              <Text className="mt-0.5 text-base">💡</Text>
              <Text className="flex-1 text-base leading-snug text-slate-700">
                <Text className="font-bold text-slate-900">연상 암기 팁: </Text>
                {word.mnemonic}
              </Text>
            </View>
          )}
        </View>

        {/* 이전/거꾸로 학습/다음 */}
        <View className="mt-5 flex-row items-center justify-between">
          <PillButton
            size="sm"
            label="← 이전"
            onPress={() => goTo(index - 1)}
          />
          <PillButton
            size="sm"
            variant={reverseMode ? "inset" : "default"}
            label={`⇄ 거꾸로 ${reverseMode ? "ON" : "OFF"}`}
            onPress={() => setReverseMode((v) => !v)}
          />
          <PillButton
            size="sm"
            label="다음 →"
            onPress={() => goTo(index + 1)}
          />
        </View>

        {/* 학습 평가 버튼 */}
        <View className="mt-4 flex-row gap-3">
          <PillButton
            size="lg"
            className="flex-1"
            label="아직 헷갈려요"
            left={<Text className="text-lg">↩️</Text>}
            onPress={() => goTo(index + 1)}
          />
          <PillButton
            size="lg"
            variant="primary"
            className="flex-1"
            label="외웠어요!"
            left={<Text className="text-lg">✅</Text>}
            onPress={() => goTo(index + 1)}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
