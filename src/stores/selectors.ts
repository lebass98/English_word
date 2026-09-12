import type { Grade } from "../constants/grades";
import { UNIT_SIZE, type Vocab, type Word } from "../constants/words";
import {
  dateKey,
  type DailyStat,
  type LastStudied,
  type StudyEntry,
} from "./useAppStore";

type Entries = Record<string, StudyEntry>;
type DailyLog = Record<string, DailyStat>;

/** 학년 하나에서 "외웠어요"로 판정한 단어 수 */
export function knownCountByGrade(
  entries: Entries,
  vocab: Vocab,
  gradeId: string,
): number {
  const words = vocab.byLevel[gradeId] ?? [];
  let n = 0;
  for (const w of words) if (entries[w.id]?.status === "known") n += 1;
  return n;
}

/** 유닛 하나에서 외운 단어 수 */
export function knownCountInWords(entries: Entries, words: Word[]): number {
  let n = 0;
  for (const w of words) if (entries[w.id]?.status === "known") n += 1;
  return n;
}

/** "헷갈려요"로 표시한 단어들. 최근에 표시한 것부터 */
export function unsureWords(
  entries: Entries,
  vocab: Vocab,
  limit?: number,
): Word[] {
  const picked = Object.entries(entries)
    .filter(([, e]) => e.status === "unsure")
    .sort((a, b) => b[1].updatedAt.localeCompare(a[1].updatedAt));

  const out: Word[] = [];
  for (const [wordId] of picked) {
    const found = vocab.find(wordId);
    if (found) out.push(found.word);
    if (limit && out.length >= limit) break;
  }
  return out;
}

/** 오늘 집계 */
export function todayStats(dailyLog: DailyLog): DailyStat {
  return dailyLog[dateKey()] ?? { seen: 0, known: 0 };
}

/**
 * 연속 학습 일수.
 * 오늘 아직 안 했으면 어제까지의 연속을 센다 (오늘 중에 끊긴 것으로 보지 않는다).
 */
export function streakDays(dailyLog: DailyLog): number {
  const hasStudy = (d: Date) => (dailyLog[dateKey(d)]?.seen ?? 0) > 0;

  const cursor = new Date();
  if (!hasStudy(cursor)) {
    cursor.setDate(cursor.getDate() - 1);
    if (!hasStudy(cursor)) return 0;
  }

  let n = 0;
  while (hasStudy(cursor)) {
    n += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return n;
}

export interface ContinuePoint {
  word: Word;
  gradeId: string;
  gradeLabel: string;
  gradeShort: string;
  unitNo: number;
  /** 유닛 안에서 몇 번째 단어인지 (1부터) */
  posInUnit: number;
  unitLen: number;
  /** 그 유닛에서 외운 단어 수 */
  unitKnown: number;
}

/** 이어하기 지점을 화면에 그릴 수 있는 형태로 풀어낸다 */
export function continuePoint(
  last: LastStudied | null,
  vocab: Vocab,
  grades: Grade[],
): ContinuePoint | null {
  if (!last) return null;
  const found = vocab.find(last.wordId);
  if (!found) return null;

  const { levelId: gradeId, words, index, word } = found;
  const grade = grades.find((g) => g.id === gradeId);
  const unitNo = Math.floor(index / UNIT_SIZE) + 1;
  const unitWords = words.slice((unitNo - 1) * UNIT_SIZE, unitNo * UNIT_SIZE);

  return {
    word,
    gradeId,
    gradeLabel: grade?.label ?? "",
    gradeShort: grade?.short ?? "",
    unitNo,
    posInUnit: (index % UNIT_SIZE) + 1,
    unitLen: unitWords.length,
    unitKnown: 0, // 호출부에서 entries로 채운다
  };
}

/** 아직 단어 데이터가 있는 단계만 */
export function availableGrades(grades: Grade[]) {
  return grades.filter((g) => g.totalWords > 0);
}

/** 데이터가 아직 없는 단계 (준비 중 안내용) */
export function upcomingGrades(grades: Grade[]) {
  return grades.filter((g) => g.totalWords === 0);
}
