import {
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
  type ReactNode,
} from "react";
import {
  Alert,
  Animated,
  Platform,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import { BackButton } from "../src/components/BackButton";
import { BottomNav } from "../src/components/BottomNav";
import { GaugeBar } from "../src/components/GaugeBar";
import { LanguageFlag } from "../src/components/flags";
import {
  NeuStateLayer,
  PressableScale,
  useSmooth,
} from "../src/components/motion";
import { SegmentButton } from "../src/components/SegmentButton";
import { PillButton } from "../src/components/PillButton";
import { Screen, ScreenHeader } from "../src/components/Screen";
import {
  ChartIcon,
  GlobeIcon,
  PersonIcon,
  SlidersIcon,
  SpeakerIcon,
} from "../src/components/icons";
import { studyLanguageOf, type StudyLangId } from "../src/constants/languages";
import { signInWithGoogle, signOutCloud } from "../src/lib/cloudSync";
import { cloudAvailable } from "../src/lib/firebase";
import { speakWord } from "../src/lib/speech";
import { isListenSupported } from "../src/lib/listen";
import { useT } from "../src/i18n";
import { UI_LANGS, UI_LANG_NAMES } from "../src/i18n/strings";
import {
  AUTO_ADVANCE_MAX_SEC,
  AUTO_ADVANCE_MIN_SEC,
  SPEECH_PITCH_MAX,
  SPEECH_PITCH_MIN,
  useAppStore,
  type VoiceGender,
} from "../src/stores/useAppStore";
import { useAuthStore } from "../src/stores/useAuthStore";

/** 웹 2단계 확인이 눌린 채로 남아 있지 않도록 되돌리는 시간 (ms) */
const CONFIRM_TIMEOUT_MS = 4000;

/** 바뀔 일이 없는 값을 useSyncExternalStore 로 읽을 때 쓰는 빈 구독 */
const noopSubscribe = () => () => {};

/** 발음 소리 크기 단계 수. 0 은 음소거, 10 은 최대 */
const VOLUME_LEVELS = 10;

/** 크기를 바꿀 때 바로 들려줄 짧은 견본. 학습 언어의 말로 읽어야 자연스럽다 */
const VOLUME_SAMPLE: Record<StudyLangId, string> = {
  en: "Hello",
  ja: "こんにちは",
};

/** 음높이 게이지는 0.1 단위 정수 단계로 다룬다 */
const PITCH_STEP = 10;

const VOICE_GENDERS: {
  id: VoiceGender;
  key: "settings.voiceDefault" | "settings.voiceFemale" | "settings.voiceMale";
}[] = [
  { id: "default", key: "settings.voiceDefault" },
  { id: "female", key: "settings.voiceFemale" },
  { id: "male", key: "settings.voiceMale" },
];

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

/** 구글 로그인과 클라우드 동기화 상태 (웹 전용) */
function AccountCard() {
  const t = useT();
  const checking = useAuthStore((s) => s.checking);
  const user = useAuthStore((s) => s.user);
  const sync = useAuthStore((s) => s.sync);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  const run = async (action: () => Promise<void>) => {
    setBusy(true);
    setFailed(false);
    try {
      await action();
    } catch (e) {
      // 사용자가 팝업을 닫은 것은 실패로 보지 않는다
      const code = (e as { code?: string })?.code ?? "";
      if (!code.includes("popup-closed") && !code.includes("cancelled")) {
        console.warn("[account]", e);
        setFailed(true);
      }
    } finally {
      setBusy(false);
    }
  };

  const syncLabel =
    sync === "syncing"
      ? t("account.syncing")
      : sync === "error"
        ? t("account.syncError")
        : t("account.synced");

  return (
    <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
      <SectionTitle icon={<PersonIcon />} label={t("account.title")} />
      {checking ? (
        <Text className="mt-3 text-[13px] text-slate-400">
          {t("account.checking")}
        </Text>
      ) : user ? (
        <>
          <View className="mt-3 flex-row items-center justify-between gap-3">
            <Text
              className="flex-1 text-[15px] text-slate-700"
              numberOfLines={1}
            >
              {user.email ?? user.name ?? ""}
            </Text>
            <Text
              className={`text-[13px] font-bold ${
                sync === "error" ? "text-rose-500" : "text-mint-dark"
              }`}
            >
              {syncLabel}
            </Text>
          </View>
          <PillButton
            className="mt-5 self-start"
            size="sm"
            label={t("account.signOut")}
            loading={busy}
            onPress={() => run(signOutCloud)}
          />
        </>
      ) : (
        <>
          <Text className="mt-3 text-[13px] text-slate-400">
            {t("account.desc")}
          </Text>
          <PillButton
            className="mt-5 self-start"
            size="sm"
            variant="primary"
            label={t("account.signIn")}
            loading={busy}
            onPress={() => run(signInWithGoogle)}
          />
        </>
      )}
      {failed ? (
        <Text className="mt-3 text-[13px] text-rose-500">
          {t("account.signInFailed")}
        </Text>
      ) : null}
    </View>
  );
}

export default function SettingsScreen() {
  const nickname = useAppStore((s) => s.nickname);
  const setNickname = useAppStore((s) => s.setNickname);
  const autoAdvance = useAppStore((s) => s.autoAdvance);
  const setAutoAdvance = useAppStore((s) => s.setAutoAdvance);
  const advanceDim = useSmooth(autoAdvance ? 1 : 0.5, { native: true });
  const autoListen = useAppStore((s) => s.autoListen);
  const setAutoListen = useAppStore((s) => s.setAutoListen);
  // 따라 말하기는 음성 인식이 되는 브라우저에서만 보여 준다 (서버에서 그릴 때는 없는 것으로)
  const canListen = useSyncExternalStore(
    noopSubscribe,
    isListenSupported,
    () => false,
  );
  const speechVolume = useAppStore((s) => s.speechVolume);
  const setSpeechVolume = useAppStore((s) => s.setSpeechVolume);
  // 예전 25% 단위로 저장된 값도 가장 가까운 10% 단계로 보여준다
  const volumeStep = Math.round(speechVolume * VOLUME_LEVELS);
  const voiceGender = useAppStore((s) => s.voiceGender);
  const setVoiceGender = useAppStore((s) => s.setVoiceGender);
  const speechPitch = useAppStore((s) => s.speechPitch);
  const setSpeechPitch = useAppStore((s) => s.setSpeechPitch);
  const pitchStep = Math.round(speechPitch * PITCH_STEP);
  const autoAdvanceSec = useAppStore((s) => s.autoAdvanceSec);
  const setAutoAdvanceSec = useAppStore((s) => s.setAutoAdvanceSec);
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

  // 웹 화면을 미리 그릴 때(SSR)는 클라우드를 못 쓰므로, 브라우저에서 다시 그린 뒤에 계정 칸을 띄운다
  const showAccount = useSyncExternalStore(
    noopSubscribe,
    () => cloudAvailable,
    () => false,
  );

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
    <Screen>
      <ScreenHeader>
        <BackButton fallbackHref="/" />
        <Text className="text-2xl font-bold text-ink">
          {t("settings.title")}
        </Text>
      </ScreenHeader>

      <ScrollView
        className="flex-1"
        // 설정 카드끼리의 간격은 다른 화면의 카드 묶음과 같은 16px
        contentContainerClassName="gap-4 px-6 pb-32 pt-6"
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {showAccount ? <AccountCard /> : null}

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

        <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
          <SectionTitle icon={<GlobeIcon />} label={t("settings.language")} />

          {/* 앱 화면에 쓰는 말 */}
          <Text className="mt-4 text-[15px] text-slate-700">
            {t("settings.uiLang")}
          </Text>
          <Text className="mt-1 text-[13px] text-slate-400">
            {t("settings.uiLangDesc")}
          </Text>
          {/* 홈의 학습 언어 고르기와 같은 모양: 국기 + 이름, 고른 쪽이 안으로 파인다 */}
          <View className="mt-3 flex-row gap-3">
            {UI_LANGS.map((id) => (
              <SegmentButton
                key={id}
                selected={uiLang === id}
                onPress={() => setUiLang(id)}
                label={UI_LANG_NAMES[id]}
                left={<LanguageFlag lang={id} size={26} />}
              />
            ))}
          </View>
        </View>

        <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
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
            {/* 앱 전체에서 파인 모양은 "켜짐·선택됨"을 뜻한다 */}
            <PressableScale
              accessibilityRole="switch"
              accessibilityLabel={t("settings.autoAdvance")}
              accessibilityState={{ checked: autoAdvance }}
              onPress={() => setAutoAdvance(!autoAdvance)}
              className="px-4 py-2"
            >
              <NeuStateLayer active={autoAdvance} radiusClass="rounded-full" />
              <Text
                className={`text-[13px] font-bold ${
                  autoAdvance ? "text-mint-dark" : "text-slate-400"
                }`}
              >
                {autoAdvance ? t("common.on") : t("common.off")}
              </Text>
            </PressableScale>
          </View>

          {/* ── 자동 넘김 간격 (5~15초) ─────────────────────── */}
          {/* 자동 넘김을 끄면 간격 게이지가 서서히 흐려진다 */}
          <Animated.View style={{ marginTop: 16, opacity: advanceDim }}>
            <View className="flex-row items-center justify-between">
              <Text className="text-[13px] text-slate-500">
                {t("settings.autoAdvanceSec")}
              </Text>
              <Text className="text-[13px] font-bold text-mint-dark">
                {t("settings.autoAdvanceSecValue", { sec: autoAdvanceSec })}
              </Text>
            </View>
            <View className="mt-3">
              <GaugeBar
                value={autoAdvanceSec}
                min={AUTO_ADVANCE_MIN_SEC}
                max={AUTO_ADVANCE_MAX_SEC}
                onChange={setAutoAdvanceSec}
                valueLabel={t("settings.autoAdvanceSecValue", {
                  sec: autoAdvanceSec,
                })}
                maxLabel={t("settings.autoAdvanceSecValue", {
                  sec: AUTO_ADVANCE_MAX_SEC,
                })}
                accessibilityLabel={t("settings.autoAdvanceSec")}
                accessibilityValueText={t("settings.autoAdvanceSecValue", {
                  sec: autoAdvanceSec,
                })}
              />
            </View>
          </Animated.View>

          {/* ── 듣고 따라 말하기 ───────────────────────────── */}
          {canListen && (
            <View className="mt-5 flex-row items-center justify-between gap-4 border-t border-slate-200/70 pt-5">
              <View className="flex-1">
                <Text className="text-[15px] text-slate-700">
                  {t("settings.autoListen")}
                </Text>
                <Text className="mt-1 text-[13px] text-slate-400">
                  {t("settings.autoListenDesc")}
                </Text>
              </View>
              <PressableScale
                accessibilityRole="switch"
                accessibilityLabel={t("settings.autoListen")}
                accessibilityState={{ checked: autoListen }}
                onPress={() => setAutoListen(!autoListen)}
                className="px-4 py-2"
              >
                <NeuStateLayer active={autoListen} radiusClass="rounded-full" />
                <Text
                  className={`text-[13px] font-bold ${
                    autoListen ? "text-mint-dark" : "text-slate-400"
                  }`}
                >
                  {autoListen ? t("common.on") : t("common.off")}
                </Text>
              </PressableScale>
            </View>
          )}

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

            {/* 끌거나 눌러 크기를 바꾸고, 손을 떼면 바뀐 크기로 한 번 들려준다 */}
            <View className="mt-3 flex-row items-center gap-3">
              <PressableScale
                onPress={() => playSample(speechVolume)}
                accessibilityRole="button"
                accessibilityLabel={t("settings.speechVolume")}
                scaleTo={0.9}
                className="h-11 w-11 items-center justify-center rounded-full bg-surface shadow-neu-sm"
              >
                <SpeakerIcon
                  size={18}
                  color={speechVolume === 0 ? "#94a3b8" : "#0eb582"}
                />
              </PressableScale>
              <View className="flex-1">
                <GaugeBar
                  value={volumeStep}
                  min={0}
                  max={VOLUME_LEVELS}
                  dimmed={volumeStep === 0}
                  valueLabel={`${volumeStep * 10}%`}
                  maxLabel="100%"
                  onChange={(step) => setSpeechVolume(step / VOLUME_LEVELS)}
                  onRelease={(step) => playSample(step / VOLUME_LEVELS)}
                  accessibilityLabel={t("settings.speechVolume")}
                  accessibilityValueText={
                    volumeStep === 0
                      ? t("settings.speechMuted")
                      : t("settings.speechVolumeLevel", {
                          percent: volumeStep * 10,
                        })
                  }
                />
              </View>
            </View>
          </View>
          {/* ── 목소리 성별 ─────────────────────────────── */}
          <View className="mt-5 border-t border-slate-200/70 pt-5">
            <Text className="text-[15px] text-slate-700">
              {t("settings.voiceGender")}
            </Text>
            <Text className="mt-1 text-[13px] text-slate-400">
              {t("settings.voiceGenderDesc")}
            </Text>
            <View className="mt-3 flex-row gap-3">
              {VOICE_GENDERS.map(({ id, key }) => (
                <SegmentButton
                  key={id}
                  selected={voiceGender === id}
                  onPress={() => {
                    setVoiceGender(id);
                    playSample(speechVolume || 1);
                  }}
                  label={t(key)}
                />
              ))}
            </View>
          </View>

          {/* ── 음높이 ─────────────────────────────────── */}
          <View className="mt-5 border-t border-slate-200/70 pt-5">
            <View className="flex-row items-center justify-between gap-4">
              <View className="flex-1">
                <Text className="text-[15px] text-slate-700">
                  {t("settings.speechPitch")}
                </Text>
                <Text className="mt-1 text-[13px] text-slate-400">
                  {t("settings.speechPitchDesc")}
                </Text>
              </View>
              <Text className="text-[13px] font-bold text-mint-dark">
                {`×${speechPitch.toFixed(1)}`}
              </Text>
            </View>
            <View className="mt-3">
              <GaugeBar
                value={pitchStep}
                min={SPEECH_PITCH_MIN * PITCH_STEP}
                max={SPEECH_PITCH_MAX * PITCH_STEP}
                valueLabel={`×${speechPitch.toFixed(1)}`}
                maxLabel={`×${SPEECH_PITCH_MAX.toFixed(1)}`}
                onChange={(step) => setSpeechPitch(step / PITCH_STEP)}
                onRelease={() => playSample(speechVolume || 1)}
                accessibilityLabel={t("settings.speechPitch")}
                accessibilityValueText={`${speechPitch.toFixed(1)}`}
              />
            </View>
          </View>
        </View>

        <View className="rounded-3xl bg-surface p-6 shadow-neu-card">
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

      <BottomNav />
    </Screen>
  );
}
