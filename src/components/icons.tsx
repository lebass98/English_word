import Svg, { Path } from "react-native-svg";

/**
 * 화면에서 쓰는 아이콘 모음.
 *
 * 모양은 구글 Material Symbols(Outlined) 원본을 그대로 쓴다.
 * 이 파일은 scripts/fetch_material_icons.py 가 만든다. 손으로 고치지 않는다.
 * 아이콘을 바꾸거나 더할 때는 그 스크립트의 ICONS 표를 고치고 다시 돌린다.
 *
 * Material Symbols 는 선이 아니라 면으로 그려진 그림이라 굵기를 바꿀 수 없다.
 * strokeWidth 는 예전 아이콘과 쓰는 자리를 맞추려고 남겨 둔 값이며 모양에 영향이 없다.
 */
export interface IconProps {
  size?: number;
  color?: string;
  /** 예전 아이콘과 호환을 위해 남겨 둔 값. 모양에 영향이 없다 */
  strokeWidth?: number;
}

/** chevron_left */
export function ChevronLeftIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M560-240 320-480l240-240 56 56-184 184 184 184-56 56Z" fill={color} />
    </Svg>
  );
}

/** chevron_right */
export function ChevronRightIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M504-480 320-664l56-56 240 240-240 240-56-56 184-184Z" fill={color} />
    </Svg>
  );
}

/** keyboard_arrow_up */
export function ChevronUpIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M480-528 296-344l-56-56 240-240 240 240-56 56-184-184Z" fill={color} />
    </Svg>
  );
}

/** keyboard_arrow_down */
export function ChevronDownIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z" fill={color} />
    </Svg>
  );
}

/** volume_up */
export function SpeakerIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M560-131v-82q90-26 145-100t55-168q0-94-55-168T560-749v-82q124 28 202 125.5T840-481q0 127-78 224.5T560-131ZM120-360v-240h160l200-200v640L280-360H120Zm440 40v-322q47 22 73.5 66t26.5 96q0 51-26.5 94.5T560-320ZM400-606l-86 86H200v80h114l86 86v-252ZM300-480Z" fill={color} />
    </Svg>
  );
}

/** schedule */
export function ClockIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="m612-292 56-56-148-148v-184h-80v216l172 172ZM480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-400Zm0 320q133 0 226.5-93.5T800-480q0-133-93.5-226.5T480-800q-133 0-226.5 93.5T160-480q0 133 93.5 226.5T480-160Z" fill={color} />
    </Svg>
  );
}

/** play_arrow (채운 모양) */
export function PlayIcon({ size = 16, color = "#10b981" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M320-200v-560l440 280-440 280Z" fill={color} />
    </Svg>
  );
}

/** pause (채운 모양) */
export function PauseIcon({ size = 16, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M560-200v-560h160v560H560Zm-320 0v-560h160v560H240Z" fill={color} />
    </Svg>
  );
}

/** arrow_back */
export function ArrowLeftIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="m313-440 224 224-57 56-320-320 320-320 57 56-224 224h487v80H313Z" fill={color} />
    </Svg>
  );
}

/** arrow_forward */
export function ArrowRightIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M647-440H160v-80h487L423-744l57-56 320 320-320 320-57-56 224-224Z" fill={color} />
    </Svg>
  );
}

/** check */
export function CheckIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z" fill={color} />
    </Svg>
  );
}

/** refresh */
export function AgainIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M480-160q-134 0-227-93t-93-227q0-134 93-227t227-93q69 0 132 28.5T720-690v-110h80v280H520v-80h168q-32-56-87.5-88T480-720q-100 0-170 70t-70 170q0 100 70 170t170 70q77 0 139-44t87-116h84q-28 106-114 173t-196 67Z" fill={color} />
    </Svg>
  );
}

