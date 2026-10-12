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
  /** 운영자 계정으로 로그인했는지 (src/lib/admin.ts) */
  isAdmin: boolean;
  /** 운영자인지 아직 가려내는 중이면 true */
  adminChecking: boolean;
  sync: SyncStatus;
}

export const useAuthStore = create<AuthState>()(() => ({
  checking: true,
  user: null,
  isAdmin: false,
  adminChecking: false,
  sync: "off",
}));
