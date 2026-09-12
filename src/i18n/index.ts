import { useCallback } from "react";
import { useAppStore } from "../stores/useAppStore";
import { STRINGS, type StringKey, type UiLangId } from "./strings";

export { UI_LANGS, UI_LANG_NAMES } from "./strings";
export type { StringKey, UiLangId } from "./strings";

type Vars = Record<string, string | number>;

/**
 * 문구 하나를 표시 언어에 맞게 꺼낸다.
 *
 * 고른 언어에 그 문구가 아직 없으면 한국어로 대신 보여준다.
 * 그래서 새 언어를 조금씩 채워 나가도 화면이 비어 보이지 않는다.
 * `{이름}` 자리는 vars 로 넘긴 값으로 바뀐다.
 */
export function translate(
  lang: UiLangId,
  key: StringKey,
  vars?: Vars,
): string {
  const text = STRINGS[lang]?.[key] ?? STRINGS.ko[key] ?? key;
  if (!vars) return text;
  return Object.entries(vars).reduce(
    (acc, [name, value]) => acc.split(`{${name}}`).join(String(value)),
    text,
  );
}

/**
 * 화면에서 쓰는 번역 함수.
 * 표시 언어가 바뀌면 이 함수를 쓴 화면이 알아서 다시 그려진다.
 */
export function useT() {
  const lang = useAppStore((s) => s.uiLang);
  return useCallback(
    (key: StringKey, vars?: Vars) => translate(lang, key, vars),
    [lang],
  );
}

/** 훅을 쓸 수 없는 곳(스토어 바깥 등)에서 지금 언어로 번역할 때 */
export function tNow(key: StringKey, vars?: Vars): string {
  return translate(useAppStore.getState().uiLang, key, vars);
}
