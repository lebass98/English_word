#!/usr/bin/env python3
"""
ComfyUI SDXL-Lightning 자동 생성 스크립트: 중학 2학년 48유닛 (20단어)
- ComfyUI API(http://127.0.0.1:8188)를 통해 순차적으로 이미지를 생성합니다.
- 생성 완료 시 assets/words/<단어>.png 로 자동 복사합니다.
"""

import json
import os
import shutil
import time
import urllib.request
import urllib.parse

COMFY_URL = "http://127.0.0.1:8188"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_WORDS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
COMFY_OUTPUT_DIR = os.path.expanduser("~/ComfyUI-Shared/output")

UNIT_48_WORDS = [
    {
        "id": "m2-941",
        "word": "low",
        "meaning": "낮은, 낮게",
        "scene": "an adorable stick figure carefully bending down low to walk under a low wooden bar, smiling",
    },
    {
        "id": "m2-942",
        "word": "sincerely",
        "meaning": "성실히, 진심으로",
        "scene": "an adorable stick figure holding hands over their heart and bowing politely with a sincere and warm smile",
    },
    {
        "id": "m2-943",
        "word": "fortunately",
        "meaning": "운 좋게, 다행히",
        "scene": "an adorable stick figure smiling happily with relief while holding a small four-leaf clover, raindrops missing them as they open an umbrella just in time",
    },
    {
        "id": "m2-944",
        "word": "finally",
        "meaning": "최후로, 마침내",
        "scene": "an adorable stick figure happily breaking through a finish line ribbon with arms raised high in triumph after a long run",
    },
    {
        "id": "m2-945",
        "word": "immediately",
        "meaning": "곧, 즉시",
        "scene": "an adorable stick figure hearing an alarm and instantly sprinting forward at top speed with tiny dash motion lines behind",
    },
    {
        "id": "m2-946",
        "word": "especially",
        "meaning": "특별히",
        "scene": "an adorable stick figure holding a single glowing star balloon among several plain balloons, presenting it with joy",
    },
    {
        "id": "m2-947",
        "word": "else",
        "meaning": "그밖에, 다른",
        "scene": "an adorable stick figure pointing curiously toward a different unique door among several ordinary doors",
    },
    {
        "id": "m2-948",
        "word": "actually",
        "meaning": "실제로",
        "scene": "an adorable stick figure lifting up a mask or curtain to reveal the real surprise behind it with wide curious eyes",
    },
    {
        "id": "m2-949",
        "word": "hardly",
        "meaning": "거의 ~아니다",
        "scene": "an adorable stick figure peeking into an almost completely empty jar with only one tiny crumb left at the bottom, looking astonished",
    },
    {
        "id": "m2-950",
        "word": "otherwise",
        "meaning": "다른 방법으로, 그렇지 않으면",
        "scene": "an adorable stick figure standing at a fork in the road with two directional sign arrows pointing left and right, pondering which path to take",
    },
    {
        "id": "m2-951",
        "word": "tightly",
        "meaning": "단단히, 꽉",
        "scene": "two adorable stick figures giving each other a warm, tight, heartfelt embrace with arms wrapped securely",
    },
    {
        "id": "m2-952",
        "word": "recently",
        "meaning": "최근에",
        "scene": "an adorable stick figure proudly holding up a freshly taken instant polaroid photo of themselves, smiling",
    },
    {
        "id": "m2-953",
        "word": "rapidly",
        "meaning": "빨리, 신속히",
        "scene": "an adorable stick figure zooming past on a skateboard with speed breeze lines, scarf trailing behind",
    },
    {
        "id": "m2-954",
        "word": "however",
        "meaning": "그러나, 아무리 ~해도",
        "scene": "an adorable stick figure happily walking in sunshine until seeing a small isolated rain cloud directly ahead, turning with an expressive pose",
    },
    {
        "id": "m2-955",
        "word": "politely",
        "meaning": "공손히, 정중하게",
        "scene": "an adorable stick figure politely offering their seat on a bench to an elder stick figure with a gentle bow",
    },
    {
        "id": "m2-956",
        "word": "rudely",
        "meaning": "무례하게",
        "scene": "a stick figure talking loudly on a phone while an annoyed adorable stick figure nearby covers their ears with furrowed brow",
    },
    {
        "id": "m2-957",
        "word": "further",
        "meaning": "더욱이, 더 먼",
        "scene": "an adorable stick figure on top of a hill looking through a telescope towards a distant mountain peak further away",
    },
    {
        "id": "m2-958",
        "word": "frankly",
        "meaning": "솔직히",
        "scene": "an adorable stick figure placing their right hand over their chest, speaking openly and honestly with an open palm",
    },
    {
        "id": "m2-959",
        "word": "properly",
        "meaning": "적당히, 올바르게",
        "scene": "an adorable stick figure carefully adjusting a crooked picture frame on the wall so that it is perfectly straight and level",
    },
    {
        "id": "m2-960",
        "word": "haste",
        "meaning": "서두름",
        "scene": "an adorable stick figure rushing frantically while putting on a coat and trying to catch toast popping out of a toaster, in a hurried frenzy",
    },
]


