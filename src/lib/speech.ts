import * as Speech from "expo-speech";

/**
 * 영어 단어 발음 재생 (TTS).
 * - 네이티브: expo-speech가 OS 음성 엔진 사용
 * - 웹: Web Speech API(speechSynthesis) 사용
 * 이미 재생 중이면 멈추고 새로 읽어 버튼 연타 시 소리가 겹치지 않는다.
 */
export function speakWord(word: string, onDone?: () => void) {
  if (!word) return;
  try {
    Speech.stop();
    Speech.speak(word, {
      language: "en-US",
      rate: 0.85,
      pitch: 1.0,
      onDone,
      onStopped: onDone,
      onError: onDone,
    });
  } catch {
    onDone?.();
  }
}

export function stopSpeaking() {
  try {
    Speech.stop();
  } catch {
    // 음성 엔진이 없는 환경은 무시
  }
}
