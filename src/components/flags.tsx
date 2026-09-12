import Svg, { Circle, Defs, G, Path, Rect, ClipPath } from "react-native-svg";
import type { StudyLangId } from "../constants/languages";

/**
 * 학습 언어를 나타내는 국기.
 *
 * 그림 파일이 아니라 SVG 로 그린다. 어떤 크기로 키워도 흐려지지 않고,
 * 앱 용량도 늘지 않는다. 모서리를 둥글게 깎아 앱의 다른 칩들과 결을 맞춘다.
 */
export interface FlagProps {
  size?: number;
}

/** 미국 국기 (영어) */
export function FlagEN({ size = 28 }: FlagProps) {
  const h = size;
  const w = size;
  // 13줄 줄무늬 중 붉은 줄은 짝수 번째(0부터)
  const stripe = h / 13;
  const stripes = Array.from({ length: 13 }, (_, i) => i).filter(
    (i) => i % 2 === 0,
  );
  // 파란 칸은 가로 40%, 세로 7줄
  const unionW = w * 0.42;
  const unionH = stripe * 7;

  return (
    <Svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <Defs>
        <ClipPath id="flagEnClip">
          <Rect x={0} y={0} width={w} height={h} rx={h * 0.22} />
        </ClipPath>
      </Defs>
      <G clipPath="url(#flagEnClip)">
        <Rect x={0} y={0} width={w} height={h} fill="#ffffff" />
        {stripes.map((i) => (
          <Rect
            key={i}
            x={0}
            y={i * stripe}
            width={w}
            height={stripe}
            fill="#d7262f"
          />
        ))}
        <Rect x={0} y={0} width={unionW} height={unionH} fill="#2a3b76" />
        {/* 별은 작은 크기에서 뭉치므로 점 아홉 개로 단순하게 찍는다 */}
        {[0, 1, 2].map((row) =>
          [0, 1, 2].map((col) => (
            <Circle
              key={`${row}-${col}`}
              cx={unionW * (0.22 + col * 0.28)}
              cy={unionH * (0.24 + row * 0.26)}
              r={Math.max(0.7, h * 0.028)}
              fill="#ffffff"
            />
          )),
        )}
      </G>
      <Rect
        x={0.5}
        y={0.5}
        width={w - 1}
        height={h - 1}
        rx={h * 0.22}
        fill="none"
        stroke="rgba(15,23,42,0.12)"
        strokeWidth={1}
      />
    </Svg>
  );
}

/** 일본 국기 (일본어) */
export function FlagJA({ size = 28 }: FlagProps) {
  const h = size;
  const w = size;
  return (
    <Svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <Defs>
        <ClipPath id="flagJaClip">
          <Rect x={0} y={0} width={w} height={h} rx={h * 0.22} />
        </ClipPath>
      </Defs>
      <G clipPath="url(#flagJaClip)">
        <Rect x={0} y={0} width={w} height={h} fill="#ffffff" />
        <Circle cx={w / 2} cy={h / 2} r={h * 0.28} fill="#bc002d" />
      </G>
      <Rect
        x={0.5}
        y={0.5}
        width={w - 1}
        height={h - 1}
        rx={h * 0.22}
        fill="none"
        stroke="rgba(15,23,42,0.12)"
        strokeWidth={1}
      />
    </Svg>
  );
}

/** 아직 국기를 안 그린 언어를 위한 자리 */
function FlagUnknown({ size = 28 }: FlagProps) {
  return (
    <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <Rect
        x={0.5}
        y={0.5}
        width={size - 1}
        height={size - 1}
        rx={size * 0.22}
        fill="#e2e8f0"
        stroke="rgba(15,23,42,0.12)"
        strokeWidth={1}
      />
      <Path
        d={`M${size * 0.3} ${size * 0.5}h${size * 0.4}`}
        stroke="#94a3b8"
        strokeWidth={2}
        strokeLinecap="round"
      />
    </Svg>
  );
}

const FLAGS: Record<StudyLangId, (p: FlagProps) => React.JSX.Element> = {
  en: FlagEN,
  ja: FlagJA,
};

/** 학습 언어에 맞는 국기를 그린다 */
export function LanguageFlag({
  lang,
  size = 28,
}: {
  lang: StudyLangId;
  size?: number;
}) {
  const Flag = FLAGS[lang] ?? FlagUnknown;
  return <Flag size={size} />;
}
