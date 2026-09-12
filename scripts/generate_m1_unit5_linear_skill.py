#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 중학교 1학년 Unit 5 단어 20종 일괄 생성 스크립트
- 대상: Unit 5 (m1-81 ~ m1-100, 총 20개 전원)
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
        "id": "m1-81",
        "word": "course",
        "meaning": "경로",
        "scene": "scenic mountain hiking trail fork, cute slender stickman hiker with backpack standing at trail signpost examining a detailed winding trail route map carved on wooden board, mountain peaks and pine trees in background"
    },
    {
        "id": "m1-82",
        "word": "contest",
        "meaning": "경연대회",
        "scene": "brightly lit school auditorium stage contest, cute slender stickman speaking into a microphone standing at podium, judges seated at long table with scoring clipboards, stage curtains and banners"
    },
    {
        "id": "m1-83",
        "word": "competition",
        "meaning": "경쟁",
        "scene": "outdoor sports festival field, two cute slender stickman runners fiercely sprinting side by side neck and neck along parallel lanes toward finish ribbon, cheering crowd in stands and stadium flags"
    },
    {
        "id": "m1-84",
        "word": "race",
        "meaning": "경주, 인종",
        "scene": "grand racing track starting grid, cute slender stickman drivers in sleek mini pedal go-karts revving engines under start lights arch, checkered flags, pit stop crew with stopwatches"
    },
    {
        "id": "m1-85",
        "word": "experience",
        "meaning": "경험",
        "scene": "cozy library study room desk, cute slender stickman proudly placing a new colorful travel badge onto a dense travel scrapbook filled with maps and sketches, globe on desk and vintage camera on shelf"
    },
    {
        "id": "m1-86",
        "word": "stair",
        "meaning": "계단",
        "scene": "grand architectural indoor staircase hall, cute slender stickman walking steadily up graceful spiral wooden stairs holding elegant handrail, tall arched windows and wall lamps"
    },
    {
        "id": "m1-87",
        "word": "step",
        "meaning": "계단, 걸음",
        "scene": "sunny garden stone pathway, cute slender stickman taking a careful joyful walking step across round stepping stones set in lawn, flowers along pathway and stepping stone trail"
    },
    {
        "id": "m1-88",
        "word": "trick",
        "meaning": "계략, 마술",
        "scene": "theater magic show stage, cute slender stickman magician in top hat waving a magic wand causing a fluffy rabbit to pop out of an empty top hat with sparkling star dust lines, spotlight and velvet curtains"
    },
    {
        "id": "m1-89",
        "word": "bill",
        "meaning": "계산서, 지폐",
        "scene": "cozy restaurant dining table, smiling waiter stickman placing a leather bill folder with receipt paper on table, cute slender stickman customer taking out wallet to pay after nice dinner, table lamp and cups"
    },
    {
        "id": "m1-90",
        "word": "continue",
        "meaning": "계속하다",
        "scene": "quiet study room desk late at night, cute slender stickman determinedly continuing to write in notebook despite a large wall clock showing late hour, steaming mug of tea and stack of finished pages"
    },
    {
        "id": "m1-91",
        "word": "project",
        "meaning": "계획, 프로젝트",
        "scene": "modern creative design studio office, two cute slender stickman teammates collaborating in front of a giant wall whiteboard covered in flowchart diagrams, sticky notes, and architectural building sketches"
    },
    {
        "id": "m1-92",
        "word": "noble",
        "meaning": "고귀한",
        "scene": "grand medieval palace throne room, dignified cute slender stickman king wearing an ornate crown and royal mantle sitting regally on an elevated throne, tapestries and ceremonial guard statues"
    },
    {
        "id": "m1-93",
        "word": "meat",
        "meaning": "고기",
        "scene": "traditional artisan butcher shop counter, smiling butcher stickman in apron carving prime fresh steaks on a thick wooden butcher block, hanging hams and cured sausages on rack behind, scale on counter"
    },
    {
        "id": "m1-94",
        "word": "ancient",
        "meaning": "고대의",
        "scene": "historic archaeological excavation site in desert, cute slender stickman archaeologist with brush carefully uncovering an ancient weathered stone obelisk with classical carvings, stone ruins and excavation tents"
    },
    {
        "id": "m1-95",
        "word": "lonely",
        "meaning": "고독한",
        "scene": "wide peaceful evening park lawn, a solitary cute slender stickman sitting quietly in thought on a long wooden park bench under a grand solitary willow tree, falling autumn leaves and distant streetlight"
    },
    {
        "id": "m1-96",
        "word": "rein",
        "meaning": "고삐",
        "scene": "sunny countryside equestrian paddock, cute slender stickman rider holding the leather bridle reins gently while standing beside a friendly tall horse, wooden fence and stable barn in background"
    },
    {
        "id": "m1-97",
        "word": "struggle",
        "meaning": "고생하다, 분투하다",
        "scene": "steep rocky mountain cliff face, cute slender stickman rock climber straining muscles pulling up onto a narrow stone ledge holding safety rope with grit and effort, mountain wind and soaring eagles"
    },
    {
        "id": "m1-98",
        "word": "expressway",
        "meaning": "고속도로",
        "scene": "modern multi-lane elevated highway expressway overpass, cute slender stickman driving a neat compact car along smooth asphalt highway, overhead directional gantry road signs, guardrails and skyline"
    },
    {
        "id": "m1-99",
        "word": "suffer",
        "meaning": "고통받다",
        "scene": "warm bedroom bedside, sick cute slender stickman lying in bed with a thermometer in mouth and ice pack on forehead suffering with a fever, caring family stickman offering hot soup bowl and medicine"
    },
    {
        "id": "m1-100",
        "word": "hometown",
        "meaning": "고향",
        "scene": "nostalgic hilltop overlook overlooking a peaceful picturesque seaside village, cute slender stickman with suitcase looking down affectionately at the familiar cozy roofs, harbor boats, and old clock tower of home"
    }
]

def generate_unit5_linear(start_index=1, skip_existing=False):
    print("==================================================")
    print("중1 유닛 5 '선형그래픽' 20개 단어 생성 시작 (m1-81 ~ m1-100)")
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
    print("중1 유닛 5 선형그래픽 생성 작업 완료!", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="중1 유닛 5 선형그래픽 단어 이미지 생성")
    parser.add_argument("--start-index", type=int, default=1, help="시작할 단어 번호 (1-indexed, 기본값: 1)")
    parser.add_argument("--skip-existing", action="store_true", help="이미 존재하는 파일 건너뛰기")
    args = parser.parse_args()

    generate_unit5_linear(start_index=args.start_index, skip_existing=args.skip_existing)
