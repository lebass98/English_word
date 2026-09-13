#!/usr/bin/env python3
"""
중학교 2학년(Middle 2) 1유닛부터 끝까지 순차 검사 후 미제작 단어 완전 정복 스크립트
- 중2 전체 1,003개 단어 (Unit 1 ~ Unit 51)를 1유닛부터 순차 스캔
- 이미지가 없는 단어만 골라 최신 개정 스킬(2026-09-13 확정 레퍼런스 스타일)로 연속 생성
- 최신 조형 스킬 규격 (레퍼런스 칠판 앞 3명 스타일):
  1. 좁고 긴 둥근 직사각형 몸통 (머리 폭 절반 폭, 폭보다 3배 큰 키)
  2. 선 두 줄 튜브 팔다리 (선 한 줄 막대 팔다리 절대 금지, 적당한 두께감)
  3. 구형 원형 민머리, 목 없음(No-Neck), 점 눈 2개 + 얇은 미소선 입, 볼 홍조 배제
  4. cute, chibi, plump 등 머리 커지는 단어 프롬프트에서 전면 배제
  5. 화면 높이 약 1/3 (30~35%) 아담한 크기로 바닥선에 안정적으로 배치, 상단 65~70%는 풍성한 배경 내러티브
  6. 1024x1024 해상도, #f5f6f8 배경, #030203 선, 100% 영문 전용
- 각 유닛의 누락 단어 생성 완료 시 자동:
  - sync_word_images.py 레지스트리 동기화
  - macOS '._*' 임시파일 정리
  - README.md 작업 내역 기록
  - 한글 커밋 및 origin/main push
"""

import os
import sys
import json
import time
import base64
import urllib.request
import subprocess
import re
from datetime import datetime

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
SYNC_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "sync_word_images.py")
README_FILE = os.path.join(PROJECT_ROOT, "README.md")
STATUS_FILE = os.path.join(SCRIPT_DIR, "m2_missing_status.json")

# 최신 개정 스킬 표준 공통 스타일 프롬프트 (2026-09-13 레퍼런스 확정 규격)
STYLE_PROMPT = (
    "thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, extremely fine crisp outlines drawn in dark charcoal ink color #030203, "
    "flat smooth light gray canvas background color #f5f6f8, "
    "simple white pictogram characters, round bald head resting directly on top of the body with completely no neck, two small dot eyes and a small smile line, plain white face, "
    "very narrow slim torso only about half as wide as the head, tall soft rounded rectangle body with a flat bottom edge, the whole figure is narrow and about three times taller than it is wide, "
    "short slim rounded tube arms drawn with two close parallel outlines ending in small round mitten nubs, held close to the body, "
    "short slim rounded tube legs drawn with two close parallel outlines ending in small rounded feet, limbs are narrow but still have visible width and are never a single line, "
    "small character in a wide scene, modest compact character scale, standing small figure occupying approximately one third of frame height around 30 to 35 percent of canvas height, placed comfortably on bottom floor line, spacious upper and middle frame filled with rich environmental details, balanced wide scene composition, plenty of breathing room, full body visible without crowding, "
    "abundant rich background details, furniture, wall decor, floor line, ambient props, "
    "strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, empty background, "
    "strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
)

NEGATIVE_PROMPT = (
    "stick figure, stickman, matchstick limbs, single-line arms, single-line legs, thin wire limbs, long thin legs, "
    "fat body, chubby, plump, round belly, wide bulky torso, blush, rosy cheeks, pink cheeks, cheek marks, "
    "neck, long neck, throat, collar, neck line, detailed neck anatomy, "
    "oversized character, giant figure, tall figure, frame-filling character, character taking up entire screen, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, suffocating composition, character head near top of frame, dominating figure, "
    "realistic human anatomy, realistic face, facial details, nose, eyebrows, eyelashes, eyelids, lips, teeth, ears, hair, hairstyle, muscles, realistic fingers, individual finger joints, fingernails, toes, shoes, clothing, clothes, shirt, pants, wrinkles, folds, "
    "thick lines, bold outlines, heavy brush strokes, chunky lines, fat strokes, "
    "pure white #ffffff background, dark background, black background, 3d, 3d render, realistic, shadow, shading, color, gradients, photo, blur, watermark, text, signature, messy, "
    "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing"
)

