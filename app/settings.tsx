import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Alert,
  Platform,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { BackButton } from "../src/components/BackButton";
import { BottomNav } from "../src/components/BottomNav";
import { PillButton } from "../src/components/PillButton";
import {
  ChartIcon,
  GlobeIcon,
  PersonIcon,
  SlidersIcon,
  SpeakerIcon,
} from "../src/components/icons";
import {
  studyLanguageOf,
  type StudyLangId,
} from "../src/constants/languages";
import { speakWord } from "../src/lib/speech";
import { useT } from "../src/i18n";
import { UI_LANGS, UI_LANG_NAMES } from "../src/i18n/strings";
import { useAppStore } from "../src/stores/useAppStore";

/** 웹 2단계 확인이 눌린 채로 남아 있지 않도록 되돌리는 시간 (ms) */
const CONFIRM_TIMEOUT_MS = 4000;

/**
 * 발음 소리 크기 단계.
 * 슬라이더 라이브러리를 새로 들이지 않고, 앱의 다른 칸과 같은 뉴모피즘
 * 막대로 만든다. 맨 왼쪽은 음소거다.
 */
const VOLUME_STEPS = [0, 0.25, 0.5, 0.75, 1];

/** 크기를 바꿀 때 바로 들려줄 짧은 견본. 학습 언어의 말로 읽어야 자연스럽다 */
const VOLUME_SAMPLE: Record<StudyLangId, string> = {
  en: "Hello",
  ja: "こんにちは",
};

/** 설정 칸의 제목 줄. 왼쪽에 아이콘이 붙는다 */
function SectionTitle({ icon, label }: { icon: ReactNode; label: string }) {
  return (
    <View className="flex-row items-center gap-2.5">
      <View className="h-9 w-9 items-center justify-center rounded-xl bg-canvas shadow-neu-inset">
        {icon}
      </View>
      <Text className="text-[15px] font-bold text-ink">{label}</Text>
    </View>
  );
}

