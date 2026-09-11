#!/usr/bin/env python3
"""
Draw Things + potrace 기반 SVG 아이콘 자동 생성 스크립트
1. Draw Things API(127.0.0.1:7860)로 선명한 흑백 라인아트/아이콘 비트맵 생성
2. 비트맵을 BMP로 변환 후 potrace를 거쳐 무한 확대 가능한 순수 벡터 SVG로 변환
3. assets/icons/<name>.svg 로 저장
"""

import sys
import os
import json
import urllib.request
import base64
import subprocess
import io
from PIL import Image

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ICONS_DIR = os.path.join(PROJECT_ROOT, "assets", "icons")

def generate_svg_icon(name: str, concept: str, seed: int = 42):
    # 초깔끔한 흑백 벡터 아이콘 유도 프롬프트
    prompt = (
        f"minimalist clean solid black vector icon of {concept}, "
        f"flat graphic design, solid black silhouette and clean outlines on pure flat white background, "
        f"app ui icon, simple glyph symbol, high contrast, smooth curves, "
        f"no text, no watermark, no gray, no shading, no gradient, 2d flat"
    )

    negative_prompt = (
        "color, colors, colored, gradient, realistic, 3d, photo, shading, shadow, grayscale, "
        "blurry, noise, messy, text, label"
    )

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 8,
        "width": 512,
        "height": 512,
        "seed": seed
    }

    print(f"[{name}] Draw Things API로 아이콘 생성 요청 중...", flush=True)
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        images = data.get("images", [])
        if not images:
            raise RuntimeError("Draw Things로부터 이미지를 받지 못했습니다.")
        raw_bytes = base64.b64decode(images[0])

    # 1. 흑백 명암비 극대화 전처리 (Thresholding)
    img = Image.open(io.BytesIO(raw_bytes)).convert("L")
    # 흰색 배경(200 이상)은 완전 흰색, 그 외는 검은색
    bw = img.point(lambda p: 255 if p > 180 else 0).convert("1")

    # 2. potrace 입력을 위한 BMP 임시 버퍼 생성
    bmp_buffer = io.BytesIO()
    bw.save(bmp_buffer, format="BMP")
    bmp_bytes = bmp_buffer.getvalue()

    os.makedirs(ICONS_DIR, exist_ok=True)
    svg_path = os.path.join(ICONS_DIR, f"{name}.svg")
    png_path = os.path.join(ICONS_DIR, f"{name}.png")

    # 원본 PNG도 함께 보존
    img.save(png_path)

    # 3. potrace 실행하여 고품질 SVG 벡터 생성
    potrace_cmd = ["/opt/homebrew/bin/potrace", "-s", "--flat", "-o", svg_path]
    proc = subprocess.run(potrace_cmd, input=bmp_bytes, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"potrace 변환 실패: {proc.stderr.decode()}")

    print(f"[{name}] SVG 아이콘 생성 완료: {svg_path}")
    return svg_path

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "vacation_ai"
    concept = sys.argv[2] if len(sys.argv) > 2 else "beach umbrella sunbed cocktail vacation trip holiday icon"
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    generate_svg_icon(name, concept, seed)
