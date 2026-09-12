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

/** 개발 중에만 콘솔에 남긴다. 왜 소리가 안 나는지 추적할 단서가 된다 */
function debug(...args: unknown[]) {
  if (__DEV__) console.warn("[speech]", ...args);
}

/**
 * 음성 엔진이 쓸 수 있는 상태인지 한 번만 확인해 콘솔에 남긴다.
 * 웹은 페이지가 뜬 직후 목소리 목록이 비어 있을 수 있고, 목소리가 하나도
 * 없으면 speak() 를 불러도 아무 일이 일어나지 않는다.
 */
let checked = false;
function checkOnce(lang: string) {
  if (checked || !__DEV__) return;
  checked = true;
  Speech.getAvailableVoicesAsync()
    .then((voices) => {
      const head = lang.split("-")[0];
      const same = voices.filter((v) => v.language?.startsWith(head));
      debug(
        `목소리 ${voices.length}개, 그중 ${lang} 계열 ${same.length}개`,
        same.slice(0, 3).map((v) => `${v.name}(${v.language})`),
      );
      if (voices.length === 0) debug("목소리가 하나도 없어 소리가 나지 않는다");
    })
    .catch((e) => debug("목소리 목록을 못 읽었다", e));
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
 * 또 iOS 사파리는 사용자가 누른 바로 그 순간에 speak() 가 불려야 하므로,
 * stop() 과 speak() 사이에 타이머나 await 를 끼워 넣지 않는다.
 */
export function speakWord(word: string, cb: SpeakCallbacks = {}) {
  if (!word) return;
  // 음소거면 굳이 음성 엔진을 깨우지 않는다. 끝난 것으로 알려 버튼 상태를 되돌린다
  if (cb.volume === 0) {
    cb.onDone?.();
    return;
  }
  const lang = cb.lang ?? "en-US";
  checkOnce(lang);
  try {
    Speech.stop();
    Speech.speak(word, {
      language: lang,
      rate: 0.85,
      pitch: 1.0,
      volume: cb.volume ?? 1,
      onStart: cb.onStart,
      onDone: cb.onDone,
      onStopped: cb.onDone,
      // 오류를 조용히 삼키면 왜 안 나는지 알 길이 없다
      onError: (e) => {
        debug(`"${word}" 재생 실패`, e);
        cb.onDone?.();
      },
    });
  } catch (e) {
    debug(`"${word}" 호출 자체가 실패`, e);
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
