import Svg, { Circle, Defs, G, Path, Rect, ClipPath } from "react-native-svg";
import type { StudyLangId } from "../constants/languages";
import type { UiLangId } from "../i18n/strings";

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

/** 태극기 괘 하나. 가운데를 원점으로 가로 막대 셋을 그린다 (true = 이어진 막대) */
function Trigram({
  bars,
  size,
  x,
  y,
  angle,
}: {
  bars: [boolean, boolean, boolean];
  size: number;
  x: number;
  y: number;
  angle: number;
}) {
  const len = size * 0.2;
  const thick = size * 0.042;
  const step = size * 0.066;
  const piece = len * 0.43;
  return (
    <G transform={`translate(${x} ${y}) rotate(${angle})`}>
      {bars.map((solid, i) => {
        const cy = (i - 1) * step - thick / 2;
        return solid ? (
          <Rect key={i} x={-len / 2} y={cy} width={len} height={thick} fill="#000000" />
        ) : (
          <G key={i}>
            <Rect x={-len / 2} y={cy} width={piece} height={thick} fill="#000000" />
            <Rect x={len / 2 - piece} y={cy} width={piece} height={thick} fill="#000000" />
          </G>
        );
      })}
    </G>
  );
}

/** 태극기 (한국어). 작은 크기에서도 알아보게 괘를 대각선 네 귀퉁이에 둔다 */
export function FlagKO({ size = 28 }: FlagProps) {
  const h = size;
  const w = size;
  const c = size / 2;
  const r = size * 0.24;
  // 괘는 가운데에서 대각선으로 이만큼 떨어져 선다
  const d = size * 0.36 * Math.SQRT1_2;
  return (
    <Svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <Defs>
        <ClipPath id="flagKoClip">
          <Rect x={0} y={0} width={w} height={h} rx={h * 0.22} />
        </ClipPath>
      </Defs>
      <G clipPath="url(#flagKoClip)">
        <Rect x={0} y={0} width={w} height={h} fill="#ffffff" />
        {/* 태극: 파란 원 위에 붉은 반쪽을 S 자로 얹고 비스듬히 돌린다 */}
        <G transform={`translate(${c} ${c}) rotate(33.69)`}>
          <Circle cx={0} cy={0} r={r} fill="#0047a0" />
          <Path
            d={`M${-r} 0A${r} ${r} 0 0 1 ${r} 0A${r / 2} ${r / 2} 0 0 1 0 0A${r / 2} ${r / 2} 0 0 0 ${-r} 0Z`}
            fill="#cd2e3a"
          />
        </G>
        <Trigram bars={[true, true, true]} size={size} x={c - d} y={c - d} angle={-45} />
        <Trigram bars={[false, true, false]} size={size} x={c + d} y={c - d} angle={45} />
        <Trigram bars={[true, false, true]} size={size} x={c - d} y={c + d} angle={45} />
        <Trigram bars={[false, false, false]} size={size} x={c + d} y={c + d} angle={-45} />
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

const FLAGS: Record<
  StudyLangId | UiLangId,
  (p: FlagProps) => React.JSX.Element
> = {
  en: FlagEN,
  ja: FlagJA,
  ko: FlagKO,
};

/** 학습 언어·표시 언어에 맞는 국기를 그린다 */
export function LanguageFlag({
  lang,
  size = 28,
}: {
  lang: StudyLangId | UiLangId;
  size?: number;
}) {
  const Flag = FLAGS[lang] ?? FlagUnknown;
  return <Flag size={size} />;
}
