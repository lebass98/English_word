# -*- coding: utf-8 -*-
"""단어 그림을 모아 대조 시트(연락지)를 만든다.

한 장씩 열어 보면 수천 번이 걸리므로 36장씩 묶어 한 장으로 만든다.
칸마다 영어 낱말과 한국어 뜻을 적어 두어, 그림이 뜻과 맞는지도 같이 본다.

  python3 scripts/build_contact_sheets.py <내보낼 폴더>
"""

import json
import pathlib
import re
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/sheets")

COLS, ROWS = 6, 6
CELL = 240
LABEL = 34
PAD = 6
HEAD = 30

LEVELS = {
    "en": [("middle-1", "m1"), ("middle-2", "m2"), ("middle-3", "m3"),
           ("high-1", "h1"), ("high-2", "h2"), ("high-3", "h3"),
           ("toeic", "tc"), ("toefl", "tf")],
    "ja": [("jlpt-n5", "n5")],
}

FONT_KO = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
FONT_EN = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def load_index():
    """그림 파일 열쇠 → (보여 줄 낱말, 뜻, 소속 단계)"""
    info: dict[str, tuple[str, str, str]] = {}
    for lang, levels in LEVELS.items():
        words = json.loads((ROOT / f"src/data/{lang}/words.json").read_text("utf-8"))
        tr = json.loads((ROOT / f"src/data/{lang}/tr/ko.json").read_text("utf-8"))
        meanings = tr.get("meanings", {})
        for level, code in levels:
            p = ROOT / f"src/data/{lang}/levels/{level}.json"
            if not p.exists():
                continue
            for i, sp in enumerate(json.loads(p.read_text("utf-8"))):
                cid = (words.get(sp) or {}).get("conceptId", sp)
                key = re.sub(r"\s+", "-", cid)
                if key in info:
                    continue
                info[key] = (sp, meanings.get(f"{code}-{i+1}", ""), f"{level}")
    return info


def fit(draw, text, font, width):
    """칸 너비에 맞게 글자를 자른다"""
    if not text:
        return ""
    while text and draw.textlength(text, font=font) > width:
        text = text[:-1]
    return text


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    info = load_index()
    files = sorted((ROOT / "assets/words").rglob("*.png"),
                   key=lambda p: (info.get(p.stem, ("", "", "zzz"))[2], p.stem))

    f_en = ImageFont.truetype(FONT_EN, 15)
    f_ko = ImageFont.truetype(FONT_KO, 14)
    f_hd = ImageFont.truetype(FONT_EN, 18)

    cw = CELL + PAD
    ch = CELL + LABEL + PAD
    W = COLS * cw + PAD
    H = HEAD + ROWS * ch + PAD

    total = (len(files) + COLS * ROWS - 1) // (COLS * ROWS)
    for n in range(total):
        chunk = files[n * COLS * ROWS : (n + 1) * COLS * ROWS]
        sheet = Image.new("RGB", (W, H), "#ffffff")
        d = ImageDraw.Draw(sheet)
        levels = sorted({info.get(p.stem, ("", "", "?"))[2] for p in chunk})
        d.text((PAD, 7), f"sheet {n+1}/{total}   [{', '.join(levels)}]",
               fill="#000000", font=f_hd)

        for k, p in enumerate(chunk):
            r, c = divmod(k, COLS)
            x = PAD + c * cw
            y = HEAD + r * ch
            try:
                with Image.open(p) as im:
                    sheet.paste(im.convert("RGB").resize((CELL, CELL)), (x, y))
            except Exception:
                d.rectangle([x, y, x + CELL, y + CELL], fill="#ffdddd")
            d.rectangle([x, y, x + CELL, y + CELL], outline="#bbbbbb")

            word, meaning, _ = info.get(p.stem, (p.stem, "", "?"))
            # 칸 번호를 적어 두면 문제가 있는 칸을 짚어 말하기 쉽다
            tag = f"{k+1:02d} {word}"
            d.text((x + 2, y + CELL + 1), fit(d, tag, f_en, CELL - 4),
                   fill="#000000", font=f_en)
            d.text((x + 2, y + CELL + 17), fit(d, meaning, f_ko, CELL - 4),
                   fill="#555555", font=f_ko)

        sheet.save(OUT / f"sheet_{n+1:03d}.png")
        if (n + 1) % 25 == 0:
            print(f"  {n+1}/{total}", flush=True)

    print(f"{total}장 생성 → {OUT}")


if __name__ == "__main__":
    main()
