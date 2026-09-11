#!/usr/bin/env python3
"""
사용자 지정 13개 단어 선형그래픽 전면 재생성 스크립트
- 대상:
  [중1 유닛 2 (7개)]
  - least, favorite, branch, worth, angle, crack, brown
  [중1 유닛 3 (6개)]
  - decrease, suddenly, unlike, upside down, deal, nearly

- 스킬 원칙 100% 준수:
  1. 1024x1024 네이티브 출력 (0.05mm 초극세 바늘선)
  2. 노넥(No-Neck) 캐릭터 (동그란 머리가 몸통에 바로 붙음, 목 없음)
  3. 배경색 #f5f6f8, 선색 #030203
  4. 후처리 없음 (순수 원본 렌더링)
  5. 한글 텍스트 전면 배제 및 영문 우선 표기 (English Only / No Korean Text)
  6. 기존 파일 존재 여부 무관하게 강제 재생성(덮어쓰기)
"""

import os
import sys
import json
import time
import base64
import urllib.request

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")

TARGET_WORDS = [
    # 중1 유닛 2 (7개)
    {
        "unit": "Unit 2",
        "id": "m1-30",
        "word": "least",
        "meaning": "가장 적은",
        "scene": "science math classroom table, cute slender stickman comparing three balance scales with candy boxes, pointing specifically to the dish holding the single smallest least amount of candy, chart on wall"
    },
    {
        "unit": "Unit 2",
        "id": "m1-31",
        "word": "favorite",
        "meaning": "가장 좋아하는",
        "scene": "sunlit study room armchair, happy cute slender stickman smiling warmly hugging a favorite beloved storybook decorated with tiny sparkling hearts, sleeping cat on side table, bookshelf and framed art"
    },
    {
        "unit": "Unit 2",
        "id": "m1-34",
        "word": "branch",
        "meaning": "가지, 지점",
        "scene": "leafy grand oak tree, detailed sturdy tree branch with a cute bird nest and tiny chirping birds, cute slender stickman below examining the branch with a magnifying glass holding a nature sketchbook"
    },
    {
        "unit": "Unit 2",
        "id": "m1-35",
        "word": "worth",
        "meaning": "가치",
        "scene": "antique appraisal shop desk, expert cute slender stickman appraiser inspecting an ornate golden chalice cup with a magnifying glass assessing its great valuable worth, eager collector watching, antique clocks"
    },
    {
        "unit": "Unit 2",
        "id": "m1-36",
        "word": "angle",
        "meaning": "각도",
        "scene": "architect drafting studio table, cute slender stickman draftsman carefully measuring precise geometric angles on blueprint paper using a large circular protractor and triangle ruler, drafting lamp and blueprints"
    },
    {
        "unit": "Unit 2",
        "id": "m1-39",
        "word": "crack",
        "meaning": "갈라진",
        "scene": "pottery artisan workshop, cute slender stickman ceramicist holding up a freshly fired glazed ceramic vase noticing a delicate fine crack line on its surface, pottery wheel and shelves of pottery jars"
    },
    {
        "unit": "Unit 2",
        "id": "m1-40",
        "word": "brown",
        "meaning": "갈색의",
        "scene": "art studio easel, cute slender stickman painter holding wooden palette with rich brown paint tubes, painting a cozy autumn scene of acorns, fallen brown oak leaves, and tree log on large canvas, paint jars"
    },

    # 중1 유닛 3 (6개)
    {
        "unit": "Unit 3",
        "id": "m1-41",
        "word": "decrease",
        "meaning": "감소",
        "scene": "office presentation room, cute slender stickman speaker pointing to a gentle downward decreasing slope graph on a large whiteboard, colleagues seated at conference table attentively analyzing the chart, laptop and coffee mugs"
    },
    {
        "unit": "Unit 3",
        "id": "m1-45",
        "word": "suddenly",
        "meaning": "갑자기",
        "scene": "surprise birthday celebration living room, door swinging open suddenly as cute slender stickman friends pop colorful party confetti poppers shouting surprise, hero stickman with hands raised in sudden delight, cake and balloons"
    },
    {
        "unit": "Unit 3",
        "id": "m1-52",
        "word": "unlike",
        "meaning": "같지 않은",
        "scene": "art design exhibition gallery, two cute slender stickman visitors comparing a wall of three identical circle paintings beside one totally unique unlike glowing star sculpture, bench and gallery spotlight"
    },
    {
        "unit": "Unit 3",
        "id": "m1-55",
        "word": "upside down",
        "meaning": "거꾸로",
        "scene": "outdoor playground monkey bars jungle gym, cute slender stickman hanging completely upside down by legs waving cheerfully with big smile, friend standing upright below laughing and clapping, playground slide"
    },
    {
        "unit": "Unit 3",
        "id": "m1-58",
        "word": "deal",
        "meaning": "거래하다",
        "scene": "modern business office meeting room, two professional cute slender stickman partners shaking hands warmly sealing a successful business deal contract on conference table, signed document folders and coffee cups"
    },
    {
        "unit": "Unit 3",
        "id": "m1-60",
        "word": "nearly",
        "meaning": "거의",
        "scene": "afternoon puzzle table, large 1000-piece jigsaw puzzle nearly finished with only one final missing piece held in cute slender stickman's fingers ready to place, friends eagerly leaning in watching the completion"
    }
]

