#!/usr/bin/env python3
"""
assets/words 내 512px를 초과하는 모든 단어 이미지를 512x512로 일괄 리사이즈하는 스크립트.
- macOS 내장 sips 명령어를 활용하여 고품질 리샘플링 수행
- 멀티스레딩(8 worker)으로 빠른 병렬 처리
- 처리 전/후 용량 및 해상도 검증 리포트 출력
"""

import os
import sys
import time
import struct
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")

def get_png_dimensions(path: str):
    try:
        with open(path, "rb") as f:
            data = f.read(24)
            if data[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", data[16:24])
                return w, h
    except Exception:
        pass
    return None

def resize_image(path: str):
    cmd = ["sips", "-z", "512", "512", path]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        return path, False, res.stderr
    return path, True, None

def main():
    print("단어 이미지 스캔 시작...")
    targets = []
    total_scanned = 0
    size_before = 0

    for root, dirs, files in os.walk(ASSETS_DIR):
        for f in files:
            if f.lower().endswith(".png"):
                total_scanned += 1
                p = os.path.join(root, f)
                dims = get_png_dimensions(p)
                if dims:
                    w, h = dims
                    if w > 512 or h > 512:
                        sz = os.path.getsize(p)
                        size_before += sz
                        targets.append((p, w, h, sz))

    print(f"전체 단어 이미지 {total_scanned}개 중 리사이즈 대상(>512px): {len(targets)}개")
    print(f"대상 파일 총 용량 (리사이즈 전): {size_before / (1024 * 1024):.2f} MB")

    if not targets:
        print("모든 이미지가 이미 512x512 이하입니다. 작업을 종료합니다.")
        return

    print("512x512 리사이즈 실행 중 (8 workers)...")
    start_time = time.time()
    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(resize_image, t[0]): t for t in targets}
        done_count = 0
        total_targets = len(targets)
        for future in as_completed(futures):
            path, success, err = future.result()
            done_count += 1
            if success:
                success_count += 1
            else:
                fail_count += 1
                print(f"[실패] {path}: {err}")

            if done_count % 200 == 0 or done_count == total_targets:
                elapsed = time.time() - start_time
                print(f"진행: {done_count}/{total_targets} ({done_count*100//total_targets}%) - {elapsed:.1f}s 경과")

    elapsed_total = time.time() - start_time
    print(f"\n리사이즈 완료: 성공 {success_count}개, 실패 {fail_count}개 (총 소요 시간: {elapsed_total:.2f}초)")

    # 검증 및 용량 비교
    size_after = 0
    post_non_512 = 0
    for t in targets:
        p = t[0]
        size_after += os.path.getsize(p)
        dims = get_png_dimensions(p)
        if dims != (512, 512):
            post_non_512 += 1
            print(f"[검증 오류] {p}: {dims}")

    saved_mb = (size_before - size_after) / (1024 * 1024)
    print("========================================")
    print(f"리사이즈 전 총 용량: {size_before / (1024 * 1024):.2f} MB")
    print(f"리사이즈 후 총 용량: {size_after / (1024 * 1024):.2f} MB")
    print(f"절감된 용량: {saved_mb:.2f} MB ({(saved_mb / (size_before / (1024 * 1024))) * 100:.1f}% 감소)")
    print(f"512x512 미달/초과 파일 수: {post_non_512}개")
    print("========================================")

if __name__ == "__main__":
    main()