/** person */
export function PersonIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M480-480q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47ZM160-160v-112q0-34 17.5-62.5T224-378q62-31 126-46.5T480-440q66 0 130 15.5T736-378q29 15 46.5 43.5T800-272v112H160Zm80-80h480v-32q0-11-5.5-20T700-306q-54-27-109-40.5T480-360q-56 0-111 13.5T260-306q-9 5-14.5 14t-5.5 20v32Zm240-320q33 0 56.5-23.5T560-640q0-33-23.5-56.5T480-720q-33 0-56.5 23.5T400-640q0 33 23.5 56.5T480-560Zm0-80Zm0 400Z" fill={color} />
    </Svg>
  );
}

/** language */
export function GlobeIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M480-80q-82 0-155-31.5t-127.5-86Q143-252 111.5-325T80-480q0-83 31.5-155.5t86-127Q252-817 325-848.5T480-880q83 0 155.5 31.5t127 86q54.5 54.5 86 127T880-480q0 82-31.5 155t-86 127.5q-54.5 54.5-127 86T480-80Zm0-82q26-36 45-75t31-83H404q12 44 31 83t45 75Zm-104-16q-18-33-31.5-68.5T322-320H204q29 50 72.5 87t99.5 55Zm208 0q56-18 99.5-55t72.5-87H638q-9 38-22.5 73.5T584-178ZM170-400h136q-3-20-4.5-39.5T300-480q0-21 1.5-40.5T306-560H170q-5 20-7.5 39.5T160-480q0 21 2.5 40.5T170-400Zm216 0h188q3-20 4.5-39.5T580-480q0-21-1.5-40.5T574-560H386q-3 20-4.5 39.5T380-480q0 21 1.5 40.5T386-400Zm268 0h136q5-20 7.5-39.5T800-480q0-21-2.5-40.5T790-560H654q3 20 4.5 39.5T660-480q0 21-1.5 40.5T654-400Zm-16-240h118q-29-50-72.5-87T584-782q18 33 31.5 68.5T638-640Zm-234 0h152q-12-44-31-83t-45-75q-26 36-45 75t-31 83Zm-200 0h118q9-38 22.5-73.5T376-782q-56 18-99.5 55T204-640Z" fill={color} />
    </Svg>
  );
}

/** menu_book */
export function BookIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M560-564v-68q33-14 67.5-21t72.5-7q26 0 51 4t49 10v64q-24-9-48.5-13.5T700-600q-38 0-73 9.5T560-564Zm0 220v-68q33-14 67.5-21t72.5-7q26 0 51 4t49 10v64q-24-9-48.5-13.5T700-380q-38 0-73 9t-67 27Zm0-110v-68q33-14 67.5-21t72.5-7q26 0 51 4t49 10v64q-24-9-48.5-13.5T700-490q-38 0-73 9.5T560-454ZM260-320q47 0 91.5 10.5T440-278v-394q-41-24-87-36t-93-12q-36 0-71.5 7T120-692v396q35-12 69.5-18t70.5-6Zm260 42q44-21 88.5-31.5T700-320q36 0 70.5 6t69.5 18v-396q-33-14-68.5-21t-71.5-7q-47 0-93 12t-87 36v394Zm-40 118q-48-38-104-59t-116-21q-42 0-82.5 11T100-198q-21 11-40.5-1T40-234v-482q0-11 5.5-21T62-752q46-24 96-36t102-12q58 0 113.5 15T480-740q51-30 106.5-45T700-800q52 0 102 12t96 36q11 5 16.5 15t5.5 21v482q0 23-19.5 35t-40.5 1q-37-20-77.5-31T700-240q-60 0-116 21t-104 59ZM280-494Z" fill={color} />
    </Svg>
  );
}

/** tune */
export function SlidersIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M440-120v-240h80v80h320v80H520v80h-80Zm-320-80v-80h240v80H120Zm160-160v-80H120v-80h160v-80h80v240h-80Zm160-80v-80h400v80H440Zm160-160v-240h80v80h160v80H680v80h-80Zm-480-80v-80h400v80H120Z" fill={color} />
    </Svg>
  );
}

/** bar_chart */
export function ChartIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M640-160v-280h160v280H640Zm-240 0v-640h160v640H400Zm-240 0v-440h160v440H160Z" fill={color} />
    </Svg>
  );
}

