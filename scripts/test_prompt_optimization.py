#!/usr/bin/env python3
"""
SDXL + ColoringBook LoRA ComfyUI: 프롬프트 최적화 테스트 (different 단어 테스트)
- LoRA 강도 0.75로 조정하여 프롬프트 순응도/상황 연출력 대폭 상승
- SDXL 맞춤형 가중치 프롬프트 적용
"""
import json
import os
import shutil
import time
import urllib.request

COMFY_URL = "http://127.0.0.1:8188"
PROJECT_ROOT = "/Users/ijaegwang/wordncode/App/English_word"
COMFY_OUTPUT_DIR = "/Users/ijaegwang/ComfyUI-Installs/ComfyUI/ComfyUI/output"

def test_workflow():
    # 다른(different) 단어의 기발한 상황:
    # 3마리 아기오리 중 가운데 1마리만 큰 선글라스+모자를 쓰고 뽐내는 코믹 대비 장면
    prompt = (
        "(Coloring Book, ColoringBookAF:1.1), (humorous comical cartoon scene:1.3), "
        "three cute little yellow ducklings in a row, "
        "(only the middle duckling is wearing oversized cool black sunglasses and a tiny funny party hat looking proud:1.4), "
        "the other two ducklings look completely ordinary and staring at him in utter shock and amazement, "
        "funny expressive faces, witty visual joke, "
        "(bold clean black outlines:1.2), (clear line art, doodle drawing:1.2), "
        "pure solid clean white background, completely empty background, "
        "strictly no color, strictly black and white line art, no text, no watermark"
    )
    
    negative = (
        "color, colors, colored, red, blue, green, yellow, grayscale shading, realistic, photo, 3d, render, "
        "messy lines, sketchy, dirty, blurry, bad anatomy, text, words, watermark, logo, frame, border"
    )

    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "DreamShaperXL_Lightning.safetensors"
            }
        },
        "2": {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": "coloringbook_sdxl.safetensors",
                "strength_model": 0.75,
                "strength_clip": 0.75,
                "model": ["1", 0],
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["2", 1]
            }
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative,
                "clip": ["2", 1]
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": 999,
                "steps": 25,
                "cfg": 6.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0
            }
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["6", 0],
                "vae": ["1", 2]
            }
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "prompt_test_different",
                "images": ["7", 0]
            }
        }
    }

    print("새로운 프롬프트 구조 전송 중...")
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        prompt_id = json.loads(resp.read().decode("utf-8")).get("prompt_id")
    print(f"Prompt ID: {prompt_id}")

    start = time.time()
    while time.time() - start < 360:
        try:
            req = urllib.request.Request(f"{COMFY_URL}/history/{prompt_id}")
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if prompt_id in res:
                    outputs = res[prompt_id].get("outputs", {})
                    for node_out in outputs.values():
                        images = node_out.get("images", [])
                        if images:
                            img_info = images[0]
                            src = os.path.join(COMFY_OUTPUT_DIR, img_info.get("subfolder", ""), img_info["filename"])
                            print(f"생성 완료! {src}")
                            return src
        except Exception:
            pass
        time.sleep(3)
    print("시간 초과")
    return None

if __name__ == "__main__":
    test_workflow()
