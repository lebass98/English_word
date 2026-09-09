import { useLocalSearchParams, useRouter } from "expo-router";
import { useState } from "react";
import { Image, Pressable, ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { PillButton } from "../../src/components/PillButton";
import { SAMPLE_WORDS } from "../../src/constants/sampleWords";
import { WORD_IMAGES } from "../../src/constants/wordImages";

export default function StudyScreen() {
  const { wordId } = useLocalSearchParams<{ wordId: string }>();
  const router = useRouter();
  const word = SAMPLE_WORDS.find((w) => w.id === wordId) ?? SAMPLE_WORDS[0];

  const [showMeaning, setShowMeaning] = useState(true);
  const [bookmarked, setBookmarked] = useState(false);
  const [reverseMode, setReverseMode] = useState(false);

  const progress = 0.4; // 세션 진행률 (데이터 연결 전 임시값)

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <ScrollView
        className="flex-1"
        contentContainerClassName="w-full px-5 pb-14 lg:mx-auto lg:max-w-2xl"
      >
        {/* 상단 세션 바: 덱 뱃지 · 진행 카운트 · 연속 학습 */}
        <View className="flex-row items-center justify-between pt-3">
          <View className="flex-row items-center gap-2">
            <View className="flex-row items-center gap-1 rounded-full bg-surface px-5 py-2 shadow-neu-sm">
              <Text className="text-base font-semibold text-slate-700">
                🎓 중고등 필수 DAY 1
              </Text>
            </View>
            <View className="flex-row items-center gap-1 rounded-full bg-surface px-5 py-2 shadow-neu-sm">
              <Text className="text-base font-bold text-mint">4</Text>
              <Text className="text-base text-slate-400">/ 10</Text>
            </View>
          </View>
          <View className="flex-row items-center gap-1 rounded-full bg-surface px-5 py-2 shadow-neu-sm">
            <Text className="text-base">🔥</Text>
            <Text className="text-base font-bold text-slate-800">7일 연속</Text>
          </View>
        </View>

        {/* 진행률 바 */}
        <View className="mt-5 h-2 w-full overflow-hidden rounded-full bg-canvas shadow-neu-inset">
          <View
            className="h-full rounded-full bg-mint"
            style={{ width: `${progress * 100}%` }}
          />
        </View>

        {/* 메인 플래시카드 */}
        <View className="mt-5 rounded-3xl bg-surface p-6 shadow-neu">
          {/* 품사 · 발음기호 · 북마크 */}
          <View className="flex-row items-center justify-between">
            <View className="flex-row items-center gap-3">
              <View className="rounded-full border border-purple-100 bg-purple-50 px-2.5 py-0.5">
                <Text className="text-base font-bold tracking-wider text-purple-700">
                  {word.pos}
                </Text>
              </View>
              <Text className="text-base font-medium text-slate-500">
                {word.phonetic}
              </Text>
            </View>
            <Pressable
              onPress={() => setBookmarked((b) => !b)}
              className={`h-8 w-8 items-center justify-center rounded-full border ${
                bookmarked
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-transparent bg-surface shadow-neu-sm"
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
            <Pressable className="flex-row items-center gap-2 rounded-full bg-surface px-5 py-2 shadow-neu-sm active:scale-95">
              <Text className="text-base">🔊</Text>
              <View className="h-3 flex-row items-center gap-0.5">
                <View className="h-1.5 w-0.5 rounded-full bg-mint" />
                <View className="h-3 w-0.5 rounded-full bg-mint" />
                <View className="h-2 w-0.5 rounded-full bg-mint" />
              </View>
            </Pressable>
          </View>

          {/* 연상 이미지 */}
          <View className="mt-6 aspect-square w-full overflow-hidden rounded-2xl bg-white shadow-neu-sm">
            <Image
              source={WORD_IMAGES[word.id] ?? { uri: word.imageUrl }}
              style={{ width: "100%", height: "100%", resizeMode: "contain" }}
            />
            <View className="absolute bottom-2.5 right-2.5 flex-row items-center gap-1 rounded-full border border-slate-200 bg-white/90 px-2.5 py-0.5">
              <Text className="text-base font-semibold text-slate-600">
                💭 {word.imageTag}
              </Text>
            </View>
          </View>

          {/* 한국어 뜻풀이 (가리기/보기 토글) */}
          <View className="mt-6 rounded-2xl bg-canvas p-5 shadow-neu-inset">
            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center gap-2">
                <View className="h-2 w-2 rounded-full bg-mint" />
                <Text className="text-base font-semibold text-slate-600">
                  한국어 뜻풀이
                </Text>
              </View>
              <Pressable onPress={() => setShowMeaning((v) => !v)}>
                <Text className="text-base font-bold text-mint">
                  {showMeaning ? "가리기 ⌃" : "뜻 보기 ⌄"}
                </Text>
              </Pressable>
            </View>

            {showMeaning && (
              <View className="mt-4 gap-3">
                <View className="flex-row items-baseline gap-3">
                  <Text className="text-xl font-bold text-slate-900">
                    {word.meanings.join(", ")}
                  </Text>
                  {word.subMeaning && (
                    <Text className="text-base font-medium text-slate-500">
                      / {word.subMeaning}
                    </Text>
                  )}
                </View>
                <View className="rounded-xl bg-surface p-4 shadow-neu-sm">
                  <Text className="text-base font-medium leading-relaxed text-slate-800">
                    &ldquo;He was found{" "}
                    <Text className="font-bold text-mint">innocent</Text> of all
                    charges.&rdquo;
                  </Text>
                  <Text className="mt-2 text-base leading-snug text-slate-500">
                    {word.exampleKo}
                  </Text>
                </View>
              </View>
            )}
          </View>

          {/* 연상 암기 팁 */}
          <View className="mt-6 flex-row items-start gap-3 rounded-xl border border-emerald-100 bg-emerald-50 px-5 py-4">
            <Text className="mt-0.5 text-base">💡</Text>
            <Text className="flex-1 text-base leading-snug text-slate-700">
              <Text className="font-bold text-slate-900">연상 암기 팁: </Text>
              {word.mnemonic}
            </Text>
          </View>
        </View>

        {/* 이전/거꾸로 학습/다음 */}
        <View className="mt-5 flex-row items-center justify-between">
          <PillButton
            size="sm"
            label="← 이전 단어"
            onPress={() => router.back()}
          />
          <PillButton
            size="sm"
            variant={reverseMode ? "inset" : "default"}
            label={`⇄ 거꾸로 학습 ${reverseMode ? "ON" : "OFF"}`}
            onPress={() => setReverseMode((v) => !v)}
          />
          <PillButton size="sm" label="다음 단어 →" />
        </View>

        {/* 학습 평가 버튼 (간격 반복) */}
        <View className="mt-4 flex-row gap-3">
          <PillButton
            size="lg"
            className="flex-1"
            label="아직 헷갈려요"
            left={<Text className="text-lg">↩️</Text>}
          />
          <PillButton
            size="lg"
            variant="primary"
            className="flex-1"
            label="외웠어요!"
            left={<Text className="text-lg">✅</Text>}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
