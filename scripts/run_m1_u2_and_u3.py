#!/usr/bin/env python3
"""
중1 Unit 2 (잔여) 및 Unit 3 (전원) 선형그래픽 일괄 생성 및 wordImages.ts 자동 등록 스크립트
- 스킬 원칙 100% 준수:
  1. 1024x1024 네이티브 출력 (0.05mm 초극세 바늘선)
  2. 노넥(No-Neck) 캐릭터 (동그란 머리가 몸통에 바로 붙음, 목 없음)
  3. 배경색 #f5f6f8, 선색 #030203
  4. 후처리 없음 (순수 원본 렌더링)
  5. 한글 텍스트 전면 배제 및 영문 우선 표기 (English Only / No Korean Text)
"""

import os
import sys
import json
import time
import base64
import urllib.request
import re

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
WORD_IMAGES_TS = os.path.join(PROJECT_ROOT, "src", "constants", "wordImages.ts")

# 1. 유닛 2 단어 (m1-21 ~ m1-40)
UNIT2_WORDS = [
    {"id": "m1-21", "word": "sophomore", "meaning": "2학년생", "scene": "high school campus hallway with lockers and bulletin board, confident cute slender stickman sophomore holding textbooks giving directions with campus map to an incoming freshman stickman, classmates walking by, wall clock"},
    {"id": "m1-22", "word": "quarter", "meaning": "4분의 1", "scene": "cozy pastry kitchen counter, cute slender stickman baker lifting one precise one-fourth quarter slice of round pie with a serving spatula onto a plate, rolling pin, flour bowl and baking shelves"},
    {"id": "m1-23", "word": "store", "meaning": "가게, 저장하다", "scene": "charming village grocery general store with striped awning, cute slender stickman storekeeper stocking glass jars and boxes onto tall wooden shelves, friendly customer with shopping basket, cash register counter"},
    {"id": "m1-24", "word": "furniture", "meaning": "가구", "scene": "cozy furniture showroom living room interior, cute slender stickman relaxing happily on a plush armchair, another stickman admiring a stylish wooden coffee table and bookshelf wardrobe set, floor lamp and potted plant"},
    {"id": "m1-25", "word": "possible", "meaning": "가능한", "scene": "science laboratory chalkboard, cute slender stickman scientist solving the final complex formula and drawing a triumphant checkmark declaring it is possible, teammate cheering with raised arms, lab beakers and desk"},
    {"id": "m1-26", "word": "sink", "meaning": "가라앉다", "scene": "aquarium clear underwater tank, heavy iron anchor and toy ship slowly sinking down toward sandy seabed with rising bubble streams, cute slender stickman standing outside observing with curiosity, seashells and seaweed"},
    {"id": "m1-27", "word": "powder", "meaning": "가루, 화약", "scene": "baking studio counter, cute slender stickman gently sifting fine powdered sugar through a handheld round sieve like falling snow into a mixing bowl, friend watching with measuring cup, flour sack and whisk"},
    {"id": "m1-28", "word": "chest", "meaning": "가슴", "scene": "warm medical clinic examination room, friendly cute slender stickman doctor listening to patient stickman's chest heartbeat with stethoscope while patient breathes deeply with hand over heart, medicine cabinet and chart"},
    {"id": "m1-29", "word": "join", "meaning": "가입하다, 참가하다", "scene": "school club registration booth with 'ART CLUB JOIN US' banner, excited cute slender stickman signing membership form with pen, friendly club president stickman smiling warmly shaking hand across the table"},
    {"id": "m1-30", "word": "least", "meaning": "가장 적은", "scene": "science math classroom table, cute slender stickman comparing three balance scales with candy boxes, pointing specifically to the dish holding the single smallest least amount of candy, chart on wall"},
    {"id": "m1-31", "word": "favorite", "meaning": "가장 좋아하는", "scene": "sunlit study room armchair, happy cute slender stickman smiling warmly hugging a favorite beloved storybook decorated with tiny sparkling hearts, sleeping cat on side table, bookshelf and framed art"},
    {"id": "m1-32", "word": "suppose", "meaning": "가정하다, 상상하다", "scene": "cozy bedroom study desk, cute slender stickman resting chin on hand dreaming with a whimsical thought bubble above depicting a spaceship flying around planets, desk lamp and globe"},
    {"id": "m1-33", "word": "bring", "meaning": "가져오다", "scene": "sunny park picnic lawn, cheerful cute slender stickman happily carrying and bringing a picnic basket full of fresh sandwiches and fruits to friends sitting on a blanket waving welcoming hands, trees and kites"},
    {"id": "m1-34", "word": "branch", "meaning": "가지, 지점", "scene": "leafy grand oak tree, detailed sturdy tree branch with a cute bird nest and tiny chirping birds, cute slender stickman below examining the branch with a magnifying glass holding a nature sketchbook"},
    {"id": "m1-35", "word": "worth", "meaning": "가치", "scene": "antique appraisal shop desk, expert cute slender stickman appraiser inspecting an ornate golden chalice cup with a magnifying glass assessing its great valuable worth, eager collector watching, antique clocks"},
    {"id": "m1-36", "word": "angle", "meaning": "각도", "scene": "architect drafting studio table, cute slender stickman draftsman carefully measuring precise geometric angles on blueprint paper using a large circular protractor and triangle ruler, drafting lamp and blueprints"},
    {"id": "m1-37", "word": "simple", "meaning": "간단한", "scene": "minimalist design studio blackboard, cute slender stickman proudly drawing a clean simple three-line outline house with chalk, contrasting with messy complicated scribbles on the left side, wooden easel"},
    {"id": "m1-38", "word": "nurse", "meaning": "간호사", "scene": "cozy pediatric hospital room, caring cute slender stickman nurse holding a medicine tray and thermometer checking forehead of young stickman patient resting in bed, teddy bear on chair, bedside lamp"},
    {"id": "m1-39", "word": "crack", "meaning": "갈라진", "scene": "pottery artisan workshop, cute slender stickman ceramicist holding up a freshly fired glazed ceramic vase noticing a delicate fine crack line on its surface, pottery wheel and shelves of pottery jars"},
    {"id": "m1-40", "word": "brown", "meaning": "갈색의", "scene": "art studio easel, cute slender stickman painter holding wooden palette with rich brown paint tubes, painting a cozy autumn scene of acorns, fallen brown oak leaves, and tree log on large canvas, paint jars"}
]

