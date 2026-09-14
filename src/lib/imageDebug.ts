import type { Vocab } from "../constants/words";
import { WORD_IMAGES } from "../constants/wordImages";

/**
 * 연상 그림이 아직 없는 단어를 세는 임시 도구.
 *
 * 그림을 다 그릴 때까지만 홈 코스 카드에 "300개 미완료"처럼 띄워 둔다.
 * 그림이 다 채워지면 이 파일과 쓰는 곳을 함께 지운다.
 *
 * 등록표(WORD_IMAGES)를 그 자리에서 세므로, 그림을 새로 등록하면
 * Fast Refresh 로 화면의 숫자가 곧바로 줄어든다.
 */

/**
 * 지금 등록된 그림 수. 화면에서 memo·목록 갱신 조건으로 쓴다.
 * 그림이 새로 등록되면 이 값이 바뀌어서 붙잡아 둔 개수도 다시 센다
 */
export function registeredImageCount(): number {
  return Object.keys(WORD_IMAGES).length;
}

/** 그림 조회 규칙은 학습 화면과 같아야 한다 */
function hasImage(word: { id: string; word: string; conceptId: string }) {
  return Boolean(WORD_IMAGES[word.conceptId] ?? WORD_IMAGES[word.word]);
}

export interface ImageCoverage {
  total: number;
  made: number;
  missing: number;
}

/** 코스 하나의 그림 현황 */
export function imageCoverageOf(vocab: Vocab, levelId: string): ImageCoverage {
  const words = vocab.byLevel[levelId] ?? [];
  let made = 0;
  for (const w of words) if (hasImage(w)) made += 1;
  return { total: words.length, made, missing: words.length - made };
}

/** 낱말 묶음(유닛 등)의 그림 현황 */
export function imageCoverageOfWords(
  words: { id: string; word: string; conceptId: string }[],
): ImageCoverage {
  let made = 0;
  for (const w of words) if (hasImage(w)) made += 1;
  return { total: words.length, made, missing: words.length - made };
}

/** 지금 학습 언어 전체의 그림 현황 */
export function imageCoverageAll(vocab: Vocab): ImageCoverage {
  let total = 0;
  let made = 0;
  for (const level of vocab.levels) {
    const c = imageCoverageOf(vocab, level.id);
    total += c.total;
    made += c.made;
  }
  return { total, made, missing: total - made };
}
