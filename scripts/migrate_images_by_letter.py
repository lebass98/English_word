#!/usr/bin/env python3
"""assets/words/<철자>.png (한 폴더) 를 assets/words/<첫 글자>/<철자>.png 로 옮긴다. 한 번만 돌린다.

모든 컴퓨터의 그림 생성이 멈춘 상태에서 돌려야 한다 (생성 중인 쪽이 옛 경로에 그림을 쓰면 섞인다).

순서
  1) image_catalog.py  : 지금 그림의 그림체 버전을 그림 내용 지문(blob)과 함께 기록
  2) git mv            : 글자 폴더로 옮김 (파일 기록 유지). 아직 커밋 안 된 그림은 그냥 옮김
  3) sync_word_images.py : 글자별 등록 파일 생성
  4) image_catalog.py  : 다시 실행. 내용이 같은 그림은 1) 의 그림체 버전을 그대로 쓴다

    python3 scripts/migrate_images_by_letter.py --dry-run   # 옮길 목록만 확인
    python3 scripts/migrate_images_by_letter.py
"""
import argparse
import os
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets/words")


def letter_of(stem):
    first = stem[:1].lower()
    return first if "a" <= first <= "z" else "_"


def run(cmd):
    print("$", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="옮길 목록만 출력")
    args = parser.parse_args()

    flat = [
        name for name in sorted(os.listdir(ASSETS))
        if name.endswith(".png") and not name.startswith("._") and os.path.isfile(os.path.join(ASSETS, name))
    ]
    by_letter = defaultdict(list)
    for name in flat:
        by_letter[letter_of(name[:-4])].append(name)
    print(f"옮길 그림 {len(flat)}장:", dict(sorted(Counter({k: len(v) for k, v in by_letter.items()}).items())))
    if not flat:
        print("옮길 그림이 없습니다 (이미 옮김)")
        return 0
    if args.dry_run:
        return 0

    status = subprocess.run(["git", "status", "--porcelain", "--", "src", "scripts"], cwd=ROOT, capture_output=True, text=True)
    if status.stdout.strip():
        print("src/ 나 scripts/ 에 커밋 안 된 변경이 있습니다. 먼저 정리하세요:\n" + status.stdout, file=sys.stderr)
        return 1

    if run(["python3", "scripts/image_catalog.py"]).returncode:
        return 1

    untracked = set(subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", "assets/words"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.split())

    for letter, names in sorted(by_letter.items()):
        os.makedirs(os.path.join(ASSETS, letter), exist_ok=True)
        tracked = [f"assets/words/{n}" for n in names if f"assets/words/{n}" not in untracked]
        for n in names:
            if f"assets/words/{n}" in untracked:
                os.rename(os.path.join(ASSETS, n), os.path.join(ASSETS, letter, n))
        # 한 글자씩 여러 파일을 한 번에 옮긴다 (파일마다 git 을 부르면 외장하드에서 느리다)
        if tracked and run(["git", "mv", *tracked, f"assets/words/{letter}/"]).returncode:
            print(f"{letter} 폴더로 옮기다 실패했습니다", file=sys.stderr)
            return 1

    if run(["python3", "scripts/sync_word_images.py"]).returncode:
        return 1
    if run(["python3", "scripts/image_catalog.py"]).returncode:
        return 1
    print("완료. npm run lint 로 확인한 뒤 assets/words, src/constants, src/data/images 를 커밋하세요")
    return 0


if __name__ == "__main__":
    sys.exit(main())