/** star (채운 모양) */
export function StarIcon({ size = 10, color = "#fbbf24" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="m233-120 65-281L80-590l288-25 112-265 112 265 288 25-218 189 65 281-247-149-247 149Z" fill={color} />
    </Svg>
  );
}

/** bookmark */
export function BookmarkIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M200-120v-640q0-33 23.5-56.5T280-840h400q33 0 56.5 23.5T760-760v640L480-240 200-120Zm80-122 200-86 200 86v-518H280v518Zm0-518h400-400Z" fill={color} />
    </Svg>
  );
}

/** bookmark (채운 모양) */
export function BookmarkFilledIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M200-120v-640q0-33 23.5-56.5T280-840h400q33 0 56.5 23.5T760-760v640L480-240 200-120Z" fill={color} />
    </Svg>
  );
}

/** home */
export function HomeIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M240-200h120v-240h240v240h120v-360L480-740 240-560v360Zm-80 80v-480l320-240 320 240v480H520v-240h-80v240H160Zm320-350Z" fill={color} />
    </Svg>
  );
}

/** image */
export function PictureIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm40-80h480L570-480 450-320l-90-120-120 160Zm-40 80v-560 560Z" fill={color} />
    </Svg>
  );
}

/** settings */
export function GearIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="m370-80-16-128q-13-5-24.5-12T307-235l-119 50L78-375l103-78q-1-7-1-13.5v-27q0-6.5 1-13.5L78-585l110-190 119 50q11-8 23-15t24-12l16-128h220l16 128q13 5 24.5 12t22.5 15l119-50 110 190-103 78q1 7 1 13.5v27q0 6.5-2 13.5l103 78-110 190-118-50q-11 8-23 15t-24 12L590-80H370Zm70-80h79l14-106q31-8 57.5-23.5T639-327l99 41 39-68-86-65q5-14 7-29.5t2-31.5q0-16-2-31.5t-7-29.5l86-65-39-68-99 42q-22-23-48.5-38.5T533-694l-13-106h-79l-14 106q-31 8-57.5 23.5T321-633l-99-41-39 68 86 64q-5 15-7 30t-2 32q0 16 2 31t7 30l-86 65 39 68 99-42q22 23 48.5 38.5T427-266l13 106Zm42-180q58 0 99-41t41-99q0-58-41-99t-99-41q-59 0-99.5 41T342-480q0 58 40.5 99t99.5 41Zm-2-140Z" fill={color} />
    </Svg>
  );
}

/** quiz */
export function QuizIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M560-360q17 0 29.5-12.5T602-402q0-17-12.5-29.5T560-444q-17 0-29.5 12.5T518-402q0 17 12.5 29.5T560-360Zm-30-128h60q0-29 6-42.5t28-35.5q30-30 40-48.5t10-43.5q0-45-31.5-73.5T560-760q-41 0-71.5 23T446-676l54 22q9-25 24.5-37.5T560-704q24 0 39 13.5t15 36.5q0 14-8 26.5T578-596q-33 29-40.5 45.5T530-488ZM320-240q-33 0-56.5-23.5T240-320v-480q0-33 23.5-56.5T320-880h480q33 0 56.5 23.5T880-800v480q0 33-23.5 56.5T800-240H320Zm0-80h480v-480H320v480ZM160-80q-33 0-56.5-23.5T80-160v-560h80v560h560v80H160Zm160-720v480-480Z" fill={color} />
    </Svg>
  );
}

/** close */
export function CloseIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z" fill={color} />
    </Svg>
  );
}

