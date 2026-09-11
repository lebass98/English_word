#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 중학교 1학년 Unit 4 단어 20종 일괄 생성 스크립트
- 대상: Unit 4 (m1-61 ~ m1-80, 총 20개 전원)
- 단어 목록:
  61. almost (거의)
  62. hardly (거의 ~않는)
  63. refuse (거절하다)
  64. beggar (거지)
  65. tough (거친, 힘든)
  66. bubble (거품)
  67. trouble (걱정, 문제)
  68. anxious (걱정되는)
  69. worry (걱정하다)
  70. health (건강)
  71. hay (건초)
  72. hang (걸다)
  73. besides (게다가)
  74. sample (견본)
  75. effect (결과, 영향, 효과)
  76. absent (결석한)
  77. wedding (결혼, 결혼식)
  78. marry (결혼하다)
  79. warn (경고하다)
  80. stadium (경기장)

- 스킬 표준:
  1. 초기 선 굵기: 0.05mm 초극세 바늘선 (thinnest possible needle-thin hairline ink stroke)
  2. 해상도: 1024x1024 네이티브 출력
  3. 조형 규칙: 노넥(No-Neck) 캐릭터 (동그란 머리가 몸통에 바로 붙음, 목 없음)
  4. 배경 색상코드: #f5f6f8 (소프트 라이트그레이 캔버스)
  5. 선 색상코드: #030203 (딥 차콜 블랙 잉크)
  6. 풍성한 씬: 인물 상호작용, 가구, 배경 오브젝트, 디테일 완비
  7. 영문 전용 프롬프트 및 한글 배제 네거티브 프롬프트
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

