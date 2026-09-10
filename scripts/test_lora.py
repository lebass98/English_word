#!/usr/bin/env python3
"""
SDXL + ColoringBook LoRA ComfyUI 생성 테스트 (단어 1개 테스트)
"""
import json
import os
import shutil
import time
import urllib.request

COMFY_URL = "http://127.0.0.1:8188"
PROJECT_ROOT = "/Users/ijaegwang/wordncode/App/English_word"
COMFY_OUTPUT_DIR = os.path.expanduser("~/ComfyUI-Shared/output")

def test_workflow():
    prompt = (
        "Coloring Book, ColoringBookAF, minimalist black and white coloring book page, "
        "a cute adorable happy chibi cartoon boy jumping high in the air with arms wide open, "
        "excited expression with big sparkling eyes, "
        "thick bold clean black outlines, smooth line art, simple doodle drawing, "
        "pure solid clean white background, completely empty background, sharp clean vector lines, "
        "strictly no color, no colors, no shading, no gradient, no gray fill, "
        "strictly no text, no words, no letters, no watermark."
    )
    
    negative = (
        "color, colors, colored, red, blue, yellow, green, grayscale shading, shadow, shadows, realistic, photo, 3d, render, "
        "messy lines, sketchy, dirty, blurry, low quality, bad anatomy, text, words, watermark, logo, frame, border"
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
                "strength_model": 1.0,
                "strength_clip": 1.0,
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
                "seed": 42,
                "steps": 25,
                "cfg": 6.0,
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
                "filename_prefix": "lora_test_excited",
                "images": ["7", 0]
            }
        }
    }

    print("전송 중...")
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        prompt_id = json.loads(resp.read().decode("utf-8")).get("prompt_id")
    print(f"Prompt ID: {prompt_id}")

    start = time.time()
    while time.time() - start < 300:
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
                            src = os.path.join(COMFY_OUTPUT_DIR, img_info["subfolder"], img_info["filename"])
                            print(f"생성 완료! {src}")
                            return src
        except Exception as e:
            pass
        time.sleep(2)
    print("시간 초과")
    return None

if __name__ == "__main__":
    test_workflow()
