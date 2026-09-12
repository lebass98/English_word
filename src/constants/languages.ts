/**
 * 학습 언어 정의.
 *
 * 표시 언어(앱 화면의 말)와 학습 언어(지금 배우는 말)는 서로 다른 축이다.
 * 한국어 화면으로 영어를 배울 수도 있고, 일본어 화면으로 영어를 배울 수도 있고,
 * 한국어 화면으로 일본어를 배울 수도 있다.
 *
 * 단계 이름은 여기에 두지 않는다. "중학 1학년"은 표시 언어에 따라 달라지므로
 * src/i18n/strings.ts 의 `level.<단계id>.label` / `.short` 에서 가져온다.
 */

export const STUDY_LANGS = ["en", "ja"] as const;
export type StudyLangId = (typeof STUDY_LANGS)[number];

/** 코스 단계 하나. code 는 단어 id 에 들어가는 짧은 표시다 (middle-1 → m1) */
export interface Level {
  id: string;
  code: string;
}

export interface StudyLanguage {
  id: StudyLangId;
  /** 발음 재생에 쓰는 음성 언어 코드 */
  speechCode: string;
  /** 코스 단계 목록 (순서대로 보여준다) */
  levels: Level[];
}

export const STUDY_LANGUAGES: Record<StudyLangId, StudyLanguage> = {
  en: {
    id: "en",
    speechCode: "en-US",
    levels: [
      { id: "middle-1", code: "m1" },
      { id: "middle-2", code: "m2" },
      { id: "middle-3", code: "m3" },
      { id: "high-1", code: "h1" },
      { id: "high-2", code: "h2" },
      { id: "high-3", code: "h3" },
    ],
  },
  ja: {
    id: "ja",
    speechCode: "ja-JP",
    levels: [
      { id: "jlpt-n5", code: "n5" },
      { id: "jlpt-n4", code: "n4" },
      { id: "jlpt-n3", code: "n3" },
      { id: "jlpt-n2", code: "n2" },
      { id: "jlpt-n1", code: "n1" },
    ],
  },
};

export function studyLanguageOf(id: StudyLangId): StudyLanguage {
  return STUDY_LANGUAGES[id] ?? STUDY_LANGUAGES.en;
}

/** 단어 id 는 `<학습언어>-<단계약칭>-<번호>` 꼴이다 (예: en-m1-1) */
export function studyLangOfWordId(wordId: string): StudyLangId {
  const head = wordId.split("-")[0];
  return (STUDY_LANGS as readonly string[]).includes(head)
    ? (head as StudyLangId)
    : "en";
}