def generate_targeted_words():
    print("==================================================", flush=True)
    print("중1 유닛 2 & 3 지정 13개 단어 선형그래픽 재생성 시작", flush=True)
    print("규칙: 1024x1024, 0.05mm 극세선, No-Neck, 한글 배제(영문 전용), #f5f6f8, #030203", flush=True)
    print("==================================================", flush=True)

    os.makedirs(ASSETS_DIR, exist_ok=True)
    total = len(TARGET_WORDS)

    for idx, item in enumerate(TARGET_WORDS, 1):
        unit = item["unit"]
        word_id = item["id"]
        word = item["word"]
        meaning = item["meaning"]
        scene = item["scene"]
        file_name = word.replace(" ", "-")
        out_path = os.path.join(ASSETS_DIR, f"{file_name}.png")

        print(f"\n[{idx}/{total}] [{unit} {word_id}] '{word}' ({meaning}) 생성 중...", flush=True)
        print(f"Scene: {scene}", flush=True)

        # 100% 영문 프롬프트 (한글 단어 뜻 배제 원칙)
        prompt = (
            f"linear graphic illustration, complete richly detailed scene of {word}, "
            f"thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, "
            f"extremely fine crisp outlines drawn in dark charcoal ink color #030203, "
            f"flat smooth light gray canvas background color #f5f6f8, "
            f"neckless cute slender doodle stickman characters with round bald circle heads attached directly to torso with completely no neck, tiny smiling dot faces, "
            f"{scene}, "
            f"abundant rich background details, furniture, wall decor, floor line, ambient props, "
            f"strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, empty background"
        )

        negative_prompt = (
            "neck, long neck, throat, collar, neck line, detailed neck anatomy, "
            "Korean text, Hangul, Korean letters, non-English text, broken characters, foreign characters, "
            "thick lines, bold outlines, heavy brush strokes, chunky lines, fat strokes, "
            "pure white #ffffff background, dark background, black background, 3d, realistic, shadow, shading, "
            "color, gradients, photo, blur, watermark, text, signature"
        )

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": 8,
            "width": 1024,
            "height": 1024,
            "seed": 900 + idx * 37
        }

        success = False
        for attempt in range(1, 4):
            try:
                t0 = time.time()
                req = urllib.request.Request(
                    API_URL,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=300) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    images = data.get("images", [])
                    if not images:
                        raise RuntimeError("No image returned")
                    raw_bytes = base64.b64decode(images[0])

                with open(out_path, "wb") as f:
                    f.write(raw_bytes)

                elapsed = time.time() - t0
                print(f"[{word}] 생성 완료 ({elapsed:.1f}초) -> {out_path}", flush=True)
                success = True
                break
            except Exception as e:
                print(f"[{word}] 시도 {attempt} 실패: {e}", flush=True)
                time.sleep(3)

        if not success:
            print(f"[오류] '{word}' 생성 실패!", flush=True)

    print("\n==================================================", flush=True)
    print("지정 13개 단어 선형그래픽 재생성 작업 완료!", flush=True)

if __name__ == "__main__":
    generate_targeted_words()
