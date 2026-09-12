import { useCallback } from "react";
import { STRINGS, type StringKey } from "./strings";

export type { StringKey } from "./strings";

type Vars = Record<string, string | number>;

/**
 * 문구 하나를 꺼낸다.
 *
 * 이 앱의 화면 말은 한국어 하나다. `{이름}` 자리는 vars 로 넘긴 값으로 바뀐다.
 */
export function translate(key: StringKey, vars?: Vars): string {
  const text: string = STRINGS[key] ?? key;
  if (!vars) return text;
  return Object.entries(vars).reduce<string>(
    (acc, [name, value]) => acc.split(`{${name}}`).join(String(value)),
    text,
  );
}

/** 화면에서 쓰는 번역 함수 */
export function useT() {
  return useCallback(
    (key: StringKey, vars?: Vars) => translate(key, vars),
    [],
  );
}
