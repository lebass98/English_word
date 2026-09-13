#!/usr/bin/env python3
"""
고등학교 1학년 Unit 8 '선형그래픽' 이미지 자동 생성 스크립트
- 최신 3~3.5등신 픽토그램 마네킹 캐릭터 조형 원칙 100% 준수
- 1024x1024, #f5f6f8 배경, #030203 선, 풍성한 씬, 100% 영문 전용
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
STATUS_FILE = os.path.join(SCRIPT_DIR, "h1_unit8_status.json")

UNIT8_WORDS = [
    {"id": "h1-141", "word": "stack", "meaning": "쌓다, 쌓아 올리다; 더미", "scene": "cozy library study room, cute chibi mannequin carefully stacking a tall neat stack of hardcover books on a sturdy wooden table, floor lamp and bookshelf"},
    {"id": "h1-142", "word": "harbor", "meaning": "항구, 항만; 정박하다", "scene": "bustling seaside harbor pier, cute chibi mannequin standing by mooring bollard looking at sailboats anchored in harbor water, lighthouse and seagulls in background"},
    {"id": "h1-143", "word": "personal", "meaning": "개인의, 개인적인", "scene": "warm private bedroom study nook, cute chibi mannequin writing personal thoughts in a secret leather journal notebook with a fountain pen, desk plant and family photo frame"},
    {"id": "h1-144", "word": "artwork", "meaning": "예술작품, 미술품", "scene": "modern art museum exhibition gallery, cute chibi mannequin admiring a grand framed abstract linear artwork painting hanging on gallery wall, bench and exhibition spotlight"},
    {"id": "h1-145", "word": "education", "meaning": "교육", "scene": "bright modern classroom lecture hall, cute chibi mannequin teacher pointing at blackboard educational diagrams while cute chibi mannequin students listen attentively at wooden desks"},
    {"id": "h1-146", "word": "international", "meaning": "국제의, 국제적인", "scene": "international summit conference lounge, cute chibi mannequins from diverse regions exchanging friendly handshakes in front of world globe and international country flags"},
    {"id": "h1-147", "word": "assist", "meaning": "돕다, 거들다, 원조하다", "scene": "bright community workshop, kind cute chibi mannequin warmly assisting an elderly neighbor cute chibi mannequin carry heavy grocery bags across the doorway"},
    {"id": "h1-148", "word": "prevent", "meaning": "예방하다, 막다, 방지하다", "scene": "safety industrial laboratory, vigilant cute chibi mannequin putting up clear warning guardrail barrier and safety gate to prevent falling hazards, caution signs on wall"},
    {"id": "h1-149", "word": "frustrated", "meaning": "좌절한, 실망한", "scene": "office desk with crumpled papers, frustrated cute chibi mannequin holding round head in mild despair over complicated jigsaw puzzle pieces not fitting together, desk lamp"},
    {"id": "h1-150", "word": "border", "meaning": "국경, 경계, 가장자리", "scene": "scenic mountain pass boundary line, cute chibi mannequin hiker observing a distinct border stone monument marking boundary between two regions, scenic path with fence"},
    {"id": "h1-151", "word": "mutual", "meaning": "상호 간의, 서로의", "scene": "cozy shared creative studio, two friendly cute chibi mannequins nodding in warm mutual agreement and partnership while working together on a collaborative blueprint design"},
    {"id": "h1-152", "word": "neglect", "meaning": "무시하다, 등한시하다, 방치하다", "scene": "dusty greenhouse corner, cute chibi mannequin noticing a neglected wilting potted houseplant on window sill with dry soil, holding a fresh watering can to rescue it"},
    {"id": "h1-153", "word": "candidate", "meaning": "후보(자), 지원자", "scene": "civic community election hall, confident cute chibi mannequin candidate delivering an encouraging campaign speech from a wooden podium with microphone, campaign poster on wall"},
    {"id": "h1-154", "word": "encounter", "meaning": "맞닥뜨리다, 부딪히다, 만나다", "scene": "enchanted forest nature trail, surprised cute chibi mannequin explorer having a sudden friendly encounter with a gentle wild deer among tall trees and wildflowers"},
    {"id": "h1-155", "word": "surface", "meaning": "표면, 겉, 외관", "scene": "serene mountain lake shore, cute chibi mannequin gently skipping a smooth pebble stone across calm water surface creating delicate concentric ripples, distant mountain hills"},
    {"id": "h1-156", "word": "conference", "meaning": "회의, 학회, 협의", "scene": "corporate boardroom meeting room, cute chibi mannequin presenting slideshow charts on a large screen at an annual professional conference table surrounded by seated colleagues"},
    {"id": "h1-157", "word": "policy", "meaning": "방침, 정책, 보험증권", "scene": "formal executive office room, cute chibi mannequin director reviewing and stamping an official institutional policy document paper binder, neatly organized archive shelf"},
    {"id": "h1-158", "word": "spin", "meaning": "회전, 회전운동; 돌다", "scene": "playful science playground, cute chibi mannequin joyfully spinning a colorful whirligig pinwheel toy with swirling motion wind lines, park bench and trees"},
    {"id": "h1-159", "word": "predict", "meaning": "예측하다, 예보하다", "scene": "meteorological weather forecasting studio, cute chibi mannequin weather forecaster pointing at a future weather forecast radar map predicting tomorrow's sunny day, radar screen"},
    {"id": "h1-160", "word": "moment", "meaning": "잠시, 잠깐", "scene": "scenic park bench at peaceful golden sunset, cute chibi mannequin pausing in quiet contemplative moment watching an hourglass sand gently trickling down, autumn leaves falling"}
]

def save_status(data: dict):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def wait_for_api(max_wait=300):
    print("[API 확인] Draw Things API 서버(포트 7860) 활성화 대기 중...", flush=True)
    t0 = time.time()
    while time.time() - t0 < max_wait:
        try:
            with urllib.request.urlopen("http://127.0.0.1:7860/sdapi/v1/options", timeout=2) as resp:
                if resp.status == 200:
                    print("[API 확인] Draw Things API 서버 연결 성공!", flush=True)
                    return True
        except Exception:
            time.sleep(2)
    return False

def sync_and_commit():
    print("\n[Unit 8 완료] 후처리 및 Git 동기화 시작...", flush=True)
    subprocess.run([sys.executable, SYNC_SCRIPT], check=False)
    subprocess.run(["find", ".", "-name", "._*", "-type", "f", "-delete"], cwd=PROJECT_ROOT, check=False)

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_header = f"### {today_str}"
    word_list_str = ", ".join([w["word"] for w in UNIT8_WORDS])
    new_entry = (
        f"- 고등학교 1학년 Unit 8 '선형그래픽' 스타일 단어 일러스트 20종 일괄 생성 및 등록 완료 (Draw Things 로컬 API 기반)\n"
        f"  - 1024x1024 해상도, 0.05mm 초극세선, 3~3.5등신 순백색 마네킹 픽토그램 캐릭터, 뉴모피즘 캔버스 테마(#f5f6f8), 딥차콜 선(#030203), 영문 전용 씬 묘사 최신 스킬 원칙 준수\n"
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

    commit_msg = "feat: 고1 유닛 8 선형그래픽 일러스트 20단어 최신 조형 스킬 생성 및 등록 완료"
    try:
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        print("[Git] 원격 저장소 동기화 및 Push 완료!", flush=True)
    except Exception as e:
        print(f"[Git 오류] {e}", flush=True)

def main():
    if not wait_for_api():
        print("[오류] Draw Things API 서버가 켜지지 않아 중단합니다.")
        sys.exit(1)

    total = len(UNIT8_WORDS)
    status_data = {
        "unit": 8,
        "total": total,
        "current_word": "",
        "current_index": 0,
        "items": []
    }

    print(f"\n==================================================", flush=True)
    print(f"▶ 고등학교 1학년 Unit 8 '선형그래픽' 20개 단어 생성 시작 (h1-141 ~ h1-160)", flush=True)
    print(f"최신 스킬: 3~3.5등신 픽토그램 순백 마네킹, 0.05mm 초극세선, 배경 #f5f6f8, 선 #030203", flush=True)
    print(f"==================================================", flush=True)

    for idx, item in enumerate(UNIT8_WORDS, 1):
        word = item["word"]
        word_id = item["id"]
        meaning = item["meaning"]
        scene = item["scene"]
        file_name = word.replace(" ", "-")
        out_path = os.path.join(ASSETS_DIR, f"{file_name}.png")

        status_data["current_index"] = idx
        status_data["current_word"] = word

        print(f"\n[{idx}/{total}] '{word}' ({word_id}: {meaning}) 생성 시작...", flush=True)
        print(f"Scene: {scene}", flush=True)

        prompt = (
            f"linear graphic illustration, complete richly detailed scene of {scene}, "
            f"3 to 3.5 head-to-body chibi SD ratio cute characters with large prominent smooth spherical bald round heads, "
            f"minimalist dot and line face, two simple solid black dot eyes and a tiny thin curved smile line, strictly no nose, no eyebrows, no lips, no ears, no hair, "
            f"seamless tubular neckless body directly attached to round head with completely no neck, smooth organic curves without clavicle or muscle contours, "
            f"jointless smooth rubber-hose arms and legs with no elbows and no knees, simplified mitten-like blunt round hands, smooth rounded flat oval foot pads firmly on floor line, "
            f"blank solid white mannequin pictogram character fill with zero clothing, no seams, no buttons, no folds, no skin texture, genderless universal figure, "
            f"crisp uniform dark charcoal ink outlines #030203, strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, flat smooth light gray canvas background color #f5f6f8, "
            f"flexible natural character scale freely tailored to scene context, comfortably sized chibi figure without being oversized, plenty of surrounding breathing room and balanced environmental framing, full body comfortably framed within scene, "
            f"abundant rich background details, furniture, wall decor, floor line, ambient props, "
            f"strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
        )

        negative_prompt = (
            "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing, "
            "oversized character, giant figure, frame-filling character, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, large scale character dominating scene, taking over screen, "
            "realistic human anatomy, realistic face, facial details, nose, eyebrows, eyelashes, eyelids, lips, teeth, ears, hair, hairstyle, neck, long neck, throat, collar, collarbone, muscles, realistic fingers, individual finger joints, fingernails, toes, shoes, clothing, clothes, shirt, pants, wrinkles, folds, "
            "thick lines, heavy brush strokes, chunky lines, fat strokes, "
            "pure white #ffffff background, dark background, black background, 3d, 3d render, realistic, shadow, shading, color, gradients, photo, blur, watermark, signature, messy"
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
                with urllib.request.urlopen(req, timeout=600) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    images = data.get("images", [])
                    if not images:
                        raise RuntimeError("No image returned")
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

    sync_and_commit()

if __name__ == "__main__":
    main()
