import { ScrollViewStyleReset } from "expo-router/html";
import type { PropsWithChildren } from "react";

/**
 * 웹에서만 쓰는 HTML 뼈대.
 *
 * 여기서 일본어 글꼴(Noto Sans JP)을 불러온다. 한글은 이 글꼴에 없으므로
 * 글꼴 목록 뒤쪽의 한글 글꼴로 자동으로 넘어간다. 덕분에 한 벌의 목록으로
 * 일본어는 Noto Sans JP, 한국어는 기존 글꼴로 나온다.
 */
export default function Root({ children }: PropsWithChildren) {
  return (
    <html lang="ko">
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, shrink-to-fit=no"
        />

        {/* 일본어 글꼴 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap"
        />

        {/* 스크롤 동작을 앱과 맞추는 expo-router 기본 리셋 */}
        <ScrollViewStyleReset />

        <style dangerouslySetInnerHTML={{ __html: FONT_STACK }} />
      </head>
      <body>{children}</body>
    </html>
  );
}

/**
 * 글꼴 목록을 앱 전체에 씌운다.
 *
 * react-native-web 은 글자 요소마다 글꼴을 직접 지정하기 때문에
 * body 에만 걸면 먹지 않는다. 그래서 모든 요소에 상속되도록 적어 준다.
 * 브라우저는 글자 하나하나마다 목록 앞에서부터 그 글자를 가진 글꼴을 고르므로
 * 일본어는 Noto Sans JP, 한글은 그다음 한글 글꼴로 자연스럽게 갈린다.
 */
const FONT_STACK = `
:root {
  --app-font: "Noto Sans JP", -apple-system, BlinkMacSystemFont, "Segoe UI",
    Roboto, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR",
    Helvetica, Arial, sans-serif;
}
html, body, #root { font-family: var(--app-font); }

/*
 * react-native-web 은 글자 요소에 font 축약 속성으로 글꼴을 박아 넣는다
 * (font: 14px -apple-system, …). 축약 속성이 글꼴을 직접 정해 버리므로
 * body 에만 걸어 둔 값은 상속되지 않는다.
 * 그래서 글자 요소가 쓰는 클래스를 직접 겨냥한다.
 * 선택자 우선순위가 한 단계 높아 !important 를 쓰지 않아도 이긴다.
 */
body [class*="css-text-"],
body [class*="css-textinput-"],
body [class*="r-fontFamily-"] { font-family: var(--app-font); }
`;
