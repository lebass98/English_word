#!/usr/bin/env python3
"""
Draw Things 기반 단어 이미지 자동 생성 스크립트: dull (중2 유닛 45 1번)
- 127.0.0.1:7860 Draw Things WebUI 호환 API (/sdapi/v1/txt2img) 연동
- assets/words/dull.png 저장 및 wordImages.ts 자동 등록
"""

import os
import sys
import json
import urllib.request
import base64
from PIL import Image

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
WORD_IMAGES_TS = os.path.join(PROJECT_ROOT, "src", "constants", "wordImages.ts")

def render_clean_framed_image(src_img: Image.Image, canvas_size=1254) -> Image.Image:
    gray = src_img.convert("L")
    
    def clean_ink(v):
        if v <= 100: return 0
        if v >= 230: return 255
        return int(((v - 100) / (230 - 100)) * 255)
    
    cleaned = gray.point(clean_ink)
    upscaled = cleaned.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)
    final_clean = upscaled.point(clean_ink)
    return final_clean.convert("RGB")

def update_word_images_ts(word: str, word_id: str = None):
    if not os.path.exists(WORD_IMAGES_TS):
        return
    with open(WORD_IMAGES_TS, "r", encoding="utf-8") as f:
        content = f.read()

    new_entries = []
    if f'"{word}": require(' not in content and f'{word}: require(' not in content:
        new_entries.append(f'  "{word}": require("../../assets/words/{word}.png"),')
    if word_id and f'"{word_id}": require(' not in content:
        new_entries.append(f'  "{word_id}": require("../../assets/words/{word}.png"),')

    if not new_entries:
        return

    target = "};\n"
    if target in content:
        idx = content.rfind(target)
        updated = content[:idx] + "\n".join(new_entries) + "\n" + content[idx:]
        with open(WORD_IMAGES_TS, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"[{word}] wordImages.ts 매핑 추가 완료: {new_entries}")

def generate_dull():
    word = "dull"
    word_id = "m2-881"
    
    prompt = (
        "minimalist black and white line art vector doodle, "
        "slender stickman looking comically confused and dull, holding a completely blunt rounded pencil with thick tip, "
        "simple cute doodle stickman, 0.1mm technical pen outline, ultra-thin delicate hairline stroke, "
        "pure white flat background, clean sharp black outlines, "
        "no shading, no grayscale, no color, no gradients, no hatching, 2d flat vector doodle"
    )
    negative_prompt = (
        "color, colors, shading, gray, grayscale, shadow, 3d, realistic, photorealistic, "
        "thick heavy bold lines, text, words, watermark"
    )

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 8,
        "width": 512,
        "height": 512,
        "seed": 42
    }

    print(f"[{word}] Draw Things API 요청 중 (http://127.0.0.1:7860)...", flush=True)
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        images = data.get("images", [])
        if not images:
            raise RuntimeError("No image returned from Draw Things API")
        raw_bytes = base64.b64decode(images[0])

    import io
    raw_img = Image.open(io.BytesIO(raw_bytes))
    final_img = render_clean_framed_image(raw_img, canvas_size=1254)

    os.makedirs(ASSETS_DIR, exist_ok=True)
    out_path = os.path.join(ASSETS_DIR, f"{word}.png")
    final_img.save(out_path, quality=98)
    print(f"[{word}] 저장 완료: {out_path}")

    update_word_images_ts(word, word_id)
    return out_path

if __name__ == "__main__":
    generate_dull()