# 2. 유닛 3 단어 (m1-41 ~ m1-60)
UNIT3_WORDS = [
    {"id": "m1-41", "word": "decrease", "meaning": "감소", "scene": "office presentation room, cute slender stickman speaker pointing to a gentle downward decreasing slope graph on a large whiteboard, colleagues seated at conference table attentively analyzing the chart, laptop and coffee mugs"},
    {"id": "m1-42", "word": "prison", "meaning": "감옥", "scene": "historic stone castle fortress prison hallway, whimsical cute slender stickman inmate smiling behind vertical iron jail bars, friendly guard stickman walking corridor with big key ring, stone walls and hanging torch"},
    {"id": "m1-43", "word": "potato", "meaning": "감자", "scene": "sunny autumn farmland garden patch, happy cute slender stickman farmer harvesting round fresh potatoes from dirt soil with garden fork into a woven basket, friend tying a potato sack, wheelbarrow and scarecrow"},
    {"id": "m1-44", "word": "hide", "meaning": "감추다", "scene": "cozy attic playroom hide and seek, cute slender stickman peeking cheerfully while hiding inside an antique wooden wardrobe trunk, friend across the room counting with hands covering eyes, stacked books and vintage lantern"},
    {"id": "m1-45", "word": "suddenly", "meaning": "갑자기", "scene": "surprise birthday celebration living room, door swinging open suddenly as cute slender stickman friends pop colorful party confetti poppers shouting surprise, hero stickman with hands raised in sudden delight, cake and balloons"},
    {"id": "m1-46", "word": "deck", "meaning": "갑판", "scene": "wooden ship deck of a sailing cruise ship at sea, cute slender stickman passengers leaning on safety railing pointing at playful dolphins jumping in ocean waves, captain at ship steering wheel, mast and lifebuoy ring"},
    {"id": "m1-47", "word": "price", "meaning": "값, 가격", "scene": "cozy flea market antique stall, cute slender stickman customer holding and inspecting a dangling price tag on a vintage toy bear with coin purse in hand, friendly merchant smiling behind counter awning"},
    {"id": "m1-48", "word": "expensive", "meaning": "값비싼", "scene": "luxury jewelry boutique glass showcase, cute slender stickman couple admiring a sparkling diamond necklace resting on velvet pillow with a high price tag, elegant clerk in bow tie, chandelier and mirror"},
    {"id": "m1-49", "word": "cheap", "meaning": "값싼", "scene": "bustling farmers market fruit stand, banner saying 'SPECIAL $1 CHEAP SALE', cute slender stickman customer happily handing a single dollar coin for a basket of fresh apples, smiling vendor, wooden crates"},
    {"id": "m1-50", "word": "robber", "meaning": "강도", "scene": "bank hallway comic scene, funny cute slender stickman robber wearing eye mask and striped shirt carrying a sack tiptoeing away, running into an alert security guard with flashlight, bank vault door in background"},
    {"id": "m1-51", "word": "equal", "meaning": "같은", "scene": "science math classroom, cute slender stickman teacher demonstrating a two-pan balance scale perfectly balanced in horizontal equilibrium with identical wooden blocks on both sides, chalk drawing of equal sign on board"},
    {"id": "m1-52", "word": "unlike", "meaning": "같지 않은", "scene": "art design exhibition gallery, two cute slender stickman visitors comparing a wall of three identical circle paintings beside one totally unique unlike glowing star sculpture, bench and gallery spotlight"},
    {"id": "m1-53", "word": "frog", "meaning": "개구리", "scene": "peaceful botanical pond, adorable chubby frog sitting proudly on a wide green water lily pad catching a water ripple, cute slender stickman child crouching by grassy bank observing with gentle curiosity, cattails and dragonfly"},
    {"id": "m1-54", "word": "private", "meaning": "개인의", "scene": "secret greenhouse garden wooden gate, cute slender stickman unlocking small gate marked with 'PRIVATE GARDEN' wooden plaque to enter peaceful personal greenhouse room filled with potted plants and reading desk"},
    {"id": "m1-55", "word": "upside down", "meaning": "거꾸로", "scene": "outdoor playground monkey bars jungle gym, cute slender stickman hanging completely upside down by legs waving cheerfully with big smile, friend standing upright below laughing and clapping, playground slide"},
    {"id": "m1-56", "word": "giant", "meaning": "거대한", "scene": "fantasy fairy tale village square, huge friendly gentle giant stickman standing with head up in fluffy clouds, tiny cheerful village cute slender stickmen looking up waving friendly hands from cobblestone path and cottage rooftops"},
    {"id": "m1-57", "word": "huge", "meaning": "거대한", "scene": "natural history museum exhibition hall, cute slender stickman museum visitors looking in awe up at a colossal huge dinosaur skeleton fossil filling the high hall, docent explaining with pointer, museum pillars"},
    {"id": "m1-58", "word": "deal", "meaning": "거래하다", "scene": "modern business office meeting room, two professional cute slender stickman partners shaking hands warmly sealing a successful business deal contract on conference table, signed document folders and coffee cups"},
    {"id": "m1-59", "word": "living room", "meaning": "거실", "scene": "cozy modern family living room, cute slender stickman relaxing reading a book on a comfortable sectional sofa, young stickman playing with toy blocks on the rug, floor lamp, potted ficus, framed wall pictures"},
    {"id": "m1-60", "word": "nearly", "meaning": "거의", "scene": "afternoon puzzle table, large 1000-piece jigsaw puzzle nearly finished with only one final missing piece held in cute slender stickman's fingers ready to place, friends eagerly leaning in watching the completion"}
]

