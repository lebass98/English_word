#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 중학교 1학년 Unit 6 단어 20종 일괄 생성 스크립트
- 대상: Unit 6 (m1-101 ~ m1-120, 총 20개 전원)
"""

import os
import sys
import json
import time
import base64
import urllib.request
import argparse

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
WORD_IMAGES_TS = os.path.join(PROJECT_ROOT, "src", "constants", "wordImages.ts")

def update_word_images_ts(word: str, word_id: str):
    if not os.path.exists(WORD_IMAGES_TS):
        return
    with open(WORD_IMAGES_TS, "r", encoding="utf-8") as f:
        content = f.read()

    new_entries = []
    file_name = word.replace(" ", "-")
    if f'"{word}": require(' not in content and f'{word}: require(' not in content:
        new_entries.append(f'  "{word}": require("../../assets/words/{file_name}.png"),')
    if word_id and f'"{word_id}": require(' not in content:
        new_entries.append(f'  "{word_id}": require("../../assets/words/{file_name}.png"),')

    if not new_entries:
        return

    target = "};\n"
    if target in content:
        idx = content.rfind(target)
        updated = content[:idx] + "\n".join(new_entries) + "\n" + content[idx:]
        with open(WORD_IMAGES_TS, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"[{word}] wordImages.ts 등록 완료: {word_id} -> {file_name}.png", flush=True)

WORDS = [
    {
        "id": "m1-101",
        "word": "grain",
        "meaning": "곡식 낱알",
        "scene": "rustic wooden barn floor, cute slender stickman farmer cupping a handful of golden wheat grains examining the tiny seeds with gentle smile, overflowing burlap sacks of grain and pitchfork against wooden wall"
    },
    {
        "id": "m1-102",
        "word": "insect",
        "meaning": "곤충",
        "scene": "sunny garden bush with blooming flowers, curious cute slender stickman child bending low with a round magnifying glass observing a cute ladybug and honeybee on green leaves, garden watering can"
    },
    {
        "id": "m1-103",
        "word": "immediately",
        "meaning": "곧, 즉시",
        "scene": "busy fire station garage, emergency bell ringing overhead, cute slender stickman firefighter jumping up immediately sliding down the brass pole in a rush, helmet and boots ready beside fire engine"
    },
    {
        "id": "m1-104",
        "word": "valley",
        "meaning": "골짜기",
        "scene": "magnificent mountain valley landscape, cute slender stickman standing on an overlook admiring a winding river flowing through a lush green valley canyon between towering rocky mountain slopes"
    },
    {
        "id": "m1-105",
        "word": "bear",
        "meaning": "곰, 낳다, 참다",
        "scene": "peaceful forest riverbank, a large gentle furry mother bear catching fish in splashing shallow river water while a cute cub watches from mossy rock, cute slender stickman watching safely from wooden overlook platform"
    },
    {
        "id": "m1-106",
        "word": "area",
        "meaning": "공간, 지역, 영역",
        "scene": "city planning design studio table, cute slender stickman architect with ruler marking a highlighted designated playground area on a large city blueprint grid map, pencils and building blocks"
    },
    {
        "id": "m1-107",
        "word": "space",
        "meaning": "공간, 우주",
        "scene": "deep outer space starry galaxy, cute slender stickman astronaut floating weightlessly on tether outside spaceship looking in awe at swirling colorful nebulae, distant crescent moon and glowing Earth"
    },
    {
        "id": "m1-108",
        "word": "public",
        "meaning": "공공의",
        "scene": "lively city public park square, multiple diverse cute slender stickman citizens reading books on public benches, playing chess at stone table, and chatting around a central stone fountain"
    },
    {
        "id": "m1-109",
        "word": "supply",
        "meaning": "공급, 공급하다",
        "scene": "community humanitarian relief center, cheerful volunteer cute slender stickman handing emergency aid supply boxes of food and water bottles from a supply truck to grateful local townspeople"
    },
    {
        "id": "m1-110",
        "word": "politely",
        "meaning": "공손히",
        "scene": "cozy tearoom entrance doorway, polite cute slender stickman bowing gently with hands neatly folded in front welcoming a guest warmly, tea tray and sliding screen door"
    },
    {
        "id": "m1-111",
        "word": "factory",
        "meaning": "공장",
        "scene": "bustling modern clean automated factory floor, cute slender stickman technician with clipboard supervising a high-tech conveyor belt assembling toy cars, robotic arms and safety warning lights"
    },
    {
        "id": "m1-112",
        "word": "common",
        "meaning": "공통적인, 흔한",
        "scene": "elementary school classroom table, two cute slender stickman friends smiling discovering they both have the exact same common favorite robot toy and matching striped school notebooks"
    },
    {
        "id": "m1-113",
        "word": "airport",
        "meaning": "공항",
        "scene": "modern airport terminal departure gate, cute slender stickman traveler with rolling luggage standing by giant glass window watching a passenger airplane boarding and taxing on runway"
    },
    {
        "id": "m1-114",
        "word": "republic",
        "meaning": "공화국",
        "scene": "historic national capitol plaza, citizens gathering before a dignified domed senate capitol hall with classical marble pillars, cute slender stickman casting vote ballot into national election box"
    },
    {
        "id": "m1-115",
        "word": "past",
        "meaning": "과거",
        "scene": "nostalgic museum exhibit hallway, cute slender stickman looking thoughtfully through vintage black-and-white historic photo frames hanging on wall depicting old steam locomotives and antique town streets"
    },
    {
        "id": "m1-116",
        "word": "fruit",
        "meaning": "과일",
        "scene": "sunny farmer market wooden stall, cute slender stickman orchard keeper proudly displaying wooden crates overflowing with ripe round apples, bananas, bunches of grapes, and juicy oranges"
    },
    {
        "id": "m1-117",
        "word": "science",
        "meaning": "과학",
        "scene": "exciting science exhibition hall, cute slender stickman student touching a glowing plasma glass sphere with electric lightning sparks reaching fingers, double helix DNA model and telescope nearby"
    },
    {
        "id": "m1-118",
        "word": "officer",
        "meaning": "관리, 경찰관, 공무원",
        "scene": "busy city street crosswalk corner, friendly cute slender stickman police officer in uniform and peaked cap smiling while raising one white-gloved hand to pause traffic safely for children crossing"
    },
    {
        "id": "m1-119",
        "word": "view",
        "meaning": "관점, 경치",
        "scene": "breathtaking scenic hilltop wooden lookout deck, cute slender stickman leaning on railing holding small binoculars enjoying a panoramic scenic view of rolling green hills, winding river and sunset horizon"
    },
    {
        "id": "m1-120",
        "word": "sight",
        "meaning": "광경, 경치",
        "scene": "mountain summit at sunrise, cute slender stickman standing in pure wonder with arms open wide witnessing a spectacular sight of glowing orange clouds rising above a sea of misty mountain peaks"
    }
]

def generate_unit6_linear(start_index=1, skip_existing=False):
    print("==================================================")
    print("중1 유닛 6 '선형그래픽' 20개 단어 생성 시작 (m1-101 ~ m1-120)")
    print(f"시작 인덱스: {start_index}, 기존 파일 스킵: {skip_existing}")
    print("규격: 1024x1024, 0.05mm 초극세선, 노넥(No-Neck), 배경 #f5f6f8, 선색 #030203, 후처리 없음")
    print("==================================================")

    os.makedirs(ASSETS_DIR, exist_ok=True)
    total = len(WORDS)

    for idx, item in enumerate(WORDS, 1):
        if idx < start_index:
            continue
        word = item["word"]
        word_id = item["id"]
        meaning = item["meaning"]
        scene = item["scene"]
        file_name = word.replace(" ", "-")
        out_path = os.path.join(ASSETS_DIR, f"{file_name}.png")

        if skip_existing and os.path.exists(out_path):
            print(f"\n[{idx}/{total}] '{word}' 이미 존재하여 건너뜀 -> {out_path}", flush=True)
            update_word_images_ts(word, word_id)
            continue

        print(f"\n[{idx}/{total}] '{word}' ({word_id}: {meaning}) 생성 중...", flush=True)
        print(f"Scene: {scene}", flush=True)

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
            "seed": 900 + idx * 31
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
                print(f"[{word}] 생성 및 저장 완료 ({elapsed:.1f}초) -> {out_path}", flush=True)
                update_word_images_ts(word, word_id)
                success = True
                break
            except Exception as e:
                print(f"[{word}] 시도 {attempt} 실패: {e}", flush=True)
                time.sleep(3)

        if not success:
            print(f"[오류] '{word}' 생성 실패!", flush=True)

    print("\n==================================================", flush=True)
    print("중1 유닛 6 선형그래픽 생성 작업 완료!", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="중1 유닛 6 선형그래픽 단어 이미지 생성")
    parser.add_argument("--start-index", type=int, default=1, help="시작할 단어 번호 (1-indexed, 기본값: 1)")
    parser.add_argument("--skip-existing", action="store_true", help="이미 존재하는 파일 건너뛰기")
    args = parser.parse_args()

    generate_unit6_linear(start_index=args.start_index, skip_existing=args.skip_existing)