def build_workflow(item, seed):
    positive_prompt = (
        f"Create a minimalist vocabulary line drawing for \"{item['word']}\" ({item['meaning']}): "
        f"{item['scene']}. "
        "Style: Minimalist black and white hand-drawn illustration, thick rounded clean black outlines, "
        "adorable simple stick figure characters with circular heads and simple dot eyes, "
        "pure white background, no fills, no colors, no grayscale shading, "
        "abundant empty negative space in the upper area, scene placed in lower-center with generous margins. "
        "No text, no letters, no watermark."
    )
    negative_prompt = (
        "text, letters, words, watermark, signature, color, shading, gradient, "
        "photorealistic, 3d render, ugly, deformed, blurry, complex background"
    )

    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 1.5,
                "denoise": 1,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "sgm_uniform",
                "seed": seed,
                "steps": 4,
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "DreamShaperXL_Lightning.safetensors",
            },
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "batch_size": 1,
                "height": 1024,
                "width": 1024,
            },
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": positive_prompt,
            },
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": negative_prompt,
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2],
            },
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"word_{item['word']}",
                "images": ["8", 0],
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


def wait_for_prompt(prompt_id, timeout_sec=180):
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
        time.sleep(2)
    return None


def main():
    os.makedirs(ASSETS_WORDS_DIR, exist_ok=True)
    total = len(UNIT_48_WORDS)
    print(f"==========================================================")
    print(f" 중2 48유닛 단어 일러스트 자동 생성 시작 (총 {total}단어)")
    print(f"==========================================================")

    for i, item in enumerate(UNIT_48_WORDS, 1):
        word = item["word"]
        target_path = os.path.join(ASSETS_WORDS_DIR, f"{word}.png")

        if os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
            print(f"[{i}/{total}] {word} ({item['id']}) - 이미 존재함 (건너뜀)")
            continue

        print(f"[{i}/{total}] {word} ({item['meaning']}) 생성 요청 중...", end="", flush=True)
        seed = 1000 + i * 37
        workflow = build_workflow(item, seed)
        
        t0 = time.time()
        prompt_id = queue_prompt(workflow)
        image_info = wait_for_prompt(prompt_id)

        if not image_info:
            print(f" -> ❌ 실패 (타임아웃)")
            continue

        filename = image_info["filename"]
        elapsed = time.time() - t0

        # 로컬 output 디렉토리에서 복사
        source_path = os.path.join(COMFY_OUTPUT_DIR, filename)
        if os.path.exists(source_path):
            shutil.copyfile(source_path, target_path)
            size_kb = os.path.getsize(target_path) / 1024
            print(f" -> ✅ 완료 ({elapsed:.1f}초, {size_kb:.0f}KB)")
        else:
            # API /view 로 다운로드 시도
            view_url = f"{COMFY_URL}/view?filename={urllib.parse.quote(filename)}&subfolder={urllib.parse.quote(image_info.get('subfolder',''))}&type=output"
            urllib.request.urlretrieve(view_url, target_path)
            size_kb = os.path.getsize(target_path) / 1024
            print(f" -> ✅ 다운로드 완료 ({elapsed:.1f}초, {size_kb:.0f}KB)")

    print(f"\n모든 48유닛 단어 이미지 생성 작업 완료!")


if __name__ == "__main__":
    main()