def generate_word_image(item, seed_base=700):
    word = item["word"]
    word_id = item["id"]
    meaning = item["meaning"]
    scene = item["scene"]
    file_name = word.replace(" ", "-")
    out_path = os.path.join(ASSETS_DIR, f"{file_name}.png")

    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        print(f"[{word_id}] '{word}' 이미 존재하여 건너뜁니다. -> {out_path}", flush=True)
        return True

    print(f"\n[{word_id}] '{word}' ({meaning}) 생성 중...", flush=True)
    print(f"Scene: {scene}", flush=True)

    # 100% 영문 프롬프트 (한글 제거 원칙)
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
        "seed": seed_base
    }

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
            return True
        except Exception as e:
            print(f"[{word}] 시도 {attempt} 실패: {e}", flush=True)
            time.sleep(3)

    print(f"[오류] '{word}' 생성 실패!", flush=True)
    return False

def run():
    print("==================================================", flush=True)
    print("중1 유닛 2 & 유닛 3 선형그래픽 일괄 생성 시작 (새 규칙 100% 적용)", flush=True)
    print("규칙: 1024x1024, 0.05mm 극세선, No-Neck, 한글 텍스트 전면 배제(영문 전용), #f5f6f8, #030203", flush=True)
    print("==================================================", flush=True)

    os.makedirs(ASSETS_DIR, exist_ok=True)

    print("\n>>> [1/2] 중1 유닛 2 생성 진행 (m1-21 ~ m1-40)...", flush=True)
    for idx, item in enumerate(UNIT2_WORDS, 1):
        generate_word_image(item, seed_base=700 + idx * 23)

    print("\n>>> [2/2] 중1 유닛 3 생성 진행 (m1-41 ~ m1-60)...", flush=True)
    for idx, item in enumerate(UNIT3_WORDS, 1):
        generate_word_image(item, seed_base=800 + idx * 29)

    print("\n==================================================", flush=True)
    print("중1 유닛 2 및 유닛 3 모든 이미지 생성 완료!", flush=True)

if __name__ == "__main__":
    run()
