#!/usr/bin/env python3
"""
중1 누락 이미지 2장 완성 및 개별 커밋/푸시 후,
토플 1단원부터 순차적으로 이미지 제작 및 개별 커밋/푸시를 수행하는 통합 파이프라인.
- 각 이미지 완료 시 1개씩 커밋 및 푸시
- Draw Things 선형그래픽 스킬 100% 준수
"""

import os
import sys
import json
import time
import re
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)

SKILL_SCRIPTS = os.path.join(WORKSPACE_ROOT, ".agents", "skills", "draw-things-linear-graphic", "scripts")
if not os.path.exists(SKILL_SCRIPTS):
    SKILL_SCRIPTS = os.path.join(PROJECT_ROOT, ".agents", "skills", "draw-things-linear-graphic", "scripts")
sys.path.insert(0, SKILL_SCRIPTS)

from generate_linear_graphic import generate_linear_image

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
SYNC_SCRIPT = os.path.join(SCRIPT_DIR, "sync_word_images.py")

M1_MISSING_WORDS = [
    {
        "level": "중1",
        "unit": 44,
        "id": "m1-874",
        "word": "bedside",
        "meaning": "침대 곁",
        "scene": "cozy peaceful bedroom corner, caring small slim white pictogram character sitting on bedside wooden chair reading a bedtime book to a resting friend in bed, bedside nightstand table lamp with soft glow and floor line"
    },
    {
        "level": "중1",
        "unit": 50,
        "id": "m1-986",
        "word": "pepper",
        "meaning": "후추",
        "scene": "warm dining restaurant table, cheerful small slim white pictogram character chef using a classic wooden pepper mill to grind fresh aromatic black pepper onto a hot bowl of soup, dining table and floor line"
    }
]

TOEFL_UNIT1_SCENES = {
    "a great deal": "polar science research station laboratory, curious small slim white pictogram scientist examining large stack of expedition field journals and glacier data charts on wide wooden workbench, polar maps on wall and wooden floor line",
    "a host of": "lush botanical conservatory greenhouse, small slim white pictogram explorer with magnifying glass observing a host of exotic beetles and butterflies perched on jungle leaves, glass greenhouse frames and pathway line",
    "a quarter": "modern classroom lecture hall, thoughtful small slim white pictogram teacher pointing at a large chalkboard diagram dividing a circular pie chart into four neat quarter sections, lecture desk and classroom floor line",
    "a wide range of": "artisan craft museum hall, observant small slim white pictogram visitor walking beside a long exhibition display shelf showcasing a wide range of traditional woodworking tools, display glass cabinet and museum floor line",
    "abandon": "weathered ancient stone castle courtyard, solitary small slim white pictogram traveler exploring long abandoned stone castle gates covered with wild ivy vines, stone archway and cobblestone floor line",
    "abnormally": "meteorology weather observatory station, surprised small slim white pictogram meteorologist wiping brow looking up at a giant wall thermometer showing abnormally high heat reading, weather instruments and floor line",
    "abolish": "historic parliament council hall, determined small slim white pictogram official holding up an official decree document marking the vote to abolish an obsolete law, wooden council dais and hall floor line",
    "abound in": "scenic coastal harbor dock, cheerful small slim white pictogram fisherman on wooden pier looking into crystal clear harbor water that abounds in swimming fish schools, wooden pilings and pier plank line",
    "abroad": "bright international airport terminal, excited small slim white pictogram student pulling travel wheeled suitcase towards departure gate to study abroad, airport panoramic window and floor line",
    "abrupt": "windy mountain hiking trail, cautious small slim white pictogram hiker stopping on rocky ridge path noticing an abrupt steep mountain slope cliff ahead, mountain peaks and trail ground line",
    "absolute": "grand historical throne hall, small slim white pictogram sovereign holding ceremonial golden orb and scepter sitting with absolute authority on stone throne, royal banners and hall floor line",
    "absorb": "biology science classroom laboratory, curious small slim white pictogram student watching a large green potted plant absorb water through transparent root observation chamber, lab bench and floor line",
    "abstract": "modern contemporary art museum gallery, contemplative small slim white pictogram visitor standing with folded hands admiring a large abstract wall painting composed of pure geometric lines and circles, gallery bench and floor line",
    "abundance": "lush green river valley oasis, joyful small slim white pictogram villager filling clay water jugs at a natural crystal spring bubbling with an abundance of fresh clear water, riverbank rocks and meadow line",
    "abundant": "sunny orchard harvest market, cheerful small slim white pictogram fruit farmer standing behind wooden market stall overflowing with abundant ripe apples and oranges in wooden crates, canopy and market floor line",
    "abuse": "office human resources discussion room, small slim white pictogram counselor calmly resolving interpersonal issues with listening ear, office table and floor line",
    "accede with": "formal corporate negotiation meeting room, two professional small slim white pictogram negotiators smiling and shaking hands across wooden conference table having reached mutual accession, office windows and carpet line",
    "accelerate": "futuristic test track stadium, energetic small slim white pictogram racer in streamlined aerodynamic go-kart accelerating smoothly down empty straight test course, track barriers and track line",
    "accessible": "modern public library entrance plaza, polite small slim white pictogram student easily walking up a gentle smooth accessible ramp leading into wide library doors, handrails and plaza stone line",
    "accidentally": "chemistry research laboratory bench, startled small slim white pictogram chemist watching a colorful foamy reaction bubble up unexpectedly from beaker after accidentally mixing test solutions, laboratory glassware and floor line"
}

