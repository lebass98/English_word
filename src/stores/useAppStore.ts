import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

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

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      activeGradeId: null,
      setActiveGradeId: (id) => set({ activeGradeId: id }),

      autoAdvance: true,
      setAutoAdvance: (on) => set({ autoAdvance: on }),

      wordStatus: {},
      setWordStatus: (wordId, status) =>
        set((s) => ({ wordStatus: { ...s.wordStatus, [wordId]: status } })),
    }),
    {
      name: "wordpic-settings",
      // 네이티브는 디스크, 웹은 localStorage — 화면 이동·뒤로가기·앱 재시작에도 유지된다
      storage: createJSONStorage(() => AsyncStorage),
      // 설정값만 저장한다.
      // wordStatus는 단어 id 체계 개편(언어 접두사 도입) 전까지 저장하지 않는다 —
      // 지금 저장하면 나중에 id가 바뀔 때 기록 마이그레이션이 필요해진다.
      partialize: (s) => ({ autoAdvance: s.autoAdvance }),
    },
  ),
);
