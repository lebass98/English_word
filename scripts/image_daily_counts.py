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
import subprocess
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "data", "images", "dailyCounts.json")


def added_by_date() -> Counter:
    """그림 파일이 처음 만들어진 날짜별 장수.

    파일을 옮기거나 이름을 고친 기록(R)을 따라간다. 예전에 글자별 폴더로
    다시 묶으면서 assets/words/unless.png 가 assets/words/u/unless.png 로
    옮겨졌는데, 옮긴 날이 아니라 처음 그린 날로 세야 한다.

    기록을 옛날부터 훑으며 "지금 경로 → 처음 만든 날"을 이어 붙인다.
    """
    log = subprocess.run(
        [
            "git", "log", "--reverse", "--diff-filter=ADR", "--name-status",
            "-M", "--pretty=format:#%ad", "--date=short", "--", "assets/words",
        ],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout

    created: dict[str, str] = {}
    date = None
    for line in log.splitlines():
        if not line.strip():
            continue
        if line.startswith("#"):
            date = line[1:].strip()
            continue
        parts = line.split("\t")
        kind = parts[0]
        if kind.startswith("R") and len(parts) >= 3:
            # 옮긴 파일은 처음 만든 날을 그대로 들고 간다
            created[parts[2]] = created.pop(parts[1], date)
        elif kind.startswith("A") and len(parts) >= 2:
            created.setdefault(parts[1], date)
        elif kind.startswith("D") and len(parts) >= 2:
            created.pop(parts[1], None)

    # 지금 실제로 남아 있는 파일만 센다. 그래야 날짜별 합이 전체 장수와 맞는다
    counts: Counter = Counter()
    for path, day in created.items():
        if day and path.endswith(".png") and os.path.exists(os.path.join(ROOT, path)):
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
