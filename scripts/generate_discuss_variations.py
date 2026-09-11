#!/usr/bin/env python3
"""
Draw Things 기반 'discuss' 단어 고품질 세밀 라인아트 생성 스크립트
- 첨부된 레퍼런스 스타일 반영:
  * 0.1mm 초극세 테크니컬 펜선 (ultra-thin delicate hairline, crisp fine ink outline)
  * 풍부한 씬 구성 (칠판/차트 앞 발표자, 메모하고 경청하는 동료들, 회의실 공간 배경)
  * 맑고 깨끗한 순백색 배경, 음영/색상 없음, 귀여운 두들 스틱맨 캐릭터
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
ARTIFACT_DIR = "/Users/ijaegwang/.gemini/antigravity-ide/brain/24504971-7802-4213-a075-eafb99ed46ff"

def clean_and_upscale_fine_lines(src_img: Image.Image, canvas_size=1254) -> Image.Image:
    """얇고 섬세한 펜선을 뭉개짐 없이 보존하면서 순백색 배경을 정제하는 고화질 업스케일"""
    gray = src_img.convert("L")
    
    # 얇은 선의 안티에일리어싱을 해치지 않고 배경(220 이상)만 깨끗한 흰색으로 정제
    def smooth_contrast(v):
        if v >= 235:
            return 255
        elif v <= 40:
            return 0
        else:
            # 부드러운 감마 보정으로 선을 가늘고 맑게 유지
            norm = (v - 40) / (235 - 40)
            return int((norm ** 1.1) * 255)
            
    refined = gray.point(smooth_contrast)
    upscaled = refined.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)
    return upscaled.convert("RGB")

def generate_discuss_candidate(seed=555, suffix=""):
    prompt = (
        "storybook minimalist black and white line art vector doodle, "
        "extremely slender stickman stick figure people with simple thin single-stroke line limbs and thin line stick torso, "
        "small perfect round circle bald heads, tiny cute dot eyes and little smile, "
        "complete vibrant office meeting room scene, "
        "three slender stickman colleagues enthusiastically discussing, "
        "one slender stick figure pointing with a slender stick arm at an idea flow chart on a clean white easel presentation board, "
        "second slender stick figure sitting attentively on a stool listening with arms crossed, "
        "third slender stick figure standing beside holding a tiny coffee mug, "
        "detailed background with floor line, bookshelf with books, hanging wall clock, small desk lamp, "
        "hairline stroke, ultra-fine 0.1mm technical pen line art, delicate crisp black contours on pure white background, "
        "completely empty pure white background, strictly hollow white objects with black outlines only, strictly no black solid fills, strictly no color, no gray, no shading, 2d flat vector doodle"
    )

    negative_prompt = (
        "solid black fill, black background, black board, filled shape, dark shading, "
        "chubby, fat body, thick torso, bulbous body, puffy, outline body, wide limbs, "
        "thick heavy bold strokes, chunky outlines, marker pen, "
        "color, colors, colored, shading, gray, grayscale, shadow, 3d, realistic, photorealistic, "
        "crosshatch, texture, pattern, watermark, text, signature, blurry, dirty background"
    )



    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 8,
        "width": 512,
        "height": 512,
        "seed": seed
    }

    print(f"Draw Things 요청 중 (seed={seed})...", flush=True)
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
            raise RuntimeError("No image returned from Draw Things")
        raw_bytes = base64.b64decode(images[0])

    raw_img = Image.open(io.BytesIO(raw_bytes))
    final_img = clean_and_upscale_fine_lines(raw_img, canvas_size=1254)

    # 1. 아티팩트 디렉토리에 저장
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    artifact_path = os.path.join(ARTIFACT_DIR, f"discuss_candidate_{seed}{suffix}.png")
    final_img.save(artifact_path, quality=98)
    print(f"아티팩트 저장 완료: {artifact_path} ({time.time() - t0:.1f}초)")

    # 2. assets/words/discuss.png에 적용
    out_path = os.path.join(ASSETS_DIR, "discuss.png")
    final_img.save(out_path, quality=98)
    print(f"assets/words/discuss.png 적용 완료!")
    return artifact_path, out_path

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 702
    generate_discuss_candidate(seed=seed)
