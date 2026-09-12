import { useLocalSearchParams, useRouter } from "expo-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Animated,
  Easing,
  Image,
  PanResponder,
  Pressable,
  ScrollView,
  Text,
  useWindowDimensions,
  View,
  Platform,
} from "react-native";
import { BlurView } from "expo-blur";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  AgainIcon,
  BookmarkIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronUpIcon,
  PauseIcon,
  PlayIcon,
  SpeakerIcon,
} from "../../src/components/icons";
import { BackButton } from "../../src/components/BackButton";
import { LabeledSection } from "../../src/components/LabeledSection";
import { PillButton } from "../../src/components/PillButton";
import { SynonymList } from "../../src/components/SynonymList";
import { gradesOf } from "../../src/constants/grades";
import {
  UNIT_SIZE,
  useVocabForWordId,
  type Word,
} from "../../src/constants/words";
import {
  studyLangOfWordId,
  studyLanguageOf,
} from "../../src/constants/languages";
import { useT } from "../../src/i18n";
import { WORD_IMAGES } from "../../src/constants/wordImages";
import { speakWord, stopSpeaking } from "../../src/lib/speech";
import { useAppStore, type WordStatus } from "../../src/stores/useAppStore";

/** 자동 넘김 간격 (초) */
const AUTO_ADVANCE_SEC = 15;

export default function StudyScreen() {
  const { wordId } = useLocalSearchParams<{ wordId: string }>();
  const router = useRouter();

  const t = useT();
  // 지금 설정이 아니라 단어 id 에 적힌 언어에서 찾는다
  const vocab = useVocabForWordId(wordId ?? "");
  const found = vocab.find(wordId ?? "");

  const goTo = useCallback(
    (id?: string) => {
      if (id) router.setParams({ wordId: id });
    },
    [router],
  );

  if (!found) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-canvas">
        <Text className="text-[14px] text-slate-500">
          {t("study.notFound")}
        </Text>
        <PillButton
          className="mt-6"
          label={t("common.backArrow")}
          onPress={() => router.back()}
        />
      </SafeAreaView>
    );
  }

  const { levelId: gradeId, words, index, word } = found;

  return (
    // key로 단어마다 새로 마운트해서 뜻 가리기·타이머 상태가 자동 초기화되게 한다.
    <StudyCard
      key={word.id}
      word={word}
      gradeId={gradeId}
      index={index}
      total={words.length}
      prev={words[index - 1]}
      next={words[index + 1]}
      onNavigate={goTo}
      onBack={() => {
        // 주소로 바로 들어오거나 새로고침한 경우엔 되돌아갈 기록이 없다.
        // 그때는 해당 학년의 유닛 목록으로 보낸다.
        if (router.canGoBack()) router.back();
        else router.replace(`/grade/${gradeId}`);
      }}
    />
  );
}

/**
 * 이미지 패널 한 칸. offset 만큼 좌우로 떨어뜨려 두면
 * 스와이프할 때 옆 그림이 자연스럽게 따라 들어온다.
 */
function WordImage({ word, offset = 0 }: { word: Word; offset?: number }) {
  const t = useT();
  const source = WORD_IMAGES[word.conceptId] ?? WORD_IMAGES[word.word];
  return (
    <View
      style={{
        position: "absolute",
        top: 0,
        bottom: 0,
        left: offset,
        right: -offset,
      }}
    >
      {source ? (
        <Image
          source={source}
          resizeMode="cover"
          style={{ width: "100%", height: "100%" }}
        />
      ) : (
        <View className="flex-1 items-center justify-center gap-3 bg-canvas">
          <Text className="text-[40px]">🖼️</Text>
          <Text className="text-[13px] text-slate-400">
            {t("study.imagePreparing")}
          </Text>
        </View>
      )}
    </View>
  );
}

interface StudyCardProps {
  word: Word;
  gradeId: string;
  index: number;
  total: number;
  /** 앞·뒤 단어. 스와이프할 때 옆 그림을 미리 보여주는 데 쓴다 */
  prev?: Word;
  next?: Word;
  onNavigate: (id?: string) => void;
  onBack: () => void;
}

