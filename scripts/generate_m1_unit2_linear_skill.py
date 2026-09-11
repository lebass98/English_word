#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 중학교 1학년 Unit 2 단어 20종 일괄 생성 스크립트
- 대상: Unit 2 (m1-21 ~ m1-40, 총 20개 전원)
- 단어:
  21. sophomore (2학년생)
  22. quarter (4분의 1)
  23. store (가게, 저장하다)
  24. furniture (가구)
  25. possible (가능한)
  26. sink (가라앉다)
  27. powder (가루, 화약)
  28. chest (가슴)
  29. join (가입하다, 참가하다)
  30. least (가장 적은)
  31. favorite (가장 좋아하는)
  32. suppose (가정하다, 상상하다)
  33. bring (가져오다)
  34. branch (가지, 지점)
  35. worth (가치)
  36. angle (각도)
  37. simple (간단한)
  38. nurse (간호사)
  39. crack (갈라진)
  40. brown (갈색의)

- 스킬 표준:
  1. 초기 선 굵기: 0.05mm 초극세 바늘선 (thinnest possible needle-thin hairline ink stroke)
  2. 해상도: 1024x1024 네이티브 출력 (업스케일 없이 직접 렌더링)
  3. 조형 규칙: 노넥(No-Neck) 캐릭터 (동그란 머리가 몸통에 바로 붙음, 목 없음)
  4. 배경 색상코드: #f5f6f8 (소프트 라이트그레이 캔버스)
  5. 선 색상코드: #030203 (딥 차콜 블랙 잉크)
  6. 풍성한 씬: 인물 상호작용, 가구, 배경 오브젝트, 디테일 완비
  7. 후처리 배제: 인위적인 필터/임계값 조작 없이 모델 순수 원본 보존
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

