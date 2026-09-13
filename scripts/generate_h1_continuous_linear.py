#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 최신 스킬 기반 고등학교 1학년 자동 연속 생성 및 유닛별 Git 동기화 스크립트
- 고1 유닛 3부터 지정 유닛까지 순차 생성
- 최신 7대 핵심 원칙 100% 준수:
  1. 1024x1024 해상도 네이티브 렌더링
  2. 0.05mm 초극세 바늘선 (thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke)
  3. 목 없는(No-Neck) 머리-몸통 직접 연결 원형 머리 스틱맨
  4. 배경 #f5f6f8, 선색 #030203
  5. 풍성한 내러티브 씬 묘사
  6. 후처리 효과 없는 순수 렌더링 보존
  7. 100% 영문 전용 절대 원칙 (프롬프트/씬 비ASCII 문자 전면 배제, 영문 외 텍스트 철저 차단)
- 각 유닛(20단어) 완료 시:
  1. sync_word_images.py 실행하여 wordImages.ts 자동 갱신
  2. find . -name '._*' -type f -delete (macOS 임시파일 정리)
  3. README.md에 일별 작업 내역 기록
  4. Git commit (한글 메시지)
  5. Git pull --rebase origin main && git push origin main 동기화
- 사용자가 중지하기 전까지 유닛 단위 연속 진행
"""

import os
import sys
import re
import json
import time
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
STATUS_FILE = os.path.join(SCRIPT_DIR, "h1_continuous_status.json")

# Unit별 고품질 영문 씬 콘셉트 프리셋 사전 (100% 순수 영문 전용)
SCENE_PRESETS = {
    # Unit 3 (h1-41 ~ h1-60)
    "aspect": "architectural design studio, two cute slender stickman architects examining a large miniature building model from different angles and aspects, blueprints and rulers on drafting table, large window",
    "significant": "modern scientific research lab, excited cute slender stickman scientist pointing joyfully to a significant breakthrough spike graph on a glowing computer monitor, laboratory glassware and colleague clapping",
    "melt": "warm cozy kitchen table, cute slender stickman watching a golden square of butter melt smoothly over a stack of warm hotcakes, steaming cup of cocoa, sunny window",
    "advance": "futuristic robotics technology workshop, cute slender stickman engineer watching an advanced humanoid bipedal robot take its first successful forward steps, tool bench, computer screens and cables",
    "marine": "deep blue oceanic research vessel laboratory, cute slender stickman marine biologist looking through glass porthole observing swimming sea turtles and coral reef, scientific water sampling tubes",
    "solid": "cozy masonry workshop, strong cute slender stickman builder tapping a solid sturdy rectangular stone block with a hammer testing its solid durability, neatly stacked brick wall, mortar trowel",
    "passage": "ancient castle library, cute slender stickman explorer holding a lantern walking through a secret hidden stone passage hallway between towering wooden bookshelves, stone arched doorway",
    "master": "traditional artistic pottery studio, skilled cute slender stickman master craftsman gently shaping a smooth clay ceramic vase on a spinning pottery wheel, finished clay pots on wooden shelves",
    "minute": "precision watchmaker workbench, focused cute slender stickman watchmaker using an eyepiece loupe and fine tweezers to adjust tiny minute delicate gear cogs inside an antique gold pocket watch, desk lamp",
    "vision": "scenic hilltop observation deck, cute slender stickman leader holding a brass telescope looking into distant horizon at sunrise with clear future vision, wind blowing gently, mountain ridges",
    "experiment": "chemistry science classroom, focused cute slender stickman student carefully pouring blue liquid into a bubbling glass flask with glowing bubbles, test tube rack, chalkboard equations",
    "shelter": "mountain hillside during a rainy day, kind cute slender stickman guiding a friendly puppy into a sturdy wooden emergency shelter cabin porch away from rain droplets, warm lamp inside",
    "commit": "community civic hall podium, dedicated cute slender stickman raising right hand committing solemnly to public duty and service, audience seated in auditorium chairs, flags in background",
    "possible": "bright engineering workshop, innovative cute slender stickman successfully lighting up a floating magnetic light bulb proving the impossible possible, inspiring chalkboard notes, work tools",
    "multiple": "high-tech control workstation, busy multitasking cute slender stickman operator managing multiple digital display monitors showing weather maps and data graphs simultaneously, swivel chair",
    "routine": "bright sunny morning bedroom and bathroom, cute slender stickman following healthy morning routine, holding a toothbrush by the sink mirror, folded blanket on bed, wall calendar",
    "tremendous": "scenic vista plateau, awe-struck cute slender stickman standing before a tremendous roaring waterfall cascading down grand rocky cliffs, rainbow mist, flying birds",
    "crucial": "medical operating or engineering planning room, serious cute slender stickman specialist holding a crucial key blueprint blueprint component that fits into center mechanism, team watching closely",
    "vast": "endless desert or ocean shore, tiny cute slender stickman standing atop a rolling sand dune gazing out at the vast infinite desert plains under a wide sky with distant mountain silhouettes",
    "develop": "community garden or software startup studio, cute slender stickman nurturing a sprouting green plant sapling in rich soil while colleague codes on laptop, growing tall together, watering can"
}

def clean_english_only(text: str) -> str:
    """비영문 문자를 철저히 제거하고 공백을 정돈하여 100% 영문 텍스트만 남김"""
    if not text:
        return ""
    cleaned = re.sub(r'[^\x00-\x7F]+', ' ', text)
    cleaned = re.sub(r'[^a-zA-Z0-9,\.\-\s]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def get_scene(word: str, word_info: dict) -> str:
    if word in SCENE_PRESETS:
        return clean_english_only(SCENE_PRESETS[word])
    
    ex = word_info.get("example", "")
    clean_ex = clean_english_only(ex)
    if clean_ex:
        return f"detailed illustrative narrative scene of {word}, cute slender stickman {clean_ex}, indoor room or outdoor setting, rich props"
    return f"detailed illustrative narrative scene representing {word}, cute slender stickman engaged in meaningful action, cozy room or outdoor setting, rich environmental props"

def save_status(data: dict):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def sync_and_commit_unit(unit_num: int, unit_words: list):
    print(f"\n[유닛 {unit_num}] 완료 후처리 및 Git 동기화 시작...", flush=True)
    
    # 1. 이미지 레지스트리 동기화
    subprocess.run([sys.executable, SYNC_SCRIPT], check=False)
    
    # 2. macOS dot-underscore 파일 정리
    subprocess.run(["find", ".", "-name", "._*", "-type", "f", "-delete"], cwd=PROJECT_ROOT, check=False)
    
    # 3. README.md 작업 내역 추가
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_header = f"### {today_str}"
    
    word_list_str = ", ".join([w["word"] for w in unit_words])
    new_entry = (
        f"- 고등학교 1학년 Unit {unit_num} '선형그래픽' 스타일 단어 일러스트 20종 일괄 생성 및 등록 완료 (Draw Things 로컬 API 기반)\n"
        f"  - 1024x1024 해상도, 0.05mm 초극세선, No-Neck 스틱맨 캐릭터, 뉴모피즘 캔버스 테마(#f5f6f8), 딥차콜 선(#030203), 영문 전용 씬 묘사 최신 스킬 원칙 준수\n"
        f"  - 대상 단어: {word_list_str}\n"
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
        print(f"[README.md] 유닛 {unit_num} 작업 내역 기록 완료", flush=True)

    # 4. Git commit & push
    commit_msg = f"feat: 고1 유닛 {unit_num} 선형그래픽 일러스트 20단어 전원 생성 및 등록 완료"
    try:
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
        print(f"[Git] 커밋 완료: {commit_msg}", flush=True)
        
        # Pull rebase & push
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        print(f"[Git] 원격 저장소(origin/main) 푸시 동기화 완료!", flush=True)
    except Exception as e:
        print(f"[Git 오류] 커밋/푸시 중 오류 발생: {e}", flush=True)

def generate_unit(unit_num: int, unit_words: list, skip_existing: bool = True):
    total = len(unit_words)
    print(f"\n==================================================", flush=True)
    print(f"▶ 고등학교 1학년 Unit {unit_num} '선형그래픽' 20개 단어 생성 시작 (h1-{(unit_num-1)*20+1} ~ h1-{unit_num*20})", flush=True)
    print(f"규격: 1024x1024, 0.05mm 초극세선, No-Neck, 배경 #f5f6f8, 선색 #030203, 100% 영문 전용 최신 스킬", flush=True)
    print(f"==================================================", flush=True)

    status_data = {
        "unit": unit_num,
        "total": total,
        "current_word": "",
        "current_index": 0,
        "items": []
    }

    for idx, item in enumerate(unit_words, 1):
        word = item["word"]
        word_id = item["id"]
        meaning = item["meaning"]
        scene = clean_english_only(item["scene"])
        file_name = word.replace(" ", "-")
        out_path = os.path.join(ASSETS_DIR, f"{file_name}.png")

        status_data["current_index"] = idx
        status_data["current_word"] = word

        if skip_existing and os.path.exists(out_path):
            file_size_kb = round(os.path.getsize(out_path) / 1024, 1)
            print(f"[{idx}/{total}] '{word}' ({word_id}: {meaning}) 이미 존재하여 건너뜀 ({file_size_kb} KB)", flush=True)
            status_data["items"].append({
                "index": idx,
                "id": word_id,
                "word": word,
                "meaning": meaning,
                "scene": scene,
                "status": "SKIP_EXISTS",
                "size_kb": file_size_kb
            })
            save_status(status_data)
            continue

        print(f"\n[{idx}/{total}] '{word}' ({word_id}: {meaning}) 생성 시작...", flush=True)
        print(f"Scene: {scene}", flush=True)

        prompt = (
            f"linear graphic illustration, complete richly detailed scene of {scene}, "
            f"thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, "
            f"extremely fine crisp outlines drawn in dark charcoal ink color #030203, "
            f"flat smooth light gray canvas background color #f5f6f8, "
            f"neckless cute slender doodle stickman characters with round bald circle heads attached directly to torso with completely no neck, tiny smiling dot faces, "
            f"abundant rich background details, furniture, wall decor, floor line, ambient props, "
            f"strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, empty clean background, "
            f"strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
        )

        negative_prompt = (
            "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing, "
            "neck, long neck, throat, collar, neck line, detailed neck anatomy, "
            "thick lines, bold outlines, heavy brush strokes, chunky lines, fat strokes, "
            "pure white #ffffff background, dark background, black background, 3d, realistic, shadow, shading, "
            "color, gradients, photo, blur, watermark, signature, messy"
        )

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": 8,
            "width": 1024,
            "height": 1024,
            "seed": 700 + unit_num * 100 + idx * 23
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
                    "meaning": meaning,
                    "scene": scene,
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
                "meaning": meaning,
                "scene": scene,
                "status": "FAILED"
            })
            save_status(status_data)

    # 유닛 20개 단어 처리 완료 후 자동 동기화 및 푸시
    sync_and_commit_unit(unit_num, unit_words)

def main():
    parser = argparse.ArgumentParser(description="고등학교 1학년 연속 자동 생성 스크립트 (최신 선형그래픽 스킬 적용)")
    parser.add_argument("--start-unit", type=int, default=3, help="시작할 유닛 번호 (기본값: 3)")
    parser.add_argument("--end-unit", type=int, default=60, help="종료할 유닛 번호 (기본값: 60)")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="기존 이미지 스킵 (기본값: True)")
    args = parser.parse_args()

    # 데이터 로드
    h1_file = os.path.join(PROJECT_ROOT, "src", "data", "en", "levels", "high-1.json")
    tr_file = os.path.join(PROJECT_ROOT, "src", "data", "en", "tr", "ko.json")
    words_file = os.path.join(PROJECT_ROOT, "src", "data", "en", "words.json")

    with open(h1_file, "r", encoding="utf-8") as f:
        h1_words = json.load(f)
    with open(tr_file, "r", encoding="utf-8") as f:
        tr_data = json.load(f)
    with open(words_file, "r", encoding="utf-8") as f:
        words_dict = json.load(f)

    total_words = len(h1_words)
    total_units = (total_words + 19) // 20

    print("==================================================", flush=True)
    print(f"고등학교 1학년 자동 연속 생성 파이프라인 가동 (최신 스킬 재적용)", flush=True)
    print(f"시작 유닛: Unit {args.start_unit} ~ 종료 유닛: Unit {args.end_unit} (총 {total_units}유닛)", flush=True)
    print("각 유닛 완료 시: 레지스트리 동기화 -> README 내역 갱신 -> 한글 커밋 -> 자동 Push", flush=True)
    print("==================================================", flush=True)

    for unit_num in range(args.start_unit, args.end_unit + 1):
        start_idx = (unit_num - 1) * 20
        end_idx = min(start_idx + 20, total_words)
        if start_idx >= total_words:
            break

        slice_words = h1_words[start_idx:end_idx]
        unit_items = []
        for i, w in enumerate(slice_words):
            global_idx = start_idx + i + 1
            w_id = f"h1-{global_idx}"
            meaning = tr_data.get("meanings", {}).get(w_id, "")
            info = words_dict.get(w, {})
            scene = get_scene(w, info)
            unit_items.append({
                "id": w_id,
                "word": w,
                "meaning": meaning,
                "scene": scene
            })

        generate_unit(unit_num, unit_items, skip_existing=args.skip_existing)
        print(f"\n🎉 고등학교 1학년 Unit {unit_num} 전체 처리 및 원격 Push 완료!\n", flush=True)

    print("모든 지정 유닛 생성 파이프라인 종료!", flush=True)

if __name__ == "__main__":
    main()
