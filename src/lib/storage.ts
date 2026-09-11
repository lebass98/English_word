import AsyncStorage, {
  type AsyncStorageStatic,
} from "@react-native-async-storage/async-storage";

/**
 * 저장할 곳이 없을 때 쓰는 빈 저장소.
 *
 * expo-router는 웹 화면을 먼저 Node에서 한 번 그려본다(SSR). 그런데 AsyncStorage의
 * 웹 구현은 window.localStorage를 그대로 부르기 때문에, window가 없는 Node에서는
 * "ReferenceError: window is not defined"로 개발 서버 프로세스까지 통째로 죽는다.
 * 그래서 window가 없는 동안에는 읽기·쓰기를 조용히 흘려보낸다.
 * 브라우저에서 다시 그릴 때 진짜 저장소로 붙으므로 사용자 기록은 잃지 않는다.
 */
const noopStorage: Pick<
  AsyncStorageStatic,
  "getItem" | "setItem" | "removeItem"
> = {
  getItem: async () => null,
  setItem: async () => undefined,
  removeItem: async () => undefined,
};

/** 네이티브에도 window는 정의돼 있다. 정말로 없는 건 Node(SSR)뿐이다 */
const hasWindow = typeof window !== "undefined";

/**
 * zustand persist에 넘기는 저장소.
 * 네이티브는 디스크, 브라우저는 localStorage, Node(SSR)에서는 아무것도 하지 않는다.
 */
export const persistStorage = hasWindow ? AsyncStorage : noopStorage;

/**
 * 플랫폼 공통 key-value 스토리지 추상화.
 * AsyncStorage는 네이티브에선 디스크, 웹에선 localStorage로 동작한다.
 * 나중에 MMKV/SQLite로 교체할 때 이 파일만 수정하면 된다.
 */
export const storage = {
  async get<T>(key: string): Promise<T | null> {
    const raw = await persistStorage.getItem(key);
    if (raw == null) return null;
    try {
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  },

  async set(key: string, value: unknown): Promise<void> {
    await persistStorage.setItem(key, JSON.stringify(value));
  },

  async remove(key: string): Promise<void> {
    await persistStorage.removeItem(key);
  },
};
