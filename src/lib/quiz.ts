import type { Word } from "../constants/words";
import { WORD_IMAGES } from "../constants/wordImages";
import type { StudyEntry, WordStatus } from "../stores/useAppStore";

/** 한 판에 푸는 문제 수 */
export const QUIZ_SIZE = 20;

/** 유닛 하나를 끝냈을 때 바로 이어지는 확인 퀴즈의 문제 수 */
export const UNIT_QUIZ_SIZE = 8;

/** 한 문제에 주는 보기 수 */
export const CHOICE_COUNT = 4;

/** 철자 맞추기에서 틀릴 수 있는 횟수 */
export const SPELLING_LIVES = 6;

/**
 * 문제 유형.
 *
 * 재인(알아보기)과 인출(직접 떠올리기)을 섞어야 한쪽으로만 외우는 걸 막는다.
 * 한 판에 여러 유형이 번갈아 나오면 다음 문제를 예측할 수 없어 덜 지루하다.
 */
export const QUIZ_KINDS = [
  /** 그림을 보고 단어 고르기 */
  "imageToWord",
  /** 단어를 보고 그림 고르기 */
  "wordToImage",
  /** 단어를 보고 뜻 고르기 */
  "wordToMeaning",
  /** 뜻을 보고 단어 고르기 */
  "meaningToWord",
  /** 발음을 듣고 단어 고르기 */
  "listenToWord",
  /** 예문 빈칸에 들어갈 단어 고르기 */
  "cloze",
  /** 철자 맞추기 (글자를 하나씩 고른다) */
  "spelling",
] as const;

export type QuizKind = (typeof QUIZ_KINDS)[number];

/** 주소에 실려 온 값이 아는 유형인지 가려낸다 */
export function isQuizKind(value: unknown): value is QuizKind {
  return (
    typeof value === "string" && (QUIZ_KINDS as readonly string[]).includes(value)
  );
}

/** 예문에서 정답 단어를 빈칸으로 바꾼 조각 */
export interface Cloze {
  before: string;
  after: string;
  /** 빈칸에 실제로 들어 있던 형태 (joined 처럼 활용형일 수 있다) */
  surface: string;
}

export interface QuizQuestion {
  /** 정답 단어 */
  answer: Word;
  /** 정답을 포함해 섞어 둔 보기. 철자 맞추기에서는 쓰지 않는다 */
  choices: Word[];
  kind: QuizKind;
  /** cloze 문제에서만 채워진다 */
  cloze?: Cloze;
}

/**
 * 뽑기 가중치.
 * 헷갈린 단어를 가장 자주, 외운 단어를 가장 드물게 낸다.
 * 순수 무작위로 뽑으면 방금 틀린 단어가 다시 안 나와서 복습이 안 된다.
 */
const WEIGHT: Record<WordStatus, number> = {
  unsure: 6,
  unseen: 3,
  known: 1,
};

/** 철자 맞추기로 낼 수 있는 길이. 너무 짧으면 싱겁고 길면 지친다 */
const SPELLING_MIN = 3;
const SPELLING_MAX = 10;

/** 학습 화면과 같은 규칙으로 그림을 찾는다 */
export function imageOf(word: Word) {
  return WORD_IMAGES[word.conceptId] ?? WORD_IMAGES[word.word];
}

/** 그림이 있는 단어만 그림 문제로 낼 수 있다 */
export function hasImage(word: Word): boolean {
  return Boolean(imageOf(word));
}

/** 뜻이 단어 철자 그대로면(= 번역이 아직 없으면) 뜻 문제로 쓸 수 없다 */
export function hasMeaning(word: Word): boolean {
  const m = word.meaning?.trim();
  return Boolean(m) && m !== word.word;
}

/** 알파벳 한 낱말이고 길이가 알맞아야 철자 문제로 낼 수 있다 */
export function spellable(word: Word): boolean {
  const w = word.word;
  return (
    /^[a-zA-Z]+$/.test(w) && w.length >= SPELLING_MIN && w.length <= SPELLING_MAX
  );
}

