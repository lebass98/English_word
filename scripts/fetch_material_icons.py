# -*- coding: utf-8 -*-
"""구글 Material Symbols 원본 SVG 를 받아 src/components/icons.tsx 를 만든다.

아이콘을 손으로 그리지 않고 구글 공식 저장소의 path 를 그대로 쓴다.
모양을 바꾸거나 새 아이콘을 넣을 때는 아래 ICONS 표만 고치고 이 스크립트를 다시 돌린다.

    python3 scripts/fetch_material_icons.py
"""

import json
import pathlib
import re
import urllib.request

BASE = (
    "https://raw.githubusercontent.com/google/material-design-icons/master"
    "/symbols/web/{name}/materialsymbolsoutlined/{file}.svg"
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "src/components/icons.tsx"

# 화면에서 쓰는 이름 → (Material Symbols 이름, 채움 여부)
ICONS = {
    "ChevronLeftIcon": ("chevron_left", False),
    "ChevronRightIcon": ("chevron_right", False),
    "ChevronUpIcon": ("keyboard_arrow_up", False),
    "ChevronDownIcon": ("keyboard_arrow_down", False),
    "SpeakerIcon": ("volume_up", False),
    "ClockIcon": ("schedule", False),
    "PlayIcon": ("play_arrow", True),
    "PauseIcon": ("pause", True),
    "ArrowLeftIcon": ("arrow_back", False),
    "ArrowRightIcon": ("arrow_forward", False),
    "CheckIcon": ("check", False),
    "AgainIcon": ("refresh", False),
    "PersonIcon": ("person", False),
    "GlobeIcon": ("language", False),
    "BookIcon": ("menu_book", False),
    "SlidersIcon": ("tune", False),
    "ChartIcon": ("bar_chart", False),
    "StarIcon": ("star", True),
    "BookmarkIcon": ("bookmark", False),
    "BookmarkFilledIcon": ("bookmark", True),
    "HomeIcon": ("home", False),
    "PictureIcon": ("image", False),
    "GearIcon": ("settings", False),
    "QuizIcon": ("quiz", False),
    "CloseIcon": ("close", False),
    "RocketIcon": ("rocket_launch", False),
    # 아래 탭 활성 상태 (채운 모양)
    "HomeFilledIcon": ("home", True),
    "BookFilledIcon": ("menu_book", True),
    "PictureFilledIcon": ("image", True),
    "GearFilledIcon": ("settings", True),
    "QuizFilledIcon": ("quiz", True),
    # 퀴즈 유형 고르는 화면
    "ShuffleIcon": ("shuffle", False),
    "TextFieldsIcon": ("text_fields", False),
    "LightbulbIcon": ("lightbulb", False),
    "HeadphonesIcon": ("headphones", False),
    "EditNoteIcon": ("edit_note", False),
    "SpellcheckIcon": ("spellcheck", False),
    # 철자 맞추기의 남은 기회
    "HeartIcon": ("favorite", True),
    "HeartEmptyIcon": ("favorite", False),
}

# 기본 색. 화면에서 color 를 넘기지 않았을 때 쓴다
DEFAULT_COLOR = "#94a3b8"


def fetch(name: str, filled: bool) -> tuple[str, str]:
    """(viewBox, path 묶음) 을 돌려준다"""
    file = f"{name}_fill1_24px" if filled else f"{name}_24px"
    url = BASE.format(name=name, file=file)
    with urllib.request.urlopen(url, timeout=30) as res:
        svg = res.read().decode("utf-8")

    view_box = re.search(r'viewBox="([^"]+)"', svg)
    paths = re.findall(r'<path[^>]*\sd="([^"]+)"', svg)
    if not view_box or not paths:
        raise RuntimeError(f"{name} 에서 path 를 못 찾았다")
    return view_box.group(1), "".join(paths)


HEADER = '''import Svg, { Path } from "react-native-svg";

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
'''

TEMPLATE = '''
/** {label} */
export function {component}({{ size = {size}, color = "{color}" }}: IconProps) {{
  return (
    <Svg width={{size}} height={{size}} viewBox="{view_box}" fill="none">
      <Path d="{path}" fill={{color}} />
    </Svg>
  );
}}
'''

# 예전 아이콘이 쓰던 기본 크기·색을 그대로 이어받는다
DEFAULTS = {
    "StarIcon": (10, "#fbbf24"),
    "PlayIcon": (16, "#10b981"),
    "PauseIcon": (16, "#94a3b8"),
    "HomeFilledIcon": (22, "#0EB582"),
    "BookFilledIcon": (22, "#0EB582"),
    "PictureFilledIcon": (22, "#0EB582"),
    "GearFilledIcon": (22, "#0EB582"),
    "QuizFilledIcon": (22, "#0EB582"),
    "HeartIcon": (16, "#0EB582"),
    "HeartEmptyIcon": (16, "#cbd5e1"),
}


def main() -> None:
    parts = [HEADER]
    for component, (name, filled) in ICONS.items():
        view_box, path = fetch(name, filled)
        size, color = DEFAULTS.get(component, (22, DEFAULT_COLOR))
        label = f"{name}{' (채운 모양)' if filled else ''}"
        parts.append(
            TEMPLATE.format(
                label=label,
                component=component,
                size=size,
                color=color,
                view_box=view_box,
                path=path,
            )
        )
        print(f"  {component:22s} ← {name}{' (fill)' if filled else ''}")

    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"\n{len(ICONS)}개 아이콘을 {OUT.relative_to(ROOT)} 에 적었다")


if __name__ == "__main__":
    main()
