import { create } from "zustand";

/** 단어별 학습 상태: 미학습 / 헷갈림 / 외움 */
export type WordStatus = "unseen" | "unsure" | "known";

/** 숙련도 별(3개 중 채워진 수) */
export const STARS_BY_STATUS: Record<WordStatus, number> = {
  unseen: 0,
  unsure: 1,
  known: 3,
};

interface AppState {
  /** 현재 선택된 학년 ID */
  activeGradeId: string | null;
  setActiveGradeId: (id: string | null) => void;

  /** 자동 넘김 사용 여부 (학습 화면 전역 설정) */
  autoAdvance: boolean;
  setAutoAdvance: (on: boolean) => void;

  /** 단어 id → 학습 상태 (현재는 세션 메모리에만 보관) */
  wordStatus: Record<string, WordStatus>;
  setWordStatus: (wordId: string, status: WordStatus) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeGradeId: null,
  setActiveGradeId: (id) => set({ activeGradeId: id }),

  autoAdvance: true,
  setAutoAdvance: (on) => set({ autoAdvance: on }),

  wordStatus: {},
  setWordStatus: (wordId, status) =>
    set((s) => ({ wordStatus: { ...s.wordStatus, [wordId]: status } })),
}));
