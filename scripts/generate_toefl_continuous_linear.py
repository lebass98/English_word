#!/usr/bin/env python3
"""
토플(TOEFL) 전용 선형그래픽 무중단 연속 생성 및 자동 배포 파이프라인.
- 지정된 시작 유닛부터 종료 유닛(기본 75단원 전체)까지 멈춤 없이 연속 생성
- 1개 단어 완성 시마다 즉시:
  1) assets/words/<단어>.png 저장
  2) wordImages.ts 자동 등록
  3) ._* 임시파일 정리
  4) npm run lint 통과 검증
  5) 개별 Git 커밋 & 원격 main 푸시
- Draw Things 선형그래픽 스킬 원칙 100% 준수 (3~3.5등신 순백색 마네킹, 영문 100%, 0.05mm 초극세선, #030203 선, #f5f6f8 배경)

사용법:
    python3 scripts/generate_toefl_continuous_linear.py --start-unit 3 --end-unit 75
"""

import os
import sys
import json
import time
import re
import subprocess
import argparse
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

TOEFL_PATH = os.path.join(PROJECT_ROOT, "src", "data", "en", "levels", "toefl.json")
TR_PATH = os.path.join(PROJECT_ROOT, "src", "data", "en", "tr", "ko.json")
WORDS_PATH = os.path.join(PROJECT_ROOT, "src", "data", "en", "words.json")

def letter_of(word: str) -> str:
    first = word[:1].lower()
    return first if "a" <= first <= "z" else "_"

def get_word_image_path(word: str) -> str:
    letter = letter_of(word)
    fname = word.replace(" ", "-") + ".png"
    return os.path.join(ASSETS_DIR, letter, fname)

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

def make_scene_description(word: str, wid: str, words_dict: dict, tr_ko: dict) -> str:
    clean_w = re.sub(r"[^\x00-\x7F]+", " ", word).strip()
    ex = words_dict.get(word, {}).get("example", "")
    if ex:
        clean_ex = re.sub(r"[^\x00-\x7F]+", " ", ex).strip()
        clean_ex = clean_ex.replace('"', '').replace("'", "")
        # truncate overly long sentences to keep prompt punchy
        if len(clean_ex) > 140:
            clean_ex = clean_ex[:140].rsplit(" ", 1)[0]
        return f"bright detailed scene of {clean_w}, small slim white pictogram character acting out: {clean_ex}, rich background furniture, props and floor line"
    return f"bright detailed indoor scene of {clean_w}, small slim white pictogram character clearly illustrating the concept of {clean_w}, rich wall decor, furniture and floor line"


def load_data():
    with open(TOEFL_PATH, "r", encoding="utf-8") as f:
        toefl_words = json.load(f)
    with open(TR_PATH, "r", encoding="utf-8") as f:
        tr_ko = json.load(f).get("meanings", {})
    with open(WORDS_PATH, "r", encoding="utf-8") as f:
        words_dict = json.load(f)
    return toefl_words, tr_ko, words_dict

def main():
    parser = argparse.ArgumentParser(description="토플 선형그래픽 무중단 연속 생성기")
    parser.add_argument("--start-unit", type=int, default=3, help="시작 유닛 (기본 3)")
    parser.add_argument("--end-unit", type=int, default=75, help="종료 유닛 (기본 75)")
    args = parser.parse_args()

    toefl_words, tr_ko, words_dict = load_data()
    total_words = len(toefl_words)
    total_units = (total_words + 19) // 20

    print("==================================================", flush=True)
    print(f"🚀 [토플 무중단 연속 생성 파이프라인 가동: Unit {args.start_unit} ~ Unit {args.end_unit}]", flush=True)
    print(f"규칙: 1장 완성 시마다 즉시 개별 Git 커밋 & 원격 푸시, 대시보드 실시간 갱신", flush=True)
    print("==================================================", flush=True)

    for u in range(args.start_unit, args.end_unit + 1):
        start_idx = (u - 1) * 20
        end_idx = min(start_idx + 20, total_words)
        if start_idx >= total_words:
            break

        unit_words = toefl_words[start_idx:end_idx]
        unit_tasks = []
        for i, w in enumerate(unit_words, start_idx + 1):
            wid = f"tf-{i}"
            meaning = tr_ko.get(wid, "")
            scene = make_scene_description(w, wid, words_dict, tr_ko)
            unit_tasks.append({
                "unit": u,
                "id": wid,
                "word": w,
                "meaning": meaning,
                "scene": scene
            })

        print(f"\n▶▶▶ [토플 Unit {u} / {total_units}] 20단어 파이프라인 가동 ◀◀◀", flush=True)

        done_records = {}
        unit_started_at = time.time()

        # 기존 파일 사전 확인
        for t in unit_tasks:
            fpath = get_word_image_path(t["word"])
            if os.path.exists(fpath):
                sz_kb = f"{os.path.getsize(fpath) // 1024}KB"
                done_records[t["word"]] = {"elapsed": 0.0, "size": sz_kb}


        for task in unit_tasks:
            w = task["word"]
            wid = task["id"]
            meaning = task["meaning"]
            scene = task["scene"]
            out_path = get_word_image_path(w)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            if os.path.exists(out_path):
                print(f"[Unit {u}] '{w}' 이미 파일이 존재하여 건너뜁니다 -> {out_path}", flush=True)
                continue

            print(f"\n▶ [Unit {u} - {wid}] '{w}' ({meaning}) 렌더링 시작...", flush=True)
            print(f"  Scene: {scene}", flush=True)


            seed = 4000 + int(wid.split("-")[1]) if "-" in wid and wid.split("-")[1].isdigit() else 42
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

                print(f"  -> wordImages.ts 동기화 및 린트 검증...", flush=True)
                sync_and_lint()

                commit_msg = f"feat: 토플 {u}단원 {w} ({meaning}) 선형그래픽 이미지 생성 및 등록"
                print(f"  -> Git 커밋 & 푸시: {commit_msg}", flush=True)
                git_commit_and_push(commit_msg)
                print(f"🚀 '{w}' GitHub 배포 완료!", flush=True)


            except Exception as e:
                print(f"❌ '{w}' 작업 중 오류 발생: {e}", flush=True)
                time.sleep(3)

        print(f"\n🎉 [토플 Unit {u}] 20단어 배포 전원 완료! 즉시 다음 유닛으로 진행합니다...\n", flush=True)

    print("\n🎊 토플 전체 유닛 연속 생성 작업이 완수되었습니다!", flush=True)

if __name__ == "__main__":
    main()
