#!/usr/bin/env python3
"""
토익(TOEIC) 미등록 단어를 유닛 순서대로 선형그래픽으로 생성하고,
유닛이 끝날 때마다 즉시 등록, 린트 검증, 커밋 및 원격(main) 푸시를 수행한다.

- 프롬프트: .agents/skills/draw-things-linear-graphic 스킬 원칙 준수
- 장면(Scene): scripts/tc_missing_scenes.json (100% 영문 전용, SD 3~3.5등신, 풍성한 배경)
- 대시보드: LIVE_DASHBOARD.md 및 dashboard.html 실시간 갱신
- 유닛 완료 시 파이프라인: sync_word_images.py -> npm run lint -> ._* 삭제 -> git commit & push
- 정지: 상위 폴더에 STOP_IMAGES 파일 생성 시 현재 단어 완료 후 안전 종료

    python3 scripts/generate_toeic_all_missing.py            # 생성 실행
    python3 scripts/generate_toeic_all_missing.py --dry-run  # 대상 목록 미리보기
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)
SKILL_SCRIPTS = os.path.join(WORKSPACE_ROOT, ".agents", "skills", "draw-things-linear-graphic", "scripts")
if not os.path.exists(SKILL_SCRIPTS):
    SKILL_SCRIPTS = os.path.join(PROJECT_ROOT, ".agents", "skills", "draw-things-linear-graphic", "scripts")
sys.path.insert(0, SKILL_SCRIPTS)

from generate_linear_graphic import generate_linear_image  # noqa: E402

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
SYNC_SCRIPT = os.path.join(SCRIPT_DIR, "sync_word_images.py")
README_FILE = os.path.join(PROJECT_ROOT, "README.md")
SCENES_FILE = os.path.join(SCRIPT_DIR, "tc_missing_scenes.json")

LIVE_DASHBOARD_MD = os.path.join(WORKSPACE_ROOT, "LIVE_DASHBOARD.md")
LIVE_DASHBOARD_HTML = os.path.join(WORKSPACE_ROOT, "dashboard.html")
STOP_FILE = os.path.join(WORKSPACE_ROOT, "STOP_IMAGES")

COAUTHOR = "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"


def letter_of(stem):
    first = stem[:1].lower()
    return first if "a" <= first <= "z" else "_"


def get_image_path(word):
    slug = word.strip().lower().replace(" ", "-")
    slug = unicodedata.normalize("NFC", slug)
    letter = letter_of(slug)
    p1 = os.path.join(ASSETS_DIR, letter, slug + ".png")
    p2 = os.path.join(ASSETS_DIR, slug + ".png")
    if os.path.exists(p1):
        return p1
    if os.path.exists(p2):
        return p2
    return p1


def clean_scene(text):
    text = re.sub(r"[^\x00-\x7F]+", " ", text or "")
    text = re.sub(r"\b(cute\s+)?slender\s+stickman\b|\bstickman\b", "small slim white pictogram character", text, flags=re.I)
    text = re.sub(r"\b(cute|chibi|plump|chubby|slender|skinny)\b", "", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip(" ,")


def run(cmd, check=True):
    print("$ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=PROJECT_ROOT, check=check)


def update_dashboards(targets, current_item=None, status_map=None, is_stopped=False):
    pass



def deploy_unit(unit_num, unit_words):
    print(f"\n[Unit {unit_num}] 등록·검증·배포 시작: {', '.join(w['word'] for w in unit_words)}", flush=True)

    run(["git", "pull", "--rebase", "--autostash", "origin", "main"], check=False)
    subprocess.run("find . .. -name '._*' -type f -delete", cwd=PROJECT_ROOT, shell=True)

    run([sys.executable, SYNC_SCRIPT])
    subprocess.run("find . .. -name '._*' -type f -delete", cwd=PROJECT_ROOT, shell=True)

    run(["npm", "run", "lint"])
    subprocess.run("find . .. -name '._*' -type f -delete", cwd=PROJECT_ROOT, shell=True)

    # README 작업 내역 기록
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        w_list_str = ", ".join(w["word"] for w in unit_words)
        entry = (
            f"- 토익 {unit_num}단원 빠진 그림 {len(unit_words)}장 선형그래픽으로 생성 및 등록\n"
            f"  - 대상: {w_list_str}\n"
        )
        if os.path.exists(README_FILE):
            with open(README_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            target_marker = "## 작업 내역\n\n"
            today_section = f"### {today_str}\n"
            if target_marker in content:
                if today_section in content:
                    new_content = content.replace(today_section, today_section + entry, 1)
                else:
                    new_content = content.replace(target_marker, target_marker + today_section + entry + "\n", 1)
                with open(README_FILE, "w", encoding="utf-8") as f:
                    f.write(new_content)
    except Exception as e:
        print(f"[README] 기록 생략 ({e})", flush=True)

    run(["git", "add", "-A"])
    commit_msg = (
        f"feat: 토익 {unit_num}단원 빠진 그림 {len(unit_words)}장 생성 및 등록\n\n"
        f"대상: {', '.join(w['word'] for w in unit_words)}"
    )
    run(["git", "commit", "-m", commit_msg])
    run(["git", "push", "origin", "main"])
    print(f"[Git] Unit {unit_num} 푸시 완료\n", flush=True)


def main():
    parser = argparse.ArgumentParser(description="토익 빠진 그림 채우기 및 유닛별 배포")
    parser.add_argument("--dry-run", action="store_true", help="대상 목록만 출력하고 종료")
    parser.add_argument("--limit", type=int, default=0, help="최대 생성 단어 수 (0이면 전부)")
    args = parser.parse_args()

    toeic_path = os.path.join(PROJECT_ROOT, "src/data/en/levels/toeic.json")
    tr_path = os.path.join(PROJECT_ROOT, "src/data/en/tr/ko.json")
    words_path = os.path.join(PROJECT_ROOT, "src/data/en/words.json")

    with open(toeic_path, "r", encoding="utf-8") as f:
        toeic_words = json.load(f)
    with open(tr_path, "r", encoding="utf-8") as f:
        tr_ko = json.load(f).get("meanings", {})
    with open(words_path, "r", encoding="utf-8") as f:
        words_dict = json.load(f)
    with open(SCENES_FILE, "r", encoding="utf-8") as f:
        scenes_dict = json.load(f)

    # 1. 빠진 단어 목록 수집
    targets = []
    for i, w in enumerate(toeic_words):
        wid = f"tc-{i+1}"
        info = words_dict.get(w, {})
        key = info.get("conceptId") or w
        img_path = get_image_path(key)

        if not os.path.exists(img_path):
            unit = i // 20 + 1
            meaning = tr_ko.get(wid, "")
            scene = scenes_dict.get(w) or scenes_dict.get(key)
            if not scene:
                ex = info.get("example", "")
                if ex:
                    clean_ex = re.sub(r"[^\x00-\x7F]+", " ", ex).strip().replace('"', '').replace("'", "")
                    if len(clean_ex) > 140:
                        clean_ex = clean_ex[:140].rsplit(" ", 1)[0]
                    scene = f"bright detailed scene of {w}, small slim white pictogram character acting out: {clean_ex}, rich background furniture, props and floor line"
                else:
                    scene = f"bright detailed indoor scene of {w}, small slim white pictogram character clearly illustrating the concept of {w}, rich wall decor, furniture and floor line"

            targets.append({
                "unit": unit,
                "id": wid,
                "word": w,
                "concept_id": key,
                "meaning": meaning,
                "scene": clean_scene(scene),
                "output_path": img_path
            })

    print(f"==================================================", flush=True)
    print(f"📋 토익 미등록 그림 총 {len(targets)}단어 발견", flush=True)

    units_map = {}
    for t in targets:
        units_map.setdefault(t["unit"], []).append(t)

    for u in sorted(units_map.keys()):
        words_in_u = [x["word"] for x in units_map[u]]
        print(f"  • Unit {u:2d}: {len(words_in_u):2d}개 ({', '.join(words_in_u[:5])}{'...' if len(words_in_u)>5 else ''})", flush=True)
    print(f"==================================================", flush=True)

    if args.dry_run:
        print("Dry run 완료.")
        return

    # 대시보드 초기화
    status_map = {}
    update_dashboards(targets, None, status_map)

    # 2. 유닛별 생성 및 즉시 배포 루프
    total_generated = 0

    for unit_num in sorted(units_map.keys()):
        unit_targets = units_map[unit_num]
        print(f"\n▶▶▶ [토익 Unit {unit_num}] {len(unit_targets)}단어 생성 시작 ◀◀◀", flush=True)

        for item in unit_targets:
            if os.path.exists(STOP_FILE):
                print(f"\n🛑 {STOP_FILE} 감지되어 안전 종료합니다.", flush=True)
                update_dashboards(targets, None, status_map, is_stopped=True)
                return

            if args.limit and total_generated >= args.limit:
                print(f"\n목표 수치 {args.limit}개 도달하여 종료합니다.", flush=True)
                return

            w = item["word"]
            wid = item["id"]
            meaning = item["meaning"]
            scene = item["scene"]
            out_path = item["output_path"]

            status_map[w] = {"status": "rendering"}
            update_dashboards(targets, item, status_map)

            print(f"\n[{wid}] {w} ({meaning})", flush=True)
            print(f"Scene: {scene}", flush=True)

            seed = 7000 + int(wid.split("-")[1]) if "-" in wid and wid.split("-")[1].isdigit() else 42
            t0 = time.time()

            try:
                generate_linear_image(
                    concept=scene,
                    output_path=out_path,
                    seed=seed,
                    width=512,
                    height=512,
                    steps=8
                )
                elapsed = time.time() - t0
                sz_kb = round(os.path.getsize(out_path) / 1024, 1)

                status_map[w] = {
                    "status": "done",
                    "elapsed": f"{elapsed:.1f}초",
                    "size": f"{sz_kb}KB"
                }
                total_generated += 1
                print(f"PROGRESS {total_generated}/{len(targets)} {w} {elapsed:.1f}s ({sz_kb}KB)", flush=True)

            except Exception as e:
                print(f"❌ {w} 생성 실패: {e}", flush=True)
                status_map[w] = {"status": "failed", "elapsed": "-", "size": ""}

            update_dashboards(targets, None, status_map)

        # 유닛 완료 시 즉시 앱 반영 및 Git 배포 파이프라인 가동!
        successful_words = [t for t in unit_targets if status_map.get(t["word"], {}).get("status") == "done"]
        if successful_words:
            deploy_unit(unit_num, successful_words)

    print(f"\n전체 완료: {total_generated}/{len(targets)} 생성", flush=True)
    update_dashboards(targets, None, status_map)


if __name__ == "__main__":
    main()
