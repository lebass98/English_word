import { Modal, Pressable, Text, View } from "react-native";
import { useT } from "../i18n";
import {
  checkForUpdate,
  downloadAndInstall,
  reopenInstaller,
  setUpdateDialogOpen,
  useUpdateStore,
} from "../lib/appUpdate";
import { PillButton } from "./PillButton";
import { RocketIcon } from "./icons";

const MINT = "#0EB582";

/**
 * 앱 안에서 하는 업데이트 창 (안드로이드 전용).
 * 새 버전 안내 → 내려받기 진행률 → 설치 화면 열기까지 이 창 하나에서 보여 준다.
 * 바깥을 누르거나 "나중에"를 누르면 닫히고, 받는 중이면 내려받기는 계속된다.
 */
export function UpdateDialog() {
  const t = useT();
  const open = useUpdateStore((s) => s.open);
  const phase = useUpdateStore((s) => s.phase);
  const release = useUpdateStore((s) => s.release);
  const progress = useUpdateStore((s) => s.progress);

  const visible =
    open &&
    (phase === "available" ||
      phase === "downloading" ||
      phase === "ready" ||
      phase === "error");
  const close = () => setUpdateDialogOpen(false);
  const percent = Math.round(progress * 100);

  const title =
    phase === "downloading"
      ? t("update.downloading", { percent })
      : phase === "ready"
        ? t("update.ready")
        : phase === "error"
          ? t("update.errorTitle")
          : t("update.found", { version: release?.version ?? "" });
  const hint =
    phase === "downloading"
      ? t("update.downloadingHint")
      : phase === "ready"
        ? t("update.readyHint")
        : phase === "error"
          ? t("update.failed")
          : t("update.installHint");

  return (
    <Modal
      transparent
      animationType="fade"
      visible={visible}
      onRequestClose={close}
      statusBarTranslucent
    >
      <Pressable
        accessibilityLabel={t("update.later")}
        onPress={close}
        className="flex-1 items-center justify-center bg-black/30 px-8"
      >
        {/* 창 안을 눌렀을 때 바깥 눌림으로 번지지 않게 막는다 */}
        <Pressable
          onPress={() => {}}
          className="w-full max-w-[380px] rounded-3xl bg-surface p-6 shadow-neu-card"
        >
          <View className="flex-row items-center gap-2.5">
            <View className="h-9 w-9 items-center justify-center rounded-xl bg-canvas shadow-neu-inset">
              <RocketIcon color={MINT} />
            </View>
            <Text
              accessibilityRole="header"
              className="flex-1 text-[16px] font-bold text-ink"
            >
              {title}
            </Text>
          </View>

          <Text className="mt-3 text-[13px] leading-5 text-slate-500">
            {hint}
          </Text>

          {phase === "downloading" || phase === "ready" ? (
            <View
              accessibilityRole="progressbar"
              accessibilityValue={{ min: 0, max: 100, now: percent }}
              className="mt-5 h-2.5 overflow-hidden rounded-full bg-canvas shadow-neu-inset"
            >
              <View
                style={{
                  width: `${percent}%`,
                  height: "100%",
                  backgroundColor: MINT,
                  borderRadius: 999,
                }}
              />
            </View>
          ) : null}

          <View className="mt-6 flex-row justify-end gap-3">
            {phase === "available" ? (
              <>
                <PillButton
                  size="sm"
                  label={t("update.later")}
                  onPress={close}
                />
                <PillButton
                  size="sm"
                  variant="primary"
                  label={t("update.now")}
                  onPress={downloadAndInstall}
                />
              </>
            ) : phase === "downloading" ? (
              <PillButton size="sm" label={t("update.hide")} onPress={close} />
            ) : phase === "ready" ? (
              <>
                <PillButton
                  size="sm"
                  label={t("update.close")}
                  onPress={close}
                />
                <PillButton
                  size="sm"
                  variant="primary"
                  label={t("update.reopen")}
                  onPress={reopenInstaller}
                />
              </>
            ) : (
              <>
                <PillButton
                  size="sm"
                  label={t("update.close")}
                  onPress={close}
                />
                <PillButton
                  size="sm"
                  variant="primary"
                  label={t("update.retry")}
                  onPress={() =>
                    release ? downloadAndInstall() : checkForUpdate()
                  }
                />
              </>
            )}
          </View>
        </Pressable>
      </Pressable>
    </Modal>
  );
}
