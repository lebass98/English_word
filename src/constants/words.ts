import { useAppStore } from "../stores/useAppStore";
import {
  studyLangOfWordId,
  studyLanguageOf,
  type Level,
  type StudyLangId,
} from "./languages";
import type { UiLangId } from "../i18n/strings";

import enLevelMiddle1 from "../data/en/levels/middle-1.json";
import enLevelMiddle2 from "../data/en/levels/middle-2.json";
import enLevelMiddle3 from "../data/en/levels/middle-3.json";
import enLevelHigh1 from "../data/en/levels/high-1.json";
import enLevelHigh2 from "../data/en/levels/high-2.json";
import enLevelHigh3 from "../data/en/levels/high-3.json";
import enTrJa from "../data/en/tr/ja.json";
import enTrKo from "../data/en/tr/ko.json";
import enWords from "../data/en/words.json";
import jaLevelN5 from "../data/ja/levels/jlpt-n5.json";
import jaTrKo from "../data/ja/tr/ko.json";
import jaWords from "../data/ja/words.json";

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
  /**
   * 이 낱말이 가리키는 뜻의 이름.
   * 연상 이미지는 낱말이 아니라 이 뜻에 붙는다. 그래서 영어 beyond 와
   * 일본어 越える 가 같은 개념을 가리키면 그림 한 장을 함께 쓴다.
   */
  conceptId: string;
  /** 읽는 법. 영어는 발음기호, 일본어는 가나 */
  phonetic?: string;
  /**
   * 품사 코드 (noun, verb, i-adj …). 뜻이 여러 개면 여럿이 온다.
   * 화면에 보일 이름은 표시 언어에 따라 달라지므로 i18n 의
   * `pos.<코드>` 에서 가져온다.
   */
  pos?: string[];
  /** 학습 언어로 쓴 예문 */
  example?: string;
  /** 아래는 한국어로 된 것들 */
  meaning: string;
  exampleTr?: string;
  etymology?: string;
  synonyms?: Synonym[];
}

export interface Unit {
  unitNo: number;
  words: Word[];
}

/** 학습 언어 자체의 정보. 한국어 뜻과 섞이지 않는 부분이다 */
interface NeutralEntry {
  conceptId?: string;
  phonetic?: string;
  pos?: string[];
  example?: string;
  synonyms?: string[];
}

/** 한국어 번역 묶음 */
interface TranslationFile {
  /** 단어 id 기준. 같은 낱말이라도 단계마다 뜻이 다를 수 있어서 id 로 묶는다 */
  meanings: Record<string, string>;
  /** 낱말 기준. 예문 해석·어원·유의어 뜻은 낱말 자체의 속성이다 */
  details: Record<
    string,
    { exampleTr?: string; etymology?: string; synonymMeanings?: string[] }
  >;
}

interface LanguageData {
  /** 단계 id → 낱말 목록 (순서가 곧 번호다) */
  levels: Record<string, string[]>;
  words: Record<string, NeutralEntry>;
  /** 표시 언어별 뜻·해석 */
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
      "middle-3": enLevelMiddle3 as string[],
      "high-1": enLevelHigh1 as string[],
      "high-2": enLevelHigh2 as string[],
      "high-3": enLevelHigh3 as string[],
    },
    words: enWords as Record<string, NeutralEntry>,
    tr: {
      ko: enTrKo as TranslationFile,
      ja: enTrJa as TranslationFile,
    },
  },
  ja: {
    levels: {
      "jlpt-n5": jaLevelN5 as string[],
    },
    words: jaWords as Record<string, NeutralEntry>,
    // 일본어 단어는 한국인 학습자용이라 한국어 뜻만 있다
    tr: { ko: jaTrKo as TranslationFile },
  },
};

/** 풀어낸 단어 모음 */
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
  // 고른 표시 언어에 아직 번역이 없으면 한국어로 대신 보여준다
  const tr = data.tr[uiLang] ?? data.tr.ko ?? EMPTY_TR;
  const fallback = data.tr.ko ?? EMPTY_TR;

  /**
   * 상세 정보는 항목 단위가 아니라 칸 단위로 채운다.
   * 예문 해석만 번역되고 어원은 아직인 단어가 있는데, 항목째로 갈아 끼우면
   * 번역이 있는 칸 하나 때문에 나머지가 통째로 사라진다.
   */
  const mergeDetail = (spelling: string) => ({
    ...fallback.details[spelling],
    ...tr.details[spelling],
  });

  const byLevel: Record<string, Word[]> = {};
  const location = new Map<string, { levelId: string; index: number }>();

  for (const level of lang.levels) {
    const spellings = data.levels[level.id] ?? [];
    const words = spellings.map((spelling, i) => {
      const localId = `${level.code}-${i + 1}`;
      const neutral = data.words[spelling] ?? {};
      const detail = mergeDetail(spelling);
      const synonymWords = neutral.synonyms ?? [];
      const synonymMeanings = detail.synonymMeanings ?? [];

      return {
        id: `${studyLang}-${localId}`,
        word: spelling,
        // 개념을 따로 안 적어 둔 낱말은 낱말 자신을 개념으로 본다
        conceptId: neutral.conceptId ?? spelling,
        phonetic: neutral.phonetic,
        pos: neutral.pos,
        example: neutral.example,
        meaning: tr.meanings[localId] ?? fallback.meanings[localId] ?? spelling,
        exampleTr: detail.exampleTr,
        etymology: detail.etymology,
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
 * 학습 언어마다 한 번만 만들어 두고 다시 쓴다.
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

/**
 * 단어 id 가 가리키는 언어의 단어 모음.
 *
 * 단어 id 앞에 학습 언어가 붙어 있으므로(en-m1-1, ja-n5-1) 지금 설정과
 * 상관없이 그 단어가 속한 언어에서 찾는다. 주소로 바로 들어오거나
 * 단어장에서 다른 언어의 단어를 눌러도 화면이 제대로 뜬다.
 */
export function vocabForWordId(wordId: string): Vocab {
  return getVocab(studyLangOfWordId(wordId), useAppStore.getState().uiLang);
}

/** 화면에서 단어 id 가 가리키는 언어의 단어 모음이 필요할 때 */
export function useVocabForWordId(wordId: string): Vocab {
  const uiLang = useAppStore((s) => s.uiLang);
  return getVocab(studyLangOfWordId(wordId), uiLang);
}

/** 훅을 쓸 수 없는 곳에서 지금 학습 언어의 단어 모음이 필요할 때 */
export function currentVocab(): Vocab {
  const { studyLang, uiLang } = useAppStore.getState();
  return getVocab(studyLang, uiLang);
}
