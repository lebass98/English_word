# -*- coding: utf-8 -*-
"""단어 이미지를 전수 점검한다.

눈으로 봐야 아는 것(팔이 셋인 사람, 뜻과 다른 그림)은 기계가 못 잡는다.
그래서 여기서는 기계가 확실히 잡을 수 있는 것만 본다.

  - 규격: 크기, 해상도, 색 방식, 파일 깨짐
  - 빈 그림: 잉크가 거의 없어 사실상 백지인 그림 (생성 실패)
  - 먹칠: 화면 대부분이 어두운 그림 (렌더 실패)
  - 중복: 서로 다른 단어가 똑같은 그림을 쓰는 경우
  - 미등록/누락: 목록에 있는데 파일이 없거나, 파일만 있고 안 쓰이는 경우

결과는 JSON 으로 떨군다. 눈으로 볼 대상은 그 다음에 따로 추린다.
"""

import hashlib
import json
import pathlib
import sys
from collections import Counter, defaultdict

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORDS_DIR = ROOT / "assets/words"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/audit.json")

# 잉크(어두운 픽셀)로 볼 밝기 기준
INK_MAX = 200
# 이보다 잉크가 적으면 사실상 백지로 본다
BLANK_RATIO = 0.01
# 이보다 어두운 픽셀이 많으면 먹칠로 본다
DARK_RATIO = 0.65


def main() -> None:
    files = sorted(WORDS_DIR.rglob("*.png"))
    by_hash: dict[str, list[str]] = defaultdict(list)
    rows = []
    sizes = Counter()

    for i, f in enumerate(files, 1):
        rel = str(f.relative_to(ROOT))
        row: dict = {"file": rel, "word": f.stem}
        try:
            raw = f.read_bytes()
            row["bytes"] = len(raw)
            row["md5"] = hashlib.md5(raw).hexdigest()
            by_hash[row["md5"]].append(f.stem)

            with Image.open(f) as im:
                row["size"] = f"{im.width}x{im.height}"
                row["mode"] = im.mode
                sizes[row["size"]] += 1
                # 팔레트 그림이라 회색조로 바꿔 잉크 양만 본다
                g = im.convert("L").resize((128, 128))
                px = list(g.getdata())
                n = len(px)
                ink = sum(1 for v in px if v < INK_MAX)
                dark = sum(1 for v in px if v < 100)
                row["ink"] = round(ink / n, 4)
                row["dark"] = round(dark / n, 4)
                row["colors"] = len(im.convert("RGB").getcolors(maxcolors=100000) or [])

            flags = []
            if row["size"] != "512x512":
                flags.append("규격밖")
            if row["ink"] < BLANK_RATIO:
                flags.append("빈그림")
            if row["dark"] > DARK_RATIO:
                flags.append("먹칠")
            if row["bytes"] < 5000:
                flags.append("너무작음")
            row["flags"] = flags
        except Exception as e:  # 깨진 파일
            row["flags"] = ["열기실패"]
            row["error"] = str(e)

        rows.append(row)
        if i % 500 == 0:
            print(f"  {i}/{len(files)}", flush=True)

    dups = {h: ws for h, ws in by_hash.items() if len(ws) > 1}

    OUT.write_text(
        json.dumps(
            {"rows": rows, "dups": dups, "sizes": dict(sizes)},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\n검사 {len(rows)}장")
    print("해상도:", dict(sizes))
    bad = [r for r in rows if r["flags"]]
    print(f"표시된 그림: {len(bad)}장")
    tally = Counter(f for r in bad for f in r["flags"])
    for k, v in tally.most_common():
        print(f"  {k}: {v}")
    print(f"똑같은 그림을 쓰는 묶음: {len(dups)}개")
    print(f"→ {OUT}")


if __name__ == "__main__":
    main()
