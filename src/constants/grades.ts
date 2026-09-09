export interface Grade {
  id: string;
  label: string;
  /** 해당 학년의 전체 단어 수 (데이터 연결 전 임시값) */
  totalWords: number;
}

export const GRADES: Grade[] = [
  { id: "elementary-6", label: "초등 6학년", totalWords: 500 },
  { id: "middle-1", label: "중학 1학년", totalWords: 700 },
  { id: "middle-2", label: "중학 2학년", totalWords: 800 },
  { id: "middle-3", label: "중학 3학년", totalWords: 900 },
];
