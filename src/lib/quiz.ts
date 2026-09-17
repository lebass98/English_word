import type { Word } from "../constants/words";
import { WORD_IMAGES } from "../constants/wordImages";
import type { StudyEntry, WordStatus } from "../stores/useAppStore";

/** 한 판에 푸는 문제 수 */
export const QUIZ_SIZE = 20;

/** 한 문제에 주는 보기 수 */
export const CHOICE_COUNT = 4;

/**
 * 문제 유형.
 * 그림을 보고 단어를 고르거나(재인), 단어를 보고 그림을 고른다(연상).
 * 둘을 섞어야 한쪽 방향으로만 외우는 걸 막는다.
 */
export type QuizKind = "imageToWord" | "wordToImage";

export interface QuizQuestion {
  /** 정답 단어 */
  answer: Word;
  /** 정답을 포함해 섞어 둔 보기 */
  choices: Word[];
  kind: QuizKind;
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

/** 그림이 있는 단어만 문제로 낼 수 있다 */
export function hasImage(word: Word): boolean {
  return Boolean(WORD_IMAGES[word.conceptId] ?? WORD_IMAGES[word.word]);
}

/** 학습 화면과 같은 규칙으로 그림을 찾는다 */
export function imageOf(word: Word) {
  return WORD_IMAGES[word.conceptId] ?? WORD_IMAGES[word.word];
}

function statusOf(
  entries: Record<string, StudyEntry>,
  word: Word,
): WordStatus {
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
 */
export function buildQuiz(
  words: Word[],
  entries: Record<string, StudyEntry>,
  size: number = QUIZ_SIZE,
): QuizQuestion[] {
  // 그림이 없는 단어는 보기로도 쓸 수 없다
  const pool = words.filter(hasImage);
  if (pool.length < CHOICE_COUNT) return [];

  const answers = pickWeighted(pool, entries, Math.min(size, pool.length));

  return answers.map((answer, i) => {
    // 정답과 같은 뜻을 가리키는 단어는 오답으로 쓰면 안 된다
    const others = pool.filter((w) => w.conceptId !== answer.conceptId);
    const distractors = shuffle(others).slice(0, CHOICE_COUNT - 1);

    return {
      answer,
      choices: shuffle([answer, ...distractors]),
      // 유형을 번갈아 내되 순서는 고정한다. 같은 유형이 내리 나오면 지루하다
      kind: i % 2 === 0 ? "imageToWord" : "wordToImage",
    } satisfies QuizQuestion;
  });
}

/** 맞힌 개수로 100점 만점 점수를 낸다 */
export function scoreOf(correct: number, total: number): number {
  if (total <= 0) return 0;
  return Math.round((correct / total) * 100);
}
