import { createAudioPlayer, type AudioPlayer } from "expo-audio";
import { Platform } from "react-native";

/**
 * 따라 말하기 판정 효과음.
 * 맞으면 "띵동", 틀리면 낮은 "뿌-뿌" 소리를 낸다. (assets/sounds 의 wav)
 *
 * 플레이어는 처음 울릴 때 한 번 만들어 두고 다시 쓴다.
 * 웹 정적 빌드를 서버에서 그릴 때는 소리를 낼 수 없으니 아무것도 하지 않는다.
 */
const SOURCES = {
  correct: require("../../assets/sounds/correct.wav"),
  wrong: require("../../assets/sounds/wrong.wav"),
};

export type FeedbackSound = keyof typeof SOURCES;

const players: Partial<Record<FeedbackSound, AudioPlayer>> = {};

export function playFeedback(kind: FeedbackSound, volume = 1) {
  if (volume <= 0) return;
  if (Platform.OS === "web" && typeof window === "undefined") return;
  try {
    const player = (players[kind] ??= createAudioPlayer(SOURCES[kind]));
    player.volume = Math.min(1, volume);
    player.seekTo(0);
    player.play();
  } catch (e) {
    // 효과음이 안 나도 학습은 이어진다
    console.warn("[feedbackSound]", e);
  }
}
