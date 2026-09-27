#!/usr/bin/env python3
"""assets/words/<글자>/<철자>.png 를 훑어 "그림이 있는 낱말" 목록을 적는다.

그림은 앱에 넣지 않고 CDN 에서 받아 온다 (src/constants/wordImages.ts 참고).
그래서 여기서는 파일을 require 하지 않고, 어떤 낱말에 그림이 있는지만 적는다.

- src/constants/wordImageKeys.ts : 그림이 있는 낱말의 열쇠 목록

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
KEYS_FILE = os.path.join(ROOT, "src/constants/wordImageKeys.ts")
OLD_BY_LETTER_DIR = os.path.join(ROOT, "src/constants/wordImagesByLetter")
LETTERS = [chr(c) for c in range(ord("a"), ord("z") + 1)] + ["_"]

KEYS_HEADER = """/**
 * 연상 그림이 있는 낱말 목록.
 *
 * 그림 파일은 앱에 넣지 않고 CDN 에서 받아 온다. 그래서 여기에는 파일이 아니라
 * "이 낱말에는 그림이 있다"는 사실만 적는다. 실제 주소를 만드는 일은
 * wordImages.ts 가 한다.
 *
 * 이 파일은 scripts/sync_word_images.py 가 만든다. 손으로 고치지 않는다.
 */
export const WORD_IMAGE_KEYS: readonly string[] = [
"""


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

    keys = sorted(seen, key=lambda k: k.lower())
    body = "".join(f"  {json.dumps(k, ensure_ascii=False)},\n" for k in keys)
    changed = []
    if write_if_changed(KEYS_FILE, KEYS_HEADER + body + "];\n"):
        changed.append("wordImageKeys.ts")

    # 예전에 쓰던 글자별 require 파일이 남아 있으면 지운다 (이제 CDN 에서 받는다)
    if os.path.isdir(OLD_BY_LETTER_DIR):
        import shutil

        shutil.rmtree(OLD_BY_LETTER_DIR)
        changed.append("wordImagesByLetter/ 제거")

    print(f"그림 {len(seen)}개 등록 | 바뀐 등록 파일: {', '.join(changed) or '없음'}")
    if orphans:
        print(f"짝이 없어 건너뛴 파일 {len(orphans)}개: {orphans}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
