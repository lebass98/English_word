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
        "scene": "a comically tall, cute chibi cartoon boy awkwardly crouching and waddling very low like a duck with funny sweat drops to squeeze underneath an absurdly low wooden ceiling beam",
    },
    {
        "id": "m2-942",
        "word": "sincerely",
        "meaning": "성실히, 진심으로",
        "scene": "an adorable chibi cartoon boy with big twinkling anime eyes placing both hands lovingly over his heart, politely bowing and presenting a giant handmade paper heart with a sweet blushing smile",
    },
    {
        "id": "m2-943",
        "word": "fortunately",
        "meaning": "운 좋게, 다행히",
        "scene": "a cute chibi cartoon girl grinning in huge relief under a tiny umbrella, holding a lucky four-leaf clover, while a giant raincloud pours water everywhere else around her, leaving her completely dry",
    },
    {
        "id": "m2-944",
        "word": "finally",
        "meaning": "최후로, 마침내",
        "scene": "two cute chibi cartoon kids, a boy and a girl runner, joyfully bursting through a finish line ribbon with broad triumphant smiles and arms raised high in victory after a race",
    },
    {
        "id": "m2-945",
        "word": "immediately",
        "meaning": "곧, 즉시",
        "scene": "a cute chibi cartoon boy hearing an alarm clock ringing and instantly blasting forward like a rocket, leaving behind funny cartoon whirlwind dust spirals at his feet",
    },
    {
        "id": "m2-946",
        "word": "especially",
        "meaning": "특별히",
        "scene": "a cute chibi cartoon girl happily spotlighting and presenting one giant glowing star cupcake with a cute crown, standing out brightly among a tray of plain ordinary cookies",
    },
    {
        "id": "m2-947",
        "word": "else",
        "meaning": "그밖에, 다른",
        "scene": "a curious cute chibi cartoon boy pointing enthusiastically towards a secret glowing whimsical wooden door, while a row of people absentmindedly walks the other normal way",
    },
    {
        "id": "m2-948",
        "word": "actually",
        "meaning": "실제로",
        "scene": "a cute chibi cartoon kid pulling off a fierce roaring monster mask with a funny wink, revealing a super gentle, sweet smiling face hugging a fluffy puppy",
    },
    {
        "id": "m2-949",
        "word": "hardly",
        "meaning": "거의 ~아니다",
        "scene": "a cute chibi cartoon boy peering with a giant magnifying glass into an almost completely empty cookie jar, comically shocked to find only one microscopic crumb remaining",
    },
    {
        "id": "m2-950",
        "word": "otherwise",
        "meaning": "다른 방법으로, 그렇지 않으면",
        "scene": "a cute chibi cartoon explorer boy scratching his head in funny confusion at a fork in the road, with two whimsical signposts pointing left and right",
    },
    {
        "id": "m2-951",
        "word": "tightly",
        "meaning": "단단히, 꽉",
        "scene": "two cute chibi cartoon best friends hugging each other comically tightly, squishing their chubby cheeks together with funny happy squished faces and tiny love hearts",
    },
    {
        "id": "m2-952",
        "word": "recently",
        "meaning": "최근에",
        "scene": "a cute chibi cartoon girl excitedly fluttering and fanning a freshly taken instant polaroid photo that still has magic sparkles on it, posing with a cute peace sign",
    },
    {
        "id": "m2-953",
        "word": "rapidly",
        "meaning": "빨리, 신속히",
        "scene": "a cute chibi cartoon boy speeding by rapidly on roller skates, his scarf and hair fluttering backwards with funny dynamic motion speed lines",
    },
    {
        "id": "m2-954",
        "word": "however",
        "meaning": "그러나, 아무리 ~해도",
        "scene": "a cute chibi cartoon boy happily eating an ice cream cone in sunny weather, suddenly freezing in comical surprise as one tiny grumpy raincloud hovers directly over his head",
    },
    {
        "id": "m2-955",
        "word": "politely",
        "meaning": "공손히, 정중하게",
        "scene": "a cute chibi cartoon boy bowing politely at a neat angle, using two hands to gently offer a warm cup of tea on a saucer with a charming, gentle smile",
    },
    {
        "id": "m2-956",
        "word": "rudely",
        "meaning": "무례하게",
        "scene": "a naughty cartoon kid shouting loudly into a megaphone, while an annoyed cute chibi friend nearby comically covers their ears with a giant grumpy pout",
    },
    {
        "id": "m2-957",
        "word": "further",
        "meaning": "더욱이, 더 먼",
        "scene": "a cute adventurous chibi boy standing on tiptoes atop a tiny wooden stool, peering through an exaggeratedly long telescoping spyglass towards a distant mountain peak",
    },
    {
        "id": "m2-958",
        "word": "frankly",
        "meaning": "솔직히",
        "scene": "a cute chibi cartoon boy with one hand raised high in a sincere pledge and the other on his chest, speaking with a comically earnest, wide-eyed honest expression",
    },
    {
        "id": "m2-959",
        "word": "properly",
        "meaning": "적당히, 올바르게",
        "scene": "a cute perfectionist chibi cartoon girl using a ruler and level tool to meticulously adjust a crooked picture frame on the wall until it is 100% straight, flashing a proud thumbs-up",
    },
    {
        "id": "m2-960",
        "word": "haste",
        "meaning": "서두름",
        "scene": "a cute chibi cartoon kid in a hilarious frantic morning rush, running with a piece of toast in mouth, jacket only half on, and backpack flying open while glancing at a giant alarm clock",
    },
]


