#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 일본어 JLPT N5 단어 자동 연속 생성 및 유닛별 Git 동기화 스크립트
- 대상: JLPT N5 단어 (총 556개, 유닛당 20개씩 총 28개 유닛)
- 최신 선형그래픽 조형 6대 원칙 + 2026-09-13/14 개정 완벽 준수:
  1. 1024x1024 해상도 네이티브 렌더링
  2. 0.05mm 초극세 바늘선 (thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke)
  3. 목 없는(No-Neck) 머리-몸통 분리 원형 머리 순백 픽토그램 (턱 밑 좁은 한 점에서 만남, 좁고 긴 직사각형 몸통, 선 두 줄 튜브 팔다리)
  4. 배경 #f5f6f8, 선색 #030203
  5. 풍성한 내러티브 씬 묘사 (바닥선, 가구, 소품 등)
  6. 후처리 효과 없는 순수 렌더링 원본 보존
  7. 100% 영문 전용 절대 원칙 (프롬프트/씬 비ASCII 문자 전면 배제, 영문 외 텍스트 철저 차단)
  8. 익사이팅한 활동 장면 (Exciting Action Moment: 뛰기, 점프, 손 뻗기 등 동작선 motion lines)
- 각 유닛(20단어) 완료 시:
  1. sync_word_images.py 실행하여 wordImages.ts 자동 갱신
  2. find . -name '._*' -type f -delete (macOS 임시파일 정리)
  3. README.md에 일별 작업 내역 기록
  4. Git commit (한글 메시지)
  5. Git pull --rebase origin main && git push origin main 동기화
