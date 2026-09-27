#!/usr/bin/env python3
"""단어 그림을 WebP 384px 로 바꿔 별도 폴더에 내보낸다.

앱이 그림을 화면에 띄우는 크기는 아무리 커도 400px 남짓이라 512px 원본은 과하다.
384px WebP 로 바꾸면 전체 용량이 236MB 에서 60MB 안팎으로 줄어, 깃허브 레포에
올려 두고 jsDelivr CDN 으로 받아 쓸 수 있다.

원본 PNG 는 그대로 둔다. 다시 뽑거나 크기를 바꿀 때 원본이 있어야 한다.

    python3 scripts/export_webp_images.py <내보낼 폴더> [--size 384] [--quality 80]
"""

import argparse
import os
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/words"


def convert(job) -> tuple[int, int]:
    src, dst, size, quality = job
    dst.parent.mkdir(parents=True, exist_ok=True)
    before = src.stat().st_size
    with Image.open(src) as im:
        im = im.convert("RGB")
        if im.width != size:
            im = im.resize((size, size), Image.LANCZOS)
        # method=6 이 가장 잘 줄이지만 느리다. 4 면 거의 같은 크기에 훨씬 빠르다
        im.save(dst, format="WEBP", quality=quality, method=4)
    return before, dst.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", help="내보낼 폴더")
    ap.add_argument("--size", type=int, default=384)
    ap.add_argument("--quality", type=int, default=80)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    files = sorted(SRC.rglob("*.png"))
    if not files:
        print("원본 그림을 찾지 못했다", file=sys.stderr)
        return 1

    jobs = [
        (f, out / f.relative_to(SRC).with_suffix(".webp"), args.size, args.quality)
        for f in files
    ]

    before = after = 0
    workers = os.cpu_count() or 4
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i, (b, a) in enumerate(pool.map(convert, jobs, chunksize=32), 1):
            before += b
            after += a
            if i % 500 == 0:
                print(f"  {i}/{len(files)}", flush=True)

    print(
        f"\n{len(files)}장 변환 완료\n"
        f"  {before/1048576:.1f} MB → {after/1048576:.1f} MB "
        f"({100 - after/before*100:.1f}% 절감)\n"
        f"  평균 {after/len(files)/1024:.1f} KB\n"
        f"→ {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
