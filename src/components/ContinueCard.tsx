import { useRouter } from "expo-router";
import { ReactNode, useMemo } from "react";
import { Image, Pressable, Text, View } from "react-native";
import { PillButton } from "./PillButton";
import { useGrades } from "../constants/grades";
import { useVocab } from "../constants/words";
import { useT } from "../i18n";
import { WORD_IMAGES } from "../constants/wordImages";
import {
  availableGrades,
  continuePoint,
  knownCountInWords,
} from "../stores/selectors";
import { useAppStore } from "../stores/useAppStore";

/** 스켈레톤과 실제 카드의 높이를 맞춰 저장소 로드 직후 화면이 밀리지 않게 한다 */
const CARD_MIN_HEIGHT = "min-h-[224px]";

function Thumb({ children }: { children: ReactNode }) {
  return (
    <View className="h-[72px] w-[72px] items-center justify-center overflow-hidden rounded-2xl bg-canvas shadow-neu-inset">
      {children}
    </View>
  );
}

/**
 * 홈 화면의 주인공 카드.
 * 마지막으로 보던 단어가 있으면 그 자리로, 없으면 첫 단어로 보낸다.
 */
export function ContinueCard() {
  const router = useRouter();
  const hydrated = useAppStore((s) => s.hydrated);
  const lastStudied = useAppStore((s) => s.lastStudied);
  const entries = useAppStore((s) => s.entries);
  const setActiveGradeId = useAppStore((s) => s.setActiveGradeId);
  const vocab = useVocab();
  const grades = useGrades();
  const t = useT();

  // 아래 계산들은 훅이라 hydrated 분기보다 먼저, 그리고 항상 실행되어야 한다.

  // 단어 색인 조회와 유닛 슬라이스를 렌더마다 돌리지 않는다
  const point = useMemo(
    () => continuePoint(lastStudied, vocab, grades),
    [lastStudied, vocab, grades],
  );

  // 기록이 없을 때 보여줄 첫 단어. 상수에서 나오므로 한 번만 계산한다
  const startPoint = useMemo(() => {
    const grade = availableGrades(grades)[0];
    const first = grade ? vocab.byLevel[grade.id]?.[0] : undefined;
    return grade && first ? { grade, first } : null;
  }, [grades, vocab]);

  // selectors의 continuePoint는 unitKnown을 0으로 주므로 여기서 직접 센다
  const unitKnown = useMemo(() => {
    if (!point) return 0;
    const unitWords =
      vocab.unitsOf(point.gradeId).find((u) => u.unitNo === point.unitNo)
        ?.words ?? [];
    return knownCountInWords(entries, unitWords);
  }, [entries, point, vocab]);

  // 저장소를 읽기 전에 "시작" 카드를 잠깐 보여주면 이어하기 카드로 바뀌며 깜빡인다
  if (!hydrated) {
    return (
      <View
        className={`${CARD_MIN_HEIGHT} rounded-3xl bg-surface shadow-neu-card`}
      />
    );
  }

  if (!point) {
    if (!startPoint) return null;
    const { grade, first } = startPoint;

    const start = () => {
      setActiveGradeId(grade.id);
      router.push(`/study/${first.id}`);
    };

    return (
      <View
        className={`${CARD_MIN_HEIGHT} justify-center rounded-3xl bg-surface p-6 shadow-neu-card`}
      >
        <Pressable
          onPress={start}
          accessibilityRole="button"
          accessibilityLabel={`${grade.short} UNIT 1 ${t("continue.start")}`}
          className="flex-row items-center gap-4 active:opacity-70"
        >
          <Thumb>
            <Text className="text-[32px]">🚀</Text>
          </Thumb>
          <View className="flex-1">
            <Text className="text-[12px] font-bold text-mint">
              {t("continue.start")}
            </Text>
            <Text className="mt-1 text-[20px] font-bold text-ink">
              {grade.short} UNIT 1
            </Text>
            <Text className="mt-1 text-[14px] text-slate-500">
              {first.word}
            </Text>
          </View>
        </Pressable>

        <PillButton
          className="mt-6"
          label={t("continue.start")}
          variant="primary"
          size="lg"
          onPress={start}
        />
      </View>
    );
  }

  const ratio = point.unitLen > 0 ? unitKnown / point.unitLen : 0;
  const source = WORD_IMAGES[point.word.id] || WORD_IMAGES[point.word.word];

  const resume = () => {
    setActiveGradeId(point.gradeId);
    router.push(`/study/${point.word.id}`);
  };

  return (
    <View
      className={`${CARD_MIN_HEIGHT} rounded-3xl bg-surface p-6 shadow-neu-card`}
    >
      <Pressable
        onPress={resume}
        accessibilityRole="button"
        accessibilityLabel={`${point.gradeShort} UNIT ${point.unitNo}, ${point.word.word} ${t("continue.resume")}`}
        className="flex-row items-center gap-4 active:opacity-70"
      >
        <Thumb>
          {source ? (
            <Image
              source={source}
              resizeMode="cover"
              style={{ width: "100%", height: "100%" }}
            />
          ) : (
            <Text className="text-[28px]">🖼️</Text>
          )}
        </Thumb>
        <View className="flex-1">
          <Text className="text-[12px] font-bold text-mint">
            {t("continue.resume")}
          </Text>
          <Text className="mt-1 text-[20px] font-bold text-ink">
            {point.gradeShort} UNIT {point.unitNo}
          </Text>
          <Text numberOfLines={1} className="mt-1 text-[14px] text-slate-500">
            {point.word.word}
          </Text>
        </View>
      </Pressable>

      <View className="mt-5 flex-row items-center gap-3">
        <View className="h-2 flex-1 overflow-hidden rounded-full bg-canvas shadow-neu-inset">
          <View
            className="h-full rounded-full bg-mint"
            style={{ width: `${Math.round(ratio * 100)}%` }}
          />
        </View>
        <Text className="text-[13px] font-bold text-slate-500">
          {unitKnown}/{point.unitLen}
        </Text>
      </View>

      <PillButton
        className="mt-5"
        label={t("continue.title")}
        variant="primary"
        size="lg"
        onPress={resume}
      />
    </View>
  );
}
