import middle1Raw from "../data/middle1.json";
import middle2Raw from "../data/middle2.json";
import wordDetailsRaw from "../data/wordDetails.json";

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

/**
 * 발음기호·예문 등 추가 정보. 단어 철자를 키로 쓰며,
 * 준비된 단어만 채워 넣으면 화면에 자동으로 나타난다.
 */
type WordDetail = Pick<Word, "phonetic" | "pos" | "example" | "exampleKo">;
const WORD_DETAILS = wordDetailsRaw as Record<string, WordDetail>;

const toWords = (raw: unknown, prefix: string): Word[] =>
  (raw as [string, string][]).map(([word, meaning], i) => ({
    id: `${prefix}-${i + 1}`,
    word,
    meaning,
    ...WORD_DETAILS[word],
  }));

/** 학년 id → 단어 목록 */
export const WORDS_BY_GRADE: Record<string, Word[]> = {
  "middle-1": toWords(middle1Raw, "m1"),
  "middle-2": toWords(middle2Raw, "m2"),
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
