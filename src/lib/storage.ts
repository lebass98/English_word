import AsyncStorage from "@react-native-async-storage/async-storage";

/**
 * 플랫폼 공통 key-value 스토리지 추상화.
 * AsyncStorage는 네이티브에선 디스크, 웹에선 localStorage로 동작한다.
 * 나중에 MMKV/SQLite로 교체할 때 이 파일만 수정하면 된다.
 */
export const storage = {
  async get<T>(key: string): Promise<T | null> {
    const raw = await AsyncStorage.getItem(key);
    if (raw == null) return null;
    try {
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  },

  async set(key: string, value: unknown): Promise<void> {
    await AsyncStorage.setItem(key, JSON.stringify(value));
  },

  async remove(key: string): Promise<void> {
    await AsyncStorage.removeItem(key);
  },
};