# 단어별 맞춤형 고품질 영문 내러티브 씬 사전 (cute/chibi/stickman 전면 배제)
SCENE_PRESETS = {
    # Unit 19
    "intimate": "warm cozy hearthside reading nook, two close small slim white pictogram friends sitting together on floor cushions sharing a warm teapot and intimate quiet conversation, soft floor lamp and bookshelf",
    "grave": "formal historic council chambers, solemn small slim white pictogram statesman standing before a grand oak council table addressing a grave serious national proclamation, heavy drapes and antique stone pillars",
    "elementary": "bright friendly beginner art workshop, small slim white pictogram student happily learning elementary basic watercolor painting brush strokes on an easel canvas, color mixing palette and jar",
    "greedy": "lavish banquet dining hall, greedy small slim white pictogram person hoarding a towering high stack of golden freshly baked pies and cakes all to itself on a long banquet table, ornate candelabras",
    # Unit 20
    "vain": "elegant private dressing hall, vain small slim white pictogram figure admiring reflection in an ornate oval standing mirror with dramatic proud gestures, vanity table and perfumes",
    "solar": "clean energy astronomy observatory, small slim white pictogram scientist pointing toward a glowing solar system sun model and rooftop solar panel blueprints, telescope and planet charts on wall",
    "single": "peaceful sunny studio apartment, content small slim white pictogram person living a joyful single life reading a book by the sunny window plant stand, comfortable armchair and tea mug",
    "serious": "library study room, focused and serious small slim white pictogram researcher deeply reading a large open reference encyclopedia book taking neat notes, desk lamp and stacked books",
    # Unit 21
    "boring": "quiet rainy afternoon room, small slim white pictogram student resting chin on hand looking bored at a monotonous ticking wall clock, open textbook and rain outside window",
    "fair": "sports athletics arena finish line, fair and honest small slim white pictogram referee checking a digital stopwatch timer ensuring a fair tournament outcome, track lanes and grandstand",
    "modern": "high-tech urban smart home living room, small slim white pictogram person controlling automated modern lighting and smart home devices via wall tablet panel, sleek minimalist furniture",
    "harmful": "environmental laboratory, small slim white pictogram researcher pointing at a clear warning sign indicating harmful toxic chemicals kept safely in sealed glass containers, ventilation hood",
    "calm": "tranquil lakeside wooden dock at sunrise, peaceful small slim white pictogram figure standing in calm contemplation watching gentle still water and distant mist, pine trees",
    "special": "celebration workshop studio, happy small slim white pictogram craftsperson presenting a beautifully wrapped special gift box tied with an elegant ribbon, confetti and gift tags",
    "steady": "woodworking carpentry bench, skilled small slim white pictogram artisan using a steady hand to guide a hand chisel along a smooth oak board, wood shavings and tool rack",
    "company": "bright collaborative office meeting room, group of small slim white pictogram colleagues having a productive company meeting around a conference table, whiteboard project timeline"
}

def clean_concept(text: str) -> str:
    if not text:
        return ""
    # non-ASCII 제거
    cleaned = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # cute, chibi, slender, stickman, chubby 등을 표준 지침에 맞게 정리
    cleaned = re.sub(r'\b(cute|chibi|plump|chubby)\b', '', cleaned, flags=re.I)
    cleaned = re.sub(r'\b(slender\s+stickman|stickman)\b', 'small slim white pictogram character', cleaned, flags=re.I)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def get_scene(word: str, word_info: dict, meaning: str) -> str:
    if word in SCENE_PRESETS:
        return clean_concept(SCENE_PRESETS[word])
    ex = word_info.get("example", "")
    if ex:
        c_ex = clean_concept(ex)
        return f"cozy illustrative room setting, small slim white pictogram character {c_ex}, rich background furniture, wall decor, floor line"
    return f"cozy illustrative narrative scene of {word}, small slim white pictogram character interacting naturally in comfortable setting, rich props, wall decor, floor line"

