#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 고등학교 1학년 Unit 1 단어 20종 일괄 생성 스크립트
- 대상: High 1 Unit 1 (h1-1 ~ h1-20, 총 20개)
- 단어 목록:
  1. present (선물, 발표하다)
  2. compare (비교하다)
  3. tune (조율하다, 곡)
  4. trigger (촉발시키다, 방아쇠)
  5. obvious (분명한, 확실한)
  6. return (반납하다, 귀환) [기존 존재 시 스킵 가능]
  7. particle (입자, 조각)
  8. carve (조각하다, 새기다) [기존 존재 시 스킵 가능]
  9. mechanic (정비사, 수리공)
  10. convince (설득하다, 납득시키다)
  11. rely (의지하다, 신뢰하다)
  12. nature (자연, 본질)
  13. voyage (항해, 여행) [기존 존재 시 스킵 가능]
  14. military (군사적인, 군대)
  15. replace (교체하다, 바꾸다) [기존 존재 시 스킵 가능]
  16. inquire (질문하다, 알아보다)
  17. resource (자원, 재원)
  18. demand (요구하다, 수요)
  19. humor (유머, 해학)
  20. obstacle (장애물, 방해물)

- 스킬 표준:
  1. 1024x1024 네이티브 해상도
  2. 0.05mm 초극세 바늘선 (thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke)
  3. 목 없는(No-Neck) 머리-몸통 직결 원형 머리 스틱맨 캐릭터
  4. 뉴모피즘 캔버스 테마 #f5f6f8 배경
  5. 선 색상 #030203 딥 차콜 블랙
  6. 풍성한 배경 씬(바닥선, 가구, 소품 등 내러티브 묘사)
  7. 씬 내 텍스트는 영문(English)만 사용하며 한글 텍스트 전면 배제
  8. 후처리 효과 없는 순수 렌더링 원본 보존
