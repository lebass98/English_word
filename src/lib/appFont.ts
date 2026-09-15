import { cloneElement, isValidElement, type ReactElement } from "react";
import { Platform, Text } from "react-native";
import type { UiLangId } from "../i18n/strings";

/**
 * 앱 글꼴.
 *
 * - 일본어 화면: Noto Sans JP 만 쓴다
 * - 한국어·영어 화면: 프리텐다드 GOV 를 쓴다
 *
 * 글꼴 파일은 프로젝트 안에 두고 쓴다 (CDN 을 타지 않는다).
 * 웹은 public/fonts 의 woff2 를 app/+html.tsx 의 @font-face 로,
 * 네이티브는 assets/fonts 의 otf·ttf 를 expo-font 로 불러온다.
 */
export const FONT_KO = "PretendardGOV";
export const FONT_JA = "NotoSansJP";

/** 표시 언어에 맞는 글꼴 이름 */
export function fontFamilyFor(uiLang: UiLangId): string {
  return uiLang === "ja" ? FONT_JA : FONT_KO;
}

/** 네이티브에서 expo-font 로 불러올 글꼴 파일. 웹은 @font-face 로 따로 건다 */
export const NATIVE_FONTS = {
  [FONT_KO]: require("../../assets/fonts/PretendardGOV-Regular.otf"),
  [`${FONT_KO}-Bold`]: require("../../assets/fonts/PretendardGOV-Bold.otf"),
  [`${FONT_KO}-Black`]: require("../../assets/fonts/PretendardGOV-Black.otf"),
  [FONT_JA]: require("../../assets/fonts/NotoSansJP-Regular.ttf"),
  [`${FONT_JA}-Bold`]: require("../../assets/fonts/NotoSansJP-Bold.ttf"),
};

/* ── 앱 전체에 글꼴 씌우기 ─────────────────────────────────────
   React Native 는 글꼴이 부모에서 자식으로 상속되지 않아서, 글자 요소마다
   따로 지정하지 않으면 시스템 글꼴이 나온다. 화면 수백 곳을 고치는 대신
   Text 가 그려질 때 기본 글꼴을 먼저 깔아 준다.
   (className 이나 style 로 준 글꼴이 있으면 그쪽이 이긴다) */

let currentFamily = FONT_KO;
let patched = false;

/** 지금 쓸 글꼴을 바꾼다. 화면은 표시 언어가 바뀌면 어차피 다시 그려진다 */
export function setAppFontFamily(uiLang: UiLangId) {
  currentFamily = fontFamilyFor(uiLang);
  if (Platform.OS === "web") {
    // 웹은 CSS 변수로 글꼴 목록을 통째로 바꾼다 (+html.tsx 참고)
    const root = globalThis.document?.documentElement;
    if (root) root.dataset.uilang = uiLang;
  }
}

/**
 * 웹에서는 CSS 로 씌우므로 손대지 않는다. react-native-web 이 글자 요소에
 * 박아 넣는 font 축약 속성을 +html.tsx 의 선택자가 덮어쓴다.
 */
export function installAppFont() {
  if (patched || Platform.OS === "web") return;
  patched = true;

  const TextAny = Text as unknown as {
    render?: (...args: unknown[]) => unknown;
  };
  const original = TextAny.render;
  if (typeof original !== "function") return; // 내부 구조가 바뀌면 조용히 넘어간다

  TextAny.render = function patchedRender(...args: unknown[]) {
    const el = original.apply(this, args);
    if (!isValidElement(el)) return el;
    const { style } = el.props as { style?: unknown };
    // 기본 글꼴을 앞에 깔아 두면 뒤에 오는 style 이 이긴다
    return cloneElement(el as ReactElement<{ style?: unknown }>, {
      style: [{ fontFamily: currentFamily }, style],
    });
  };
}