/** rocket_launch */
export function RocketIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="m226-559 78 33q14-28 29-54t33-52l-56-11-84 84Zm142 83 114 113q42-16 90-49t90-75q70-70 109.5-155.5T806-800q-72-5-158 34.5T492-656q-42 42-75 90t-49 90Zm178-65q-23-23-23-56.5t23-56.5q23-23 57-23t57 23q23 23 23 56.5T660-541q-23 23-57 23t-57-23Zm19 321 84-84-11-56q-26 18-52 32.5T532-299l33 79Zm313-653q19 121-23.5 235.5T708-419l20 99q4 20-2 39t-20 33L538-80l-84-197-171-171-197-84 167-168q14-14 33.5-20t39.5-2l99 20q104-104 218-147t235-24ZM157-321q35-35 85.5-35.5T328-322q35 35 34.5 85.5T327-151q-25 25-83.5 43T82-76q14-103 32-161.5t43-83.5Zm57 56q-10 10-20 36.5T180-175q27-4 53.5-13.5T270-208q12-12 13-29t-11-29q-12-12-29-11.5T214-265Z" fill={color} />
    </Svg>
  );
}

/** home (채운 모양) */
export function HomeFilledIcon({ size = 22, color = "#0EB582" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M160-120v-480l320-240 320 240v480H560v-280H400v280H160Z" fill={color} />
    </Svg>
  );
}

/** menu_book (채운 모양) */
export function BookFilledIcon({ size = 22, color = "#0EB582" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M560-564v-68q33-14 67.5-21t72.5-7q26 0 51 4t49 10v64q-24-9-48.5-13.5T700-600q-38 0-73 9.5T560-564Zm0 220v-68q33-14 67.5-21t72.5-7q26 0 51 4t49 10v64q-24-9-48.5-13.5T700-380q-38 0-73 9t-67 27Zm0-110v-68q33-14 67.5-21t72.5-7q26 0 51 4t49 10v64q-24-9-48.5-13.5T700-490q-38 0-73 9.5T560-454Zm-40 176q44-21 88.5-31.5T700-320q36 0 70.5 6t69.5 18v-396q-33-14-68.5-21t-71.5-7q-47 0-93 12t-87 36v394Zm-40 118q-48-38-104-59t-116-21q-42 0-82.5 11T100-198q-21 11-40.5-1T40-234v-482q0-11 5.5-21T62-752q47-23 96.5-35.5T260-800q58 0 113.5 15T480-740q51-30 106.5-45T700-800q52 0 101.5 12.5T898-752q11 5 16.5 15t5.5 21v482q0 23-19.5 35t-40.5 1q-37-20-77.5-31T700-240q-60 0-116 21t-104 59Z" fill={color} />
    </Svg>
  );
}

/** image (채운 모양) */
export function PictureFilledIcon({ size = 22, color = "#0EB582" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm40-160h480L570-480 450-320l-90-120-120 160Z" fill={color} />
    </Svg>
  );
}

/** settings (채운 모양) */
export function GearFilledIcon({ size = 22, color = "#0EB582" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="m370-80-16-128q-13-5-24.5-12T307-235l-119 50L78-375l103-78q-1-7-1-13.5v-27q0-6.5 1-13.5L78-585l110-190 119 50q11-8 23-15t24-12l16-128h220l16 128q13 5 24.5 12t22.5 15l119-50 110 190-103 78q1 7 1 13.5v27q0 6.5-2 13.5l103 78-110 190-118-50q-11 8-23 15t-24 12L590-80H370Zm112-260q58 0 99-41t41-99q0-58-41-99t-99-41q-59 0-99.5 41T342-480q0 58 40.5 99t99.5 41Z" fill={color} />
    </Svg>
  );
}

/** quiz (채운 모양) */
export function QuizFilledIcon({ size = 22, color = "#0EB582" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M560-360q17 0 29.5-12.5T602-402q0-17-12.5-29.5T560-444q-17 0-29.5 12.5T518-402q0 17 12.5 29.5T560-360Zm-30-128h60q0-29 6-42.5t28-35.5q30-30 40-48.5t10-43.5q0-45-31.5-73.5T560-760q-41 0-71.5 23T446-676l54 22q9-25 24.5-37.5T560-704q24 0 39 13.5t15 36.5q0 14-8 26.5T578-596q-33 29-40.5 45.5T530-488ZM320-240q-33 0-56.5-23.5T240-320v-480q0-33 23.5-56.5T320-880h480q33 0 56.5 23.5T880-800v480q0 33-23.5 56.5T800-240H320ZM160-80q-33 0-56.5-23.5T80-160v-560h80v560h560v80H160Z" fill={color} />
    </Svg>
  );
}

