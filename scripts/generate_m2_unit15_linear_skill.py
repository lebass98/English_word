#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 중학교 2학년 Unit 15 단어 19종 일괄 재생성 스크립트
- 대상: Unit 15의 2번째 단어부터 20번째 단어까지 (m2-282 ~ m2-300, 총 19개)
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

# 19개 단어 목록 및 풍성한 씬 정의 (m2-282 ~ m2-300)
WORDS = [
    {
        "id": "m2-282",
        "word": "shrug",
        "meaning": "어깨를 으쓱하다",
        "scene": "classroom with desks and books, cute slender stickman with raised shoulders and hands out in a nonchalant shrug, friend looking on with question mark, wall clock and bookshelf in background"
    },
    {
        "id": "m2-283",
        "word": "sniff",
        "meaning": "냄새 맡다",
        "scene": "cozy bakery kitchen with counter shelves of warm bread and croissants, cute slender stickman with closed eyes gently sniffing delicious steam, baker friend beside, oven and teacup"
    },
    {
        "id": "m2-284",
        "word": "scream",
        "meaning": "날카롭게 소리치다",
        "scene": "amusement park roller coaster drop, cute slender stickman riders with arms raised high shouting thrilling scream with open mouths, flags and ferris wheel backdrop"
    },
    {
        "id": "m2-285",
        "word": "rid",
        "meaning": "제거하다",
        "scene": "tidy garden porch deck, cute slender stickman diligently sweeping dust and fallen leaves into a dustpan with broom to rid the porch of mess, potted flower plants and bench"
    },
    {
        "id": "m2-286",
        "word": "surround",
        "meaning": "둘러싸다",
        "scene": "park grassy lawn, four friendly cute slender stickmen holding hands forming a complete protective circle surrounding a cute little kitten in the center, park bench and tree"
    },
    {
        "id": "m2-287",
        "word": "cleave",
        "meaning": "쪼개다, 찢다",
        "scene": "rustic wood cabin yard, cute slender stickman swinging a sturdy axe cleanly splitting a round wooden log in two on chopping block, stack of logs and pine trees"
    },
    {
        "id": "m2-288",
        "word": "carve",
        "meaning": "새기다, 조각하다",
        "scene": "carpentry workshop, cute slender stickman using chisel and mallet carefully carving an intricate little bird sculpture from wood block on workbench, tool rack on wall"
    },
    {
        "id": "m2-289",
        "word": "except",
        "meaning": "제외하다",
        "scene": "market fruit stall counter, four round apples in a basket with one single pointed star fruit singled out as the exception, cute slender stickman pointing at it with basket beside"
    },
    {
        "id": "m2-290",
        "word": "invent",
        "meaning": "발명하다",
        "scene": "whimsical workshop laboratory, cute slender stickman inventor assembling an intricate gadget of cogs and levers with glowing lightbulb idea above, blueprint scrolls on shelf"
    },
    {
        "id": "m2-291",
        "word": "search",
        "meaning": "찾다",
        "scene": "study room interior, cute slender stickman detective on knees examining footprints on floor through a large magnifying glass, assistant holding lantern, clue board on wall"
    },
    {
        "id": "m2-292",
        "word": "abuse",
        "meaning": "남용하다, 학대하다",
        "scene": "park walkway, compassionate cute slender stickman stepping forward with open hand held up firmly to stop mistreatment of a stray puppy, peaceful trees and path"
    },
    {
        "id": "m2-293",
        "word": "owe",
        "meaning": "힘입다, 빚이 있다",
        "scene": "cozy cafe counter, cute slender stickman politely bowing and handing a shiny coin to a smiling friend acknowledging a debt, mugs on small table"
    },
    {
        "id": "m2-294",
        "word": "bless",
        "meaning": "축복하다",
        "scene": "warm room with arched window, wise elder stickman gently resting a blessing hand on the head of a kneeling young stickman, candlelight and books"
    },
    {
        "id": "m2-295",
        "word": "graduate",
        "meaning": "졸업하다",
        "scene": "commencement hall stage, proud cute slender stickman in cap and gown tossing mortarboard cap into air holding tied diploma scroll, clapping friends in background"
    },
    {
        "id": "m2-296",
        "word": "replace",
        "meaning": "~을 대신하다, 교체하다",
        "scene": "living room with chair, cute slender stickman standing on sturdy stool unscrewing an old lightbulb to replace with a fresh bright bulb, friend holding box below"
    },
    {
        "id": "m2-297",
        "word": "collect",
        "meaning": "모으다, 수집하다",
        "scene": "hobby study room, cute slender stickman hobbyist using tweezers to carefully place rare postage stamps into an open collector album, display cabinet with treasures"
    },
    {
        "id": "m2-298",
        "word": "upset",
        "meaning": "뒤엎다, 당황하게 하다",
        "scene": "office desk, cute slender stickman accidentally knocking over a mug of tea flustered with hands on cheeks as tea spills across desk and papers, scattered pencils"
    },
    {
        "id": "m2-299",
        "word": "arrest",
        "meaning": "체포하다",
        "scene": "city street sidewalk, cute slender stickman police officer placing handcuffs on captured bandit, police car and streetlamp in background"
    },
    {
        "id": "m2-300",
        "word": "prove",
        "meaning": "증명하다",
        "scene": "mathematics classroom, cute slender stickman professor chalk in hand triumphantly finishing geometric chalkboard proof writing Q.E.D., attentive students at desks"
    }
]

def update_word_images_ts():
    """wordImages.ts에 19개 단어 매핑이 모두 있는지 확인하고 없으면 등록"""
    if not os.path.exists(WORD_IMAGES_TS):
        return
    with open(WORD_IMAGES_TS, "r", encoding="utf-8") as f:
        content = f.read()

    new_lines = []
    for item in WORDS:
        w = item["word"]
        wid = item["id"]
        if f'"{w}": require(' not in content and f'{w}: require(' not in content:
            new_lines.append(f'  "{w}": require("../../assets/words/{w}.png"),')
        if f'"{wid}": require(' not in content:
            new_lines.append(f'  "{wid}": require("../../assets/words/{w}.png"),')

    if not new_lines:
        return

    target = "};\n"
    if target in content:
        idx = content.rfind(target)
        updated = content[:idx] + "\n  // 중학교 2학년 15Unit 선형그래픽 매핑\n" + "\n".join(new_lines) + "\n" + content[idx:]
        with open(WORD_IMAGES_TS, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"wordImages.ts에 {len(new_lines)}개 항목 매핑 등록 완료!")

def generate_unit15_linear():
    print(f"==================================================")
    print(f"중2 유닛 15 '선형그래픽' 19개 단어 일괄 생성 시작 (m2-282 ~ m2-300)")
    print(f"규격: 1024x1024, 0.05mm 초극세선, 배경 #f5f6f8, 선색 #030203, 후처리 없음")
    print(f"==================================================")

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
            f"cute slender doodle stickman stick figure characters with small round bald circle heads and tiny smiling dot faces, "
            f"{scene}, "
            f"abundant rich background details, furniture, wall decor, floor line, ambient props, "
            f"strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, empty background"
        )

        negative_prompt = (
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
            "seed": 500 + idx * 13
        }

        # 최대 3회 재시도
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

                # 순수 원본 1024x1024 저장
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

    # wordImages.ts 매핑 점검 및 등록
    update_word_images_ts()

    print("\n==================================================")
    print("중2 유닛 15 선형그래픽 19종 생성 작업 완료!")

if __name__ == "__main__":
    generate_unit15_linear()