function StudyCard({
  word,
  gradeId,
  index,
  total,
  prev,
  next,
  onNavigate,
  onBack,
}: StudyCardProps) {
  const prevId = prev?.id;
  const nextId = next?.id;
  const autoAdvance = useAppStore((s) => s.autoAdvance);
  const setAutoAdvance = useAppStore((s) => s.setAutoAdvance);
  const recordStudy = useAppStore((s) => s.recordStudy);
  const markSeen = useAppStore((s) => s.markSeen);
  const toggleSaved = useAppStore((s) => s.toggleSaved);
  // 이 단어가 단어장에 담겨 있는지. saved 전체를 구독하면 다른 단어를 담을 때도 다시 그려진다
  const isSaved = useAppStore((s) => Boolean(s.saved[word.id]));
  const t = useT();
  const uiLang = useAppStore((s) => s.uiLang);
  const speechCode = studyLanguageOf(studyLangOfWordId(word.id)).speechCode;

  const { width: screenWidth } = useWindowDimensions();

  /** 정답(뜻·예문)을 보여줄지 여부. 끄면 뜻까지 통째로 가려진다 */
  const [showAnswer, setShowAnswer] = useState(true);
  const [speaking, setSpeaking] = useState(false);
  /** 자동 넘김 진행도 0 → 1. 애니메이션 값이라 매 프레임 부드럽게 움직인다.
      한 번만 만들어 두고 계속 같은 값을 쓴다 */
  const [progress] = useState(() => new Animated.Value(0));

  const advance = useCallback(() => onNavigate(nextId), [onNavigate, nextId]);

  /** 이미지를 좌우로 밀어서 단어를 넘기는 스와이프.
      그림만 손가락을 따라 흐르고, 충분히 밀면 옆 그림이 자리를 넘겨받으며 단어가 바뀐다 */
  const [panelW, setPanelW] = useState(0);
  const [dragX] = useState(() => new Animated.Value(0));
  const swipe = useMemo(() => {
    // 웹에서는 네이티브 드라이버를 쓸 수 없다
    const useNativeDriver = Platform.OS !== "web";
    const springBack = () =>
      Animated.spring(dragX, {
        toValue: 0,
        bounciness: 6,
        useNativeDriver,
      }).start();

    return PanResponder.create({
      // 세로 스크롤을 방해하지 않도록 가로로 확실히 움직였을 때만 잡는다
      onMoveShouldSetPanResponder: (_, g) =>
        Math.abs(g.dx) > 12 && Math.abs(g.dx) > Math.abs(g.dy) * 1.5,
      onPanResponderMove: (_, g) => {
        // 첫 단어/마지막 단어 쪽으로는 조금만 끌리게 해 더 갈 곳이 없음을 알린다
        const blocked = (g.dx > 0 && !prevId) || (g.dx < 0 && !nextId);
        dragX.setValue(blocked ? g.dx * 0.18 : g.dx);
      },
      onPanResponderRelease: (_, g) => {
        // 패널 너비의 4분의 1쯤 밀었거나 빠르게 튕겼으면 넘긴다
        const enough =
          Math.abs(g.dx) > (panelW || 200) * 0.26 || Math.abs(g.vx) > 0.35;
        const target = g.dx < 0 ? nextId : prevId;
        if (!enough || !target) return springBack();

        // 옆 그림이 자리를 다 채운 다음에 단어를 바꾼다.
        // 카드가 새로 마운트되면서 위치는 저절로 초기화된다
        Animated.timing(dragX, {
          toValue: g.dx < 0 ? -panelW : panelW,
          duration: 180,
          easing: Easing.out(Easing.quad),
          useNativeDriver,
        }).start(({ finished }) => {
          if (finished) onNavigate(target);
          else springBack();
        });
      },
      onPanResponderTerminate: springBack,
    });
  }, [dragX, panelW, prevId, nextId, onNavigate]);

  // 자동 넘김 타이머.
  // 예전에는 200ms마다 상태를 바꿔 바를 다시 그렸는데, 그 간격만큼 계단처럼 끊겨 보였다.
  // 지금은 15초 동안 0에서 1까지 일정한 속도로 흐르는 애니메이션 하나로 처리해
  // 왼쪽에서 오른쪽으로 끊김 없이 채워진다.
  useEffect(() => {
    progress.setValue(0);
    if (!autoAdvance) return;

    const animation = Animated.timing(progress, {
      toValue: 1,
      duration: AUTO_ADVANCE_SEC * 1000,
      easing: Easing.linear,
      // 너비는 레이아웃 속성이라 네이티브 드라이버를 쓸 수 없다
      useNativeDriver: false,
    });
    animation.start(({ finished }) => {
      if (finished) advance();
    });

    return () => animation.stop();
  }, [autoAdvance, advance, progress]);

  // 단어가 바뀌면 발음을 자동으로 한 번 들려준다.
  // (단어마다 key로 새로 마운트되므로 단어당 정확히 한 번 실행된다)
  // 화면을 벗어날 때는 재생 중인 음성을 멈춘다.
  useEffect(() => {
    speakWord(word.word, {
      lang: speechCode,
      onStart: () => setSpeaking(true),
      onDone: () => setSpeaking(false),
    });
    return stopSpeaking;
  }, [word.word, speechCode]);

  // 이어하기 지점과 "오늘 본 단어"는 화면에 뜬 시점에 기록한다.
  // 판정 버튼에서 기록하면 보다 만 단어와 자동 넘김으로 지나간 단어가 빠진다.
  useEffect(() => {
    markSeen(word.id, gradeId);
  }, [word.id, gradeId, markSeen]);

  // 헤더는 자리가 좁으므로 짧은 이름을 쓴다 (중학 2학년 → 중2)
  // 단계 이름도 지금 설정이 아니라 이 단어가 속한 언어에서 가져온다
  const gradeLabel =
    gradesOf(studyLangOfWordId(word.id), uiLang).find((g) => g.id === gradeId)
      ?.short ?? "";
  const unitNo = Math.floor(index / UNIT_SIZE) + 1;
  const posInUnit = (index % UNIT_SIZE) + 1;
  // 마지막 유닛은 20개보다 적을 수 있다.
  const unitLen = Math.min(UNIT_SIZE, total - (unitNo - 1) * UNIT_SIZE);
  const hasSynonyms = (word.synonyms?.length ?? 0) > 0;

  // 단어가 길어도 두 줄로 넘기지 않고 글자 크기를 줄여 한 줄에 담는다.
  // 단어는 이미지 패널 위에 얹히므로 그 안쪽 폭을 기준으로 계산한다.
  // 화면 좌우 여백(48) + 카드 안쪽 여백(48) + 겹침 영역 좌우 여백(32)
  //   + 스피커 버튼(44) + 버튼과의 간격(12)
  const wordAreaWidth = Math.max(110, screenWidth - 184);
  // 굵은 글씨는 한 글자가 글자 크기의 약 0.58배 너비를 차지한다
  // 최대 크기는 31px (24px 이 너무 작아 30% 키웠다)
  const wordFontSize = Math.max(
    10,
    Math.min(31, Math.floor(wordAreaWidth / (word.word.length * 0.58))),
  );


  const handleSpeak = () => {
    speakWord(word.word, {
      lang: speechCode,
      onStart: () => setSpeaking(true),
      onDone: () => setSpeaking(false),
    });
  };

  const decide = (next: WordStatus) => {
    recordStudy(word.id, next);
    onNavigate(nextId);
  };

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View className="w-full flex-1">
        {/* ── 상단 바: 뒤로 · 유닛/진행 · 자동 넘김 ──────────── */}
        <View className="flex-row items-center justify-between px-6 pt-8 pb-3">
          <BackButton onPress={onBack} />

          {/* 유닛과 진행 개수를 하나의 알약에 담는다 */}
          <View className="relative mx-2 h-12 flex-1 flex-row items-center justify-center gap-2 overflow-hidden rounded-full bg-surface px-4 shadow-neu-sm">
            <Text
              numberOfLines={1}
              className="text-[14px] font-bold leading-[15px] tracking-tight text-slate-700"
            >
              {gradeLabel} UNIT {unitNo}
            </Text>
            <Text className="text-[14px] leading-[15px] text-slate-300">·</Text>
            <View className="flex-row items-center">
              <Text className="text-[13px] font-extrabold leading-[15px] text-emerald-500">
                {posInUnit}
              </Text>
              <Text className="text-[13px] font-medium leading-[15px] text-slate-400">
                /{unitLen}
              </Text>
            </View>

            {/* 유닛 진행률: 알약 안쪽 하단에 겹쳐서 표시한다 (높이 3px) */}
            <View className="absolute inset-x-0 bottom-0 h-[3px] bg-slate-200">
              <View
                className="h-full bg-emerald-500"
                style={{ width: `${(posInUnit / unitLen) * 100}%` }}
              />
            </View>
          </View>

          {/* 자동 넘김 켜기/끄기 (중간 버튼 줄에서 헤더로 옮김) */}
          <Pressable
            accessibilityLabel={t("study.autoAdvanceToggle")}
            onPress={() => setAutoAdvance(!autoAdvance)}
            className={`h-12 flex-row items-center justify-center gap-1 rounded-full px-3.5 active:scale-95 ${
              autoAdvance
                ? "bg-surface shadow-neu-sm"
                : "bg-canvas shadow-neu-inset"
            }`}
          >
            {autoAdvance ? <PlayIcon size={14} /> : <PauseIcon size={14} />}
            <View
              className={`ml-0.5 rounded-full px-1.5 py-0.5 ${
                autoAdvance ? "bg-emerald-500" : "bg-slate-400"
              }`}
            >
              <Text className="text-[11px] font-black text-white">
                {autoAdvance ? "ON" : "OFF"}
              </Text>
            </View>
          </Pressable>
        </View>

        {/* ── 메인 플래시카드 ──────────────────────────────── */}
        <ScrollView
          className="flex-1"
          contentContainerClassName="px-6 pb-10 pt-8"
          showsVerticalScrollIndicator={false}
        >
          <View className="rounded-[32px] bg-surface p-6 shadow-neu-card">
            {/* 연상 이미지 + 좌우 이동 버튼.
                바깥 View는 잘라내지 않아야 화살표가 패널 밖으로 걸쳐 보인다.
                이미지가 1024x1024 정사각형이라 패널도 정사각형으로 꽉 채운다 */}
            <View className="relative w-full" {...swipe.panHandlers}>
              <View
                onLayout={(e) => setPanelW(e.nativeEvent.layout.width)}
                className="aspect-square w-full overflow-hidden rounded-2xl bg-canvas shadow-neu-inset"
              >
                {/* 그림만 손가락을 따라 흐른다. 위에 얹힌 단어·발음 영역은 제자리에 둔다.
                    앞·뒤 그림을 양옆에 붙여 놓아 밀면 옆 그림이 따라 들어온다 */}
                <Animated.View
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    transform: [{ translateX: dragX }],
                  }}
                >
                  <WordImage word={word} />
                  {panelW > 0 && prev && (
                    <WordImage word={prev} offset={-panelW} />
                  )}
                  {panelW > 0 && next && (
                    <WordImage word={next} offset={panelW} />
                  )}
                </Animated.View>

                {/* 단어 · 발음기호 · 발음 듣기: 이미지 위쪽에 반투명 블러(Glassmorphism) 배경으로 표시 */}
                <View
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    borderTopLeftRadius: 16,
                    borderTopRightRadius: 16,
                    overflow: "hidden",
                    borderBottomWidth: 1,
                    borderBottomColor: "rgba(255, 255, 255, 0.45)",
                  }}
                >
                  <BlurView
                    intensity={65}
                    tint="light"
                    style={{
                      width: "100%",
                      ...(Platform.OS === "web"
                        ? {
                            backdropFilter: "saturate(180%) blur(7px)",
                            WebkitBackdropFilter: "saturate(180%) blur(7px)",
                          }
                        : {}),
                    }}
                  >
                    <View
                      style={{
                        backgroundColor: "rgba(241, 242, 246, 0.05)",
                      }}
                      className="flex-row items-start justify-between px-4 pb-3 pt-4"
                    >
                      <View className="flex-1 pr-3">
                        <Text
                          numberOfLines={1}
                          adjustsFontSizeToFit
                          style={{
                            fontSize: wordFontSize,
                            lineHeight: Math.round(wordFontSize * 1.15),
                          }}
                          className="font-black tracking-wider text-slate-900"
                        >
                          {word.word}
                        </Text>
                        {(word.phonetic || word.pos?.length) && (
                          <View className="mt-1 flex-row flex-wrap items-center gap-2">
                            {word.phonetic && (
                              <Text className="text-[13px] tracking-wide text-slate-500">
                                {word.phonetic}
                              </Text>
                            )}
                            {/* 품사 표시. 뜻이 여럿이면 여러 개가 붙는다 */}
                            {word.pos?.map((code) => (
                              <View
                                key={code}
                                className="rounded-md bg-canvas px-1.5 py-0.5 shadow-neu-sm"
                              >
                                <Text className="text-[11px] font-bold text-mint-dark">
                                  {t(`pos.${code}` as never)}
                                </Text>
                              </View>
                            ))}
                          </View>
                        )}
                      </View>
                      <Pressable
                        accessibilityLabel={t("study.speak", { word: word.word })}
                        onPress={handleSpeak}
                        className={`h-11 w-11 items-center justify-center rounded-full active:scale-95 ${
                          speaking
                            ? "bg-canvas shadow-neu-inset"
                            : "bg-surface shadow-neu-sm"
                        }`}
                      >
                        <SpeakerIcon color={speaking ? "#0eb582" : "#334155"} />
                      </Pressable>
                    </View>
                  </BlurView>
                </View>

                {/* 자동 넘김 초시계: 이미지 카드 안쪽 하단에 겹쳐서 표시한다 */}
                <View className="absolute inset-x-0 bottom-0 h-1.5 bg-slate-200">
                  {/* Animated.View 에는 className 이 적용되지 않아
                      높이와 색을 인라인 스타일로 지정한다 */}
                  <Animated.View
                    style={{
                      height: "100%",
                      backgroundColor: autoAdvance ? "#10b981" : "#cbd5e1",
                      width: progress.interpolate({
                        inputRange: [0, 1],
                        outputRange: ["0%", "100%"],
                      }),
                    }}
                  />
                </View>
              </View>

              {/* 이전 단어 (버튼 높이 36px의 절반만큼 올려 세로 중앙에 둔다) */}
              <Pressable
                accessibilityLabel={t("study.prevWord")}
                disabled={!prevId}
                onPress={() => onNavigate(prevId)}
                style={{ top: "50%", marginTop: -18, left: -16 }}
                className={`absolute h-9 w-9 items-center justify-center rounded-full bg-surface shadow-neu-sm active:scale-95 active:shadow-neu-pressed ${
                  prevId ? "" : "opacity-40"
                }`}
              >
                <ChevronLeftIcon size={14} />
              </Pressable>

              {/* 다음 단어 */}
              <Pressable
                accessibilityLabel={t("study.nextWord")}
                disabled={!nextId}
                onPress={() => onNavigate(nextId)}
                style={{ top: "50%", marginTop: -18, right: -16 }}
                className={`absolute h-9 w-9 items-center justify-center rounded-full bg-surface shadow-neu-sm active:scale-95 active:shadow-neu-pressed ${
                  nextId ? "" : "opacity-40"
                }`}
              >
                <ChevronRightIcon size={14} />
              </Pressable>
            </View>

            {/* 한국어 뜻풀이 */}
            <View className="mt-4 rounded-2xl bg-surface p-4 shadow-neu-sm">
              {/* 한글 뜻과 가리기 버튼을 한 줄에 둔다 (제목 없이) */}
              <View className="flex-row items-center justify-between gap-3">
                {showAnswer ? (
                  <Text className="flex-1 text-[20px] font-black tracking-tight text-slate-950">
                    {word.meaning}
                  </Text>
                ) : (
                  /* 가려진 자리. 눌러도 바로 뜻이 나오게 해 둔다 */
                  <Pressable
                    onPress={() => setShowAnswer(true)}
                    className="h-[26px] flex-1 items-center justify-center rounded-xl bg-canvas shadow-neu-inset active:opacity-70"
                  >
                    <Text className="text-[13px] font-bold tracking-[3px] text-slate-400">
                      ● ● ● ●
                    </Text>
                  </Pressable>
                )}
                <Pressable
                  onPress={() => setShowAnswer((v) => !v)}
                  className="flex-row items-center gap-1 active:opacity-70"
                >
                  <Text className="text-[12px] font-bold text-emerald-500">
                    {showAnswer ? t("study.hide") : t("study.show")}
                  </Text>
                  {showAnswer ? <ChevronUpIcon /> : <ChevronDownIcon />}
                </Pressable>
              </View>

              {/* 예문·유의어·어원. 뜻과 함께 가려진다 —
                  단어만 보고 스스로 떠올려 보기 좋다 */}
              {showAnswer && (word.example || hasSynonyms || word.etymology) && (
                <View className="mt-4 gap-5 border-t border-slate-200 pt-4">
                  {word.example && (
                    <LabeledSection label={t("study.example")}>
                      <Text className="text-[15px] font-semibold leading-snug text-slate-800">
                        {word.example}
                      </Text>
                      {word.exampleTr && (
                        <Text className="mt-1 text-[14px] font-medium leading-snug text-slate-500">
                          {word.exampleTr}
                        </Text>
                      )}
                    </LabeledSection>
                  )}

                  {hasSynonyms && (
                    <LabeledSection label={t("study.synonyms")}>
                      <SynonymList items={word.synonyms!} />
                    </LabeledSection>
                  )}

                  {word.etymology && (
                    <LabeledSection label={t("study.etymology")}>
                      <Text className="text-[14px] leading-relaxed text-slate-600">
                        {word.etymology}
                      </Text>
                    </LabeledSection>
                  )}
                </View>
              )}
            </View>
          </View>
        </ScrollView>

        {/* ── 학습 평가 버튼 (가운데는 단어장에 담기) ────────── */}
        <View className="mx-6 flex-row items-stretch gap-1.5 px-1 pb-4 pt-3">
          {/* 세 버튼을 똑같이 flex-1 로 나눠 가진다. 폭도 좌우 여백도 셋이 같아야
              가지런해 보인다 (한쪽만 글씨에 맞추면 그 버튼만 좁아 보인다) */}
          <Pressable
            onPress={() => decide("unsure")}
            style={{ flex: 1 }}
            className="flex-row items-center justify-center gap-1.5 rounded-[28px] bg-surface px-1 py-4 shadow-neu-sm active:scale-[0.98] active:shadow-neu-pressed"
          >
            <View className="h-6 w-6 items-center justify-center rounded-lg bg-slate-300">
              <AgainIcon />
            </View>
            <Text
              numberOfLines={1}
              className="text-[14px] font-extrabold tracking-tight text-slate-800"
            >
              {t("study.unsure")}
            </Text>
          </Pressable>

          {/* 가운데 저장 버튼도 같은 몫을 가진다. 폭이 고정되어 있어
              담겨서 '저장 → 저장됨' 으로 글자가 늘어도 버튼이 흔들리지 않는다 */}
          <Pressable
            onPress={() => toggleSaved(word.id)}
            accessibilityRole="button"
            accessibilityState={{ selected: isSaved }}
            style={{ flex: 1 }}
            accessibilityLabel={t("study.saveToggle")}
            className={`flex-row items-center justify-center gap-1.5 rounded-[28px] px-1 active:scale-[0.98] ${
              isSaved
                ? "bg-canvas shadow-neu-inset"
                : "bg-surface shadow-neu-sm active:shadow-neu-pressed"
            }`}
          >
            <BookmarkIcon
              size={16}
              filled={isSaved}
              color={isSaved ? "#0eb582" : "#94a3b8"}
            />
            <Text
              numberOfLines={1}
              className={`text-[14px] font-extrabold tracking-tight ${
                isSaved ? "text-mint-dark" : "text-slate-500"
              }`}
            >
              {t(isSaved ? "study.saved" : "study.save")}
            </Text>
          </Pressable>

          <Pressable
            onPress={() => decide("known")}
            style={{ flex: 1 }}
            className="flex-row items-center justify-center gap-1.5 rounded-[28px] bg-[#dff5ea] px-1 py-4 shadow-neu-sm active:scale-[0.98] active:shadow-neu-pressed"
          >
            <View className="h-6 w-6 items-center justify-center rounded-md bg-emerald-500">
              <CheckIcon />
            </View>
            <Text
              numberOfLines={1}
              className="text-[14px] font-black tracking-tight text-emerald-800"
            >
              {t("study.known")}
            </Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}