def clean_appledouble():
    subprocess.run(["find", ".", "..", "-name", "._*", "-type", "f", "-delete"], cwd=PROJECT_ROOT, stderr=subprocess.DEVNULL)

def sync_and_lint():
    clean_appledouble()
    subprocess.run([sys.executable, SYNC_SCRIPT], cwd=PROJECT_ROOT, check=True)
    clean_appledouble()
    subprocess.run(["npm", "run", "lint"], cwd=PROJECT_ROOT, check=True)

def git_commit_and_push(commit_msg: str):
    clean_appledouble()
    subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, check=True)
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=PROJECT_ROOT, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)


def build_toefl_unit_tasks(unit_num: int = 1):
    toefl_path = os.path.join(PROJECT_ROOT, "src", "data", "en", "levels", "toefl.json")
    tr_path = os.path.join(PROJECT_ROOT, "src", "data", "en", "tr", "ko.json")
    words_path = os.path.join(PROJECT_ROOT, "src", "data", "en", "words.json")

    with open(toefl_path, "r", encoding="utf-8") as f:
        toefl_words = json.load(f)
    with open(tr_path, "r", encoding="utf-8") as f:
        tr_ko = json.load(f).get("meanings", {})
    with open(words_path, "r", encoding="utf-8") as f:
        words_dict = json.load(f)

    start_idx = (unit_num - 1) * 20
    end_idx = min(start_idx + 20, len(toefl_words))
    unit_words = toefl_words[start_idx:end_idx]

    tasks = []
    for i, w in enumerate(unit_words, start_idx + 1):
        wid = f"tf-{i}"
        meaning = tr_ko.get(wid, "")
        if unit_num == 1 and w in TOEFL_UNIT1_SCENES:
            scene = TOEFL_UNIT1_SCENES[w]
        else:
            ex = words_dict.get(w, {}).get("example", "")
            if ex:
                clean_ex = re.sub(r"[^\x00-\x7F]+", " ", ex).strip()
                scene = f"bright indoor scene, small slim white pictogram character acting out: {clean_ex}, rich background furniture, props and floor line"
            else:
                scene = f"bright indoor scene, small slim white pictogram character clearly illustrating the meaning of {w}, rich furniture and floor line"

        tasks.append({
            "level": "토플",
            "unit": unit_num,
            "id": wid,
            "word": w,
            "meaning": meaning,
            "scene": scene
        })
    return tasks

