import middle1Raw from "../data/middle1.json";
import middle2Raw from "../data/middle2.json";

export interface Word {
  id: string;
  word: string;
  meaning: string;
  /** 아래는 컨텐츠가 준비되면 채우는 선택 필드 */
  phonetic?: string;
  pos?: string;
  example?: string;
  exampleKo?: string;
  mnemonic?: string;
  imageTag?: string;
}

export const UNIT_SIZE = 20;

/** 학년 id → 단어 목록 */
export const WORDS_BY_GRADE: Record<string, Word[]> = {
  "middle-1": (middle1Raw as [string, string][]).map(([word, meaning], i) => ({
    id: `m1-${i + 1}`,
    word,
    meaning,
  })),
  "middle-2": (middle2Raw as [string, string][]).map(([word, meaning], i) => ({
    id: `m2-${i + 1}`,
    word,
    meaning,
  })),
};

/** 단어 id로 (학년, 목록, 인덱스) 찾기 */
export function findWord(wordId: string) {
  for (const [gradeId, words] of Object.entries(WORDS_BY_GRADE)) {
    const index = words.findIndex((w) => w.id === wordId);
    if (index >= 0) return { gradeId, words, index, word: words[index] };
  }
  return null;
}

export function unitsOf(gradeId: string) {
  const words = WORDS_BY_GRADE[gradeId] ?? [];
  const units = [];
  for (let i = 0; i < words.length; i += UNIT_SIZE) {
    units.push({
      unitNo: Math.floor(i / UNIT_SIZE) + 1,
      words: words.slice(i, i + UNIT_SIZE),
    });
  }
  return units;
}
