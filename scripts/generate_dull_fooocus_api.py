#!/usr/bin/env python3
"""
Fooocus WebUI 자동화 생성 스크립트: 중2 유닛 45 1번 dull
- 127.0.0.1:7865 Gradio API와 직접 소통하여 웹 UI 상에서 이미지를 생성합니다.
"""
import urllib.request
import json
import time
import os
import shutil

FOOOCUS_URL = "http://127.0.0.1:7865"
PROJECT_ROOT = "/Users/ijaegwang/wordncode/App/English_word"
ASSETS_DIR = "/Users/ijaegwang/wordncode/App/English_word/assets/words"
ARTIFACT_DIR = "/Users/ijaegwang/.gemini/antigravity-ide/brain/0188bbd9-5001-41c3-b74f-b1dc07110b40"

def generate_word():
    # 1. config 로드
    req = urllib.request.urlopen(f"{FOOOCUS_URL}/config")
    cfg = json.loads(req.read().decode())
    dep67 = cfg["dependencies"][67]
    input_ids = dep67["inputs"]
    comp_map = {c["id"]: c for c in cfg["components"]}

    # 기본 파라미터 리스트 구성
    data = []
    for cid in input_ids:
        c = comp_map[cid]
        val = c.get("props", {}).get("value")
        data.append(val)

    prompt = (
        "(Coloring Book, ColoringBookAF:1.2), (minimalist black and white cartoon line art:1.4), (cute round bald doodle stick figure:1.4), "
        "one cute round bald head stick figure character in middle looking comically confused and dull, "
        "holding a completely blunt rounded wooden pencil with thick blunt tip, "
        "another round-headed cartoon stick figure friend next to him scratching his head in disbelief, "
        "(bold clean black outlines:1.3), hand drawn doodle illustration, "
        "pure solid white background, completely empty background, "
        "(strictly black and white line art only, strictly no color, no shading:1.5), strictly no text"
    )
    negative_prompt = (
        "color, colors, colored, red, blue, yellow, green, shading, grayscale, shadow, 3d, realistic, "
        "complex clothes, detailed anatomy, text, words, watermark"
    )

    # 매핑:
    # Index 1: generate_image_grid (False)
    # Index 2: prompt
    # Index 3: negative_prompt
    # Index 4: selected_styles
    # Index 5: performance
    # Index 7: image_number
    # Index 16: enable LoRA 1
    # Index 17: LoRA 1 model
    # Index 18: LoRA 1 weight
    data[2] = prompt
    data[3] = negative_prompt
    data[4] = ["SAI Line Art"]
    data[5] = "Speed"
    data[7] = 1 # image number 1장
    data[16] = True
    data[17] = "coloringbook_sdxl.safetensors"
    data[18] = 0.85

    print("Fooocus Task 준비 중...")
    # 1) get_task 호출 (fn_index 67)
    payload = json.dumps({"fn_index": 67, "data": data}).encode("utf-8")
    req_task = urllib.request.Request(f"{FOOOCUS_URL}/api/predict", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req_task) as resp:
        res_task = json.loads(resp.read().decode())
    current_task = res_task["data"][0]
    print("Task 획득 완료! Fooocus 엔진으로 이미지 생성을 시작합니다...")

    # 2) generate_clicked 호출 (fn_index 68)
    gen_payload = json.dumps({"fn_index": 68, "data": [current_task]}).encode("utf-8")
    req_gen = urllib.request.Request(f"{FOOOCUS_URL}/api/predict", data=gen_payload, headers={"Content-Type": "application/json"})
    
    start_t = time.time()
    with urllib.request.urlopen(req_gen) as resp:
        res_gen = json.loads(resp.read().decode())
    
    elapsed = time.time() - start_t
    print(f"생성 완료! ({elapsed:.1f}초)")

    gallery = res_gen["data"][3]
    if gallery:
        img_item = gallery[0]
        name = img_item.get("name")
        print(f"생성된 이미지 파일: {name}")

        target_path = os.path.join(ASSETS_DIR, "dull.png")
        shutil.copy(name, target_path)
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        raw_artifact = os.path.join(ARTIFACT_DIR, "word_dull_fooocus.png")
        shutil.copy(name, raw_artifact)
        print(f"assets 및 artifact 복사 완료 -> {target_path}")

        # 투명화 처리
        try:
            from PIL import Image
            import numpy as np
            from scipy import ndimage

            img = Image.open(target_path).convert("RGB")
            arr = np.array(img)
            gray = np.mean(arr, axis=2)

            white_mask = gray > 230
            labeled, _ = ndimage.label(white_mask)

            border_labels = set()
            border_labels.update(labeled[0, :])
            border_labels.update(labeled[-1, :])
            border_labels.update(labeled[:, 0])
            border_labels.update(labeled[:, -1])
            border_labels.discard(0)

            outer_bg = np.isin(labeled, list(border_labels))

            alpha = np.full((img.height, img.width), 255, dtype=np.uint8)
            alpha[outer_bg] = 0

            dilated = ndimage.binary_dilation(outer_bg, iterations=2)
            edge_zone = dilated & ~outer_bg

            for y, x in zip(*np.where(edge_zone)):
                v = 255 - gray[y, x]
                alpha[y, x] = int(min(255, v * 1.8))

            rgba = np.dstack((arr, alpha))
            out = Image.fromarray(rgba, "RGBA")
            out.save(target_path)
            cutout_artifact = os.path.join(ARTIFACT_DIR, "word_dull_fooocus_cutout.png")
            out.save(cutout_artifact)
            print("투명화 적용 성공!")
        except Exception as e:
            print(f"투명화 실패: {e}")
    else:
        print("갤러리에서 이미지를 찾을 수 없습니다.")

if __name__ == "__main__":
    generate_word()