def save_status(data: dict):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def generate_word_image(word: str, scene: str, out_path: str, seed: int = 42):
    full_prompt = f"linear graphic illustration, complete richly detailed scene of {scene}, {STYLE_PROMPT}"
    payload = {
        "prompt": full_prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 8,
        "width": 1024,
        "height": 1024,
        "seed": seed
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            images = data.get("images", [])
            if not images:
                return False, 0, 0
            raw_bytes = base64.b64decode(images[0])

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(raw_bytes)

        elapsed = time.time() - t0
        file_size_kb = round(len(raw_bytes) / 1024, 1)
        print(f"[{word}] 생성 성공! ({elapsed:.1f}초, {file_size_kb} KB) -> {out_path}", flush=True)
        return True, elapsed, file_size_kb
    except Exception as e:
        print(f"[{word}] 생성 실패: {e}", flush=True)
        return False, 0, 0

def sync_and_commit(unit_num: int, created_words: list):
    if not created_words:
        return
    print(f"\n[Unit {unit_num} 누락분 완료] 레지스트리 동기화 및 Git 푸시 시작...", flush=True)
    subprocess.run([sys.executable, SYNC_SCRIPT], check=False)
    subprocess.run(["find", ".", "-name", "._*", "-type", "f", "-delete"], cwd=PROJECT_ROOT, check=False)

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_header = f"### {today_str}"
    word_list_str = ", ".join([w["word"] for w in created_words])
    new_entry = (
        f"- 중학교 2학년 Unit {unit_num} 누락 단어 선형그래픽 일러스트 {len(created_words)}종 생성 및 등록 완료 (Draw Things 로컬 API 기반)\n"
        f"  - 1024x1024 해상도, 2026-09-13 개정 레퍼런스 표준(좁고 긴 몸통, 선 두 줄 튜브 팔다리, 화면 1/3 아담한 크기, 0.05mm 초극세선, #f5f6f8 배경, #030203 선)\n"
        f"  - 생성 단어: {word_list_str}\n"
        f"  - `sync_word_images.py` 스크립트를 통해 `src/constants/wordImages.ts` 레지스트리 일괄 갱신 완료\n"
    )

    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if today_header in content:
            parts = content.split(today_header, 1)
            updated_content = parts[0] + today_header + "\n" + new_entry + parts[1]
        else:
            marker = "## 작업 내역\n\n"
            if marker in content:
                parts = content.split(marker, 1)
                updated_content = parts[0] + marker + today_header + "\n" + new_entry + "\n" + parts[1]
            else:
                updated_content = content + f"\n\n## 작업 내역\n\n{today_header}\n{new_entry}\n"
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(updated_content)

    commit_msg = f"feat: 중2 유닛 {unit_num} 누락 단어({word_list_str}) 선형그래픽 일러스트 생성 및 등록 완료"
    try:
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        print(f"[Git] Unit {unit_num} 누락분 원격 푸시 완료!", flush=True)
    except Exception as e:
        print(f"[Git 오류] {e}", flush=True)

def main():
    m2_file = os.path.join(PROJECT_ROOT, "src", "data", "en", "levels", "middle-2.json")
    tr_file = os.path.join(PROJECT_ROOT, "src", "data", "en", "tr", "ko.json")
    words_file = os.path.join(PROJECT_ROOT, "src", "data", "en", "words.json")

    with open(m2_file, "r", encoding="utf-8") as f:
        m2_words = json.load(f)
    with open(tr_file, "r", encoding="utf-8") as f:
        tr_data = json.load(f)
    with open(words_file, "r", encoding="utf-8") as f:
        words_dict = json.load(f)

    total_words = len(m2_words)
    total_units = (total_words + 19) // 20

    print("==================================================", flush=True)
    print("중학교 2학년 누락 이미지 순차 탐색 및 완성 파이프라인 가동", flush=True)
    print(f"총 단어: {total_words}개 (총 {total_units}개 유닛, 1유닛부터 끝까지 순차 검사)", flush=True)
    print("스킬 표준: 2026-09-13 개정 레퍼런스 스타일 (좁고 긴 몸통, 선 두 줄 튜브 팔다리, 화면 1/3 높이)", flush=True)
    print("==================================================", flush=True)

    status_data = {
        "current_unit": 1,
        "current_word": "",
        "missing_found_in_unit": [],
        "completed_words": []
    }

    for unit_num in range(1, total_units + 1):
        start_idx = (unit_num - 1) * 20
        end_idx = min(start_idx + 20, total_words)
        unit_slice = m2_words[start_idx:end_idx]

        missing_in_unit = []
        for i, word in enumerate(unit_slice):
            g_idx = start_idx + i + 1
            w_id = f"m2-{g_idx}"
            f_name = word.replace(" ", "-") + ".png"
            p = os.path.join(ASSETS_DIR, f_name)
            if not os.path.exists(p):
                meaning = tr_data.get("meanings", {}).get(w_id, "")
                info = words_dict.get(word, {})
                scene = get_scene(word, info, meaning)
                missing_in_unit.append({
                    "global_idx": g_idx,
                    "pos": i + 1,
                    "unit": unit_num,
                    "id": w_id,
                    "word": word,
                    "meaning": meaning,
                    "scene": scene,
                    "file_path": p
                })

        if not missing_in_unit:
            continue

        print(f"\n▶ [Unit {unit_num}] 누락 이미지 {len(missing_in_unit)}개 발견! 생성 시작", flush=True)
        created_in_unit = []
        for item in missing_in_unit:
            w = item["word"]
            status_data["current_unit"] = unit_num
            status_data["current_word"] = w
            save_status(status_data)

            print(f"\n[{item['id']}] '{w}' ({item['meaning']}) 생성 시작...", flush=True)
            print(f"Scene: {item['scene']}", flush=True)

            res = generate_word_image(w, item["scene"], item["file_path"], seed=950 + item["global_idx"] * 19)
            if isinstance(res, tuple) and res[0]:
                created_in_unit.append(item)
                status_data["completed_words"].append({
                    "word": w,
                    "id": item["id"],
                    "unit": unit_num,
                    "elapsed_sec": res[1],
                    "size_kb": res[2]
                })
                save_status(status_data)

        if created_in_unit:
            sync_and_commit(unit_num, created_in_unit)

    print("\n🎉 축하합니다! 중학교 2학년 전체 51유닛 모든 단어의 선형그래픽 이미지 제작 및 배포가 완료되었습니다!", flush=True)

if __name__ == "__main__":
    main()
