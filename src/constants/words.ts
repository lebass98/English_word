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
  /** 비슷한 뜻의 영어 단어들 */
  synonyms?: string[];
  /** 말의 유래 (한국어 한두 문장) */
  etymology?: string;
  mnemonic?: string;
  imageTag?: string;
}

export const UNIT_SIZE = 20;

/**
 * 발음기호·예문 등 추가 정보. 단어 철자를 키로 쓰며,
 * 준비된 단어만 채워 넣으면 화면에 자동으로 나타난다.
 */
type WordDetail = Pick<
  Word,
  "phonetic" | "pos" | "example" | "exampleKo" | "synonyms" | "etymology"
>;
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

/**
 * 단어 id → (학년, 인덱스) 색인.
 * 단어 목록은 모듈 로드 시 한 번 만들어지고 바뀌지 않으므로 색인도 한 번만 만든다.
 * 단어장·홈처럼 기록 수만큼 findWord를 반복하는 화면이 매번 수천 개를 훑지 않게 한다.
 */
const WORD_LOCATION = new Map<string, { gradeId: string; index: number }>();
for (const [gradeId, words] of Object.entries(WORDS_BY_GRADE)) {
  words.forEach((w, index) => WORD_LOCATION.set(w.id, { gradeId, index }));
}

/** 단어 id로 (학년, 목록, 인덱스) 찾기 */
export function findWord(wordId: string) {
  const at = WORD_LOCATION.get(wordId);
  if (!at) return null;
  const words = WORDS_BY_GRADE[at.gradeId];
  return { gradeId: at.gradeId, words, index: at.index, word: words[at.index] };
}

export interface Unit {
  unitNo: number;
  words: Word[];
}

/**
 * 학년별 유닛 목록 캐시.
 * 원본 단어 목록이 불변이라 결과도 불변이다. 같은 참조를 돌려주므로
 * 호출부에서 반환값을 변형해서는 안 된다.
 */
const UNITS_CACHE = new Map<string, Unit[]>();

export function unitsOf(gradeId: string): Unit[] {
  const cached = UNITS_CACHE.get(gradeId);
  if (cached) return cached;

  const words = WORDS_BY_GRADE[gradeId] ?? [];
  const units: Unit[] = [];
  for (let i = 0; i < words.length; i += UNIT_SIZE) {
    units.push({
      unitNo: Math.floor(i / UNIT_SIZE) + 1,
      words: words.slice(i, i + UNIT_SIZE),
    });
  }
  UNITS_CACHE.set(gradeId, units);
  return units;
}
