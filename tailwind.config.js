const plugin = require("tailwindcss/plugin");

/**
 * 뉴모피즘 그림자. 어두운 그림자와 흰 하이라이트가 한 쌍이라야 입체로 보인다.
 * (배경 #ecedf1 기준)
 */
const NEU = {
  neu: "14px 14px 28px rgba(174, 174, 192, 0.45), -10px -10px 24px #ffffff",
  // 스크롤 영역 안의 큰 카드용. 그림자가 퍼지는 최대 거리를 24px로 맞춰
  // 스크롤 컨테이너(좌우 여백 24px)에서 잘리지 않게 한다.
  // 오른쪽/아래 8+16=24px, 왼쪽/위 6+14=20px
  "neu-card": "8px 8px 16px rgba(174, 174, 192, 0.45), -6px -6px 14px #ffffff",
  "neu-pressed": "6px 6px 12px rgba(174, 174, 192, 0.4), -4px -4px 10px #ffffff",
  // 작은 요소(칩·버튼)용 뉴모피즘
  "neu-sm": "5px 5px 10px rgba(174, 174, 192, 0.4), -4px -4px 8px #ffffff",
  // 안쪽으로 파인 뉴모피즘 (진행률 트랙 등)
  "neu-inset":
    "inset 4px 4px 8px rgba(174, 174, 192, 0.4), inset -3px -3px 6px #ffffff",
};

/**
 * NativeWind 의 기본 shadow 유틸리티는 네이티브에서 쉼표로 나열한 그림자 중
 * 첫 번째만 살리고 나머지를 버린다. inset 도 무시해 파인 자리가 도리어 솟는다.
 * (nativewind/dist/tailwind/shadows.js 의 `ast.find(...)` 한 줄)
 *
 * React Native 0.86 은 boxShadow 를 여러 겹·inset 까지 그대로 받으므로,
 * 네이티브에서는 boxShadow 를 직접 넘겨 웹과 같은 모양이 되게 한다.
 * 웹에서는 -rn- 속성이 뜻 없는 CSS 가 되므로 손대지 않는다.
 */
const isNative = (process.env.NATIVEWIND_OS ?? "web") !== "web";

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./src/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        // Vocab Spark 팔레트 (DESIGN.md)
        mint: "#0EB582",
        "mint-dark": "#006C4C",
        lavender: "#8B70E8",
        ink: "#121826",
        // 뉴모피즘 기본 서피스: 배경과 카드가 거의 같은 톤
        canvas: "#ecedf1",
        surface: "#f1f2f6",
      },
      boxShadow: {
        // 네이티브에서는 아래 플러그인이 대신 만든다. 여기에 두면 NativeWind 의
        // 기본 shadow 유틸리티가 같은 이름을 먼저 차지해 플러그인이 묻힌다
        ...(isNative ? {} : NEU),
        mint: "0px 4px 14px 0px rgba(14, 181, 130, 0.3)",
        indigo: "0px 4px 14px 0px rgba(107, 121, 232, 0.35)",
      },
      fontSize: {
        xs: ["9px", { lineHeight: "13px" }],
        sm: ["10px", { lineHeight: "14px" }],
        base: ["12px", { lineHeight: "17px" }],
        lg: ["13px", { lineHeight: "19px" }],
        xl: ["15px", { lineHeight: "21px" }],
        "2xl": ["17px", { lineHeight: "24px" }],
        "3xl": ["21px", { lineHeight: "28px" }],
        "4xl": ["26px", { lineHeight: "34px" }],
        "5xl": ["34px", { lineHeight: "42px" }],
      },
    },
  },
  plugins: isNative
    ? [
        plugin(({ matchUtilities }) => {
          matchUtilities(
            { shadow: (value) => ({ "-rn-box-shadow": value }) },
            { values: NEU, type: ["shadow"] },
          );
        }),
      ]
    : [],
};
