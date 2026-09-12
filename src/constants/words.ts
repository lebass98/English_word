import { useAppStore } from "../stores/useAppStore";
import type { UiLangId } from "../i18n/strings";
import {
  studyLanguageOf,
  type Level,
  type StudyLangId,
} from "./languages";

import enLevelMiddle1 from "../data/en/levels/middle-1.json";
import enLevelMiddle2 from "../data/en/levels/middle-2.json";
import enWords from "../data/en/words.json";
import enTrJa from "../data/en/tr/ja.json";
import enTrKo from "../data/en/tr/ko.json";

export const UNIT_SIZE = 20;

/** 유의어 하나. 뜻은 표제어의 뜻과 통하는 쪽으로 골라 둔다 */
export interface Synonym {
  word: string;
  meaning: string;
}

/** 화면에 그릴 수 있게 다 풀어낸 단어 하나 */
export interface Word {
  /** `<학습언어>-<단계약칭>-<번호>` (예: en-m1-1) */
  id: string;
  /** 학습 언어로 쓴 낱말 그 자체 */
  word: string;
  /** 아래 둘은 학습 언어에 속한다. 표시 언어가 바뀌어도 그대로다 */
  phonetic?: string;
  example?: string;
  /** 아래는 표시 언어로 된 것들 */
  meaning: string;
  exampleTr?: string;
  etymology?: string;
  synonyms?: Synonym[];
}

export interface Unit {
  unitNo: number;
  words: Word[];
}

/** 학습 언어 자체의 정보 (발음기호·예문·유의어 철자) */
interface NeutralEntry {
  phonetic?: string;
  example?: string;
  synonyms?: string[];
}

/** 표시 언어 하나의 번역 묶음 */
interface TranslationFile {
  /** 단어 id 기준. 같은 철자라도 단계마다 뜻이 다를 수 있어서 id 로 묶는다 */
  meanings: Record<string, string>;
  /** 단어 철자 기준. 예문 해석·어원·유의어 뜻은 낱말 자체의 속성이다 */
  details: Record<
    string,
    { exampleTr?: string; etymology?: string; synonymMeanings?: string[] }
  >;
}

interface LanguageData {
  /** 단계 id → 낱말 목록 (순서가 곧 번호다) */
  levels: Record<string, string[]>;
  words: Record<string, NeutralEntry>;
  tr: Partial<Record<UiLangId, TranslationFile>>;
}

const EMPTY_TR: TranslationFile = { meanings: {}, details: {} };

/**
 * 학습 언어별 원본 데이터.
 * 새 언어를 붙일 때는 여기에 항목을 추가하고 json 을 import 하면 된다.
 */
const DATA: Record<StudyLangId, LanguageData> = {
  en: {
    levels: {
      "middle-1": enLevelMiddle1 as string[],
      "middle-2": enLevelMiddle2 as string[],
    },
    words: enWords as Record<string, NeutralEntry>,
    tr: {
      ko: enTrKo as TranslationFile,
      ja: enTrJa as TranslationFile,
    },
  },
  ja: {
    levels: {},
    words: {},
    tr: {},
  },
};

/** 풀어낸 단어 모음. 표시 언어가 섞이지 않도록 언어 조합마다 따로 만든다 */
export interface Vocab {
  studyLang: StudyLangId;
  uiLang: UiLangId;
  levels: Level[];
  byLevel: Record<string, Word[]>;
  totalOf: (levelId: string) => number;
  unitsOf: (levelId: string) => Unit[];
  find: (
    wordId: string,
  ) => { levelId: string; words: Word[]; index: number; word: Word } | null;
}

function buildVocab(studyLang: StudyLangId, uiLang: UiLangId): Vocab {
  const lang = studyLanguageOf(studyLang);
  const data = DATA[studyLang];
  // 고른 표시 언어에 아직 번역이 없으면 한국어로 대신 보여준다.
  // 덕분에 새 언어를 조금씩 채워 나가도 화면이 비지 않는다.
  const tr = data.tr[uiLang] ?? data.tr.ko ?? EMPTY_TR;
  const fallback = data.tr.ko ?? EMPTY_TR;

  const pick = <T>(
    primary: T | undefined,
    backup: T | undefined,
  ): T | undefined => primary ?? backup;

  const byLevel: Record<string, Word[]> = {};
  const location = new Map<string, { levelId: string; index: number }>();

  for (const level of lang.levels) {
    const spellings = data.levels[level.id] ?? [];
    const words = spellings.map((spelling, i) => {
      const localId = `${level.code}-${i + 1}`;
      const neutral = data.words[spelling] ?? {};
      const detail = pick(tr.details[spelling], fallback.details[spelling]);
      const synonymWords = neutral.synonyms ?? [];
      const synonymMeanings = detail?.synonymMeanings ?? [];

      return {
        id: `${studyLang}-${localId}`,
        word: spelling,
        phonetic: neutral.phonetic,
        example: neutral.example,
        meaning:
          pick(tr.meanings[localId], fallback.meanings[localId]) ?? spelling,
        exampleTr: detail?.exampleTr,
        etymology: detail?.etymology,
        synonyms: synonymWords.length
          ? synonymWords.map((w, k) => ({
              word: w,
              meaning: synonymMeanings[k] ?? "",
            }))
          : undefined,
      } satisfies Word;
    });

    byLevel[level.id] = words;
    words.forEach((w, index) =>
      location.set(w.id, { levelId: level.id, index }),
    );
  }

  const unitCache = new Map<string, Unit[]>();

  return {
    studyLang,
    uiLang,
    levels: lang.levels,
    byLevel,
    totalOf: (levelId) => byLevel[levelId]?.length ?? 0,
    unitsOf: (levelId) => {
      const cached = unitCache.get(levelId);
      if (cached) return cached;
      const words = byLevel[levelId] ?? [];
      const units: Unit[] = [];
      for (let i = 0; i < words.length; i += UNIT_SIZE) {
        units.push({
          unitNo: Math.floor(i / UNIT_SIZE) + 1,
          words: words.slice(i, i + UNIT_SIZE),
        });
      }
      unitCache.set(levelId, units);
      return units;
    },
    find: (wordId) => {
      const at = location.get(wordId);
      if (!at) return null;
      const words = byLevel[at.levelId];
      return {
        levelId: at.levelId,
        words,
        index: at.index,
        word: words[at.index],
      };
    },
  };
}

/**
 * 언어 조합마다 한 번만 만들어 두고 다시 쓴다.
 * 단어가 2천 개라 화면을 그릴 때마다 새로 만들면 낭비다.
 */
const VOCAB_CACHE = new Map<string, Vocab>();

export function getVocab(studyLang: StudyLangId, uiLang: UiLangId): Vocab {
  const key = `${studyLang}:${uiLang}`;
  const cached = VOCAB_CACHE.get(key);
  if (cached) return cached;
  const built = buildVocab(studyLang, uiLang);
  VOCAB_CACHE.set(key, built);
  return built;
}

/** 화면에서 쓰는 단어 모음. 언어를 바꾸면 알아서 다시 그려진다 */
export function useVocab(): Vocab {
  const studyLang = useAppStore((s) => s.studyLang);
  const uiLang = useAppStore((s) => s.uiLang);
  return getVocab(studyLang, uiLang);
}

/** 훅을 쓸 수 없는 곳에서 지금 언어의 단어 모음이 필요할 때 */
export function currentVocab(): Vocab {
  const { studyLang, uiLang } = useAppStore.getState();
  return getVocab(studyLang, uiLang);
}
