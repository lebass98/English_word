import * as Speech from "expo-speech";

interface SpeakCallbacks {
  /** 읽어 줄 언어 코드 (예: en-US, ja-JP). 없으면 영어로 읽는다 */
  lang?: string;
  /** 소리 크기 (0 = 음소거 … 1 = 최대). 없으면 최대로 읽는다 */
  volume?: number;
  /** 실제로 소리가 나기 시작할 때 (음성 엔진이 비동기로 호출) */
  onStart?: () => void;
  /** 재생이 끝났거나 중단·실패했을 때 */
  onDone?: () => void;
}

/**
 * 영어 단어 발음 재생 (TTS).
 * - 네이티브: expo-speech가 OS 음성 엔진 사용
 * - 웹: Web Speech API(speechSynthesis) 사용
 *
 * 이미 재생 중이면 멈추고 새로 읽어 버튼 연타나 빠른 단어 이동 시 소리가 겹치지 않는다.
 *
 * 참고: 웹 브라우저는 사용자가 페이지를 한 번이라도 클릭하기 전에는
 * 자동 재생을 막는다. 첫 화면의 자동 발음이 안 나올 수 있는 이유다.
 */
export function speakWord(word: string, cb: SpeakCallbacks = {}) {
  if (!word) return;
  // 음소거면 굳이 음성 엔진을 깨우지 않는다. 끝난 것으로 알려 버튼 상태를 되돌린다
  if (cb.volume === 0) {
    cb.onDone?.();
    return;
  }
  try {
    Speech.stop();
    // 웹(크롬)은 speechSynthesis.cancel() 직후 같은 틱에 speak() 를 부르면
    // 새 발화가 조용히 사라진다. 한 틱 뒤로 미뤄 이 문제를 피한다.
    setTimeout(() => {
      try {
        Speech.speak(word, {
          language: cb.lang ?? "en-US",
          rate: 0.85,
          pitch: 1.0,
          volume: cb.volume ?? 1,
          onStart: cb.onStart,
          onDone: cb.onDone,
          onStopped: cb.onDone,
          onError: cb.onDone,
        });
      } catch {
        cb.onDone?.();
      }
    }, 0);
  } catch {
    cb.onDone?.();
  }
}

export function stopSpeaking() {
  try {
    Speech.stop();
  } catch {
    // 음성 엔진이 없는 환경은 무시
  }
}