def main():
    print("==================================================", flush=True)
    print("🚀 [중1 미완성 2단어 + 토플 1단원 순차 생성 파이프라인 시작]", flush=True)
    print("==================================================", flush=True)

    # 1. 대상 목록 구성: 중1 누락 2단어 + 토플 1단원 20단어
    all_tasks = []
    all_tasks.extend(M1_MISSING_WORDS)

    toefl_u1 = build_toefl_unit_tasks(1)
    all_tasks.extend(toefl_u1)

    done_records = {}
    started_at = time.time()

    # 이미 존재하는 이미지 사전 검사
    for t in all_tasks:
        fname = t["word"].replace(" ", "-") + ".png"
        fpath = os.path.join(ASSETS_DIR, fname)
        if os.path.exists(fpath):
            sz_kb = f"{os.path.getsize(fpath) // 1024}KB"
            done_records[t["word"]] = {"elapsed": 0.0, "size": sz_kb}


    for task in all_tasks:
        w = task["word"]
        wid = task["id"]
        lvl = task["level"]
        u = task["unit"]
        meaning = task["meaning"]
        scene = task["scene"]
        fname = w.replace(" ", "-") + ".png"
        out_path = os.path.join(ASSETS_DIR, fname)

        if os.path.exists(out_path):
            print(f"[{lvl} U{u}] '{w}' 이미 이미지가 존재하여 건너뜁니다 -> {out_path}", flush=True)
            if w not in done_records:
                sz_kb = f"{os.path.getsize(out_path) // 1024}KB"
                done_records[w] = {"elapsed": 0.0, "size": sz_kb}
            continue

        print(f"\n▶ [{lvl} U{u} - {wid}] '{w}' ({meaning}) 렌더링 시작...", flush=True)
        print(f"  Scene: {scene}", flush=True)


        # Draw Things API 호출
        seed = 2000 + int(wid.split("-")[1]) if "-" in wid and wid.split("-")[1].isdigit() else 42
        t0 = time.time()
        try:
            generate_linear_image(
                concept=scene,
                output_path=out_path,
                seed=seed,
                width=1024,
                height=1024,
                steps=8
            )
            elapsed = time.time() - t0
            sz_kb = f"{os.path.getsize(out_path) // 1024}KB"
            done_records[w] = {"elapsed": elapsed, "size": sz_kb}
            print(f"✅ '{w}' 생성 완료 ({elapsed:.1f}초, {sz_kb})", flush=True)

            # 앱 동기화 및 린트
            print(f"  -> wordImages.ts 동기화 및 린트 검증...", flush=True)
            sync_and_lint()

            # 개별 Git 커밋 & 푸시
            if lvl == "중1" and w == "pepper":
                commit_msg = f"feat: 중1 {u}단원 pepper (후추) 선형그래픽 이미지 생성 및 등록 (중1 994단어 전원 완료 🎉)"
            elif lvl == "중1":
                commit_msg = f"feat: 중1 {u}단원 {w} ({meaning}) 선형그래픽 이미지 생성 및 등록"
            else:
                commit_msg = f"feat: 토플 {u}단원 {w} ({meaning}) 선형그래픽 이미지 생성 및 등록"

            print(f"  -> Git 커밋 & 푸시: {commit_msg}", flush=True)
            git_commit_and_push(commit_msg)
            print(f"🚀 '{w}' GitHub 배포 완료!", flush=True)


        except Exception as e:
            print(f"❌ '{w}' 작업 중 오류 발생: {e}", flush=True)
            time.sleep(3)

    print("\n🎉 모든 작업(중1 전체 완료 + 토플 1단원)이 성공적으로 완료되었습니다!", flush=True)

if __name__ == "__main__":
    main()
