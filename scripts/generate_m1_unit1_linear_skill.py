#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 중학교 1학년 Unit 1 단어 20종 일괄 재생성 스크립트
- 대상: Unit 1 (m1-1 ~ m1-20, 총 20개 전원)
- 스킬 표준:
  1. 초기 선 굵기: 0.05mm 초극세 바늘선 (thinnest possible needle-thin hairline ink stroke)
  2. 해상도: 1024x1024 네이티브 출력 (업스케일 없이 직접 렌더링)
  3. 배경 색상코드: #f5f6f8 (소프트 라이트그레이 캔버스)
  4. 선 색상코드: #030203 (딥 차콜 블랙 잉크)
  5. 풍성한 씬: 인물 상호작용, 가구, 배경 오브젝트, 디테일 완비
  6. 후처리 배제: 인위적인 필터/임계값 조작 없이 모델 순수 원본 보존
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
WORD_IMAGES_TS = os.path.join(PROJECT_ROOT, "src", "constants", "wordImages.ts")

WORDS = [
    {
        "id": "m1-1",
        "word": "beyond",
        "meaning": "~너머로",
        "scene": "high hilltop observation deck with railing, cute slender stickman with telescope pointing to a majestic castle and rainbow beyond distant mountain peaks, friend looking through binoculars, bench and flying birds"
    },
    {
        "id": "m1-2",
        "word": "either",
        "meaning": "~도 (어느 한쪽)",
        "scene": "cozy bakery dessert counter, cute slender stickman smiling happily holding a cupcake in one hand and a cookie in the other considering either option, pastry shelves and menu board"
    },
    {
        "id": "m1-3",
        "word": "neither",
        "meaning": "~도 아닌",
        "scene": "boutique clothing shop, shopkeeper holding up two funny striped hats, cute slender stickman crossing hands waving both away with polite smile saying neither is right, mirror and clothes rack"
    },
    {
        "id": "m1-4",
        "word": "behind",
        "meaning": "~뒤의",
        "scene": "living room hide and seek, cute slender stickman peeking cheerfully from behind a large comfy sofa, seeker friend in center covering eyes, potted plant and tall bookshelf"
    },
    {
        "id": "m1-5",
        "word": "bound",
        "meaning": "~로 향하는",
        "scene": "train station platform with 'BOUND FOR SEOUL' sign hanging above, backpacker slender stickman walking eagerly toward waiting train, conductor waving whistle, station clock and bench"
    },
    {
        "id": "m1-6",
        "word": "below",
        "meaning": "~아래로",
        "scene": "cozy loft apartment, cute slender stickman on second-floor railing looking down calling out to friend below feeding a cat in the living room, wooden ladder and bookshelf"
    },
    {
        "id": "m1-7",
        "word": "without",
        "meaning": "~없이",
        "scene": "rainy city sidewalk, carefree cute slender stickman joyfully splashing through puddles without an umbrella, friend beside under a big umbrella watching in amusement, streetlamp and raindrops"
    },
    {
        "id": "m1-8",
        "word": "belong",
        "meaning": "~에 속하다",
        "scene": "sports clubhouse room, three cute slender stickman friends in matching numbered team jerseys with arms over shoulders celebrating together, trophy case and team flag on wall"
    },
    {
        "id": "m1-9",
        "word": "replace",
        "meaning": "~을 대체하다",
        "scene": "bicycle repair workshop, cute slender stickman mechanic replacing an old flat tire wheel with a shiny brand-new wheel on bike frame, friend holding wrench, tool board on wall"
    },
    {
        "id": "m1-10",
        "word": "along",
        "meaning": "~을 따라서",
        "scene": "peaceful lakeside park trail, cute slender stickman riding bicycle along a winding wooden river fence with friend walking beside, willow trees and gentle water ripple lines"
    },
    {
        "id": "m1-11",
        "word": "except",
        "meaning": "~을 제외하고",
        "scene": "bakery display counter, tray of four round donuts with one single star-shaped pastry singled out as the exception, cute slender stickman pointing with tongs, coffee cup and wall shelves"
    },
    {
        "id": "m1-12",
        "word": "become",
        "meaning": "~이 되다",
        "scene": "magic dressing room studio, cute slender stickman in front of vanity mirror wearing a tall magician hat and cape holding magic wand proudly becoming a magician, sparkling fairy lights"
    },
    {
        "id": "m1-13",
        "word": "since",
        "meaning": "~이후로",
        "scene": "bedroom wall with marked growth chart lines for years 2023 2024 2025, cute slender stickman standing tall checking height growth since childhood, parent measuring with ruler, bed and clock"
    },
    {
        "id": "m1-14",
        "word": "pretend",
        "meaning": "~인 체하다",
        "scene": "living room playtime, cute slender stickman pretending to be a brave knight wearing cardboard armor holding paper sword, friend pretending to be king wearing paper crown, cushion fort"
    },
    {
        "id": "m1-15",
        "word": "whether",
        "meaning": "~인지 아닌지",
        "scene": "hallway entrance mirror, cute slender stickman thoughtfully weighing whether to take an umbrella or sunglasses looking out window at cloudy sky, coat rack and shoe bench"
    },
    {
        "id": "m1-16",
        "word": "toward",
        "meaning": "~쪽으로",
        "scene": "coastal shore at dusk, cute slender stickman and friend walking forward along sandy beach path toward a glowing seaside lighthouse in the distance, gentle waves and flying sea birds"
    },
    {
        "id": "m1-17",
        "word": "while",
        "meaning": "~하는 동안",
        "scene": "sunny kitchen dining table, one cute slender stickman happily frying eggs at stove while friend sits across reading morning newspaper sipping tea, pantry shelves and wall clock"
    },
    {
        "id": "m1-18",
        "word": "unless",
        "meaning": "~하지 않는 한",
        "scene": "library museum entrance gate, cute slender stickman visitor showing entry pass to security guard at turnstile beneath sign saying 'NO ENTRY UNLESS WITH PASS', book stacks in background"
    },
    {
        "id": "m1-19",
        "word": "deserve",
        "meaning": "~할 가치가 있다",
        "scene": "school auditorium podium, cute slender stickman beaming with joy holding a large shiny trophy and medal, enthusiastic friends applauding and handing celebratory flowers, banner above"
    },
    {
        "id": "m1-20",
        "word": "teenager",
        "meaning": "10대",
        "scene": "cozy teen bedroom, three cheerful slender stickman teenagers with headphones around necks posing for a smartphone selfie with skateboard leaning against desk, music posters on wall"
    }
]

def generate_unit1_linear():
    print("==================================================")
    print("중1 유닛 1 '선형그래픽' 20개 단어 일괄 재생성 시작 (m1-1 ~ m1-20)")
    print("규격: 1024x1024, 0.05mm 초극세선, 배경 #f5f6f8, 선색 #030203, 후처리 없음")
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
            "seed": 600 + idx * 17
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
    print("중1 유닛 1 선형그래픽 20종 생성 작업 완료!")

if __name__ == "__main__":
    generate_unit1_linear()
