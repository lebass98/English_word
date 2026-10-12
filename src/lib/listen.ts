import { Platform } from "react-native";

/**
 * 따라 말하기 (음성 인식 → 발음 판정).
 *
 * 웹: 브라우저의 Web Speech API(SpeechRecognition) 를 쓴다.
 *     크롬·엣지·사파리(iOS 14.5+)가 지원하고, 파이어폭스는 지원하지 않는다.
 * 네이티브: 아직 음성 인식 모듈이 없어 쓸 수 없다고 알린다.
 *     (expo-speech-recognition 같은 네이티브 모듈과 개발 빌드가 필요하다)
 *
 * 인식 결과는 브라우저가 들은 "글자"다. 소리 자체를 채점하지 않으므로
 * 엔진이 그 단어로 알아들었으면 맞음, 비슷한 다른 말로 들었으면 틀림으로 본다.
 */

/** 인식이 실패한 까닭. 화면 문구를 고르는 데 쓴다 */
export type ListenError =
  /** 아무 말도 들리지 않았다 */
  | "no-speech"
  /** 마이크 권한을 막았다 */
  | "not-allowed"
  /** 이 기기·브라우저에서는 음성 인식을 쓸 수 없다 */
  | "unsupported"
  /** 그 밖의 오류 (네트워크 등) */
  | "failed";

interface ListenCallbacks {
  /** 들은 말 후보들. 엔진이 그럴듯하다고 본 순서다 */
  onResult: (alternatives: string[]) => void;
  onError: (error: ListenError) => void;
}