"""

import os
import sys
import re
import json
import time
import glob
import base64
import urllib.request
import argparse
import subprocess
from datetime import datetime

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
SYNC_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "sync_word_images.py")
README_FILE = os.path.join(PROJECT_ROOT, "README.md")

# 일본어 N5 단어별 고품질 영문 씬 콘셉트 사전 (100% 순수 영문 전용)
N5_SCENE_PRESETS = {
    # Unit 1 (n5-1 ~ n5-20)
    "私": "energetic character jumping happily and proudly pointing to oneself with thumbs up on a sunlit balcony with flowering planters and city skyline view, motion lines",
    "あなた": "cozy sunny art studio, one joyful character leaping and pointing excitedly with both hands toward the viewer with an inviting warm smile, easel with canvas, art stool, motion marks",
    "人": "bustling open city pedestrian plaza, active character sprinting happily across wide stone pavement lined with benches, street lamps, distant cafe terrace, motion lines",
    "男": "modern active gym room, strong energetic male character triumphantly lifting a barbell with a happy grin, exercise equipment, mirror on wall, dumbbell racks",
    "女": "sunny outdoor botanical garden path, graceful energetic female character happily jogging along stone trail waving cheerfully, flower beds, garden archway and trees",
    "子供": "colorful lively playground, playful little child character energetically jumping off a swing set into the air with arms outstretched in joy, slide, sandbox, fence",
    "大人": "stylish contemporary library cafe, confident adult character striding with coffee tumbler, sleek wooden bookshelves, armchair, laptop on work desk",
    "家族": "warm cozy home living room, happy family characters joyfully hugging and cheering together around a coffee table, comfortable sofa, framed pictures on wall, rug",
    "父": "backyard lawn patio, proud energetic father character tossing a baseball playfully in the air with his glove, garden bench, picket fence, barbecue grill",
    "母": "bright cheerful kitchen, loving energetic mother character joyfully taking a steaming fresh batch of cookies from the oven, kitchen counter, spice jars, apron",
    "兄": "neighborhood basketball court, athletic older brother character jumping high to shoot a basketball into the hoop, chain link fence, sports bench, basketball rack",
    "姉": "bright study music room, cheerful energetic older sister character playing an upbeat tune on an acoustic guitar with notes floating, music stand, bookshelf",
    "弟": "playful room floor, energetic little brother character happily zooming a toy race car across the wooden floor, toy building blocks, low table, toy chest",
    "妹": "sunny grassy garden, enthusiastic little sister character joyfully chasing colorful fluttering butterflies with a little net, flowers, birdhouse, stone path",
    "友達": "scenic hilltop trail, two best friend characters joyfully jumping together giving a high-five against a panoramic mountain view, backpacks, hiking trail",
    "先生": "bright energetic classroom, inspiring smiling teacher character standing before a large chalkboard pointing to an exciting star diagram with a wooden pointer, student desks, globe",
    "学生": "school courtyard walkway, enthusiastic student character with a backpack leaping forward clutching a textbook happily heading to class, school entrance gate, trees",
    "会社員": "modern high-rise business office, active office worker character striding briskly holding a briefcase and coffee cup with a cheerful confident smile, desks, computer monitors",
    "医者": "clean bright clinic consultation room, kind smiling doctor character with stethoscope around neck giving a reassuring thumbs up, examination table, medical chart on wall",
    "名前": "festive registration greeting desk, enthusiastic character proudly stamping an official name tag badge on desk with clear bold letters NAME, welcome banner, podium, balloons",

    # Unit 2 (n5-21 ~ n5-40)
    "国": "international cultural hall, cheerful character standing proudly before an array of diverse national flags and a large globe map on an exhibition wall, travel brochures",
    "今": "vibrant city clock tower square, excited character pointing urgently to an active wall clock showing present time NOW, stone fountain, pavement benches",
    "今日": "bright morning bedroom with wide window, joyful character tearing off yesterday page from a wall calendar revealing exciting TODAY with sun rays streaming in",
    "明日": "scenic hilltop campsite at dawn, character looking forward enthusiastically through telescope toward tomorrow rising sun on the horizon, tent, campfire pit",
    "昨日": "cozy library study nook, nostalgic character happily smiling while flipping through yesterday journal diary scrapbook filled with fun photos on a desk lamp table",
    "毎日": "sunny home jogging path, energetic character running with athletic stride on a daily morning route past green park trees, fitness tracker, sunrise glow",
    "朝": "bright sunny kitchen dining nook, cheerful character stretching arms wide welcoming morning sunshine beside a breakfast table with toast and steaming mug, open curtains",
    "昼": "bustling park picnic lawn at midday, hungry happy character sitting on checkered blanket opening a bento lunchbox under bright noon sun, trees, bicycle parked",
    "夜": "peaceful rooftop terrace under a starlit night sky with glowing crescent moon, relaxed character looking through stargazing telescope, cozy lanterns on railing",
    "午後": "cozy sunlit tea cafe patio, relaxed character enjoying peaceful afternoon tea time with teapot and slice of cake on round table, garden plants, gentle breeze",
    "時間": "antique clockmaker workshop, focused character admiring a variety of vintage pendulums, hourglasses and ticking wall clocks showing passage of time, workbench tools",
    "来週": "bright organized home office, excited character marking an energetic red circle around next week dates on a large wall planner calendar, desk, pinboard",
    "来年": "festive New Year countdown party room, joyful character raising a party horn beneath a banner celebrating the coming new year, streamers, confetti, clock",
    "春": "vibrant springtime park meadow, delighted character leaping among blooming cherry blossom trees and dancing flower petals in gentle spring breeze, picnic bench",
    "夏": "tropical summer beach resort, energetic character in swim shorts running excitedly toward ocean waves with a colorful beach ball, palm trees, beach umbrella",
    "秋": "serene mountain forest pathway, cheerful character joyfully tossing golden autumn fallen leaves into the crisp air, maple trees, wooden trail fence",
    "冬": "sparkling snowy winter wonderland, happy character building a smiling snowman with a carrot nose and scarf, falling snowflakes, pine trees with snow",
    "誕生日": "colorful birthday party room, thrilled character blowing out candles on a tall decorated birthday cake surrounded by cheering friends, party hats, gift boxes",
    "休み": "tropical seaside hammock, completely relaxed character swaying gently between two palm trees holding a coconut drink with umbrella straw, ocean waves",
    "家": "charming suburban front yard, proud character welcoming guests with open arms in front of a lovely two-story cottage house with chimney, flower garden, stone path",
}

def clean_english_only(text: str) -> str:
    """비영문 문자를 철저히 제거하고 공백을 정돈하여 100% 영문 텍스트만 남김"""
    if not text:
        return ""
    cleaned = re.sub(r'[^\x00-\x7F]+', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def get_registered_image_keys():
    """현재 등록된 이미지 키 목록 수집"""
    keys = set()
    for p in glob.glob(os.path.join(PROJECT_ROOT, "src", "constants", "wordImagesByLetter", "*.ts")):
        with open(p, encoding="utf-8") as f:
            for line in f:
                if ":" in line and "require(" in line:
                    k = line.split(":")[0].strip().strip("\"'")
                    keys.add(k)
    return keys

def get_asset_path(word: str, concept_id: str):
    """단어 또는 conceptId에 따른 에셋 저장 경로 판정"""
    # conceptId가 영문이면 영문 첫 글자 폴더 우선
    target = concept_id if (concept_id and concept_id != word and "a" <= concept_id[:1].lower() <= "z") else word
    first = target[:1].lower()
    letter = first if "a" <= first <= "z" else "_"
    filename = f"{target.replace(' ', '-')}.png"
    return os.path.join(ASSETS_DIR, letter, filename), letter, target

def load_n5_words():
    """N5 단어 목록 및 메타데이터 로드"""
    with open(os.path.join(PROJECT_ROOT, "src", "data", "ja", "levels", "jlpt-n5.json"), encoding="utf-8") as f:
        n5_list = json.load(f)
    with open(os.path.join(PROJECT_ROOT, "src", "data", "ja", "words.json"), encoding="utf-8") as f:
        words_meta = json.load(f)
    with open(os.path.join(PROJECT_ROOT, "src", "data", "ja", "tr", "ko.json"), encoding="utf-8") as f:
        ko_meanings = json.load(f).get("meanings", {})

    items = []
    for idx, w in enumerate(n5_list, 1):
        nid = f"n5-{idx}"
        meta = words_meta.get(w, {})
        cid = meta.get("conceptId") or w
        meaning = ko_meanings.get(nid, "")
        items.append({
            "idx": idx,
            "id": nid,
            "word": w,
            "conceptId": cid,
            "phonetic": meta.get("phonetic", ""),
            "meaning": meaning,
            "unit": ((idx - 1) // 20) + 1
        })
    return items

def generate_image_for_word(item: dict, registered_keys: set):
    """단어 1개에 대해 선형그래픽 이미지 생성"""
    word = item["word"]
    cid = item["conceptId"]
    meaning = item["meaning"]
    out_path, letter, key = get_asset_path(word, cid)

    # 이미 파일이 존재하거나 등록되어 있으면 건너뜀
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return True, "already_exists"

    # 프리셋 씬 가져오기 또는 기본 동작 씬 구성
    scene = N5_SCENE_PRESETS.get(word) or N5_SCENE_PRESETS.get(cid)
    if not scene:
        # 안전한 기본 영문 동작 씬
        scene = f"energetic lively scene representing the concept of {clean_english_only(cid or word)}, character actively engaging in dynamic movement with motion lines, well-furnished room or outdoor background with rich details"

    clean_scene = clean_english_only(scene)

    prompt = (
        f"linear graphic illustration, complete richly detailed scene of {clean_scene}, "
        "thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, extremely fine crisp outlines drawn in dark charcoal ink color #030203, "
        "flat smooth light gray canvas background color #f5f6f8, "
        "simple white pictogram characters, two small dot eyes and a small smile line, plain white face, "
        "the round bald head is drawn as its own complete closed circle outline, and directly below it the narrow torso starts with its own separate small rounded top edge, "
        "head and body are two clearly separate shapes that touch only at one small narrow point under the chin, no thick neck, "
        "very narrow slim torso only about half as wide as the head, tall soft rounded rectangle body with a flat bottom edge, the whole figure is narrow and about three times taller than it is wide, "
        "short slim rounded tube arms drawn with two close parallel outlines ending in small round mitten nubs, "
        "short slim rounded tube legs drawn with two close parallel outlines ending in small rounded feet, limbs are narrow but still have visible width and are never a single line, "
        "the characters are caught in the middle of an exciting energetic activity, dynamic action pose full of movement such as running, jumping, leaping, reaching, throwing or climbing, "
        "arms and legs move freely with the action while keeping the same slim tube shape, playful adventurous mood, small motion lines and action marks showing speed and excitement, lively storytelling moment, "
        "small character in a wide scene, modest compact character scale, standing small figure occupying approximately one third of frame height around 30 to 35 percent of canvas height, placed comfortably on bottom floor line, spacious upper and middle frame filled with rich environmental details, balanced wide scene composition, plenty of breathing room, full body visible without crowding, "
        "abundant rich background details, furniture, wall decor, floor line, ambient props, "
        "strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, empty background, "
        "strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
    )

    negative_prompt = (
        "stick figure, stickman, matchstick limbs, single-line arms, single-line legs, thin wire limbs, long thin legs, "
        "fat body, chubby, plump, round belly, wide bulky torso, blush, rosy cheeks, pink cheeks, cheek marks, "
        "thick neck, wide neck, head merged into body, head and torso as one continuous blob, head outline flowing into shoulders, "
        "long neck, throat, collar, detailed neck anatomy, "
        "oversized character, giant figure, tall figure, frame-filling character, character taking up entire screen, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, suffocating composition, character head near top of frame, dominating figure, "
        "realistic human anatomy, realistic face, facial details, nose, eyebrows, eyelashes, eyelids, lips, teeth, ears, hair, hairstyle, muscles, realistic fingers, individual finger joints, fingernails, toes, shoes, clothing, clothes, shirt, pants, wrinkles, folds, "
        "thick lines, bold outlines, heavy brush strokes, chunky lines, fat strokes, "
        "pure white #ffffff background, dark background, black background, 3d, 3d render, realistic, shadow, shading, color, gradients, photo, blur, watermark, text, signature, messy, "
        "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing"
    )

    seed = 2000 + item["idx"] * 13
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 8,
        "width": 1024,
        "height": 1024,
        "seed": seed
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

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
            return True, "generated"
        except Exception as e:
            print(f"[{word}] 시도 {attempt} 실패: {e}", flush=True)
            time.sleep(3)

    return False, "failed"

def sync_and_commit(unit_num: int, words_summary: str):
    """단어 등록, 린트, README 기록, 커밋 및 푸시 동기화"""
    print(f"\n[유닛 {unit_num} 동기화 시작]", flush=True)

    # 1. sync_word_images.py 실행
    subprocess.run([sys.executable, SYNC_SCRIPT], check=True)

    # 2. macOS 임시파일 제거
    subprocess.run(["find", ".", "-name", "._*", "-type", "f", "-delete"], cwd=PROJECT_ROOT)

    # 3. README.md 작업 내역 추가
    today_str = datetime.now().strftime("%Y-%m-%d")
    header_today = f"### {today_str}"
    entry_line = f"- 일본어 JLPT N5 Unit {unit_num} 단어 선형그래픽 이미지 제작 및 등록 ({words_summary})"

    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        if header_today in content:
            # 해당 날짜 섹션 아래에 추가
            parts = content.split(header_today)
            new_content = parts[0] + header_today + "\n" + entry_line + parts[1]
        else:
            # 작업 내역 섹션 바로 아래에 날짜 신규 생성
            marker = "## 작업 내역\n"
            if marker in content:
                parts = content.split(marker)
                new_content = parts[0] + marker + "\n" + header_today + "\n" + entry_line + "\n" + parts[1]
            else:
                new_content = content + f"\n\n## 작업 내역\n\n{header_today}\n{entry_line}\n"

        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

    # 4. Git add & commit
    commit_msg = f"feat: 일본어 JLPT N5 Unit {unit_num} 선형그래픽 이미지 제작 및 등록"
    subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
    res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, capture_output=True, text=True)
    print(res.stdout)

    # 5. Git pull --rebase & push
    try:
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        print(f"[유닛 {unit_num}] Git 푸시 동기화 완료!", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"[유닛 {unit_num}] Git 동기화 중 오류 발생: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="JLPT N5 단어 선형그래픽 자동 연속 생성 도구")
    parser.add_argument("--unit", "-u", type=int, default=1, help="시작할 유닛 번호 (기본: 1)")
    parser.add_argument("--end-unit", "-e", type=int, default=1, help="종료 유닛 번호 (기본: 1)")
    args = parser.parse_args()

    items = load_n5_words()
    registered_keys = get_registered_image_keys()

    for u in range(args.unit, args.end_unit + 1):
        unit_words = [item for item in items if item["unit"] == u]
        if not unit_words:
            print(f"[Unit {u}] 대상 단어가 없습니다.")
            continue

        print(f"\n==================================================", flush=True)
        print(f"JLPT N5 Unit {u} 선형그래픽 생성 시작 ({len(unit_words)}단어)", flush=True)
        print(f"==================================================", flush=True)

        generated_list = []
        for item in unit_words:
            ok, status = generate_image_for_word(item, registered_keys)
            if status == "generated":
                generated_list.append(item["word"])

        # 해당 유닛 단어 요약
        words_summary = ", ".join([w["word"] for w in unit_words[:5]]) + f" 외 {len(unit_words)-5}개"
        if generated_list:
            sync_and_commit(u, words_summary)
        else:
            print(f"[Unit {u}] 이미 모든 이미지가 생성되어 동기화를 건너뜁니다.")

    print("\n모든 지정 유닛 작업이 완료되었습니다.", flush=True)

if __name__ == "__main__":
    main()
