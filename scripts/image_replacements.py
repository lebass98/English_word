#!/usr/bin/env python3
"""그림 저장소(../word-images-repo)의 git 기록에서 "교체한 그림"을 뽑아 낸다.

처음 올린 뒤 내용을 다시 바꾼(M) 그림이 교체한 그림이다. 결과는
src/data/images/replaced.json 에 적고, 앱은 그 파일을 두 곳에서 쓴다.

- 현황 화면: 교체한 그림에 "교체됨" 표시를 붙이고, 교체한 것만 골라 본다
- 그림 주소: 교체한 그림 주소 끝에 ?v=<커밋> 을 붙인다. 주소가 같으면
  expo-image 가 디스크에 담아 둔 옛 그림을 그대로 보여 주기 때문이다

그림을 교체해 그림 저장소에 올린 뒤에는 이 스크립트를 다시 돌린다:

    python3 scripts/image_replacements.py
"""

import json
import os
import re
import subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(os.path.dirname(ROOT), "word-images-repo")
KEYS_FILE = os.path.join(ROOT, "src/constants/wordImageKeys.ts")
OUT = os.path.join(ROOT, "src/data/images/replaced.json")


def slug_to_key() -> dict[str, str]:
    """파일 이름(living-room) → 등록표 열쇠(living room)"""
    text = open(KEYS_FILE, encoding="utf-8").read()
    keys = json.loads("[" + ",".join(re.findall(r'^\s*(".*"),?$', text, re.M)) + "]")
    return {re.sub(r"\s+", "-", k.strip()): k for k in keys}


def replaced() -> dict[str, dict]:
    """열쇠 → {date: 마지막으로 교체한 날, rev: 그 커밋, count: 교체 횟수}"""
    log = subprocess.run(
        ["git", "log", "--reverse", "--diff-filter=M", "--name-status",
         "--pretty=format:#%h %ad", "--date=short", "--", "*.webp"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout

    keys = slug_to_key()
    out: dict[str, dict] = {}
    rev = date = None
    for line in log.splitlines():
        if not line.strip():
            continue
        if line.startswith("#"):
            rev, date = line[1:].split()
            continue
        path = line.split("\t")[-1]
        slug = os.path.splitext(os.path.basename(path))[0]
        # macOS 가 외장하드에 만드는 ._ 메타데이터 파일은 그림이 아니다
        if slug.startswith("._"):
            continue
        key = keys.get(slug, slug.replace("-", " "))
        prev = out.get(key, {"count": 0})
        out[key] = {"date": date, "rev": rev, "count": prev["count"] + 1}
    return out


def main():
    items = replaced()
    data = {
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(items),
        # 최근에 교체한 것이 앞에 오게 둔다
        "items": dict(sorted(items.items(), key=lambda kv: kv[1]["date"], reverse=True)),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"교체한 그림 {len(items)}장 → {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