WORDS = [
    {
        "id": "m1-61",
        "word": "almost",
        "meaning": "거의",
        "scene": "running track sprint race finish line, cute slender stickman runner stretching hands forward just an inch almost touching the finish line tape, cheering spectators in grandstand, stopwatches and stadium flags"
    },
    {
        "id": "m1-62",
        "word": "hardly",
        "meaning": "거의 ~않는",
        "scene": "dark foggy quiet room with a tiny candle flame, cute slender stickman squinting closely trying to read an open book, can hardly see the small printed words, vintage coat rack and window curtain"
    },
    {
        "id": "m1-63",
        "word": "refuse",
        "meaning": "거절하다",
        "scene": "bakery cafe counter, friendly baker offering a giant chocolate iced donut on a tray, cute slender stickman smiling politely with one hand raised palm forward gesturing polite refusal, pastry glass display case and menu board"
    },
    {
        "id": "m1-64",
        "word": "beggar",
        "meaning": "거지",
        "scene": "historic cobblestone town plaza, gentle humble cute slender stickman sitting on stone step with a small coin bowl, kind passerby stickman dropping a shining gold coin, antique street lamp and townhouse brick wall"
    },
    {
        "id": "m1-65",
        "word": "tough",
        "meaning": "거친, 힘든",
        "scene": "outdoor rugged mountain fitness obstacle course, cute slender stickman determinedly climbing up a steep muddy rock wall holding a thick knotted rope, tough physical challenge, tree line and summit flag"
    },
    {
        "id": "m1-66",
        "word": "bubble",
        "meaning": "거품",
        "scene": "sunny outdoor park grassy lawn, happy cute slender stickman blowing giant shimmering soap bubbles through a plastic ring wand, floating round bubbles drifting into sky, picnic blanket and trees"
    },
    {
        "id": "m1-67",
        "word": "trouble",
        "meaning": "걱정, 문제",
        "scene": "garage mechanic workshop, cute slender stickman looking down scratching head in trouble beside a smoking car engine with open hood, spilled toolbox with wrench on floor, tire rack and workbench"
    },
    {
        "id": "m1-68",
        "word": "anxious",
        "meaning": "걱정되는",
        "scene": "hospital waiting room corridor, cute slender stickman sitting on bench nervously fidgeting with clock on wall ticking, pacing friend beside water dispenser, exam room door with red light"
    },
    {
        "id": "m1-69",
        "word": "worry",
        "meaning": "걱정하다",
        "scene": "cozy study room desk late at night, cute slender stickman sitting with chin resting in hands worrying about upcoming big exam paper, stacked textbooks, warm desk lamp and starry night window"
    },
    {
        "id": "m1-70",
        "word": "health",
        "meaning": "건강",
        "scene": "bright wellness fitness park, energetic healthy cute slender stickman jogging happily with water bottle in hand, nearby friend stretching on yoga mat under tree, fresh fruit basket on bench"
    },
    {
        "id": "m1-71",
        "word": "hay",
        "meaning": "건초",
        "scene": "sunny countryside rustic barnyard, cute slender stickman farmer pitching dry golden hay stalks with a wooden pitchfork onto a large hay bale stack, peaceful horse peeking from stable door, tractor"
    },
    {
        "id": "m1-72",
        "word": "hang",
        "meaning": "걸다",
        "scene": "cozy home art wall hallway, cute slender stickman standing on step stool carefully hanging a framed landscape painting straight onto wall hook, friend below pointing to check alignment, hammer and picture wire"
    },
    {
        "id": "m1-73",
        "word": "besides",
        "meaning": "게다가",
        "scene": "grocery store checkout counter, cute slender stickman loading fresh vegetables into bag while cashier also hands an extra free gift cookie saying besides this bonus, shopping cart and receipt register"
    },
    {
        "id": "m1-74",
        "word": "sample",
        "meaning": "견본",
        "scene": "lively supermarket food tasting aisle, smiling vendor in apron offering a toothpick sample cube of artisanal cheese on a round tray, cute slender stickman customer taking a small sample bite with delight, food shelves"
    },
    {
        "id": "m1-75",
        "word": "effect",
        "meaning": "결과, 영향, 효과",
        "scene": "science chemistry laboratory, cute slender stickman researcher pouring one drop from test tube into flask causing an instant magical sparkling foaming reaction effect rising with soft smoke, laboratory glassware and whiteboard notes"
    },
    {
        "id": "m1-76",
        "word": "absent",
        "meaning": "결석한",
        "scene": "sunny school classroom during morning attendance, teacher stickman holding attendance clipboard pointing to one prominent empty vacant wooden desk and chair, attentive students looking around, chalkboard and clock"
    },
    {
        "id": "m1-77",
        "word": "wedding",
        "meaning": "결혼, 결혼식",
        "scene": "romantic flower arch garden wedding ceremony, cute slender stickman bride and groom couple holding hands happily exchanging wedding rings under floral trellis, cheering guests throwing flower petals, aisle chairs and ribbon decor"
    },
    {
        "id": "m1-78",
        "word": "marry",
        "meaning": "결혼하다",
        "scene": "scenic sunset ocean cliff gazebo, cute slender stickman groom kneeling down on one knee holding open velvet ring box asking partner to marry him, joyful partner covering smile with hands, sunset waves and lantern"
    },
    {
        "id": "m1-79",
        "word": "warn",
        "meaning": "경고하다",
        "scene": "rainy city street construction site sidewalk, cute slender stickman safety guard holding a yellow handheld caution sign warning pedestrians around an open puddle trench with striped cones, barrier tape and excavator"
    },
    {
        "id": "m1-80",
        "word": "stadium",
        "meaning": "경기장",
        "scene": "grand sports stadium arena, huge oval stadium filled with cheering crowd tiers, cute slender stickman soccer player kicking ball towards goal net under towering bright floodlights, electronic scoreboard"
    }
]

def generate_unit4_linear(start_index=1, skip_existing=False):
    print("==================================================")
    print("중1 유닛 4 '선형그래픽' 20개 단어 생성 시작 (m1-61 ~ m1-80)")
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
                success = True
                break
            except Exception as e:
                print(f"[{word}] 시도 {attempt} 실패: {e}", flush=True)
                time.sleep(3)

        if not success:
            print(f"[오류] '{word}' 생성 실패!", flush=True)

    print("\n==================================================", flush=True)
    print("중1 유닛 4 선형그래픽 생성 작업 완료!", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="중1 유닛 4 선형그래픽 단어 이미지 생성")
    parser.add_argument("--start-index", type=int, default=1, help="시작할 단어 번호 (1-indexed, 기본값: 1)")
    parser.add_argument("--skip-existing", action="store_true", help="이미 존재하는 파일 건너뛰기")
    args = parser.parse_args()

    generate_unit4_linear(start_index=args.start_index, skip_existing=args.skip_existing)
