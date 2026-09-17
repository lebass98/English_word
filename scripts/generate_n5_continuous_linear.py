#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 일본어 JLPT N5 단어 자동 연속 생성 및 유닛별 Git 동기화 스크립트
- 대상: JLPT N5 단어 (총 556개, 유닛당 20개씩 총 28개 유닛)
- 유닛에서 멈추지 않고 다음 유닛으로 자동 연속 진행
- 최신 선형그래픽 조형 6대 원칙 + 2026-09-13/14 개정 완벽 준수:
  1. 스킬 기본 해상도(현재 512x512, IMAGE_SIZE 로 변경 가능)
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
  6. 다음 유닛으로 멈추지 않고 자동 계속 진행
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
SCENES_FILE = os.path.join(SCRIPT_DIR, "n5_scenes.json")
# 프롬프트는 여기서 따로 들고 있지 않고 스킬 스크립트를 그대로 쓴다 (스킬이 바뀌면 자동 반영)
sys.path.insert(0, os.path.join(PROJECT_ROOT, ".agents", "skills", "draw-things-linear-graphic", "scripts"))
from generate_linear_graphic import generate_linear_image  # noqa: E402
REGENERATE = False  # --regenerate 로 켜면 이미 있는 그림도 다시 그린다

def load_scenes_db():
    if os.path.exists(SCENES_FILE):
        with open(SCENES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

N5_SCENES = load_scenes_db()

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
    out_path, letter, key = get_asset_path(word, cid)

    # 이미 파일이 존재하거나 키가 등록되어 있으면 건너뜀
    if not REGENERATE:
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            return True, "already_exists"
        if word in registered_keys or cid in registered_keys:
            return True, "already_registered"

    # 영문 씬 가져오기
    scene = N5_SCENES.get(word) or N5_SCENES.get(cid)
    if not scene:
        en_hint = clean_english_only(cid) if (cid and cid != word) else "daily life action"
        scene = f"bright lively scene illustrating {en_hint}, energetic character in dynamic action pose with motion lines, rich background details, furniture and floor line"

    clean_scene = clean_english_only(scene)
    if not clean_scene:
        clean_scene = "active character engaging in an exciting energetic movement with motion lines in a well-furnished room with floor line"

    seed = 3000 + item["idx"] * 19
    size = int(os.environ.get("IMAGE_SIZE", "512"))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    for attempt in range(1, 4):
        try:
            t0 = time.time()
            generate_linear_image(clean_scene, out_path, seed=seed, width=size, height=size)
            if os.path.getsize(out_path) < 1000:
                raise RuntimeError("파일이 너무 작음")
            elapsed = time.time() - t0
            print(f"[{word}] 생성 완료 ({elapsed:.1f}초) -> {out_path}", flush=True)
            return True, "generated"
        except Exception as e:
            print(f"[{word}] 시도 {attempt} 실패: {e}", flush=True)
            time.sleep(3)

    return False, "failed"

def resolve_readme_conflict():
    """README 충돌은 같은 날짜에 양쪽이 줄을 넣은 것뿐이라 두 쪽을 모두 남긴다 (2026-09-13 사용자 승인)"""
    with open(README_FILE, encoding="utf-8") as f:
        s = f.read()
    s2, n = re.subn(r"<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n",
                    lambda m: m.group(1).rstrip("\n") + "\n" + m.group(2).rstrip("\n") + "\n", s, flags=re.S)
    if re.search(r"^(<<<<<<<|=======|>>>>>>>)", s2, re.M):
        return False
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(s2)
    subprocess.run(["git", "add", "--", "README.md"], cwd=PROJECT_ROOT)
    return n > 0


def git(*args, check=False):
    return subprocess.run(["git", *args], cwd=PROJECT_ROOT, check=check, capture_output=True, text=True)


def rebasing():
    d = git("rev-parse", "--git-dir").stdout.strip()
    return bool(d) and (os.path.isdir(os.path.join(PROJECT_ROOT, d, "rebase-merge")) or os.path.isdir(os.path.join(PROJECT_ROOT, d, "rebase-apply")))


def pull_rebase():
    """받아서 rebase. README 만 충돌하면 두 쪽을 남기고 이어 간다. 성공이면 True"""
    subprocess.run(["find", ".", "-name", "._*", "-type", "f", "-not", "-path", "./node_modules/*", "-delete"], cwd=PROJECT_ROOT)
    git("pull", "--rebase", "--autostash", "origin", "main")
    for _ in range(5):
        if not rebasing():
            return True
        files = [x for x in git("diff", "--name-only", "--diff-filter=U").stdout.splitlines() if x]
        if files != ["README.md"] or not resolve_readme_conflict():
            break
        git("-c", "core.editor=true", "rebase", "--continue")
    if rebasing():
        files = git("diff", "--name-only", "--diff-filter=U").stdout.split()
        git("rebase", "--abort")
        print(f"[Git] 충돌로 중단 ({', '.join(files) or '원인 불명'}). 커밋은 로컬에 남아 있음", file=sys.stderr, flush=True)
        return False
    return True


def sync_and_commit(unit_num: int, words_summary: str):
    """단어 등록, 린트, README 기록, 커밋 및 푸시 동기화"""
    print(f"\n[유닛 {unit_num} 동기화 시작]", flush=True)

    # 0. 다른 컴퓨터도 같은 날짜 README 에 줄을 넣으므로, README 를 고치기 전에 먼저 받는다
    if not pull_rebase():
        return

    # 1. sync_word_images.py 실행
    subprocess.run([sys.executable, SYNC_SCRIPT], check=True)

    # 2. macOS 임시파일 제거
    subprocess.run(["find", ".", "-name", "._*", "-type", "f", "-not", "-path", "./node_modules/*", "-delete"], cwd=PROJECT_ROOT)

    # 3. README.md 작업 내역 추가
    today_str = datetime.now().strftime("%Y-%m-%d")
    header_today = f"### {today_str}"
    entry_line = f"- 일본어 JLPT N5 Unit {unit_num} 단어 선형그래픽 이미지 제작 및 등록 ({words_summary})"

    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if header_today in content:
            parts = content.split(header_today, 1)
            new_content = parts[0] + header_today + "\n" + entry_line + parts[1]
        else:
            marker = "## 작업 내역\n"
            if marker in content:
                parts = content.split(marker, 1)
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

    # 5. push, 거절되면 다시 받아서 올린다
    for attempt in range(3):
        if git("push", "origin", "main").returncode == 0:
            print(f"[유닛 {unit_num}] Git 푸시 동기화 완료!", flush=True)
            return
        print(f"[유닛 {unit_num}] push 거절 ({attempt + 1}/3), 다시 받아서 올린다", flush=True)
        if not pull_rebase():
            return
    print(f"[유닛 {unit_num}] Git 동기화 중 오류 발생: push 가 3번 거절됨", file=sys.stderr, flush=True)

def main():
    parser = argparse.ArgumentParser(description="JLPT N5 단어 선형그래픽 자동 연속 생성 도구")
    parser.add_argument("--unit", "-u", type=int, default=2, help="시작할 유닛 번호 (기본: 2)")
    parser.add_argument("--end-unit", "-e", type=int, default=28, help="종료 유닛 번호 (기본: 28)")
    parser.add_argument("--regenerate", action="store_true", help="이미 있는 그림도 새 장면으로 다시 그린다")
    args = parser.parse_args()
    global REGENERATE
    REGENERATE = args.regenerate

    items = load_n5_words()

    for u in range(args.unit, args.end_unit + 1):
        unit_words = [item for item in items if item["unit"] == u]
        if not unit_words:
            print(f"[Unit {u}] 대상 단어가 없습니다.")
            continue

        registered_keys = get_registered_image_keys()

        print(f"\n==================================================", flush=True)
        print(f"JLPT N5 Unit {u} 선형그래픽 생성 시작 ({len(unit_words)}단어)", flush=True)
        print(f"==================================================", flush=True)

        generated_list = []
        for item in unit_words:
            ok, status = generate_image_for_word(item, registered_keys)
            if status == "generated":
                generated_list.append(item["word"])
            elif status == "failed":
                print(f"[경고] 단어 '{item['word']}' 생성 실패, 다음 단어로 계속 진행합니다.")

        # 해당 유닛 단어 요약
        words_summary = ", ".join([w["word"] for w in unit_words[:5]]) + f" 외 {len(unit_words)-5}개"
        if generated_list:
            sync_and_commit(u, words_summary)
            print(f"[Unit {u}] 완료! 자동으로 다음 유닛으로 이동합니다...\n", flush=True)
        else:
            print(f"[Unit {u}] 이미 모든 이미지가 준비되어 있어 바로 다음 유닛으로 이동합니다.\n", flush=True)

    print("\n모든 지정 유닛 작업(Unit 2~28)이 완료되었습니다!", flush=True)

if __name__ == "__main__":
    main()
