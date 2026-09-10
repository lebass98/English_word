#!/usr/bin/env python3
"""
ComfyUI SDXL + ColoringBook LoRA 자동 생성 스크립트: 중학 2학년 47유닛 (20단어)
- 스타일: 초미니멀 귀여운 둥근 머리 두들 스틱맨 (가는 선 한 줄 팔다리, 위트 있는 행동 연출)
- 순수 흑백 라인아트 (Monochrome pure line art)
- 스마트 배경 누끼 투명화 (Transparent PNG)
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
        "scene": "one cute stick figure person jumping high in the air with arms spread wide, huge cheerful open mouth smile with dot eyes, celebratory curved action burst lines around him",
    },
    {
        "id": "m2-922",
        "word": "alive",
        "meaning": "살아있는",
        "scene": "a cute happy stick figure person joyfully watering a tiny smiling plant sprout with a watering can, tiny cute hearts and life sparkles floating",
    },
    {
        "id": "m2-923",
        "word": "brown",
        "meaning": "갈색의, 갈색",
        "scene": "a cute stick figure person happily holding up a giant chocolate donut with a bite taken out, smiling playfully",
    },
    {
        "id": "m2-924",
        "word": "different",
        "meaning": "다른",
        "scene": "three stick figure people standing in a row, two are standing straight and plain, while the middle stick figure is wearing funny oversized sunglasses and striking a goofy funny dance pose",
    },
    {
        "id": "m2-925",
        "word": "difficult",
        "meaning": "어려운",
        "scene": "a confused stick figure person scratching head, looking comically puzzled at a giant single jigsaw puzzle piece taller than himself with a tiny question mark over his head",
    },
    {
        "id": "m2-926",
        "word": "interesting",
        "meaning": "재미있는",
        "scene": "a curious stick figure person holding a giant magnifying glass inspecting a tiny cute snail, sparkling wide fascinated eyes",
    },
    {
        "id": "m2-927",
        "word": "unlike",
        "meaning": "같지 않은",
        "scene": "two stick figures side by side, one is calm and sleeping peacefully, while the other is bouncing wildly with energetic motion zigzag lines",
    },
    {
        "id": "m2-928",
        "word": "least",
        "meaning": "가장 적은, 최소한의",
        "scene": "a funny sad stick figure person holding only one tiny coin in an open empty wallet, standing beside a giant tall stack of coins",
    },
    {
        "id": "m2-929",
        "word": "afraid",
        "meaning": "무서워하여",
        "scene": "a frightened stick figure person with hands raised in shock and trembling knees, startled by a dark cave opening or tiny shadow, panic action lines",
    },
    {
        "id": "m2-930",
        "word": "cool",
        "meaning": "서늘한, 냉정한",
        "scene": "a very chill stick figure person wearing black shades relaxing comfortably right in front of a blowing electric fan, wind breeze lines",
    },
    {
        "id": "m2-931",
        "word": "pretty",
        "meaning": "예쁜, 상당히",
        "scene": "a charming sweet stick figure character wearing a simple flower in hair, admiring reflection in a small handheld mirror with cute blushing cheek dots",
    },
    {
        "id": "m2-932",
        "word": "kind",
        "meaning": "친절한, 종류",
        "scene": "a gentle kind stick figure person generously holding an umbrella over a tiny shivering soaked bird in the rain with a sweet warm smile",
    },
    {
        "id": "m2-933",
        "word": "sick",
        "meaning": "병든, 싫증난",
        "scene": "a sick stick figure person tucked under a blanket with a thermometer in mouth and an ice pack on head, droopy sad eyes",
    },
    {
        "id": "m2-934",
        "word": "useless",
        "meaning": "쓸모없는",
        "scene": "a comically disappointed stick figure person holding an umbrella full of big holes while rain pours right through onto head, funny sweat drops",
    },
    {
        "id": "m2-935",
        "word": "busy",
        "meaning": "바쁜",
        "scene": "a frantic busy stick figure person with multiple funny comic motion blur arms holding a ringing telephone, typing on a laptop, and checking a watch",
    },
    {
        "id": "m2-936",
        "word": "early",
        "meaning": "일찍이",
        "scene": "a bright energetic stick figure person in running sneakers stretching early in the morning with a cute rising sun yawning in the background",
    },
    {
        "id": "m2-937",
        "word": "past",
        "meaning": "과거의, ~을 지나서",
        "scene": "a stick figure person walking forward cheerfully through a door frame with arrow signs pointing forward, waving goodbye to an old calendar behind",
    },
    {
        "id": "m2-938",
        "word": "dark",
        "meaning": "어두운",
        "scene": "a brave stick figure person holding a glowing flashlight beam into an inky dark opening, illuminating a tiny friendly smiling ghost or bat",
    },
    {
        "id": "m2-939",
        "word": "cloudy",
        "meaning": "구름이 낀",
        "scene": "a cute stick figure person looking up at a giant fluffy cartoon cloud that is gently covering the sun, simple sky doodle",
    },
    {
        "id": "m2-940",
        "word": "short",
        "meaning": "짧은, 키가 작은",
        "scene": "a very short tiny cute stick figure kid standing on tiptoes next to an absurdly tall sunflower or ladder, looking way up high with round eyes",
    },
]


def build_workflow(item, seed):
    positive_prompt = (
        "(ultra minimalist cute doodle line art:1.4), (simple cute round head stick figure character:1.4), "
        f"{item['scene']}, "
        "cute round ball head with tiny simple hair flick, cute two dot eyes and simple curved smile, "
        "simple tubular torso, single thin curved stick line arms, single thin stick legs with tiny oval feet, "
        "(clean thick smooth uniform marker outlines, hand drawn doodle illustration:1.3), "
        "pure solid white background, completely empty background, "
        "(strictly black and white line art only, strictly no color, no colors, no shading, no gray fill, no texture:1.5), "
        "isolated subject, strictly no text, no words, no watermark"
    )

    negative_prompt = (
        "color, colors, colored, red, blue, yellow, green, shading, grayscale, shadow, 3d, realistic, "
        "complex clothes, detailed anatomy, realistic fingers, realistic muscles, hairy, messy sketch, dirty lines, text, words, watermark"
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
                "strength_model": 0.85,
                "strength_clip": 0.85,
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
                "cfg": 7.0,
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
                "filename_prefix": f"unit47_doodle_{item['word']}",
                "images": ["7", 0],
            },
        },
    }


def make_transparent(src_path, dest_path):
    """
    모서리와 연결된 외부 흰색 배경을 투명(0)으로 날리고
    검은색 굵은 마커 라인과 캐릭터 본체는 선명하게 보존
    """
    try:
        from PIL import Image
        import numpy as np
        from scipy import ndimage

        img = Image.open(src_path).convert("RGB")
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
        out.save(dest_path)
        return True
    except Exception as e:
        print(f" 투명화 변환 오류 ({e}), 일반 복사 수행")
        shutil.copy(src_path, dest_path)
        return False


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


def main():
    parser = argparse.ArgumentParser(description="SDXL + ColoringBook LoRA 두들 스틱맨 47유닛 자동 생성")
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
    print(f" 두들 스틱맨 (25스텝, 흑백라인, 투명배경) 중2 47유닛 생성 (총 {total}단어)")
    print(f"==========================================================")

    for i, item in enumerate(words_to_process, 1):
        word = item["word"]
        target_path = os.path.join(ASSETS_WORDS_DIR, f"{word}.png")

        if not args.force and os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
            # 이전에 다른 스타일로 임시 저장된 파일이 있으면 덮어쓰도록 force 옵션 권장
            pass

        print(f"[{i}/{total}] {word} ({item['meaning']}) 생성 요청 중...", end="", flush=True)
        seed = 7777 + i * 53
        workflow = build_workflow(item, seed)

        prompt_id = queue_prompt(workflow)
        if not prompt_id:
            print(" [요청 실패]")
            continue

        print(f" [큐: {prompt_id[:8]}] -> 생성 중...", end="", flush=True)
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