export default function SettingsScreen() {
  const nickname = useAppStore((s) => s.nickname);
  const setNickname = useAppStore((s) => s.setNickname);
  const autoAdvance = useAppStore((s) => s.autoAdvance);
  const setAutoAdvance = useAppStore((s) => s.setAutoAdvance);
  const speechVolume = useAppStore((s) => s.speechVolume);
  const setSpeechVolume = useAppStore((s) => s.setSpeechVolume);
  const studyLang = useAppStore((s) => s.studyLang);

  /** 고른 크기로 짧은 견본을 들려준다. 음소거면 들려줄 것이 없다 */
  const playSample = (volume: number) => {
    if (volume <= 0) return;
    speakWord(VOLUME_SAMPLE[studyLang], {
      lang: studyLanguageOf(studyLang).speechCode,
      volume,
    });
  };
  const entries = useAppStore((s) => s.entries);
  const resetProgress = useAppStore((s) => s.resetProgress);
  const uiLang = useAppStore((s) => s.uiLang);
  const setUiLang = useAppStore((s) => s.setUiLang);
  const t = useT();

  /** 웹에는 Alert이 없어 버튼을 두 번 눌러 확인받는다 */
  const [confirming, setConfirming] = useState(false);

  const counts = useMemo(() => {
    let known = 0;
    let unsure = 0;
    for (const entry of Object.values(entries)) {
      if (entry.status === "known") known += 1;
      else if (entry.status === "unsure") unsure += 1;
    }
    return { known, unsure };
  }, [entries]);

  const hasRecord = counts.known > 0 || counts.unsure > 0;

  // 확인 상태로 방치된 버튼을 잘못 누르는 일이 없도록 잠시 뒤 되돌린다
  useEffect(() => {
    if (!confirming) return;
    const timer = setTimeout(() => setConfirming(false), CONFIRM_TIMEOUT_MS);
    return () => clearTimeout(timer);
  }, [confirming]);

  const handleReset = () => {
    if (Platform.OS === "web") {
      if (!confirming) {
        setConfirming(true);
        return;
      }
      setConfirming(false);
      resetProgress();
      return;
    }

    Alert.alert(t("settings.resetProgress"), t("settings.resetConfirmDesc"), [
      { text: t("common.cancel"), style: "cancel" },
      {
        text: t("common.delete"),
        style: "destructive",
        onPress: resetProgress,
      },
    ]);
  };

  return (
    <SafeAreaView className="flex-1 bg-canvas">
      <View className="w-full flex-1">
        <View className="flex-row items-center gap-4 px-6 pb-4 pt-8">
          <BackButton fallbackHref="/" />
          <Text className="text-2xl font-bold text-ink">
            {t("settings.title")}
          </Text>
        </View>

        <ScrollView
          className="flex-1"
          contentContainerClassName="px-6 pb-32 pt-2"
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
            <SectionTitle icon={<PersonIcon />} label={t("settings.myName")} />
            <TextInput
              value={nickname}
              onChangeText={setNickname}
              placeholder={t("settings.namePlaceholder")}
              placeholderTextColor="#94a3b8"
              maxLength={12}
              returnKeyType="done"
              className="mt-3 rounded-2xl bg-canvas px-4 py-3 text-[15px] text-ink shadow-neu-inset"
            />
          </View>

          <View className="mt-6 rounded-3xl bg-surface p-6 shadow-neu-card">
            <SectionTitle icon={<GlobeIcon />} label={t("settings.language")} />

            {/* 앱 화면에 쓰는 말 */}
            <Text className="mt-4 text-[15px] text-slate-700">
              {t("settings.uiLang")}
            </Text>
            <Text className="mt-1 text-[13px] text-slate-400">
              {t("settings.uiLangDesc")}
            </Text>
            <View className="mt-3 flex-row flex-wrap gap-2">
              {UI_LANGS.map((id) => (
                <PillButton
                  key={id}
                  size="sm"
                  label={UI_LANG_NAMES[id]}
                  variant={uiLang === id ? "inset" : "default"}
                  onPress={() => setUiLang(id)}
                />
              ))}
            </View>
          </View>

          <View className="mt-6 rounded-3xl bg-surface p-6 shadow-neu-card">
            <SectionTitle
              icon={<SlidersIcon />}
              label={t("settings.studySettings")}
            />
            <View className="mt-4 flex-row items-center justify-between gap-4">
              <View className="flex-1">
                <Text className="text-[15px] text-slate-700">
                  {t("settings.autoAdvance")}
                </Text>
                <Text className="mt-1 text-[13px] text-slate-400">
                  {t("settings.autoAdvanceDesc")}
                </Text>
              </View>
              <Pressable
                accessibilityRole="switch"
                accessibilityLabel={t("settings.autoAdvance")}
                accessibilityState={{ checked: autoAdvance }}
                onPress={() => setAutoAdvance(!autoAdvance)}
                className={`rounded-full px-4 py-2 active:opacity-70 ${
                  autoAdvance
                    ? "bg-surface shadow-neu-sm"
                    : "bg-canvas shadow-neu-inset"
                }`}
              >
                <Text
                  className={`text-[13px] font-bold ${
                    autoAdvance ? "text-mint-dark" : "text-slate-400"
                  }`}
                >
                  {autoAdvance ? t("common.on") : t("common.off")}
                </Text>
              </Pressable>
            </View>

            {/* ── 발음 소리 크기 ─────────────────────────────── */}
            <View className="mt-5 border-t border-slate-200/70 pt-5">
              <View className="flex-row items-center justify-between gap-4">
                <View className="flex-1">
                  <Text className="text-[15px] text-slate-700">
                    {t("settings.speechVolume")}
                  </Text>
                  <Text className="mt-1 text-[13px] text-slate-400">
                    {t("settings.speechVolumeDesc")}
                  </Text>
                </View>
                <Text
                  className={`text-[13px] font-bold ${
                    speechVolume === 0 ? "text-slate-400" : "text-mint-dark"
                  }`}
                >
                  {speechVolume === 0
                    ? t("settings.speechMuted")
                    : `${Math.round(speechVolume * 100)}%`}
                </Text>
              </View>

              {/* 단계를 누르면 바뀐 크기로 바로 한 번 들려준다.
                  막대 자체는 낮은 단계일수록 짧아 누르기 어려우므로, 누르는
                  자리는 막대 높이와 상관없이 48px 로 잡고 그 안에 막대를 그린다 */}
              <View className="mt-3 flex-row items-end gap-2">
                <Pressable
                  onPress={() => playSample(speechVolume)}
                  accessibilityRole="button"
                  accessibilityLabel={t("settings.speechVolume")}
                  className="h-12 justify-center pr-1 active:opacity-60"
                >
                  <SpeakerIcon
                    size={18}
                    color={speechVolume === 0 ? "#94a3b8" : "#0eb582"}
                  />
                </Pressable>
                {VOLUME_STEPS.map((step, i) => {
                  const on = speechVolume >= step && step > 0;
                  return (
                    <Pressable
                      key={step}
                      accessibilityRole="button"
                      accessibilityState={{ selected: speechVolume === step }}
                      accessibilityLabel={
                        step === 0
                          ? t("settings.speechMuted")
                          : t("settings.speechVolumeLevel", {
                              percent: Math.round(step * 100),
                            })
                      }
                      onPress={() => {
                        setSpeechVolume(step);
                        playSample(step);
                      }}
                      style={{ flex: 1 }}
                      className="h-12 justify-end active:opacity-70"
                    >
                      <View
                        style={{ height: 12 + i * 8 }}
                        className={`rounded-lg ${
                          on
                            ? "bg-mint"
                            : // 음소거를 고른 상태도 눌린 티가 나야 한다
                              step === 0 && speechVolume === 0
                              ? "bg-slate-300"
                              : "bg-canvas shadow-neu-inset"
                        }`}
                      />
                    </Pressable>
                  );
                })}
              </View>
            </View>
          </View>

          <View className="mt-6 rounded-3xl bg-surface p-6 shadow-neu-card">
            <SectionTitle icon={<ChartIcon />} label={t("settings.record")} />
            {/* 기록이 없으면 "0개 · 0개" 대신 안내를 보여주고, 지울 것도 없으니 버튼을 감춘다 */}
            {hasRecord ? (
              <>
                <Text className="mt-3 text-[13px] text-slate-700">
                  {t("settings.recordSummary", {
                    known: counts.known,
                    unsure: counts.unsure,
                  })}
                </Text>
                <PillButton
                  className="mt-5 self-start"
                  size="sm"
                  label={
                    confirming
                      ? t("settings.resetConfirmTitle")
                      : t("settings.resetProgress")
                  }
                  onPress={handleReset}
                />
              </>
            ) : (
              <Text className="mt-3 text-[13px] text-slate-400">
                {t("settings.noRecord")}
              </Text>
            )}
          </View>
        </ScrollView>
      </View>

      <BottomNav />
    </SafeAreaView>
  );
}
