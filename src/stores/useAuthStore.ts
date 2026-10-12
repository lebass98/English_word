import { create } from "zustand";

/** 클라우드 동기화 상태. 화면 표시용이라 저장하지 않는다 */
export type SyncStatus = "off" | "syncing" | "synced" | "error";

export interface AuthUser {
  uid: string;
  email: string | null;
  name: string | null;
}

interface AuthState {
  /** 로그인 상태를 아직 확인 중이면 true */
  checking: boolean;
  user: AuthUser | null;
  sync: SyncStatus;
}

export const useAuthStore = create<AuthState>()(() => ({
  checking: true,
  user: null,
  sync: "off",
}));