WORDS = [
    {
        "id": "m1-21",
        "word": "sophomore",
        "meaning": "2학년생",
        "scene": "high school campus hallway with lockers and bulletin board, confident cute slender stickman sophomore holding textbooks giving directions with campus map to an incoming freshman stickman, classmates walking by, wall clock"
    },
    {
        "id": "m1-22",
        "word": "quarter",
        "meaning": "4분의 1",
        "scene": "cozy pastry kitchen counter, cute slender stickman baker lifting one precise one-fourth quarter slice of round pie with a serving spatula onto a plate, rolling pin, flour bowl and baking shelves"
    },
    {
        "id": "m1-23",
        "word": "store",
        "meaning": "가게, 저장하다",
        "scene": "charming village grocery general store with striped awning, cute slender stickman storekeeper stocking glass jars and boxes onto tall wooden shelves, friendly customer with shopping basket, cash register counter"
    },
    {
        "id": "m1-24",
        "word": "furniture",
        "meaning": "가구",
        "scene": "cozy furniture showroom living room interior, cute slender stickman relaxing happily on a plush armchair, another stickman admiring a stylish wooden coffee table and bookshelf wardrobe set, floor lamp and potted plant"
    },
    {
        "id": "m1-25",
        "word": "possible",
        "meaning": "가능한",
        "scene": "science laboratory chalkboard, cute slender stickman scientist solving the final complex formula and drawing a triumphant checkmark declaring it is possible, teammate cheering with raised arms, lab beakers and desk"
    },
    {
        "id": "m1-26",
        "word": "sink",
        "meaning": "가라앉다",
        "scene": "aquarium clear underwater tank, heavy iron anchor and toy ship slowly sinking down toward sandy seabed with rising bubble streams, cute slender stickman standing outside observing with curiosity, seashells and seaweed"
    },
    {
        "id": "m1-27",
        "word": "powder",
        "meaning": "가루, 화약",
        "scene": "baking studio counter, cute slender stickman gently sifting fine powdered sugar through a handheld round sieve like falling snow into a mixing bowl, friend watching with measuring cup, flour sack and whisk"
    },
    {
        "id": "m1-28",
        "word": "chest",
        "meaning": "가슴",
        "scene": "warm medical clinic examination room, friendly cute slender stickman doctor listening to patient stickman's chest heartbeat with stethoscope while patient breathes deeply with hand over heart, medicine cabinet and chart"
    },
    {
        "id": "m1-29",
        "word": "join",
        "meaning": "가입하다, 참가하다",
        "scene": "school club registration booth with 'ART CLUB JOIN US' banner, excited cute slender stickman signing membership form with pen, friendly club president stickman smiling warmly shaking hand across the table"
    },
    {
        "id": "m1-30",
        "word": "least",
        "meaning": "가장 적은",
        "scene": "science math classroom table, cute slender stickman comparing three balance scales with candy boxes, pointing specifically to the dish holding the single smallest least amount of candy, chart on wall"
    },
    {
        "id": "m1-31",
        "word": "favorite",
        "meaning": "가장 좋아하는",
        "scene": "sunlit study room armchair, happy cute slender stickman smiling warmly hugging a favorite beloved storybook decorated with tiny sparkling hearts, sleeping cat on side table, bookshelf and framed art"
    },
    {
        "id": "m1-32",
        "word": "suppose",
        "meaning": "가정하다, 상상하다",
        "scene": "cozy bedroom study desk, cute slender stickman resting chin on hand dreaming with a whimsical thought bubble above depicting a spaceship flying around planets, desk lamp and globe"
    },
    {
        "id": "m1-33",
        "word": "bring",
        "meaning": "가져오다",
        "scene": "sunny park picnic lawn, cheerful cute slender stickman happily carrying and bringing a picnic basket full of fresh sandwiches and fruits to friends sitting on a blanket waving welcoming hands, trees and kites"
    },
    {
        "id": "m1-34",
        "word": "branch",
        "meaning": "가지, 지점",
        "scene": "leafy grand oak tree, detailed sturdy tree branch with a cute bird nest and tiny chirping birds, cute slender stickman below examining the branch with a magnifying glass holding a nature sketchbook"
    },
    {
        "id": "m1-35",
        "word": "worth",
        "meaning": "가치",
        "scene": "antique appraisal shop desk, expert cute slender stickman appraiser inspecting an ornate golden chalice cup with a magnifying glass assessing its great valuable worth, eager collector watching, antique clocks"
    },
    {
        "id": "m1-36",
        "word": "angle",
        "meaning": "각도",
        "scene": "architect drafting studio table, cute slender stickman draftsman carefully measuring precise geometric angles on blueprint paper using a large circular protractor and triangle ruler, drafting lamp and blueprints"
    },
    {
        "id": "m1-37",
        "word": "simple",
        "meaning": "간단한",
        "scene": "minimalist design studio blackboard, cute slender stickman proudly drawing a clean simple three-line outline house with chalk, contrasting with messy complicated scribbles on the left side, wooden easel"
    },
    {
        "id": "m1-38",
        "word": "nurse",
        "meaning": "간호사",
        "scene": "cozy pediatric hospital room, caring cute slender stickman nurse holding a medicine tray and thermometer checking forehead of young stickman patient resting in bed, teddy bear on chair, bedside lamp"
    },
    {
        "id": "m1-39",
        "word": "crack",
        "meaning": "갈라진",
        "scene": "pottery artisan workshop, cute slender stickman ceramicist holding up a freshly fired glazed ceramic vase noticing a delicate fine crack line on its surface, pottery wheel and shelves of pottery jars"
    },
    {
        "id": "m1-40",
        "word": "brown",
        "meaning": "갈색의",
        "scene": "art studio easel, cute slender stickman painter holding wooden palette with rich brown paint tubes, painting a cozy autumn scene of acorns, fallen brown oak leaves, and tree log on large canvas, paint jars"
    }
]

def generate_unit2_linear():
    print("==================================================")
    print("중1 유닛 2 '선형그래픽' 20개 단어 일괄 생성 시작 (m1-21 ~ m1-40)")
    print("규격: 1024x1024, 0.05mm 초극세선, 노넥(No-Neck), 배경 #f5f6f8, 선색 #030203, 후처리 없음")
    print("==================================================")

    os.makedirs(ASSETS_DIR, exist_ok=True)
    total = len(WORDS)

    for idx, item in enumerate(WORDS, 1):
        word = item["word"]
        word_id = item["id"]
        meaning = item["meaning"]
        scene = item["scene"]
        out_path = os.path.join(ASSETS_DIR, f"{word}.png")

        print(f"\n[{idx}/{total}] '{word}' ({word_id}: {meaning}) 생성 중...")
        print(f"Scene: {scene}")

        prompt = (
            f"linear graphic illustration, complete richly detailed scene of {word} ({meaning}), "
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
            "seed": 700 + idx * 23
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
                print(f"[{word}] 생성 및 저장 완료 ({elapsed:.1f}초) -> {out_path}")
                success = True
                break
            except Exception as e:
                print(f"[{word}] 시도 {attempt} 실패: {e}")
                time.sleep(3)

        if not success:
            print(f"[오류] '{word}' 생성 실패!")

    print("\n==================================================")
    print("중1 유닛 2 선형그래픽 20종 생성 작업 완료!")

if __name__ == "__main__":
    generate_unit2_linear()