/** shuffle */
export function ShuffleIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M560-160v-80h104L537-367l57-57 126 126v-102h80v240H560Zm-344 0-56-56 504-504H560v-80h240v240h-80v-104L216-160Zm151-377L160-744l56-56 207 207-56 56Z" fill={color} />
    </Svg>
  );
}

/** text_fields */
export function TextFieldsIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M280-160v-520H80v-120h520v120H400v520H280Zm360 0v-320H520v-120h360v120H760v320H640Z" fill={color} />
    </Svg>
  );
}

/** lightbulb */
export function LightbulbIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M480-80q-33 0-56.5-23.5T400-160h160q0 33-23.5 56.5T480-80ZM320-200v-80h320v80H320Zm10-120q-69-41-109.5-110T180-580q0-125 87.5-212.5T480-880q125 0 212.5 87.5T780-580q0 81-40.5 150T630-320H330Zm24-80h252q45-32 69.5-79T700-580q0-92-64-156t-156-64q-92 0-156 64t-64 156q0 54 24.5 101t69.5 79Zm126 0Z" fill={color} />
    </Svg>
  );
}

/** headphones */
export function HeadphonesIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M360-120H200q-33 0-56.5-23.5T120-200v-280q0-75 28.5-140.5t77-114q48.5-48.5 114-77T480-840q75 0 140.5 28.5t114 77q48.5 48.5 77 114T840-480v280q0 33-23.5 56.5T760-120H600v-320h160v-40q0-117-81.5-198.5T480-760q-117 0-198.5 81.5T200-480v40h160v320Zm-80-240h-80v160h80v-160Zm400 0v160h80v-160h-80Zm-400 0h-80 80Zm400 0h80-80Z" fill={color} />
    </Svg>
  );
}

/** edit_note */
export function EditNoteIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M160-400v-80h280v80H160Zm0-160v-80h440v80H160Zm0-160v-80h440v80H160Zm360 560v-123l221-220q9-9 20-13t22-4q12 0 23 4.5t20 13.5l37 37q8 9 12.5 20t4.5 22q0 11-4 22.5T863-380L643-160H520Zm300-263-37-37 37 37ZM580-220h38l121-122-18-19-19-18-122 121v38Zm141-141-19-18 37 37-18-19Z" fill={color} />
    </Svg>
  );
}

/** spellcheck */
export function SpellcheckIcon({ size = 22, color = "#94a3b8" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="M564-80 394-250l56-56 114 114 226-226 56 56L564-80ZM120-320l194-520h94l194 520h-92l-46-132H254l-46 132h-88Zm162-208h156l-76-216h-4l-76 216Z" fill={color} />
    </Svg>
  );
}

/** favorite (채운 모양) */
export function HeartIcon({ size = 16, color = "#0EB582" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="m480-120-58-52q-101-91-167-157T150-447.5Q111-500 95.5-544T80-634q0-94 63-157t157-63q52 0 99 22t81 62q34-40 81-62t99-22q94 0 157 63t63 157q0 46-15.5 90T810-447.5Q771-395 705-329T538-172l-58 52Z" fill={color} />
    </Svg>
  );
}

/** favorite */
export function HeartEmptyIcon({ size = 16, color = "#cbd5e1" }: IconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 -960 960 960" fill="none">
      <Path d="m480-120-58-52q-101-91-167-157T150-447.5Q111-500 95.5-544T80-634q0-94 63-157t157-63q52 0 99 22t81 62q34-40 81-62t99-22q94 0 157 63t63 157q0 46-15.5 90T810-447.5Q771-395 705-329T538-172l-58 52Zm0-108q96-86 158-147.5t98-107q36-45.5 50-81t14-70.5q0-60-40-100t-100-40q-47 0-87 26.5T518-680h-76q-15-41-55-67.5T300-774q-60 0-100 40t-40 100q0 35 14 70.5t50 81q36 45.5 98 107T480-228Zm0-273Z" fill={color} />
    </Svg>
  );
}
