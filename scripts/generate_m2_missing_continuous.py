#!/usr/bin/env python3
"""
중학교 2학년(Middle 2) 1유닛부터 전체 단어 순차 검사 후 누락된 이미지만 자동 연속 생성 스크립트
- 중2 전체 1,003개 단어 (Unit 1 ~ Unit 51)를 1유닛부터 차례대로 스캔
- 이미지가 없는 단어를 발견하면 최신 선형그래픽 스킬 규격으로 즉시 생성
- 최신 조형 스킬 규격:
  1. 3~3.5등신 SD 픽토그램 순백색 마네킹 (blank solid white mannequin)
  2. 점 눈 2개 + 얇은 미소선 입, 코/눈썹/귀/머리카락 일절 없음
  3. 목 없는 일체형 튜브 몸체 (No-Neck), 관절 없는 고무관 팔다리, 벙어리장갑 손, 타원형 발 패드
  4. 인물 크기 자연스러운 자유도 부여 & 과도하게 큰 거대 인물화 원천 방지 (Negative space & wide framing)
  5. 1024x1024 해상도, #f5f6f8 배경, #030203 선, 100% 영문 전용
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
from datetime import datetime

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
SYNC_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "sync_word_images.py")
README_FILE = os.path.join(PROJECT_ROOT, "README.md")
STATUS_FILE = os.path.join(SCRIPT_DIR, "m2_missing_status.json")

# 최신 3~3.5등신 순백색 마네킹 픽토그램 스타일 프롬프트
STYLE_PROMPT = (
    "linear graphic illustration, "
    "3 to 3.5 head-to-body chibi SD ratio cute characters with large prominent smooth spherical bald round heads, "
    "minimalist dot and line face, two simple solid black dot eyes and a tiny thin curved smile line, strictly no nose, no eyebrows, no lips, no ears, no hair, "
    "seamless tubular neckless body directly attached to round head with completely no neck, smooth organic curves without clavicle or muscle contours, "
    "jointless smooth rubber-hose arms and legs with no elbows and no knees, simplified mitten-like blunt round hands, smooth rounded flat oval foot pads firmly on floor line, "
    "blank solid white mannequin pictogram character fill with zero clothing, no seams, no buttons, no folds, no skin texture, genderless universal figure, "
    "crisp uniform dark charcoal ink outlines #030203, strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, flat smooth light gray canvas background color #f5f6f8, "
    "small modest chibi character height strictly under 50 to 60 percent of frame height, small character occupying less than half the canvas height, spacious wide environmental framing, abundant negative space around character, full body comfortably framed with generous breathing room, "
    "abundant rich background details, furniture, wall decor, floor line, ambient props, "
    "strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
)

NEGATIVE_PROMPT = (
    "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing, "
    "character height over 60 percent of canvas, character taller than half screen, oversized character, giant figure, frame-filling character, tall character, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, large scale character dominating scene, taking over screen, "
    "realistic human anatomy, realistic face, facial details, nose, eyebrows, eyelashes, eyelids, lips, teeth, ears, hair, hairstyle, neck, long neck, throat, collar, collarbone, muscles, realistic fingers, individual finger joints, fingernails, toes, shoes, clothing, clothes, shirt, pants, wrinkles, folds, "
    "thick lines, heavy brush strokes, chunky lines, fat strokes, "
    "pure white #ffffff background, dark background, black background, 3d, 3d render, realistic, shadow, shading, color, gradients, photo, blur, watermark, signature, messy"
)

# 단어별 맞춤형 고품질 내러티브 씬 사전
SCENE_PRESETS = {
    "hydrogen": "clean chemistry science laboratory, cute chibi mannequin scientist observing a clear glass electrolysis container separating water into glowing hydrogen and oxygen gas bubbles, scientific flasks and Periodic Table poster on wall",
    "control": "high-tech operations control room, calm cute chibi mannequin operator at a neat console desk steering control levers and monitoring orderly signal monitors with complete steady composure",
    "uniform": "tailor studio and fitting room, cute chibi mannequin looking into a full-length dressing mirror admiring a crisp neat classic school uniform jacket displayed on a tailor mannequin stand",
    "damage": "cozy suburban house attic and roof, cute chibi mannequin inspector carefully examining cracked storm damage shingles on a wooden roof with a clipboard and gentle inspection tool after heavy rain"
}

def save_status(data: dict):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_scene(word: str, word_info: dict, meaning: str) -> str:
    if word in SCENE_PRESETS:
        return SCENE_PRESETS[word]
    ex = word_info.get("example", "")
    if ex:
        import re
        clean_ex = re.sub(r'[^a-zA-Z0-9,\.\-\s]', ' ', ex).strip()
        return f"cozy illustrative room setting, cute chibi mannequin {clean_ex}, rich background furniture, wall decor, floor line"
    return f"cozy illustrative narrative scene of {word}, cute chibi mannequin interacting naturally in comfortable setting, rich props, wall decor, floor line"

def generate_word_image(word: str, scene: str, out_path: str, seed: int = 42) -> bool:
    full_prompt = f"complete richly detailed scene of {scene}, {STYLE_PROMPT}"
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
                return False
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
    print(f"\n[Unit {unit_num} 완료] 동기화 및 Git 푸시 시작...", flush=True)
    subprocess.run([sys.executable, SYNC_SCRIPT], check=False)
    subprocess.run(["find", ".", "-name", "._*", "-type", "f", "-delete"], cwd=PROJECT_ROOT, check=False)

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_header = f"### {today_str}"
    word_list_str = ", ".join([w["word"] for w in created_words])
    new_entry = (
        f"- 중학교 2학년 Unit {unit_num} 누락 단어 선형그래픽 일러스트 {len(created_words)}종 생성 및 등록 완료 (Draw Things 로컬 API 기반)\n"
        f"  - 1024x1024 해상도, 3~3.5등신 순백색 마네킹 픽토그램 캐릭터, 인물 스케일링 자유도, 뉴모피즘 캔버스 테마(#f5f6f8), 딥차콜 선(#030203)\n"
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

    commit_msg = f"feat: 중2 유닛 {unit_num} 누락 단어({word_list_str}) 선형그래픽 생성 및 등록 완료"
    try:
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        print(f"[Git] Unit {unit_num} 원격 푸시 완료!", flush=True)
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
    print("중학교 2학년 누락 이미지 순차 탐색 및 자동 생성 파이프라인 가동", flush=True)
    print(f"총 단어: {total_words}개 (총 {total_units}개 유닛, Unit 1부터 순차 스캔)", flush=True)
    print("스킬 규격: 3~3.5등신 픽토그램 순백 마네킹, 인물 크기 자연스러운 자유도, 1024x1024, 영문 전용", flush=True)
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

            print(f"[{item['id']}] '{w}' ({item['meaning']}) 생성 시작...", flush=True)
            print(f"Scene: {item['scene']}", flush=True)

            res = generate_word_image(w, item["scene"], item["file_path"], seed=900 + item["global_idx"] * 17)
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

    print("\n🎉 중학교 2학년 전체 유닛 검사 및 모든 누락 이미지 생성 완료!", flush=True)

if __name__ == "__main__":
    main()
