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
        // 뉴모피즘: 우하단 어두운 그림자 + 좌상단 흰 하이라이트 (배경 #ecedf1 기준)
        neu: "14px 14px 28px rgba(174, 174, 192, 0.45), -10px -10px 24px #ffffff",
        "neu-pressed":
          "6px 6px 12px rgba(174, 174, 192, 0.4), -4px -4px 10px #ffffff",
        // 작은 요소(칩·버튼)용 뉴모피즘
        "neu-sm":
          "5px 5px 10px rgba(174, 174, 192, 0.4), -4px -4px 8px #ffffff",
        // 안쪽으로 파인 뉴모피즘 (진행률 트랙 등)
        "neu-inset":
          "inset 4px 4px 8px rgba(174, 174, 192, 0.4), inset -3px -3px 6px #ffffff",
        mint: "0px 4px 14px 0px rgba(14, 181, 130, 0.3)",
        indigo: "0px 4px 14px 0px rgba(107, 121, 232, 0.35)",
      },
    },
  },
  plugins: [],
};
