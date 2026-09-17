#!/usr/bin/env python3
"""assets/words/<글자>/<철자>.png 를 글자별 등록 파일에 다시 적는다.

- src/constants/wordImagesByLetter/<글자>.ts : 그 글자로 시작하는 그림만 require 한다
- src/constants/wordImages.ts                : 글자별 파일을 합쳐 WORD_IMAGES 로 내보낸다
                                               (화면은 이것만 쓴다)

글자별로 나눈 이유: 여러 컴퓨터가 알파벳 범위를 나눠 그림을 그리므로 각자 자기
글자 파일만 바꾸게 되어, 올릴 때 등록 파일끼리 충돌하지 않는다.
내용이 같으면 파일을 다시 쓰지 않는다.

화면은 그림을 단어 번호가 아니라 conceptId(= 뜻)와 철자로 찾으므로 열쇠는 철자다.
띄어쓰기가 있는 낱말은 파일 이름에서 빈칸을 붙임표로 바꾼다 (living room → l/living-room.png).
a~z 가 아닌 글자로 시작하면 "_" 폴더에 둔다.

    python3 scripts/sync_word_images.py
"""
import json
import os
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets/words")
BY_LETTER_DIR = os.path.join(ROOT, "src/constants/wordImagesByLetter")
INDEX = os.path.join(ROOT, "src/constants/wordImages.ts")
LETTERS = [chr(c) for c in range(ord("a"), ord("z") + 1)] + ["_"]

LETTER_HEADER = '''import { ImageSourcePropType } from "react-native";

// "{letter}" 로 시작하는 단어 그림. scripts/sync_word_images.py 가 만든다 (손으로 고치지 않는다)
'''

INDEX_HEADER = '''import { ImageSourcePropType } from "react-native";

/**
 * 단어별 연상 이미지 모음.
 *
 * 열쇠는 단어의 철자(= 뜻을 가리키는 conceptId)다. 그림은 철자 하나에 한 장이고,
 * 학년·코스는 철자 목록만 가지므로 같은 철자는 어느 과정에서든 같은 그림을 쓴다.
 *
 * 그림은 assets/words/<첫 글자>/<철자>.png 에 두고, 등록은 글자별 파일
 * (wordImagesByLetter/<글자>.ts) 에 나눠 적는다. 여러 컴퓨터가 알파벳 범위를
 * 나눠 그림을 그려도 등록 파일끼리 충돌하지 않게 하려는 것이다.
 *
 * 이 파일과 글자별 파일은 scripts/sync_word_images.py 가 만든다. 손으로 고치지 않는다.
 */
'''


def letter_of(stem):
    first = stem[:1].lower()
    return first if "a" <= first <= "z" else "_"


def ident(letter):
    return "IMAGES_" + ("OTHER" if letter == "_" else letter.upper())


def known_keys():
    """등록해도 되는 열쇠 모음 (모든 학습 언어의 철자와 conceptId)"""
    keys = set()
    for lang in os.listdir(os.path.join(ROOT, "src/data")):
        path = os.path.join(ROOT, "src/data", lang, "words.json")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for spelling, entry in json.load(f).items():
                s_norm = unicodedata.normalize("NFC", spelling)
                c_norm = unicodedata.normalize("NFC", entry.get("conceptId") or spelling)
                keys.add(s_norm)
                keys.add(c_norm)
    return keys


def write_if_changed(path, text):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            if f.read() == text:
                return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return True


def main():
    keys = known_keys()
    rows = {letter: [] for letter in LETTERS}
    orphans, misplaced = [], []

    # 글자 폴더 밖(assets/words 바로 아래)에 남은 그림은 옮기기 전 모습이다
    for name in sorted(os.listdir(ASSETS)):
        if name.endswith(".png") and not name.startswith("._") and os.path.isfile(os.path.join(ASSETS, name)):
            misplaced.append(name)

    for letter in LETTERS:
        folder = os.path.join(ASSETS, letter)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".png") or name.startswith("._"):
                continue
            stem = unicodedata.normalize("NFC", name[:-4])
            if letter_of(stem) != letter:
                misplaced.append(f"{letter}/{name}")
                continue
            key = stem if stem in keys else stem.replace("-", " ")
            if key not in keys:
                orphans.append(f"{letter}/{name}")
                continue
            rows[letter].append((key, name))

    if misplaced:
        print(
            f"글자 폴더에 맞지 않는 그림 {len(misplaced)}개: {misplaced[:20]}\n"
            "scripts/migrate_images_by_letter.py 로 옮기거나 알맞은 글자 폴더에 두세요",
            file=sys.stderr,
        )
        return 1

    seen = {}
    for letter in LETTERS:
        rows[letter].sort(key=lambda r: r[0].lower())
        for key, name in rows[letter]:
            if key in seen:
                print(f"열쇠가 겹칩니다: {key} ← {seen[key]}, {letter}/{name}", file=sys.stderr)
                return 1
            seen[key] = f"{letter}/{name}"

    changed = []
    for letter in LETTERS:
        body = "".join(
            (f'  {k}: require("../../../assets/words/{letter}/{n}"),\n' if k.isidentifier()
             else f'  {json.dumps(k, ensure_ascii=False)}: require("../../../assets/words/{letter}/{n}"),\n')
            for k, n in rows[letter]
        )
        text = (
            LETTER_HEADER.replace("{letter}", letter)
            + f"export const {ident(letter)}: Record<string, ImageSourcePropType> = {{\n"
            + body
            + "};\n"
        )
        if write_if_changed(os.path.join(BY_LETTER_DIR, f"{letter}.ts"), text):
            changed.append(letter)

    imports = "".join(f'import {{ {ident(l)} }} from "./wordImagesByLetter/{l}";\n' for l in LETTERS)
    spread = "".join(f"  ...{ident(l)},\n" for l in LETTERS)
    index = (
        INDEX_HEADER
        + imports
        + "\nexport const WORD_IMAGES: Record<string, ImageSourcePropType> = {\n"
        + spread
        + "};\n"
    )
    if write_if_changed(INDEX, index):
        changed.append("wordImages.ts")

    print(f"그림 {len(seen)}개 등록 | 바뀐 등록 파일: {', '.join(changed) or '없음'}")
    if orphans:
        print(f"짝이 없어 건너뛴 파일 {len(orphans)}개: {orphans}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
