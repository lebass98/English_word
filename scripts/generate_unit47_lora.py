#!/usr/bin/env python3
"""
ComfyUI SDXL + ColoringBook LoRA 자동 생성 스크립트: 중학 2학년 47유닛 (20단어)
- ComfyUI API(http://127.0.0.1:8188)를 통해 순차적으로 이미지를 생성합니다.
- 생성 완료 시 assets/words/<단어>.png 로 자동 복사합니다.
"""

import argparse
import json
import os
import shutil
import time
import urllib.parse
import urllib.request

COMFY_URL = "http://127.0.0.1:8188"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_WORDS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
COMFY_OUTPUT_DIR = "/Users/ijaegwang/ComfyUI-Installs/ComfyUI/ComfyUI/output"

UNIT_47_WORDS = [
    {
        "id": "m2-921",
        "word": "excited",
        "meaning": "흥분한",
        "scene": "a cute adorable happy chibi cartoon boy jumping high in the air with arms wide open, huge excited smile with sparkling anime eyes, stars floating around him",
    },
    {
        "id": "m2-922",
        "word": "alive",
        "meaning": "살아있는",
        "scene": "a cute tiny chibi sprout character with big round shining eyes stretching its little leafy arms happily towards a cheerful smiling sun, vibrant with life",
    },
    {
        "id": "m2-923",
        "word": "brown",
        "meaning": "갈색의, 갈색",
        "scene": "a cute fluffy chibi cartoon teddy bear sitting down happily hugging a big honey pot with sweet cheerful expression",
    },
    {
        "id": "m2-924",
        "word": "different",
        "meaning": "다른",
        "scene": "three identical cute little round ducklings standing in a row, but one cheerful middle duckling is wearing a funny detective hat and glasses looking proud",
    },
    {
        "id": "m2-925",
        "word": "difficult",
        "meaning": "어려운",
        "scene": "a cute chibi cartoon boy scratching his head in confusion at a giant complex jigsaw puzzle piece taller than him, funny tiny question marks floating",
    },
    {
        "id": "m2-926",
        "word": "interesting",
        "meaning": "재미있는",
        "scene": "a curious cute chibi cartoon girl with big fascinated eyes reading a magical pop-up storybook with tiny cute flying dragons popping out of the pages",
    },
    {
        "id": "m2-927",
        "word": "unlike",
        "meaning": "같지 않은",
        "scene": "a cute chibi cat and a cute puppy sitting side by side, the cat looking cool and composed while the puppy is wagging its tail with hilarious energetic excitement",
    },
    {
        "id": "m2-928",
        "word": "least",
        "meaning": "가장 적은, 최소한의",
        "scene": "a funny cute chibi cartoon squirrel looking comically sad holding just one tiny acorn seed, standing next to a mountain of acorns",
    },
    {
        "id": "m2-929",
        "word": "afraid",
        "meaning": "무서워하여",
        "scene": "a cute chibi cartoon boy hiding under a cozy blanket shivering comically with funny big startled wide eyes seeing a harmless tiny moth shadow",
    },
    {
        "id": "m2-930",
        "word": "cool",
        "meaning": "서늘한, 냉정한",
        "scene": "an ultra stylish cute chibi cartoon penguin wearing black sunglasses sitting in front of a blowing electric fan, looking delightfully relaxed and cool",
    },
    {
        "id": "m2-931",
        "word": "pretty",
        "meaning": "예쁜, 상당히",
        "scene": "a charming cute chibi cartoon girl wearing a lovely floral flower crown looking into a hand mirror with sweet blushing cheeks and twinkling smile",
    },
    {
        "id": "m2-932",
        "word": "kind",
        "meaning": "친절한, 종류",
        "scene": "a warm-hearted cute chibi cartoon boy kindly offering his umbrella to a shivering tiny soaked kitten in the rain with gentle sweet smile",
    },
    {
        "id": "m2-933",
        "word": "sick",
        "meaning": "병든, 싫증난",
        "scene": "a cute chibi cartoon boy lying in bed with a cooling ice pack on his head and a thermometer in his mouth, sleepy gentle eyes, looking pitifully cute",
    },
    {
        "id": "m2-934",
        "word": "useless",
        "meaning": "쓸모없는",
        "scene": "a comically perplexed cute chibi cartoon boy holding an umbrella that is full of big holes while rain pours right through it onto his head, funny sweat drops",
    },
    {
        "id": "m2-935",
        "word": "busy",
        "meaning": "바쁜",
        "scene": "a cute chibi cartoon kid with multiple funny motion blur arms holding a ringing phone, typing on a laptop, and checking a watch all at once with dizzy eyes",
    },
    {
        "id": "m2-936",
        "word": "early",
        "meaning": "일찍이",
        "scene": "a bright energetic cute chibi cartoon rooster crowing on a fence at dawn, wearing running shoes and stretching early in the morning",
    },
    {
        "id": "m2-937",
        "word": "past",
        "meaning": "과거의, ~을 지나서",
        "scene": "a cute chibi cartoon boy happily stepping through an open magical doorway leading out of an antique grandfather clock towards the future",
    },
    {
        "id": "m2-938",
        "word": "dark",
        "meaning": "어두운",
        "scene": "a brave cute chibi cartoon explorer holding a glowing bright lantern in a mysterious night cave, illuminating a funny cute little bat hanging upside down",
    },
    {
        "id": "m2-939",
        "word": "cloudy",
        "meaning": "구름이 낀",
        "scene": "a funny cute chibi cloud character floating above with chubby cheeks, blowing puffy soft white clouds across the sky",
    },
    {
        "id": "m2-940",
        "word": "short",
        "meaning": "짧은, 키가 작은",
        "scene": "a super cute tiny chibi cartoon hamster standing next to a giant tall sunflower, looking way up high on tiptoes with funny awe-inspired wide eyes",
    },
]


