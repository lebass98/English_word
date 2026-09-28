#!/usr/bin/env python3
"""단어 그림을 384px 리사이즈 + 색상 양자화 + AVIF 변환하여 내보낸다.

1) AVIF 포맷: 차세대 코덱으로 WebP 대비 20~30% 높은 압축률
2) 색상 양자화: 선형그래픽 특성을 살려 64색 팔레트로 최적화
3) 384px 리사이징: 모바일 최적 해상도로 용량 급감

사용법:
    # Git 원본 히스토리에서 직접 추출하여 내보낼 때:
    python3 scripts/export_avif_images.py <내보낼 폴더> --from-git

    # 지정 폴더의 PNG/WebP 들을 변환할 때:
    python3 scripts/export_avif_images.py <내보낼 폴더> --src <원본 폴더>
"""

import argparse
import os
import pathlib
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor

import pillow_heif
from PIL import Image

pillow_heif.register_heif_opener()

ROOT = pathlib.Path(__file__).resolve().parent.parent


def convert_one(job) -> tuple[int, int]:
    src_path, dst_path, size, quality, quantize_colors = job
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    before = src_path.stat().st_size

    try:
        with Image.open(src_path) as im:
            im = im.convert("RGB")
            # 1. 384px 리사이징 (3번)
            if im.width != size or im.height != size:
                im = im.resize((size, size), Image.Resampling.LANCZOS)

            # 2. 색상 양자화 (2번) - 선형그래픽 최적화
            if quantize_colors and quantize_colors > 0:
                im = im.quantize(colors=quantize_colors).convert("RGB")

            # 3. AVIF 고효율 인코딩 (1번)
            im.save(dst_path, format="AVIF", quality=quality)
        return before, dst_path.stat().st_size
    except Exception as e:
        print(f"Error converting {src_path}: {e}", file=sys.stderr)
        return before, 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", help="결과물이 저장될 폴더")
    ap.add_argument("--src", help="원본 이미지 폴더 (기본: assets/words)")
    ap.add_argument("--from-git", action="store_true", help="Git 히스토리(f3de609c^)에서 원본 추출")
    ap.add_argument("--size", type=int, default=384, help="가로/세로 픽셀 (기본: 384)")
    ap.add_argument("--quality", type=int, default=65, help="AVIF 품질 (기본: 65)")
    ap.add_argument("--quantize", type=int, default=64, help="팔레트 색상 수 (기본: 64, 0이면 해제)")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out)
    temp_dir = None

    if args.from_git:
        temp_dir = tempfile.TemporaryDirectory()
        src_dir = pathlib.Path(temp_dir.name) / "words"
        src_dir.mkdir(parents=True, exist_ok=True)
        print("Git 히스토리(f3de609c^)에서 원본 PNG 추출 중...")
        cmd = "git archive f3de609c^ assets/words/ | tar -x -C " + str(temp_dir.name)
        subprocess.run(cmd, shell=True, check=True, cwd=str(ROOT))
        src_dir = pathlib.Path(temp_dir.name) / "assets/words"
    elif args.src:
        src_dir = pathlib.Path(args.src)
    else:
        src_dir = ROOT / "assets/words"

    if not src_dir.exists():
        print(f"원본 폴더를 찾을 수 없습니다: {src_dir}", file=sys.stderr)
        print("힌트: Git 원본에서 추출하려면 --from-git 플래그를 사용하세요.", file=sys.stderr)
        return 1

    files = sorted(list(src_dir.rglob("*.png")) + list(src_dir.rglob("*.webp")))
    if not files:
        print(f"{src_dir} 안에 변환할 이미지가 없습니다.", file=sys.stderr)
        return 1

    print(f"총 {len(files)}장 이미지 변환 준비 완료 (AVIF q={args.quality}, size={args.size}px, quantize={args.quantize}색)")
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs = [
        (f, out_dir / f.relative_to(src_dir).with_suffix(".avif"), args.size, args.quality, args.quantize)
        for f in files
    ]

    before = after = 0
    workers = os.cpu_count() or 4
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i, (b, a) in enumerate(pool.map(convert_one, jobs, chunksize=32), 1):
            before += b
            after += a
            if i % 200 == 0 or i == len(files):
                print(f"  진행률: {i}/{len(files)} ({(i/len(files))*100:.1f}%)", flush=True)

    print(
        f"\n변환 완료!\n"
        f"  - 원본 총용량: {before/1048576:.1f} MB\n"
        f"  - AVIF 총용량: {after/1048576:.1f} MB\n"
        f"  - 절감률: {100 - after/before*100:.1f}%\n"
        f"  - 파일당 평균: {after/len(files)/1024:.1f} KB\n"
        f"  - 저장 위치: {out_dir}\n"
    )

    if temp_dir:
        temp_dir.cleanup()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
