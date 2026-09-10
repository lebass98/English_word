#!/usr/bin/env python3
"""
Draw Things 기반 단어 이미지 자동 생성 스크립트 (슈퍼샘플링 쨍한 라인아트 버전)
- 미니멀 흑백 라인아트 (날씬한 두들 스틱맨 스타일)
- pause.png 기준 피사체 점유율(약 65% 높이, 하단 여백 7%) 구도 및 리프레이밍
- 칼로 자른 듯 쨍하고 선명한 순수 칠흑색(#000000) 잉크 라인 (8px / 6px)
- assets/words/<단어>.png 저장 및 wordImages.ts 연동
"""

import sys
import os
import json
import urllib.request
import base64
import math
from PIL import Image, ImageFilter

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
WORD_IMAGES_TS = os.path.join(PROJECT_ROOT, "src", "constants", "wordImages.ts")

def render_clean_framed_image(src_img: Image.Image, canvas_size=1254) -> Image.Image:
    """
    씬 전체 일러스트(방, 바닥선, 가구, 캐릭터)의 구도와 울트라씬 선을 100% 보존하면서
    1254x1254 규격으로 깔끔하게 렌더링합니다.
    """
    gray = src_img.convert("L")
    
    # 순수 칠흑색(#000000) 잉크 + 순백색(#ffffff) 배경 정제
    def clean_ink(v):
        if v <= 100: return 0
        if v >= 230: return 255
        return int(((v - 100) / (230 - 100)) * 255)
    
    cleaned = gray.point(clean_ink)
    
    # 씬 전체 비율을 그대로 1254x1254 고품질 업스케일
    upscaled = cleaned.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)
    final_clean = upscaled.point(clean_ink)
    
    return final_clean.convert("RGB")

def generate_word_image(word: str, action_desc: str, seed: int = 303, stroke_width: int = 8) -> str:
    # 날씬한 스틱맨 + 방/공간 전체 씬 채움 + 울트라씬 0.1mm 기술펜 극세선
    prompt = (
        f"minimalist black and white line art vector doodle, complete interior room scene, "
        f"very slender slim doodle stickman with lean thin body proportions and long thin limbs, "
        f"small simple round bald head, cute happy face, standing thoughtfully on horizontal floor line, "
        f"{action_desc}, "
        f"0.1mm technical pen outline, ultra-thin delicate hairline stroke, light fine vector line art, single crisp thin ink line, "
        f"pure white flat background, clean sharp black outlines, "
        f"no shading, no grayscale, no color, no gradients, no hatching, 2d flat vector doodle"
    )

    negative_prompt = (
        "chubby, fat, bulky, wide body, thick torso, thick limbs, stout, puffy, round belly, "
        "thick heavy bold lines, chunky outlines, "
        "color, colors, shading, gray, grayscale, shadow, 3d, realistic, photorealistic, "
        "hatched, crosshatch, fill, dark background, gradient, texture, blurry, messy, watermark, text"
    )

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 8,
        "width": 512,
        "height": 512,
        "seed": seed
    }

    print(f"[{word}] Draw Things 요청 중 (seed={seed})...", flush=True)
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        images = data.get("images", [])
        if not images:
            raise RuntimeError("No image returned from Draw Things API")
        raw_bytes = base64.b64decode(images[0])

    import io
    raw_img = Image.open(io.BytesIO(raw_bytes))
    final_img = render_clean_framed_image(raw_img, canvas_size=1254)

    out_path = os.path.join(ASSETS_DIR, f"{word}.png")
    os.makedirs(ASSETS_DIR, exist_ok=True)
    final_img.save(out_path, quality=98)
    print(f"[{word}] 저장 완료: {out_path}")
    return out_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 generate_word_drawthings.py <word> <action_desc> [seed] [stroke_width]")
        print("Example: python3 generate_word_drawthings.py refrigerator 'standing beside an open refrigerator reaching inside' 303 8")
        sys.exit(1)
    word = sys.argv[1]
    desc = sys.argv[2]
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 303
    stroke = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    generate_word_image(word, desc, seed, stroke)