/** 정규식에 넣기 전에 특수문자를 막는다 */
function escapeRe(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * 예문에서 정답 단어를 찾아 빈칸으로 바꾼다.
 *
 * 예문에는 활용형이 들어 있는 경우가 많다 (join → joined, hide → hid).
 * 그래서 낱말 그대로 찾아본 뒤, 없으면 앞 글자가 충분히 겹치는 낱말을 찾는다.
 * 그래도 못 찾으면 이 단어는 빈칸 문제로 내지 않는다.
 */
export function clozeOf(word: Word): Cloze | null {
  const sentence = word.example?.trim();
  const target = word.word;
  if (!sentence || !/^[a-zA-Z]+$/.test(target)) return null;

  const exact = new RegExp(`\\b${escapeRe(target)}\\b`, "i");
  const hit = exact.exec(sentence);
  if (hit) {
    return {
      before: sentence.slice(0, hit.index),
      after: sentence.slice(hit.index + hit[0].length),
      surface: hit[0],
    };
  }

  // 활용형을 찾는다. 원형과 앞부분이 이만큼 겹쳐야 같은 낱말로 본다
  const need = Math.max(3, target.length - 2);
  if (target.length < need) return null;
  const stem = target.slice(0, need).toLowerCase();

  for (const m of sentence.matchAll(/[a-zA-Z]+/g)) {
    const token = m[0];
    if (token.length < need) continue;
    if (token.toLowerCase().startsWith(stem)) {
      const at = m.index ?? 0;
      return {
        before: sentence.slice(0, at),
        after: sentence.slice(at + token.length),
        surface: token,
      };
    }
  }
  return null;
}

/** 그 유형으로 이 단어를 낼 수 있는지 */
function supports(word: Word, kind: QuizKind): boolean {
  switch (kind) {
    case "imageToWord":
    case "wordToImage":
      return hasImage(word);
    case "wordToMeaning":
    case "meaningToWord":
      return hasMeaning(word);
    case "listenToWord":
      return true;
    case "cloze":
      return clozeOf(word) !== null;
    case "spelling":
      return spellable(word) && (hasImage(word) || hasMeaning(word));
  }
}

/** 그 유형의 보기로 쓸 수 있는지. 정답과 조건이 다를 수 있다 */
function usableAsChoice(word: Word, kind: QuizKind): boolean {
  switch (kind) {
    case "imageToWord":
    case "wordToImage":
      return hasImage(word);
    case "wordToMeaning":
    case "meaningToWord":
      return hasMeaning(word);
    default:
      return true;
  }
}

function statusOf(entries: Record<string, StudyEntry>, word: Word): WordStatus {
  return entries[word.id]?.status ?? "unseen";
}

/** 배열을 섞는다 (피셔-예이츠) */
function shuffle<T>(list: T[]): T[] {
  const out = [...list];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/**
 * 가중치를 반영해 중복 없이 count 개를 뽑는다.
 * 뽑을 때마다 후보에서 빼므로 같은 단어가 두 번 나오지 않는다.
 */
function pickWeighted(
  pool: Word[],
  entries: Record<string, StudyEntry>,
  count: number,
): Word[] {
  const rest = [...pool];
  const weights = rest.map((w) => WEIGHT[statusOf(entries, w)]);
  const picked: Word[] = [];

  while (picked.length < count && rest.length > 0) {
    let total = 0;
    for (const w of weights) total += w;

    let roll = Math.random() * total;
    let index = rest.length - 1;
    for (let i = 0; i < rest.length; i++) {
      roll -= weights[i];
      if (roll <= 0) {
        index = i;
        break;
      }
    }

    picked.push(rest[index]);
    rest.splice(index, 1);
    weights.splice(index, 1);
  }

  return picked;
}

/**
 * 한 판치 문제를 만든다.
 *
 * 학년 전체에서 뽑으므로 유닛 경계가 없다. 대신 20문제로 끊어서
 * "한 판 끝냈다"는 매듭과 점수는 남긴다.
 * 유형은 돌아가며 배정하되, 그 단어로 낼 수 없는 유형은 건너뛴다.
 */
export function buildQuiz(
  words: Word[],
  entries: Record<string, StudyEntry>,
  size: number = QUIZ_SIZE,
  kinds: readonly QuizKind[] = QUIZ_KINDS,
  /**
   * 오답 보기를 가져올 단어 목록. 없으면 문제로 낼 단어와 같은 목록을 쓴다.
   *
   * 유닛 하나(20단어)만으로 문제를 내면 보기가 늘 같은 얼굴이라 금방 외워진다.
   * 그래서 문제는 유닛에서 내되 오답은 학년 전체에서 가져온다.
   */
  choicePool: Word[] = words,
): QuizQuestion[] {
  // 어떤 유형으로도 낼 수 없는 단어는 애초에 뽑지 않는다
  const pool = words.filter((w) => kinds.some((k) => supports(w, k)));
  if (pool.length === 0) return [];
  const choices = choicePool.filter((w) =>
    kinds.some((k) => supports(w, k)),
  );
  if (choices.length < CHOICE_COUNT) return [];

  const answers = pickWeighted(pool, entries, Math.min(size, pool.length));
  // 유형 순서를 판마다 섞어 같은 차례로 반복되지 않게 한다
  const rotation = shuffle([...kinds]);

  const questions: QuizQuestion[] = [];
  answers.forEach((answer, i) => {
    // 이번 차례부터 훑어 이 단어로 낼 수 있는 유형을 찾는다
    let kind: QuizKind | null = null;
    for (let step = 0; step < rotation.length; step++) {
      const candidate = rotation[(i + step) % rotation.length];
      if (supports(answer, candidate)) {
        kind = candidate;
        break;
      }
    }
    if (!kind) return;

    /*
     * 정답과 같은 뜻을 가리키는 단어는 오답으로 쓰면 안 된다.
     *
     * 개념이 다른데 뜻풀이가 똑같은 짝도 있다 (giant / huge 둘 다 "거대한").
     * 뜻을 다루는 유형에서 이런 짝이 보기에 같이 들어가면 답이 둘이 되므로 뺀다.
     */
    const meaningKind = kind === "wordToMeaning" || kind === "meaningToWord";
    const others = choices.filter(
      (w) =>
        w.conceptId !== answer.conceptId &&
        usableAsChoice(w, kind) &&
        !(meaningKind && w.meaning === answer.meaning),
    );
    const distractors = shuffle(others).slice(0, CHOICE_COUNT - 1);
    // 보기가 모자라면 찍기 문제가 되므로 내지 않는다 (철자 맞추기는 보기가 없다)
    if (kind !== "spelling" && distractors.length < CHOICE_COUNT - 1) return;

    questions.push({
      answer,
      choices: shuffle([answer, ...distractors]),
      kind,
      cloze: kind === "cloze" ? (clozeOf(answer) ?? undefined) : undefined,
    });
  });

  return questions;
}

/** 맞힌 개수로 100점 만점 점수를 낸다 */
export function scoreOf(correct: number, total: number): number {
  if (total <= 0) return 0;
  return Math.round((correct / total) * 100);
}
