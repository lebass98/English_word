#!/usr/bin/env python3
"""
FLUX.1 [schnell] GGUF 4bit 모델 다운로드 스크립트
- VAE, CLIP-L, T5-XXL Q4, FLUX.1-schnell Q4_K_S 를 다운로드합니다.
"""

import os
import sys
import time
import urllib.request

FILES = [
    {
        "name": "ae.safetensors (FLUX VAE)",
        "url": "https://huggingface.co/modelzpalace/ae.safetensors/resolve/main/ae.safetensors",
        "dest": "/Users/ijaegwang/ComfyUI-Shared/models/vae/ae.safetensors",
    },
    {
        "name": "clip_l.safetensors (CLIP-L)",
        "url": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors",
        "dest": "/Users/ijaegwang/ComfyUI-Shared/models/clip/clip_l.safetensors",
    },
    {
        "name": "t5-v1_1-xxl-encoder-Q4_K_M.gguf (T5-XXL Q4)",
        "url": "https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf/resolve/main/t5-v1_1-xxl-encoder-Q4_K_M.gguf",
        "dest": "/Users/ijaegwang/ComfyUI-Shared/models/clip/t5-v1_1-xxl-encoder-Q4_K_M.gguf",
    },
    {
        "name": "flux1-schnell-Q4_K_S.gguf (FLUX.1 schnell UNet)",
        "url": "https://huggingface.co/city96/FLUX.1-schnell-gguf/resolve/main/flux1-schnell-Q4_K_S.gguf",
        "dest": "/Users/ijaegwang/ComfyUI-Shared/models/unet/flux1-schnell-Q4_K_S.gguf",
    },
]


def download_file(item):
    name = item["name"]
    url = item["url"]
    dest = item["dest"]
    part = dest + ".part"

    os.makedirs(os.path.dirname(dest), exist_ok=True)

    if os.path.exists(dest) and os.path.getsize(dest) > 1000000:
        size_mb = os.path.getsize(dest) / (1024 * 1024)
        print(f"[{name}] 이미 존재함 ({size_mb:.1f} MB) - 건너뜀", flush=True)
        return

    print(f"\n==========================================", flush=True)
    print(f"[{name}] 다운로드 시작...", flush=True)
    print(f"URL: {url}", flush=True)
    print(f"저장 경로: {dest}", flush=True)

    existing_size = os.path.getsize(part) if os.path.exists(part) else 0
    headers = {"User-Agent": "Mozilla/5.0"}
    if existing_size > 0:
        headers["Range"] = f"bytes={existing_size}-"
        print(f"이어받기 시작: {existing_size / (1024*1024):.1f} MB 부터", flush=True)

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        content_range = resp.headers.get("Content-Range")
        if content_range:
            total_size = int(content_range.split("/")[-1])
        else:
            total_size = int(resp.headers.get("Content-Length", 0)) + existing_size

        mode = "ab" if existing_size > 0 else "wb"
        downloaded = existing_size
        t0 = time.time()
        last_log = t0

        with open(part, mode) as f:
            while True:
                chunk = resp.read(1024 * 1024 * 4)  # 4MB
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                now = time.time()
                if now - last_log >= 10:
                    elapsed = now - t0
                    speed = (downloaded - existing_size) / (1024 * 1024) / elapsed if elapsed > 0 else 0
                    pct = (downloaded / total_size * 100) if total_size > 0 else 0
                    print(
                        f"  -> {downloaded/(1024*1024):.1f} / {total_size/(1024*1024):.1f} MB ({pct:.1f}%) | {speed:.1f} MB/s",
                        flush=True,
                    )
                    last_log = now

    os.rename(part, dest)
    print(f"[{name}] 다운로드 완료! -> {dest}", flush=True)


def main():
    print("==========================================================")
    print(" FLUX.1 [schnell] GGUF 4bit 필수 모델 일괄 다운로드")
    print("==========================================================")

    for item in FILES:
        download_file(item)

    # diffusion_models 에도 심볼릭 링크 생성 (호환성 확보)
    unet_file = "/Users/ijaegwang/ComfyUI-Shared/models/unet/flux1-schnell-Q4_K_S.gguf"
    diff_dir = "/Users/ijaegwang/ComfyUI-Shared/models/diffusion_models"
    diff_link = os.path.join(diff_dir, "flux1-schnell-Q4_K_S.gguf")
    if os.path.exists(unet_file) and not os.path.exists(diff_link):
        try:
            os.symlink(unet_file, diff_link)
        except Exception:
            pass

    print("\n🎉 모든 FLUX.1 [schnell] 모델 다운로드 및 세팅 완료!")


if __name__ == "__main__":
    main()
