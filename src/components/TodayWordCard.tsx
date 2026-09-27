import { Image, Text, View } from "react-native";
import { PressableScale } from "./motion";
import type { Word } from "../constants/words";
import { WORD_IMAGES } from "../constants/wordImages";
import { useT } from "../i18n";
import { PictureIcon } from "./icons";

/**
 * 홈의 오늘의 단어 카드.
 * 볼록한 고리 안에 파인 원을 두고 그 속에 연상 그림을 넣는다. 누르면 그 단어를 공부한다.
 */
export function TodayWordCard({
  word,
  onPress,
}: {
  word: Word;
  onPress: () => void;
}) {
  const t = useT();
  const source = WORD_IMAGES[word.conceptId] ?? WORD_IMAGES[word.word];
  const pos = word.pos?.[0];

  return (
    <PressableScale
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={t("a11y.studyWord", { word: word.word })}
      containerStyle={{ flex: 1 }}
      className="flex-1 items-center justify-center rounded-3xl bg-surface px-4 py-5 shadow-neu-card"
    >
      <View className="h-[108px] w-[108px] rounded-full bg-surface p-2 shadow-neu-sm">
        <View className="flex-1 items-center justify-center overflow-hidden rounded-full bg-[#f5f6f8] shadow-neu-inset">
          {source ? (
            <Image
              source={source}
              resizeMode="cover"
              style={{ width: "100%", height: "100%" }}
            />
          ) : (
            <PictureIcon size={32} color="#cbd5e1" />
          )}
        </View>
      </View>
      <Text className="mt-3.5 text-[11px] font-bold text-mint">
        {t("home.todayWord")}
      </Text>
      <Text
        numberOfLines={1}
        adjustsFontSizeToFit
        className="mt-0.5 text-[22px] font-extrabold text-ink"
      >
        {word.word}
      </Text>
      <Text numberOfLines={1} className="text-[13px] text-slate-500">
        {word.meaning}
        {pos ? ` · ${t(`pos.${pos}` as never)}` : ""}
      </Text>
    </PressableScale>
  );
}
