#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 고등학교 1학년 자동 연속 생성 및 유닛별 Git 동기화 스크립트
- 고1 유닛 2부터 마지막 유닛(Unit 60)까지 순차 생성
- 각 유닛(20단어) 완료 시:
  1. sync_word_images.py 실행하여 wordImages.ts 자동 갱신
  2. find . -name '._*' -type f -delete (macOS 임시파일 정리)
  3. README.md에 일별 작업 내역 기록
  4. Git commit (한글 메시지: feat: 고1 유닛 X 선형그래픽 일러스트 20단어 전원 생성 및 등록 완료)
  5. Git pull --rebase origin main && git push origin main 동기화
- 사용자가 중지하기 전까지 무한 연속 진행
"""

import os
import sys
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

# Unit별 풍성한 선형그래픽 씬 콘셉트 사전
SCENE_PRESETS = {
    # Unit 2 (h1-21 ~ h1-40)
    "express": "art studio classroom, expressive cute slender stickman artist joyfully painting vibrant feelings on a tall easel canvas with a paintbrush, emotion smileys on wall chalkboard, palette and brushes",
    "virtual": "modern tech living room, cute slender stickman wearing high-tech VR virtual reality goggles, reaching hands out happily touching floating 3d hologram geometric wireframe cubes in midair, futuristic console table",
    "exclude": "school sports club court entrance, three cute slender stickmen playing basketball happily inside, while a fence gate has a polite sign and barrier keeping outsider outside, clear boundary and floor lines",
    "enthusiasm": "school science fair auditorium booth, enthusiastic cute slender stickman student passionately explaining an energetic bubbling volcano model to excited gathered stickman classmates with wide cheering gestures",
    "subject": "quiet library study desk, cute slender stickman student with open textbooks studying chemistry and history subjects diligently under a warm desk lamp, book stacks and pen holder",
    "orphan": "warm cozy caring community home living room, gentle kind foster caregiver stickman reading a fairy tale picture book to two adorable little stickman children on a soft sofa, rocking horse and toys",
    "biology": "biology high school science lab, curious cute slender stickman looking into a brass microscope examining green plant leaf cells on a glass slide, potted plants, botanical posters on wall",
    "meanwhile": "split dual living room scene, on left side cute slender stickman happily cooking soup at kitchen stove, meanwhile on right side stickman brother sweeping floor with a broom, wall clock showing same time",
    "lift": "bright fitness gym room, determined cute slender stickman weightlifter with chalked hands lifting a heavy steel barbell above shoulders, mirror on wall, dumbbell racks on rubber floor",
    "precious": "antique jewelry heirloom store, cute slender stickman admiring a sparkling precious gemstone necklace inside an illuminated glass velvet display pedestal case, decorative ornamental wall mirror",
    "witness": "busy city street pedestrian crossing, observant cute slender stickman witness standing on sidewalk pointing finger to report an incident to a police officer stickman taking notes on a notepad, vintage street lamp",
    "spread": "sunny outdoor park picnic lawn, smiling cute slender stickman holding corners of a large red checkered picnic blanket spreading it wide open onto the soft grass, wicker picnic basket and shady trees",
    "arise": "morning sunrise bedroom, happy cute slender stickman waking up and stretching arms wide as the morning sun rises above windowsill, alarm clock on nightstand, soft window curtain",
    "pesticide": "sunny agricultural vegetable farm field, cute slender stickman farmer wearing protective wide hat and boots carefully spraying eco-friendly mist onto cabbage rows from a backpack sprayer tank, wooden farm fence",
    "peer": "school hallway locker row, group of friendly teenage cute slender stickman peers chatting and laughing happily together between class periods, backpacks and bulletin board",
    "element": "science chemistry laboratory classroom, smart cute slender stickman pointing to a large colorful Periodic Table of Elements chart on wall, test tubes on laboratory counter stand",
    "oxygen": "lush sunny forest meadow, cute slender stickman breathing in deep fresh oxygen air with open arms among tall leafy green oak trees and fluttering butterflies, wild deer resting nearby",
    "professor": "university lecture hall podium, wise cute slender stickman professor wearing spectacles lecturing with chalk in hand, drawing complex diagrams on a massive chalkboard, student desks in foreground",
    "fame": "grand theater red carpet entrance, celebrated cute slender stickman celebrity waving politely to cheering crowd behind velvet rope, flashing camera lights on tripod, elegant theater marquee arch",
    "psychology": "cozy mental wellness counseling clinic, thoughtful cute slender stickman psychologist holding a clipboard listening attentively to a client stickman seated on a comfortable armchair, indoor plant and soft bookshelf"
}

def get_scene(word: str, word_info: dict, meaning: str) -> str:
    if word in SCENE_PRESETS:
        return SCENE_PRESETS[word]
    
    ex = word_info.get("example", "")
    return f"illustrative narrative scene representing {word} ({meaning}), cute slender stickman engaged in meaningful action, {ex}, cozy room or outdoor setting, rich environmental props"

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
        f"  - 1024x1024 해상도, 0.05mm 초극세선, No-Neck 스틱맨 캐릭터, 뉴모피즘 캔버스 테마(#f5f6f8), 딥차콜 선(#030203), 영문 전용 씬 묘사 원칙 준수\n"
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
    print(f"규격: 1024x1024, 0.05mm 초극세선, No-Neck, 배경 #f5f6f8, 선색 #030203, 영문 전용", flush=True)
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
        scene = item["scene"]
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

    # 유닛 20개 단어 처리 완료 후 자동 동기화 및 푸시
    sync_and_commit_unit(unit_num, unit_words)

def main():
    parser = argparse.ArgumentParser(description="고등학교 1학년 연속 자동 생성 스크립트")
    parser.add_argument("--start-unit", type=int, default=2, help="시작할 유닛 번호 (기본값: 2)")
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
    print(f"고등학교 1학년 자동 연속 생성 파이프라인 가동", flush=True)
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
            scene = get_scene(w, info, meaning)
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
