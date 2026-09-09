import { WORDS_BY_GRADE } from "./words";

export interface Grade {
  id: string;
  label: string;
  /** 해당 학년의 전체 단어 수 (데이터 연결 전 임시값) */
  totalWords: number;
}

const countWords = (gradeId: string) => WORDS_BY_GRADE[gradeId]?.length ?? 0;

export const GRADES: Grade[] = [
  { id: "middle-1", label: "중학 1학년", totalWords: countWords("middle-1") },
  { id: "middle-2", label: "중학 2학년", totalWords: countWords("middle-2") },
  { id: "middle-3", label: "중학 3학년", totalWords: countWords("middle-3") },
  { id: "high-1", label: "고등 1학년", totalWords: countWords("high-1") },
  { id: "high-2", label: "고등 2학년", totalWords: countWords("high-2") },
  { id: "high-3", label: "고등 3학년", totalWords: countWords("high-3") },
];
