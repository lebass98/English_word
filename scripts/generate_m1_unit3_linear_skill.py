#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 중학교 1학년 Unit 3 단어 20종 일괄 생성 스크립트
- 대상: Unit 3 (m1-41 ~ m1-60, 총 20개 전원)
- 단어:
  41. decrease (감소)
  42. prison (감옥)
  43. potato (감자)
  44. hide (감추다)
  45. suddenly (갑자기)
  46. deck (갑판)
  47. price (값)
  48. expensive (값비싼)
  49. cheap (값싼)
  50. robber (강도)
  51. equal (같은)
  52. unlike (같지 않은)
  53. frog (개구리)
  54. private (개인의)
  55. upside down (거꾸로)
  56. giant (거대한)
  57. huge (거대한)
  58. deal (거래하다)
  59. living room (거실)
  60. nearly (거의)

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
        "id": "m1-41",
        "word": "decrease",
        "meaning": "감소",
        "scene": "office presentation room, cute slender stickman speaker pointing to a gentle downward decreasing slope graph on a large whiteboard, colleagues seated at conference table attentively analyzing the chart, laptop and coffee mugs"
    },
    {
        "id": "m1-42",
        "word": "prison",
        "meaning": "감옥",
        "scene": "historic stone castle fortress prison hallway, whimsical cute slender stickman inmate smiling behind vertical iron jail bars, friendly guard stickman walking corridor with big key ring, stone walls and hanging torch"
    },
    {
        "id": "m1-43",
        "word": "potato",
        "meaning": "감자",
        "scene": "sunny autumn farmland garden patch, happy cute slender stickman farmer harvesting round fresh potatoes from dirt soil with garden fork into a woven basket, friend tying a potato sack, wheelbarrow and scarecrow"
    },
    {
        "id": "m1-44",
        "word": "hide",
        "meaning": "감추다",
        "scene": "cozy attic playroom hide and seek, cute slender stickman peeking cheerfully while hiding inside an antique wooden wardrobe trunk, friend across the room counting with hands covering eyes, stacked books and vintage lantern"
    },
    {
        "id": "m1-45",
        "word": "suddenly",
        "meaning": "갑자기",
        "scene": "surprise birthday celebration living room, door swinging open suddenly as cute slender stickman friends pop colorful party confetti poppers shouting surprise, hero stickman with hands raised in sudden delight, cake and balloons"
    },
    {
        "id": "m1-46",
        "word": "deck",
        "meaning": "갑판",
        "scene": "wooden ship deck of a sailing cruise ship at sea, cute slender stickman passengers leaning on safety railing pointing at playful dolphins jumping in ocean waves, captain at ship steering wheel, mast and lifebuoy ring"
    },
    {
        "id": "m1-47",
        "word": "price",
        "meaning": "값, 가격",
        "scene": "cozy flea market antique stall, cute slender stickman customer holding and inspecting a dangling price tag on a vintage toy bear with coin purse in hand, friendly merchant smiling behind counter awning"
    },
    {
        "id": "m1-48",
        "word": "expensive",
        "meaning": "값비싼",
        "scene": "luxury jewelry boutique glass showcase, cute slender stickman couple admiring a sparkling diamond necklace resting on velvet pillow with a high price tag, elegant clerk in bow tie, chandelier and mirror"
    },
    {
        "id": "m1-49",
        "word": "cheap",
        "meaning": "값싼",
        "scene": "bustling farmers market fruit stand, banner saying 'SPECIAL $1 CHEAP SALE', cute slender stickman customer happily handing a single dollar coin for a basket of fresh apples, smiling vendor, wooden crates"
    },
    {
        "id": "m1-50",
        "word": "robber",
        "meaning": "강도",
        "scene": "bank hallway comic scene, funny cute slender stickman robber wearing eye mask and striped shirt carrying a sack tiptoeing away, running into an alert security guard with flashlight, bank vault door in background"
    },
    {
        "id": "m1-51",
        "word": "equal",
        "meaning": "같은",
        "scene": "science math classroom, cute slender stickman teacher demonstrating a two-pan balance scale perfectly balanced in horizontal equilibrium with identical wooden blocks on both sides, chalk drawing of equal sign on board"
    },
    {
        "id": "m1-52",
        "word": "unlike",
        "meaning": "같지 않은",
        "scene": "art design exhibition gallery, two cute slender stickman visitors comparing a wall of three identical circle paintings beside one totally unique unlike glowing star sculpture, bench and gallery spotlight"
    },
    {
        "id": "m1-53",
        "word": "frog",
        "meaning": "개구리",
        "scene": "peaceful botanical pond, adorable chubby frog sitting proudly on a wide green water lily pad catching a water ripple, cute slender stickman child crouching by grassy bank observing with gentle curiosity, cattails and dragonfly"
    },
    {
        "id": "m1-54",
        "word": "private",
        "meaning": "개인의",
        "scene": "secret greenhouse garden wooden gate, cute slender stickman unlocking small gate marked with 'PRIVATE GARDEN' wooden plaque to enter peaceful personal greenhouse room filled with potted plants and reading desk"
    },
    {
        "id": "m1-55",
        "word": "upside down",
        "meaning": "거꾸로",
        "scene": "outdoor playground monkey bars jungle gym, cute slender stickman hanging completely upside down by legs waving cheerfully with big smile, friend standing upright below laughing and clapping, playground slide"
    },
    {
        "id": "m1-56",
        "word": "giant",
        "meaning": "거대한",
        "scene": "fantasy fairy tale village square, huge friendly gentle giant stickman standing with head up in fluffy clouds, tiny cheerful village cute slender stickmen looking up waving friendly hands from cobblestone path and cottage rooftops"
    },
    {
        "id": "m1-57",
        "word": "huge",
        "meaning": "거대한",
        "scene": "natural history museum exhibition hall, cute slender stickman museum visitors looking in awe up at a colossal huge dinosaur skeleton fossil filling the high hall, docent explaining with pointer, museum pillars"
    },
    {
        "id": "m1-58",
        "word": "deal",
        "meaning": "거래하다",
        "scene": "modern business office meeting room, two professional cute slender stickman partners shaking hands warmly sealing a successful business deal contract on conference table, signed document folders and coffee cups"
    },
    {
        "id": "m1-59",
        "word": "living room",
        "meaning": "거실",
        "scene": "cozy modern family living room, cute slender stickman relaxing reading a book on a comfortable sectional sofa, young stickman playing with toy blocks on the rug, floor lamp, potted ficus, framed wall pictures"
    },
    {
        "id": "m1-60",
        "word": "nearly",
        "meaning": "거의",
        "scene": "afternoon puzzle table, large 1000-piece jigsaw puzzle nearly finished with only one final missing piece held in cute slender stickman's fingers ready to place, friends eagerly leaning in watching the completion"
    }
]

def generate_unit3_linear():
    print("==================================================")
    print("중1 유닛 3 '선형그래픽' 20개 단어 일괄 생성 시작 (m1-41 ~ m1-60)")
    print("규격: 1024x1024, 0.05mm 초극세선, 노넥(No-Neck), 배경 #f5f6f8, 선색 #030203, 후처리 없음")
    print("==================================================")

    os.makedirs(ASSETS_DIR, exist_ok=True)
    total = len(WORDS)

    for idx, item in enumerate(WORDS, 1):
        word = item["word"]
        word_id = item["id"]
        meaning = item["meaning"]
        scene = item["scene"]
        file_name = word.replace(" ", "-")
        out_path = os.path.join(ASSETS_DIR, f"{file_name}.png")

        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            print(f"[{idx}/{total}] '{word}' ({word_id}) 이미 존재하여 건너뜁니다. -> {out_path}", flush=True)
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
            "seed": 800 + idx * 29
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
    print("중1 유닛 3 선형그래픽 20종 생성 작업 완료!", flush=True)

if __name__ == "__main__":
    generate_unit3_linear()