def build_workflow(item, seed):
    positive_prompt = (
        f"A minimalist black and white cartoon line art illustration depicting: {item['scene']}. "
        "Style: Minimalist black and white cartoon coloring book line art, thick smooth rounded bold black outlines, "
        "adorable cute chibi cartoon characters with big expressive dot eyes and round friendly faces, simple clean doodle style, "
        "pure solid white background, no fills, no color, no grayscale shading, abundant empty space in the upper portion, "
        "strictly no text, no words, no letters, no watermark."
    )

    return {
        "1": {
            "class_type": "UnetLoaderGGUF",
            "inputs": {
                "unet_name": "flux1-schnell-Q4_K_S.gguf",
            },
        },
        "2": {
            "class_type": "DualCLIPLoaderGGUF",
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5-v1_1-xxl-encoder-Q4_K_M.gguf",
                "type": "flux",
            },
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.safetensors",
            },
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "batch_size": 1,
                "height": 1024,
                "width": 1024,
            },
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["2", 0],
                "text": positive_prompt,
            },
        },
        "6": {
            "class_type": "FluxGuidance",
            "inputs": {
                "conditioning": ["5", 0],
                "guidance": 3.5,
            },
        },
        "7": {
            "class_type": "ConditioningZeroOut",
            "inputs": {
                "conditioning": ["6", 0],
            },
        },
        "8": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 1.0,
                "denoise": 1.0,
                "latent_image": ["4", 0],
                "model": ["1", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "simple",
                "seed": seed,
                "steps": 4,
            },
        },
        "9": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["8", 0],
                "vae": ["3", 0],
            },
        },
        "10": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"flux_{item['word']}",
                "images": ["9", 0],
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


import argparse


def main():
    parser = argparse.ArgumentParser(description="FLUX.1 [schnell] 단어 이미지 일괄 생성")
    parser.add_argument("--force", action="store_true", help="기존 파일이 있어도 덮어쓰기 생성")
    parser.add_argument("--words", nargs="*", help="특정 단어들만 지정하여 생성 (예: --words low sincerely)")
    parser.add_argument("--exclude", nargs="*", default=["finally"], help="제외할 단어 목록 (기본: finally)")
    args = parser.parse_args()

    os.makedirs(ASSETS_WORDS_DIR, exist_ok=True)

    words_to_process = UNIT_48_WORDS
    if args.words:
        target_words = set(args.words)
        words_to_process = [item for item in UNIT_48_WORDS if item["word"] in target_words]
    elif args.exclude:
        exclude_words = set(args.exclude)
        words_to_process = [item for item in UNIT_48_WORDS if item["word"] not in exclude_words]

    total = len(words_to_process)
    print(f"==========================================================")
    print(f" FLUX.1 [schnell] 48유닛 단어 일러스트 생성 (총 {total}단어)")
    print(f"==========================================================")

    for i, item in enumerate(words_to_process, 1):
        word = item["word"]
        target_path = os.path.join(ASSETS_WORDS_DIR, f"{word}.png")

        if not args.force and os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
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

    print(f"\n모든 작업 완료!")


if __name__ == "__main__":
    main()
