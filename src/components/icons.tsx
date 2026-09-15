import Svg, { Circle, Path, Polygon, Polyline, Rect } from "react-native-svg";

export interface IconProps {
  size?: number;
  color?: string;
  strokeWidth?: number;
}

/** ‹ 뒤로가기 */
export function ChevronLeftIcon({
  size = 16,
  color = "#475569",
  strokeWidth = 2.5,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M15 19l-7-7 7-7"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** › 다음 (이미지 좌우 이동 버튼용) */
export function ChevronRightIcon({
  size = 16,
  color = "#475569",
  strokeWidth = 2.5,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M9 5l7 7-7 7"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** ⌃ 접기 */
export function ChevronUpIcon({
  size = 14,
  color = "#10b981",
  strokeWidth = 2.5,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M5 15l7-7 7 7"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** ⌄ 펼치기 */
export function ChevronDownIcon({
  size = 14,
  color = "#10b981",
  strokeWidth = 2.5,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M19 9l-7 7-7-7"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** 🔊 발음 듣기 (단일 스피커 아이콘) */
export function SpeakerIcon({
  size = 20,
  color = "#334155",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" fill={color} />
      <Path
        d="M15.54 8.46a5 5 0 0 1 0 7.07"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <Path
        d="M19.07 4.93a10 10 0 0 1 0 14.14"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** ⏱ 자동 넘김 타이머 */
export function ClockIcon({
  size = 14,
  color = "#10b981",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Circle cx={12} cy={12} r={9} stroke={color} strokeWidth={strokeWidth} />
      <Polyline
        points="12 7 12 12 15 15"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </Svg>
  );
}

/** ▶ 자동 넘김 ON */
export function PlayIcon({ size = 16, color = "#10b981" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Polygon points="5 3 19 12 5 21 5 3" fill={color} />
    </Svg>
  );
}

/** ⏸ 자동 넘김 OFF */
export function PauseIcon({ size = 16, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Rect x={6} y={4} width={4} height={16} rx={1.5} fill={color} />
      <Rect x={14} y={4} width={4} height={16} rx={1.5} fill={color} />
    </Svg>
  );
}

/** ← 이전 */
export function ArrowLeftIcon({
  size = 15,
  color = "#334155",
  strokeWidth = 2.4,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M19 12H5M12 19l-7-7 7-7"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** → 다음 */
export function ArrowRightIcon({
  size = 15,
  color = "#334155",
  strokeWidth = 2.4,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M5 12h14M12 5l7 7-7 7"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** ✓ 외웠어요 */
export function CheckIcon({
  size = 14,
  color = "#ffffff",
  strokeWidth = 3,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M5 13l4 4L19 7"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** ↩ 헷갈려요 (다시 보기) */
export function AgainIcon({
  size = 14,
  color = "#475569",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M3 10h10a5 5 0 0 1 5 5v2m0 0l-3-3m3 3l3-3M3 10l3 3m-3-3l3-3"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** 👤 내 이름 (설정) */
export function PersonIcon({
  size = 18,
  color = "#0eb582",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Circle cx={12} cy={8} r={3.6} stroke={color} strokeWidth={strokeWidth} />
      <Path
        d="M4.5 20c0-3.6 3.4-5.6 7.5-5.6s7.5 2 7.5 5.6"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />
    </Svg>
  );
}

/** 🌐 언어 (설정) */
export function GlobeIcon({
  size = 18,
  color = "#0eb582",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Circle cx={12} cy={12} r={9} stroke={color} strokeWidth={strokeWidth} />
      <Path
        d="M3 12h18M12 3c2.5 2.6 2.5 15.4 0 18M12 3c-2.5 2.6-2.5 15.4 0 18"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />
    </Svg>
  );
}

/** 📖 학습 언어 (설정) */
export function BookIcon({
  size = 18,
  color = "#0eb582",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10a2 2 0 0 1 2 2v13a2 2 0 0 0-2-2H5.5A1.5 1.5 0 0 1 4 15.5V5.5Z"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
      />
      <Path
        d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14a2 2 0 0 0-2 2v13a2 2 0 0 1 2-2h4.5a1.5 1.5 0 0 0 1.5-1.5V5.5Z"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** ⚙ 학습 설정 (설정) */
export function SlidersIcon({
  size = 18,
  color = "#0eb582",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M5 6h14M5 12h14M5 18h14"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />
      <Circle cx={9} cy={6} r={2.3} fill="#f1f2f6" stroke={color} strokeWidth={strokeWidth} />
      <Circle cx={15} cy={12} r={2.3} fill="#f1f2f6" stroke={color} strokeWidth={strokeWidth} />
      <Circle cx={8} cy={18} r={2.3} fill="#f1f2f6" stroke={color} strokeWidth={strokeWidth} />
    </Svg>
  );
}

/** 📊 학습 기록 (설정) */
export function ChartIcon({
  size = 18,
  color = "#0eb582",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M4 20h16"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />
      <Rect x={5.5} y={11} width={3.6} height={6} rx={1.2} stroke={color} strokeWidth={strokeWidth} />
      <Rect x={10.2} y={7} width={3.6} height={10} rx={1.2} stroke={color} strokeWidth={strokeWidth} />
      <Rect x={14.9} y={13.5} width={3.6} height={3.5} rx={1.2} stroke={color} strokeWidth={strokeWidth} />
    </Svg>
  );
}

/** ★ 숙련도 표시 */
export function StarIcon({ size = 10, color = "#fbbf24" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M12 2.5l2.9 5.9 6.5.95-4.7 4.58 1.11 6.47L12 17.35 6.19 20.4 7.3 13.93 2.6 9.35l6.5-.95L12 2.5z"
        fill={color}
      />
    </Svg>
  );
}

/** 🔖 단어장에 담기 (학습 화면 저장 버튼) */
export function BookmarkIcon({
  size = 16,
  color = "#0eb582",
  strokeWidth = 2.2,
  filled = false,
}: IconProps & { filled?: boolean }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M6 4.5A1.5 1.5 0 0 1 7.5 3h9A1.5 1.5 0 0 1 18 4.5V21l-6-4-6 4V4.5Z"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
        fill={filled ? color : "none"}
      />
    </Svg>
  );
}

/** 🏠 홈으로 (학습 화면 상단 왼쪽) */
export function HomeIcon({
  size = 22,
  color = "#334155",
  strokeWidth = 2.4,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M3.5 10.5 12 4l8.5 6.5V19a1.5 1.5 0 0 1-1.5 1.5h-3.5V15h-3v5.5H5A1.5 1.5 0 0 1 3.5 19v-8.5Z"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </Svg>
  );
}

/** 🖼 그림 현황 (하단 독) */
export function PictureIcon({
  size = 20,
  color = "#334155",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Rect
        x={3}
        y={4.5}
        width={18}
        height={15}
        rx={3}
        stroke={color}
        strokeWidth={strokeWidth}
      />
      {/* 해와 언덕. 액자 안에 그림이 들어 있음을 알린다 */}
      <Circle cx={8.75} cy={9.75} r={1.6} stroke={color} strokeWidth={strokeWidth} />
      <Path
        d="M4 16.5l4.2-3.8a2 2 0 0 1 2.7 0L14 15.5l1.7-1.4a2 2 0 0 1 2.6 0L20 15.6"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/** ⚙ 설정 (하단 독) */
export function GearIcon({
  size = 20,
  color = "#334155",
  strokeWidth = 2.2,
}: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Circle cx={12} cy={12} r={3.2} stroke={color} strokeWidth={strokeWidth} />
      {/* 톱니 여덟 개를 짧은 선으로 돌려 놓는다 */}
      <Path
        d="M12 2.8v2.4M12 18.8v2.4M21.2 12h-2.4M5.2 12H2.8M18.5 5.5l-1.7 1.7M7.2 16.8l-1.7 1.7M18.5 18.5l-1.7-1.7M7.2 7.2 5.5 5.5"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />
    </Svg>
  );
}

/* ── 하단 독의 꽉 찬 아이콘 ───────────────────────────────────
   활성 탭에만 쓴다. 액자·톱니처럼 안이 뚫린 모양은 뚫린 자리를
   바탕색으로 덮어 그린다. 그래서 바탕색을 받는다 (활성 탭은 bg-canvas) */

export interface FilledIconProps extends IconProps {
  /** 뚫린 자리를 덮을 바탕색 */
  bg?: string;
}

/** 홈 (활성) */
export function HomeFilledIcon({
  size = 20,
  color = "#006C4C",
}: FilledIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M11.36 3.2a1 1 0 0 1 1.28 0l8.5 7.13a1 1 0 0 1-.64 1.77H19.5v7.4A1.5 1.5 0 0 1 18 21h-3.25v-5.2h-5.5V21H6a1.5 1.5 0 0 1-1.5-1.5v-7.4H3.5a1 1 0 0 1-.64-1.77l8.5-7.13Z"
        fill={color}
      />
    </Svg>
  );
}

/** 단어장 (활성) */
export function BookFilledIcon({
  size = 20,
  color = "#006C4C",
}: FilledIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10a2 2 0 0 1 2 2v13a2 2 0 0 0-2-2H5.5A1.5 1.5 0 0 1 4 15.5V5.5Z"
        fill={color}
      />
      <Path
        d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14a2 2 0 0 0-2 2v13a2 2 0 0 1 2-2h4.5a1.5 1.5 0 0 0 1.5-1.5V5.5Z"
        fill={color}
      />
    </Svg>
  );
}

/** 그림 현황 (활성) */
export function PictureFilledIcon({
  size = 20,
  color = "#006C4C",
  bg = "#ecedf1",
}: FilledIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Rect x={3} y={4.5} width={18} height={15} rx={3} fill={color} />
      {/* 해와 언덕을 바탕색으로 파낸다 */}
      <Circle cx={8.75} cy={9.75} r={1.9} fill={bg} />
      <Path
        d="M3 19.5v-2.6l5-4.5a2 2 0 0 1 2.7 0L14 15.4l1.7-1.4a2 2 0 0 1 2.6 0l2.7 2.3v3.2H3Z"
        fill={bg}
      />
    </Svg>
  );
}

/** 설정 (활성) */
export function GearFilledIcon({
  size = 20,
  color = "#006C4C",
  bg = "#ecedf1",
}: FilledIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      {/* 톱니를 굵은 선으로 돌려 놓고 가운데를 원으로 채운다 */}
      <Path
        d="M12 2.4v3.2M12 18.4v3.2M21.6 12h-3.2M5.6 12H2.4M18.8 5.2l-2.3 2.3M7.5 16.5l-2.3 2.3M18.8 18.8l-2.3-2.3M7.5 7.5 5.2 5.2"
        stroke={color}
        strokeWidth={3.4}
        strokeLinecap="round"
      />
      <Circle cx={12} cy={12} r={6.2} fill={color} />
      <Circle cx={12} cy={12} r={2.5} fill={bg} />
    </Svg>
  );
}