/* 표준 타입 정의에 아직 없어 필요한 만큼만 적어 둔다 */
interface RecognitionAlternative {
  transcript: string;
}
interface RecognitionEvent {
  results: ArrayLike<ArrayLike<RecognitionAlternative>>;
}
interface Recognition {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  maxAlternatives: number;
  onresult: ((e: RecognitionEvent) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  abort: () => void;
}
type RecognitionCtor = new () => Recognition;

function recognitionCtor(): RecognitionCtor | null {
  if (Platform.OS !== "web" || typeof window === "undefined") return null;
  const w = window as unknown as {
    SpeechRecognition?: RecognitionCtor;
    webkitSpeechRecognition?: RecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

/**
 * 이 기기에서 따라 말하기를 쓸 수 있는지.
 * 웹 정적 빌드는 서버에서 먼저 그려지므로 화면이 뜬 뒤(useEffect 안)에서 불러야 한다.
 */
export function isListenSupported() {
  return recognitionCtor() !== null;
}

/**
 * 한 번 듣고 끝낸다. 말이 끝나면 엔진이 알아서 멈춘다.
 * 돌려주는 함수를 부르면 듣기를 그만둔다 (이때는 콜백을 부르지 않는다).
 */
export function listenOnce(lang: string, cb: ListenCallbacks): () => void {
  const Ctor = recognitionCtor();
  if (!Ctor) {
    cb.onError("unsupported");
    return () => {};
  }

  let settled = false;
  const settle = (fn: () => void) => {
    if (settled) return;
    settled = true;
    fn();
  };

  const rec = new Ctor();
  rec.lang = lang;
  rec.interimResults = false;
  rec.continuous = false;
  rec.maxAlternatives = 5;

  rec.onresult = (e) => {
    const first = e.results[0];
    const alternatives: string[] = [];
    for (let i = 0; i < (first?.length ?? 0); i++) {
      const text = first[i]?.transcript?.trim();
      if (text) alternatives.push(text);
    }
    settle(() =>
      alternatives.length ? cb.onResult(alternatives) : cb.onError("no-speech"),
    );
  };
  rec.onerror = (e) => {
    // 그만두라고 해서 끊긴 것은 오류가 아니다
    if (e.error === "aborted") return;
    const error: ListenError =
      e.error === "no-speech"
        ? "no-speech"
        : e.error === "not-allowed" || e.error === "service-not-allowed"
          ? "not-allowed"
          : e.error === "audio-capture"
            ? "unsupported"
            : "failed";
    settle(() => cb.onError(error));
  };
  // 결과도 오류도 없이 끝나는 브라우저가 있다 (사파리가 조용하면 그렇다)
  rec.onend = () => settle(() => cb.onError("no-speech"));

  try {
    rec.start();
  } catch {
    settle(() => cb.onError("failed"));
  }

  return () => {
    settled = true;
    try {
      rec.abort();
    } catch {
      // 이미 끝난 인식은 무시
    }
  };
}

/** 판정 결과. close 는 철자가 거의 같은 말로 들린 경우다 */
export type Verdict = "correct" | "close" | "wrong";

export interface Judgement {
  verdict: Verdict;
  /** 화면에 "이렇게 들렸어요" 로 보여 줄 말 */
  heard: string;
}

/** 가타카나를 히라가나로 바꾼다. 일본어는 엔진이 어느 쪽으로 적을지 모른다 */
function toHiragana(s: string) {
  return s.replace(/[ァ-ヶ]/g, (c) =>
    String.fromCharCode(c.charCodeAt(0) - 0x60),
  );
}

/** 비교용으로 다듬는다. 대소문자·문장부호·하이픈·아포스트로피를 없애고 띄어쓰기는 한 칸으로 */
function normalize(s: string) {
  return toHiragana(s.normalize("NFKC").toLowerCase())
    .replace(/['’`\-‐]/g, "")
    .replace(/[^\p{L}\p{N}~\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/** 두 글자열이 얼마나 비슷한지 0~1 (편집 거리 기반) */
function similarity(a: string, b: string) {
  if (a === b) return 1;
  if (!a || !b) return 0;
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) {
      cur[j] = Math.min(
        prev[j] + 1,
        cur[j - 1] + 1,
        prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1),
      );
    }
    prev = cur;
  }
  return 1 - prev[b.length] / Math.max(a.length, b.length);
}

/**
 * 들은 말이 목표와 맞는지.
 * - 그대로 같거나, 앞뒤에 다른 말이 붙어도 그 단어가 통째로 들어 있으면 맞음
 * - "as ~ as possible" 처럼 물결(~)이 있으면 그 자리에 무슨 말이 와도 된다
 */
function matches(target: string, heard: string) {
  const t = normalize(target);
  const h = normalize(heard);
  if (!t || !h) return false;
  if (t.includes("~")) {
    const parts = t
      .split("~")
      .map((p) => p.trim())
      .filter(Boolean);
    let from = 0;
    for (const part of parts) {
      const at = h.indexOf(part, from);
      if (at < 0) return false;
      from = at + part.length;
    }
    return true;
  }
  if (h.replace(/ /g, "") === t.replace(/ /g, "")) return true;
  return ` ${h} `.includes(` ${t} `);
}

/**
 * 들은 말 후보들을 목표 단어와 견줘 판정한다.
 * @param targets 맞는 답으로 칠 표기들 (단어, 일본어는 읽기 가나도 함께)
 */
export function judge(targets: string[], alternatives: string[]): Judgement {
  const heard = alternatives[0] ?? "";
  const goals = targets.filter(Boolean);

  // 엔진이 둘째·셋째 후보로라도 그 단어를 들었다면 맞게 말한 것으로 본다
  for (const alt of alternatives) {
    if (goals.some((g) => matches(g, alt)))
      return { verdict: "correct", heard: alt };
  }

  let best = 0;
  for (const alt of alternatives) {
    for (const g of goals) {
      const s = similarity(
        normalize(g).replace(/[ ~]/g, ""),
        normalize(alt).replace(/ /g, ""),
      );
      best = Math.max(best, s);
    }
  }
  return { verdict: best >= 0.75 ? "close" : "wrong", heard };
}

/**
 * 마이크 소리 크기를 실시간으로 읽는다 (파형 그리기용).
 * 매 화면 갱신마다 0~1 사이 크기를 넘긴다. 음성 인식과는 따로 마이크를 연다.
 * 돌려주는 함수를 부르면 마이크를 닫는다.
 * 마이크를 열지 못하면 onUnavailable 을 부른다 (파형 대신 대체 모양을 보여 주면 된다).
 */
export function watchMicLevel(
  onLevel: (level: number) => void,
  onUnavailable: () => void,
): () => void {
  const media =
    Platform.OS === "web" && typeof navigator !== "undefined"
      ? navigator.mediaDevices
      : undefined;
  const AudioCtx =
    typeof window === "undefined"
      ? undefined
      : (window.AudioContext ??
        (window as unknown as { webkitAudioContext?: typeof AudioContext })
          .webkitAudioContext);
  if (!media?.getUserMedia || !AudioCtx) {
    onUnavailable();
    return () => {};
  }

  let closed = false;
  let frame = 0;
  let stream: MediaStream | null = null;
  let ctx: AudioContext | null = null;

  media
    .getUserMedia({ audio: true })
    .then((s) => {
      if (closed) {
        s.getTracks().forEach((tr) => tr.stop());
        return;
      }
      stream = s;
      ctx = new AudioCtx();
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 512;
      ctx.createMediaStreamSource(s).connect(analyser);
      const buf = new Float32Array(analyser.fftSize);
      const tick = () => {
        if (closed) return;
        analyser.getFloatTimeDomainData(buf);
        let sum = 0;
        for (const v of buf) sum += v * v;
        const rms = Math.sqrt(sum / buf.length);
        // 말소리의 rms 는 0.01~0.3 쯤이라 제곱근으로 펴서 작은 소리도 보이게 한다
        onLevel(Math.min(1, Math.sqrt(rms) * 1.8));
        frame = requestAnimationFrame(tick);
      };
      tick();
    })
    .catch(() => {
      if (!closed) onUnavailable();
    });

  return () => {
    closed = true;
    cancelAnimationFrame(frame);
    stream?.getTracks().forEach((tr) => tr.stop());
    ctx?.close().catch(() => {});
  };
}
