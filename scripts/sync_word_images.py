#!/usr/bin/env python3
"""assets/words 의 그림을 src/constants/wordImages.ts 에 다시 등록한다.

화면은 그림을 단어 번호가 아니라 conceptId(= 뜻)와 철자로 찾는다.
그래서 등록 열쇠는 반드시 철자여야 하고, 파일을 넣고 등록을 빠뜨리면
그림이 있어도 안 나온다. 그림을 추가한 뒤 이 스크립트를 돌리면 된다.

    python3 scripts/sync_word_images.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets/words")
TARGET = os.path.join(ROOT, "src/constants/wordImages.ts")

HEADER = '''import { ImageSourcePropType } from "react-native";

/**
 * 단어별 연상 이미지 모음.
 *
 * 열쇠는 단어의 철자(= 뜻을 가리키는 conceptId)다. 예전에는 `m1-1` 같은
 * 단어 번호로도 등록했는데, 화면은 번호가 아니라 conceptId 와 철자로만
 * 찾으므로 번호로 등록한 그림은 영영 안 나왔다. 그래서 번호 열쇠는 없앴다.
 *
 * 이 파일은 scripts/sync_word_images.py 가 만든다. 손으로 고치지 말고
 * assets/words/<철자>.png 를 넣은 뒤 스크립트를 다시 돌리면 된다.
 * 띄어쓰기가 있는 낱말은 파일 이름에서 빈칸을 붙임표로 바꾼다
 * (living room → living-room.png).
 */
export const WORD_IMAGES: Record<string, ImageSourcePropType> = {
'''


def known_keys():
    """등록해도 되는 열쇠 모음 (모든 학습 언어의 철자와 conceptId)"""
    keys = set()
    for lang in os.listdir(os.path.join(ROOT, "src/data")):
        path = os.path.join(ROOT, "src/data", lang, "words.json")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for spelling, entry in json.load(f).items():
                keys.add(spelling)
                keys.add(entry.get("conceptId") or spelling)
    return keys


def main():
    keys = known_keys()
    rows, orphans = [], []
    for name in sorted(os.listdir(ASSETS)):
        if not name.endswith(".png"):
            continue
        stem = name[:-4]
        key = stem if stem in keys else stem.replace("-", " ")
        if key not in keys:
            orphans.append(name)
            continue
        rows.append((key, name))

    rows.sort(key=lambda r: r[0].lower())
    seen = {}
    for key, name in rows:
        if key in seen:
            print(f"열쇠가 겹칩니다: {key} ← {seen[key]}, {name}", file=sys.stderr)
            return 1
        seen[key] = name

    body = "\n".join(
        (f'  {k}: require("../../assets/words/{n}"),' if k.isidentifier()
         else f'  "{k}": require("../../assets/words/{n}"),')
        for k, n in rows
    )
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(HEADER + body + "\n};\n")

    print(f"그림 {len(rows)}개 등록")
    if orphans:
        print(f"짝이 없어 건너뛴 파일 {len(orphans)}개: {orphans}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
