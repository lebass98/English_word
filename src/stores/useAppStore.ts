import { create } from "zustand";

interface AppState {
  /** 현재 선택된 학년 ID */
  activeGradeId: string | null;
  setActiveGradeId: (id: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeGradeId: null,
  setActiveGradeId: (id) => set({ activeGradeId: id }),
}));
