#!/usr/bin/env python3
"""
Draw Things 기반 중학교 2학년 Unit 15 단어 이미지 일괄 생성 스크립트
- 대상: Unit 15 (m2-281 ~ m2-300) 중 미등록 단어 18개
- Draw Things API (http://127.0.0.1:7860/sdapi/v1/txt2img) 연동
- 생성 규격: 1254x1254 순수 칠흑색(#000000) 잉크 + 순백색 배경
- assets/words/<단어>.png 저장 및 src/constants/wordImages.ts 자동 등록
"""

import os
import sys
import json
import time
import base64
import urllib.request
import io
from PIL import Image

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
WORD_IMAGES_TS = os.path.join(PROJECT_ROOT, "src", "constants", "wordImages.ts")
PROMPTS_FILE = os.path.join(SCRIPT_DIR, "m2_units11_15_prompts.json")

def render_clean_framed_image(src_img: Image.Image, canvas_size=1254) -> Image.Image:
    """순수 칠흑색 잉크 라인 및 순백색 배경으로 정제 후 1254x1254 고품질 업스케일"""
    gray = src_img.convert("L")
    
    def clean_ink(v):
        if v <= 100: return 0
        if v >= 230: return 255
        return int(((v - 100) / (230 - 100)) * 255)
    
    cleaned = gray.point(clean_ink)
    upscaled = cleaned.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)
    final_clean = upscaled.point(clean_ink)
    return final_clean.convert("RGB")

def update_word_images_ts(entries: list):
    """wordImages.ts 파일에 여러 단어 및 ID 매핑을 일괄 등록"""
    if not os.path.exists(WORD_IMAGES_TS):
        return
    with open(WORD_IMAGES_TS, "r", encoding="utf-8") as f:
        content = f.read()

    new_lines = []
    for word, word_id in entries:
        if f'"{word}": require(' not in content and f'{word}: require(' not in content:
            new_lines.append(f'  "{word}": require("../../assets/words/{word}.png"),')
        if word_id and f'"{word_id}": require(' not in content:
            new_lines.append(f'  "{word_id}": require("../../assets/words/{word}.png"),')

    if not new_lines:
        return

    target = "};\n"
    if target in content:
        idx = content.rfind(target)
        updated = content[:idx] + "\n  // 중학교 2학년 15Unit 매핑\n" + "\n".join(new_lines) + "\n" + content[idx:]
        with open(WORD_IMAGES_TS, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"wordImages.ts에 {len(new_lines)}개 항목 매핑 등록 완료!")

def generate_unit15_words():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        all_prompts = json.load(f)

    unit15_items = [x for x in all_prompts if x.get("unit") == 15]
    print(f"총 {len(unit15_items)}개 Unit 15 단어 로드됨")

    os.makedirs(ASSETS_DIR, exist_ok=True)
    success_entries = []

    for idx, item in enumerate(unit15_items, 1):
        word = item["word"]
        word_id = item["id"]
        meaning = item.get("meaning", "")
        scene = item.get("scene", "")

        out_path = os.path.join(ASSETS_DIR, f"{word}.png")
        if os.path.exists(out_path):
            print(f"[{idx}/{len(unit15_items)}] '{word}' ({word_id}) 이미 파일 존재함 -> 건너뜀")
            success_entries.append((word, word_id))
            continue

        print(f"\n==================================================")
        print(f"[{idx}/{len(unit15_items)}] '{word}' ({word_id}: {meaning}) Draw Things 생성 중...")
        print(f"Scene: {scene}")

        prompt = (
            f"minimalist black and white line art vector doodle, complete interior room scene, "
            f"very slender slim doodle stickman with lean thin body proportions and long thin limbs, "
            f"small simple round bald head, cute happy face, standing thoughtfully on horizontal floor line, "
            f"{scene}, "
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
            "seed": 300 + idx * 7
        }

        # 요청 재시도 로직
        max_retries = 3
        done = False
        for attempt in range(1, max_retries + 1):
            try:
                t0 = time.time()
                req = urllib.request.Request(
                    API_URL,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=180) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    images = data.get("images", [])
                    if not images:
                        raise RuntimeError("No image returned")
                    raw_bytes = base64.b64decode(images[0])

                raw_img = Image.open(io.BytesIO(raw_bytes))
                final_img = render_clean_framed_image(raw_img, canvas_size=1254)
                final_img.save(out_path, quality=98)
                elapsed = time.time() - t0
                print(f"[{word}] 생성 및 저장 완료 ({elapsed:.1f}초) -> {out_path}")
                success_entries.append((word, word_id))
                done = True
                break
            except Exception as e:
                print(f"[{word}] 시도 {attempt}/{max_retries} 실패: {e}")
                time.sleep(3)

        if not done:
            print(f"[경고] '{word}' 이미지 생성 실패!")

    # 일괄 wordImages.ts 매핑 갱신
    if success_entries:
        update_word_images_ts(success_entries)

    print("\n==================================================")
    print(f"Unit 15 완료: 총 {len(success_entries)}/{len(unit15_items)} 개 단어 준비됨")

if __name__ == "__main__":
    generate_unit15_words()
