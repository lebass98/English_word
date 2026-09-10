#!/usr/bin/env python3
"""
FLUX.1 [schnell] 신규 카툰 캐릭터 라인아트 스타일 테스트: finally
- 사용자가 첨부한 이미지 스타일 반영:
  (두껍고 둥근 외곽선, 귀여운 치비 2D 카툰 캐릭터 소년/소녀, 순백색 배경, 색칠공부/라인아트 스타일, 무채색, 상단 여백)
"""

import json
import os
import shutil
import time
import urllib.request

COMFY_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = os.path.expanduser("~/ComfyUI-Shared/output")
ARTIFACT_DIR = "/Users/ijaegwang/.gemini/antigravity-ide/brain/a965b718-7061-4420-ae74-3d9bec6a9f15"

prompt_text = (
    "A minimalist black and white cartoon line art illustration depicting: "
    "two cute adorable chibi cartoon kids, a boy and a girl runner, joyfully bursting through a finish line ribbon with broad triumphant smiles and arms raised high in victory after a race. "
    "Style: Minimalist black and white cartoon coloring book line art, thick smooth rounded bold black outlines, "
    "adorable cute chibi cartoon characters with big expressive dot eyes and round friendly faces, simple clean doodle style, "
    "pure solid white background, no fills, no color, no grayscale shading, abundant empty space in the upper portion, "
    "strictly no text, no words, no letters, no watermark."
)

workflow = {
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
            "text": prompt_text,
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
            "seed": 2026,
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
            "filename_prefix": "cartoon_finally_test",
            "images": ["9", 0],
        },
    },
}

def main():
    print("FLUX.1 [schnell] 새 카툰 캐릭터 스타일 테스트 요청 중...")
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        prompt_id = json.loads(resp.read().decode("utf-8")).get("prompt_id")
    print(f"Prompt ID: {prompt_id}")

    start = time.time()
    while time.time() - start < 400:
        try:
            req = urllib.request.Request(f"{COMFY_URL}/history/{prompt_id}")
            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                if prompt_id in res_data:
                    outputs = res_data[prompt_id].get("outputs", {})
                    for node_out in outputs.values():
                        images = node_out.get("images", [])
                        if images:
                            fname = images[0]["filename"]
                            src = os.path.join(OUTPUT_DIR, fname)
                            dst = os.path.join(ARTIFACT_DIR, "cartoon_finally_test.png")
                            if os.path.exists(src):
                                shutil.copyfile(src, dst)
                                print(f"생성 완료 및 복사됨: {dst} ({time.time() - start:.1f}초)")
                                return
        except Exception as e:
            pass
        time.sleep(3)

if __name__ == "__main__":
    main()
