import { ScrollViewStyleReset } from "expo-router/html";
import type { PropsWithChildren } from "react";

/**
 * 배포 주소. 공유 미리보기 이미지는 전체 주소여야 해서 필요하다.
 * 도메인을 바꾸면 EXPO_PUBLIC_SITE_URL 로 덮어쓴다.
 */
const SITE_URL = (
  process.env.EXPO_PUBLIC_SITE_URL || "https://wordpic-ten.vercel.app"
).replace(/\/$/, "");
const SITE_TITLE = "WordPic - 그림으로 외우는 영어 단어";
const SITE_DESCRIPTION =
  "중학·고등·토익·토플 영어 단어를 그림과 함께 외우는 단어장. 퀴즈와 단어장으로 복습하고, 구글 로그인으로 기록을 이어 보세요.";
/** scripts/make_og_image.py 가 만든 1200x630 카드 (public/og-image.png) */
const OG_IMAGE = `${SITE_URL}/og-image.png`;

/**
 * 웹에서만 쓰는 HTML 뼈대.
 *
 * 글꼴은 프로젝트 안(public/fonts)에 둔 파일을 쓴다. 바깥 CDN 을 타지 않는다.
 * 일본어 화면은 Noto Sans JP 만, 한국어·영어 화면은 프리텐다드 GOV 를 쓴다.
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

        {/* 페이지 제목과 링크 공유 미리보기 (카카오톡·슬랙·페이스북·X) */}
        <title>{SITE_TITLE}</title>
        <meta name="description" content={SITE_DESCRIPTION} />
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="WordPic" />
        <meta property="og:locale" content="ko_KR" />
        <meta property="og:url" content={SITE_URL} />
        <meta property="og:title" content={SITE_TITLE} />
        <meta property="og:description" content={SITE_DESCRIPTION} />
        <meta property="og:image" content={OG_IMAGE} />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        <meta property="og:image:alt" content={SITE_TITLE} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={SITE_TITLE} />
        <meta name="twitter:description" content={SITE_DESCRIPTION} />
        <meta name="twitter:image" content={OG_IMAGE} />

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
/* 프로젝트에 설치한 글꼴. 가변 글꼴 한 벌로 모든 굵기를 낸다 */
@font-face {
  font-family: "PretendardGOV";
  src: url("/fonts/PretendardGOVVariable.woff2") format("woff2-variations");
  font-weight: 45 920;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "NotoSansJP";
  src: url("/fonts/NotoSansJP-Variable.woff2") format("woff2-variations");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}

/*
 * 한국어·영어 화면은 프리텐다드 GOV.
 * 뒤에 Noto Sans JP 를 두는 까닭은, 한국어 화면에서 일본어 단어를 볼 때
 * 프리텐다드에 없는 가나가 시스템 글꼴로 튀지 않게 하기 위해서다.
 * 브라우저는 글자마다 목록 앞에서부터 그 글자를 가진 글꼴을 고른다.
 */
:root {
  --app-font: "PretendardGOV", "NotoSansJP", -apple-system, BlinkMacSystemFont,
    "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* 일본어 화면은 Noto Sans JP 만 쓴다 */
:root[data-uilang="ja"] {
  --app-font: "NotoSansJP", -apple-system, BlinkMacSystemFont, "Segoe UI",
    Roboto, Helvetica, Arial, sans-serif;
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