"""

import os
import sys
import json
import time
import base64
import urllib.request
import argparse
import subprocess

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
SYNC_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "sync_word_images.py")
STATUS_LOG = os.path.join(SCRIPT_DIR, "h1_unit1_status.json")

WORDS = [
    {
        "id": "h1-1",
        "word": "present",
        "meaning": "선물, 발표하다",
        "scene": "warm birthday living room party, cute slender stickman proudly handing a beautifully wrapped gift box with a big satin ribbon to an excited stickman friend, colorful party streamers and balloons on wall, wooden table with cake"
    },
    {
        "id": "h1-2",
        "word": "compare",
        "meaning": "비교하다",
        "scene": "bright grocery fruit market stall, thoughtful cute slender stickman holding a large round fresh apple in left hand and an orange in right hand, carefully comparing their size and weight, wooden market crates and price signs"
    },
    {
        "id": "h1-3",
        "word": "tune",
        "meaning": "조율하다, 곡",
        "scene": "classical music practice studio, cute slender stickman musician adjusting guitar pegs with a silver tuning fork ringing gently near ear, acoustic guitar on knee, music stand with sheet notes, vintage floor lamp"
    },
    {
        "id": "h1-4",
        "word": "trigger",
        "meaning": "촉발시키다, 작동시키다",
        "scene": "creative game room, cute slender stickman gently tapping the first domino brick triggering a long elaborate winding chain reaction of falling dominoes and marble ramps across wooden floor, wall clock and bookshelf"
    },
    {
        "id": "h1-5",
        "word": "obvious",
        "meaning": "분명한, 확실한",
        "scene": "bright sunny meadow crossroad, smiling cute slender stickman looking at a giant bold wooden signpost with an unmistakable large arrow pointing straight to town, totally clear and obvious direction, fence and flowers"
    },
    {
        "id": "h1-6",
        "word": "return",
        "meaning": "반납하다, 되돌아오다",
        "scene": "cozy library circulation counter, polite cute slender stickman returning a stack of borrowed hardcover books to the librarian stickman behind desk, library shelves full of novels, return book drop box and desk lamp"
    },
    {
        "id": "h1-7",
        "word": "particle",
        "meaning": "입자, 조각",
        "scene": "quiet sunny study attic, cozy window beam of warm sunlight shining through dusty air, cute slender stickman sitting on a wooden bench curiously watching tiny glowing dust particles floating gently in sunbeam, antique armchair"
    },
    {
        "id": "h1-8",
        "word": "carve",
        "meaning": "조각하다, 새기다",
        "scene": "woodworking workshop bench, skilled cute slender stickman artisan wearing an apron carefully carving intricate floral patterns into a block of wood using a sharp chisel and wooden mallet, wood shavings on table, tool rack on wall"
    },
    {
        "id": "h1-9",
        "word": "mechanic",
        "meaning": "정비사, 수리공",
        "scene": "auto repair garage, cute slender stickman mechanic in work overalls holding a silver wrench, inspecting car engine under open vehicle hood, rolling tool chest with wrenches, hanging ceiling lamp, tires stacked on floor"
    },
    {
        "id": "h1-10",
        "word": "convince",
        "meaning": "설득하다, 납득시키다",
        "scene": "office conference room whiteboard, persuasive cute slender stickman passionately explaining a brilliant chart diagram to convince an interested colleague stickman who is nodding in agreement, coffee cups and laptops on table"
    },
    {
        "id": "h1-11",
        "word": "rely",
        "meaning": "의지하다, 신뢰하다",
        "scene": "outdoor mountain hiking trail, cute slender stickman hiker with ankle sprain resting arm across shoulder of a trusted loyal stickman friend for steady support, walking sticks, scenic mountain ridge line and pine trees"
    },
    {
        "id": "h1-12",
        "word": "nature",
        "meaning": "자연, 본질",
        "scene": "peaceful lush green forest clearing, happy cute slender stickman walking along winding natural stream, bird resting on branch, wild deer drinking water, tall trees, mushrooms, butterflies and blooming wild plants"
    },
    {
        "id": "h1-13",
        "word": "voyage",
        "meaning": "항해, 여행",
        "scene": "majestic wooden sailing ship deck on ocean waves, brave cute slender stickman captain looking through a long brass telescope toward distant horizon, billowing ship sails, rigging ropes, seagulls soaring in breezy sky"
    },
    {
        "id": "h1-14",
        "word": "military",
        "meaning": "군사적인, 군대",
        "scene": "historic military watchtower base, alert cute slender stickman soldier in neat uniform standing at attention beside fortress stone wall, observation binoculars, fluttering national flag on pole, distant mountain hills"
    },
    {
        "id": "h1-15",
        "word": "replace",
        "meaning": "교체하다, 바꾸다",
        "scene": "living room ladder, cute slender stickman carefully unscrewing an old dim burnt light bulb from ceiling fixture to replace it with a new glowing efficient round bulb, tool box on floor, sofa and floor carpet"
    },
    {
        "id": "h1-16",
        "word": "inquire",
        "meaning": "질문하다, 알아보다",
        "scene": "train station customer service information booth, curious cute slender stickman traveler with suitcase politely inquiring about platform directions to clerk behind round desk, station departure schedule board on wall"
    },
    {
        "id": "h1-17",
        "word": "resource",
        "meaning": "자원, 재원",
        "scene": "sunny eco-energy research station, cute slender stickman scientist inspecting high-tech solar panels and a clean spinning wind turbine harnessing natural renewable resources, battery storage bank, grassy rolling hills"
    },
    {
        "id": "h1-18",
        "word": "demand",
        "meaning": "요구하다, 수요",
        "scene": "busy artisan bakery shop door, long line of eager stickman customers waiting outside to buy fresh morning baguettes, high product demand, bakery window display full of warm breads and awning"
    },
    {
        "id": "h1-19",
        "word": "humor",
        "meaning": "유머, 해학",
        "scene": "lively community comedy stage, witty cute slender stickman stand-up comedian holding a vintage microphone telling funny jokes, audience of cute stickmen in front rows bursting into cheerful laughter, stage spotlight"
    },
    {
        "id": "h1-20",
        "word": "obstacle",
        "meaning": "장애물, 방해물",
        "scene": "running athletics track hurdle event, agile cute slender stickman athlete leaping gracefully over a tall hurdle obstacle bar, running lane lines on ground, cheer banners and stadium spectator grandstand in background"
    }
]

def save_status(status_dict):
    try:
        with open(STATUS_LOG, "w", encoding="utf-8") as f:
            json.dump(status_dict, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def generate_h1_unit1(start_index=1, skip_existing=False):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    total = len(WORDS)

    status_data = {
        "unit": "High 1 Unit 1",
        "total": total,
        "current_index": start_index,
        "current_word": "",
        "items": []
    }

    print("==================================================", flush=True)
    print("고등학교 1학년 Unit 1 '선형그래픽' 20개 단어 생성 시작 (h1-1 ~ h1-20)", flush=True)
    print(f"시작 인덱스: {start_index}, 기존 파일 스킵: {skip_existing}", flush=True)
    print("규격: 1024x1024, 0.05mm 초극세선, 노넥(No-Neck), 배경 #f5f6f8, 선색 #030203, 순수 렌더링", flush=True)
    print("==================================================", flush=True)

    for idx, item in enumerate(WORDS, 1):
        word = item["word"]
        word_id = item["id"]
        meaning = item["meaning"]
        scene = item["scene"]
        file_name = word.replace(" ", "-")
        out_path = os.path.join(ASSETS_DIR, f"{file_name}.png")

        if idx < start_index:
            continue

        status_data["current_index"] = idx
        status_data["current_word"] = word

        if skip_existing and os.path.exists(out_path):
            file_size_kb = round(os.path.getsize(out_path) / 1024, 1)
            print(f"[{idx}/{total}] '{word}' ({word_id}: {meaning}) 이미 존재하여 건너뜀 ({file_size_kb} KB)", flush=True)
            status_data["items"].append({
                "index": idx,
                "id": word_id,
                "word": word,
                "status": "SKIP_EXISTS",
                "size_kb": file_size_kb
            })
            save_status(status_data)
            continue

        print(f"\n[{idx}/{total}] '{word}' ({word_id}: {meaning}) 생성 시작...", flush=True)
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
            "seed": 800 + idx * 37
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
                        raise RuntimeError("No image returned from Draw Things API")
                    raw_bytes = base64.b64decode(images[0])

                with open(out_path, "wb") as f:
                    f.write(raw_bytes)

                elapsed = time.time() - t0
                file_size_kb = round(len(raw_bytes) / 1024, 1)
                print(f"[{word}] 생성 완료! ({elapsed:.1f}초, {file_size_kb} KB) -> {out_path}", flush=True)

                status_data["items"].append({
                    "index": idx,
                    "id": word_id,
                    "word": word,
                    "status": "SUCCESS",
                    "elapsed_sec": round(elapsed, 1),
                    "size_kb": file_size_kb
                })
                save_status(status_data)
                success = True
                break
            except Exception as e:
                print(f"[{word}] 시도 {attempt} 실패: {e}", flush=True)
                time.sleep(3)

        if not success:
            print(f"[오류] '{word}' 생성 실패!", flush=True)
            status_data["items"].append({
                "index": idx,
                "id": word_id,
                "word": word,
                "status": "FAILED"
            })
            save_status(status_data)

    print("\n==================================================", flush=True)
    print("단어 이미지 동기화 실행 중 (sync_word_images.py)...", flush=True)
    subprocess.run([sys.executable, SYNC_SCRIPT], check=False)
    print("고등학교 1학년 Unit 1 선형그래픽 일괄 생성 완료!", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="고등학교 1학년 Unit 1 선형그래픽 단어 이미지 생성")
    parser.add_argument("--start-index", type=int, default=1, help="시작 단어 번호 (1~20)")
    parser.add_argument("--skip-existing", action="store_true", help="기존 이미지 파일 건너뛰기")
    args = parser.parse_args()

    generate_h1_unit1(start_index=args.start_index, skip_existing=args.skip_existing)
