import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { persistStorage } from "../lib/storage";

/** 단어별 학습 상태: 미학습 / 헷갈림 / 외움 */
export type WordStatus = "unseen" | "unsure" | "known";

/** 숙련도 별(3개 중 채워진 수) */
export const STARS_BY_STATUS: Record<WordStatus, number> = {
  unseen: 0,
  unsure: 1,
  known: 3,
};

/** 단어 하나의 학습 기록 */
export interface StudyEntry {
  status: WordStatus;
  /** 마지막으로 판정한 시각 (ISO). 나중에 복습 주기를 계산할 때 쓴다 */
  updatedAt: string;
}

/** 이어하기 지점 */
export interface LastStudied {
  wordId: string;
  gradeId: string;
  updatedAt: string;
}

/** 하루치 집계 */
export interface DailyStat {
  /** 오늘 학습 화면에서 본 단어 수 */
  seen: number;
  /** 오늘 "외웠어요"로 판정한 단어 수 */
  known: number;
}

/** 일별 기록 보관 기간. 스트릭 계산에 필요한 만큼만 남긴다 */
const DAILY_LOG_KEEP_DAYS = 60;

/** 기기 로컬 자정 기준 날짜 키 (YYYY-MM-DD) */
export function dateKey(d: Date = new Date()): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** 오래된 일별 기록을 잘라낸다 */
function trimDailyLog(
  log: Record<string, DailyStat>,
): Record<string, DailyStat> {
  const keys = Object.keys(log).sort();
  if (keys.length <= DAILY_LOG_KEEP_DAYS) return log;
  const next: Record<string, DailyStat> = {};
  for (const k of keys.slice(-DAILY_LOG_KEEP_DAYS)) next[k] = log[k];
  return next;
}

interface AppState {
  /** 저장소에서 값을 다 읽어왔는지. 읽기 전에 빈 화면을 보여주지 않으려고 쓴다 */
  hydrated: boolean;

  /** 현재 선택된 학년 ID */
  activeGradeId: string | null;
  setActiveGradeId: (id: string | null) => void;

  /** 자동 넘김 사용 여부 (학습 화면 전역 설정) */
  autoAdvance: boolean;
  setAutoAdvance: (on: boolean) => void;

  /** 단어 id → 학습 기록 */
  entries: Record<string, StudyEntry>;
  /** 마지막으로 본 단어 (이어하기 지점) */
  lastStudied: LastStudied | null;
  /** 날짜별 집계 */
  dailyLog: Record<string, DailyStat>;
  /** 사용자가 정한 이름 (설정 화면에서 변경) */
  nickname: string;

  /**
   * 학습 화면에 단어가 떴을 때 호출한다.
   * 이어하기 지점을 갱신하고 "오늘 본 단어"를 센다.
   * 판정 버튼이 아니라 화면 진입 시점이어야 자동 넘김으로 지나간 단어도 집계된다.
   */
  markSeen: (wordId: string, gradeId: string) => void;

  /** "외웠어요 / 아직 헷갈려요" 판정. 기록과 일별 집계를 한 번에 갱신한다 */
  recordStudy: (wordId: string, status: WordStatus) => void;

  setNickname: (name: string) => void;
  /** 학습 기록 전체 삭제 (설정 화면) */
  resetProgress: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      hydrated: false,

      activeGradeId: null,
      setActiveGradeId: (id) => set({ activeGradeId: id }),

      autoAdvance: true,
      setAutoAdvance: (on) => set({ autoAdvance: on }),

      entries: {},
      lastStudied: null,
      dailyLog: {},
      nickname: "",

      markSeen: (wordId, gradeId) =>
        set((s) => {
          const today = dateKey();
          // 같은 단어를 오늘 이미 봤다면 "오늘 본 단어"를 중복해서 세지 않는다
          const sameWordToday =
            s.lastStudied?.wordId === wordId &&
            s.lastStudied.updatedAt.slice(0, 10) === today;
          const prev = s.dailyLog[today] ?? { seen: 0, known: 0 };

          return {
            lastStudied: {
              wordId,
              gradeId,
              updatedAt: new Date().toISOString(),
            },
            dailyLog: sameWordToday
              ? s.dailyLog
              : trimDailyLog({
                  ...s.dailyLog,
                  [today]: { ...prev, seen: prev.seen + 1 },
                }),
          };
        }),

      recordStudy: (wordId, status) =>
        set((s) => {
          const today = dateKey();
          const prev = s.dailyLog[today] ?? { seen: 0, known: 0 };
          // 이미 외운 단어를 또 외웠다고 눌러도 오늘 개수는 한 번만 는다
          const wasKnown = s.entries[wordId]?.status === "known";
          const knownDelta = status === "known" && !wasKnown ? 1 : 0;

          return {
            entries: {
              ...s.entries,
              [wordId]: { status, updatedAt: new Date().toISOString() },
            },
            dailyLog: trimDailyLog({
              ...s.dailyLog,
              [today]: { ...prev, known: prev.known + knownDelta },
            }),
          };
        }),

      setNickname: (name) => set({ nickname: name }),

      resetProgress: () =>
        set({ entries: {}, lastStudied: null, dailyLog: {} }),
    }),
    {
      name: "wordpic-store",
      version: 1,
      // 네이티브는 디스크, 웹은 localStorage — 화면 이동·뒤로가기·앱 재시작에도 유지된다.
      // Node(SSR)에서는 빈 저장소로 떨어져 window 참조로 죽지 않는다
      storage: createJSONStorage(() => persistStorage),
      // hydrated는 저장하지 않는다. 매 실행마다 false에서 시작해야 한다
      partialize: (s) => ({
        autoAdvance: s.autoAdvance,
        activeGradeId: s.activeGradeId,
        entries: s.entries,
        lastStudied: s.lastStudied,
        dailyLog: s.dailyLog,
        nickname: s.nickname,
      }),
      // NOTE: entries·lastStudied의 키는 단어 id(m1-N / m2-N)다.
      // 나중에 언어 접두사(en-m1-N)를 도입할 때 version을 2로 올리고
      // 여기서 키를 기계적으로 바꿔 주면 기존 기록을 잃지 않는다.
      onRehydrateStorage: () => () => {
        useAppStore.setState({ hydrated: true });
      },
    },
  ),
);