def build_workflow(item, seed):
    positive_prompt = (
        f"Coloring Book, ColoringBookAF, minimalist black and white coloring book page, "
        f"{item['scene']}, "
        f"thick bold clean black outlines, smooth line art, simple doodle drawing, "
        f"pure solid clean white background, completely empty background, sharp clean vector lines, "
        f"strictly no color, no colors, no shading, no gradient, no gray fill, "
        f"strictly no text, no words, no letters, no watermark."
    )

    negative_prompt = (
        "color, colors, colored, red, blue, yellow, green, grayscale shading, shadow, shadows, realistic, photo, 3d, render, "
        "messy lines, sketchy, dirty, blurry, low quality, bad anatomy, text, words, watermark, logo, frame, border"
    )

    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "DreamShaperXL_Lightning.safetensors",
            },
        },
        "2": {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": "coloringbook_sdxl.safetensors",
                "strength_model": 1.0,
                "strength_clip": 1.0,
                "model": ["1", 0],
                "clip": ["1", 1],
            },
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive_prompt,
                "clip": ["2", 1],
            },
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_prompt,
                "clip": ["2", 1],
            },
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1,
            },
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": seed,
                "steps": 25,
                "cfg": 6.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
            },
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["6", 0],
                "vae": ["1", 2],
            },
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"unit47_{item['word']}",
                "images": ["7", 0],
            },
        },
    }


def queue_prompt(workflow):
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8")).get("prompt_id")


def wait_for_prompt(prompt_id, timeout_sec=900):
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            req = urllib.request.Request(f"{COMFY_URL}/history/{prompt_id}")
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if prompt_id in data:
                    outputs = data[prompt_id].get("outputs", {})
                    for node_out in outputs.values():
                        images = node_out.get("images", [])
                        if images:
                            return images[0]
        except Exception:
            pass
        time.sleep(3)
    return None


def make_transparent(src_path, dest_path):
    """
    모서리와 연결된 외부 흰색 배경만 투명화하고 캐릭터 내부 및 굵은 선은 깔끔하게 유지합니다.
    """
    try:
        from PIL import Image
        import numpy as np
        from scipy import ndimage

        img = Image.open(src_path).convert('RGB')
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
        out = Image.fromarray(rgba, 'RGBA')
        out.save(dest_path)
        return True
    except Exception as e:
        print(f" 투명화 변환 오류 ({e}), 일반 복사 수행")
        shutil.copy(src_path, dest_path)
        return False


def main():
    parser = argparse.ArgumentParser(description="SDXL + ColoringBook LoRA 중2 47유닛 자동 생성")
    parser.add_argument("--force", action="store_true", help="기존 파일이 있어도 덮어쓰기")
    parser.add_argument("--words", nargs="*", help="특정 단어 지정 (예: --words excited alive)")
    args = parser.parse_args()

    os.makedirs(ASSETS_WORDS_DIR, exist_ok=True)

    words_to_process = UNIT_47_WORDS
    if args.words:
        target_words = set(args.words)
        words_to_process = [item for item in UNIT_47_WORDS if item["word"] in target_words]

    total = len(words_to_process)
    print(f"==========================================================")
    print(f" SDXL + ColoringBook LoRA (25스텝, 투명배경) 47유닛 (총 {total}단어)")
    print(f"==========================================================")

    for i, item in enumerate(words_to_process, 1):
        word = item["word"]
        target_path = os.path.join(ASSETS_WORDS_DIR, f"{word}.png")

        # 1번째 excited는 이미 생성되어 투명화 적용 완료
        if word == "excited":
            print(f"[{i}/{total}] {word} ({item['meaning']}) - 투명 배경 적용 완료! -> {target_path}")
            continue

        if not args.force and os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
            print(f"[{i}/{total}] {word} ({item['id']}) - 이미 존재함 (건너뜀)")
            continue

        print(f"[{i}/{total}] {word} ({item['meaning']}) 생성 요청 중...", end="", flush=True)
        seed = 2026 + i * 47
        workflow = build_workflow(item, seed)

        prompt_id = queue_prompt(workflow)
        if not prompt_id:
            print(" [요청 실패]")
            continue

        print(f" [큐 등록: {prompt_id[:8]}] -> 생성 중...", end="", flush=True)
        start_t = time.time()
        img_info = wait_for_prompt(prompt_id)

        if img_info:
            elapsed = time.time() - start_t
            filename = img_info["filename"]
            subfolder = img_info.get("subfolder", "")
            src_path = os.path.join(COMFY_OUTPUT_DIR, subfolder, filename)

            if os.path.exists(src_path):
                make_transparent(src_path, target_path)
                print(f" 완료 (투명화 저장, {elapsed:.1f}초) -> {target_path}")
            else:
                print(f" 파일 찾기 실패 ({src_path})")
        else:
            print(" 시간 초과")


if __name__ == "__main__":
    main()
