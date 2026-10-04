#!/usr/bin/env python3
"""일자별로 그림을 몇 장 만들었는지 git 기록에서 뽑아 낸다.

앱은 번들 안에서 돌아가므로 git 을 볼 수 없다. 그래서 여기서 미리 세어
src/data/images/dailyCounts.json 에 적어 두고, 현황판이 그 파일을 읽는다.

그림을 새로 만든 뒤 현황판의 날짜별 수를 갱신하려면 이 스크립트를 다시 돌린다:

    python3 scripts/image_daily_counts.py

그림 한 장마다 자동으로 돌리지는 않는다. 여러 컴퓨터가 같은 저장소에
그림을 올리고 있어서, 매 커밋마다 이 파일이 바뀌면 서로 부딪히기 때문이다.
"""

import json
import os
import re
import subprocess
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "data", "images", "dailyCounts.json")


REPO = os.path.join(os.path.dirname(ROOT), "word-images-repo")
KEYS_FILE = os.path.join(ROOT, "src", "constants", "wordImageKeys.ts")


def git_log(cwd: str, *paths: str) -> str:
    return subprocess.run(
        [
            "git", "log", "--reverse", "--diff-filter=ADR", "--name-status",
            "-M", "--pretty=format:#%ad", "--date=short", "--", *paths,
        ],
        cwd=cwd, capture_output=True, text=True, check=True,
    ).stdout


def slug_of(path: str) -> str:
    """assets/words/l/living-room.png → living-room"""
    return os.path.splitext(os.path.basename(path))[0]


def added_by_date() -> Counter:
    """그림이 처음 만들어진 날짜별 장수.

    그림은 2026-09-24 에 앱 저장소(assets/words)에서 그림 저장소(../word-images-repo)
    로 옮겨졌다. 그래서 두 곳의 기록을 이어 본다.

    - 앱 저장소: 처음 그린 날. 옮기면서 지운 기록(D)은 무시한다
    - 그림 저장소: 옮긴 뒤 새로 더한 그림. 옮긴 날 한꺼번에 올린 것은
      앱 저장소에서 이미 날짜를 알고 있으므로 덮어쓰지 않는다

    파일을 옮기거나 이름을 고친 기록(R)은 이름(철자)으로 묶이므로 따로 따라가지
    않아도 처음 만든 날이 남는다.
    """
    created: dict[str, str] = {}
    for cwd, paths, ext in ((ROOT, ("assets/words",), ".png"),
                            (REPO, ("*.webp",), ".webp")):
        if not os.path.isdir(cwd):
            continue
        date = None
        for line in git_log(cwd, *paths).splitlines():
            if not line.strip():
                continue
            if line.startswith("#"):
                date = line[1:].strip()
                continue
            parts = line.split("\t")
            kind = parts[0]
            if (kind.startswith("A") or kind.startswith("R")) and parts[-1].endswith(ext):
                created.setdefault(slug_of(parts[-1]), date)

    # 지금 등록표에 있는 그림만 센다. 그래야 날짜별 합이 전체 장수와 맞는다
    text = open(KEYS_FILE, encoding="utf-8").read()
    keys = json.loads("[" + ",".join(re.findall(r'^\s*(".*"),?$', text, re.M)) + "]")
    counts: Counter = Counter()
    for key in keys:
        day = created.get(re.sub(r"\s+", "-", key.strip()))
        if day:
            counts[day] += 1
    return counts


def main() -> None:
    counts = added_by_date()
    days = [{"date": d, "count": c} for d, c in sorted(counts.items())]
    data = {
        "generatedAt": subprocess.run(
            ["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True
        ).stdout.strip(),
        "total": sum(counts.values()),
        "days": days,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, OUT)

    print(f"{len(days)}일치, 전체 {data['total']}장 → {os.path.relpath(OUT, ROOT)}")
    for d in days[-7:]:
        print(f"  {d['date']}  {d['count']:>4}장")


if __name__ == "__main__":
    main()
