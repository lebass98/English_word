#!/usr/bin/env python3
"""고1(high-1) 에서 그림이 없는 단어를 앞에서부터 한 장씩 그려 올린다.

한 장마다: 원격 확인 → Draw Things 생성 → 글자별 등록 → 커밋 → 받아서 올리기.
카탈로그(src/data/images/catalog.json)는 파생 파일이라 여기서 건드리지 않는다.
다른 컴퓨터와 같은 파일을 고치지 않아 올릴 때 부딪히지 않는다.

멈추기: 저장소 바깥 상위 폴더에 STOP_IMAGES 파일을 만들면 지금 장까지만 하고 멈춘다.

    python3 scripts/generate_h1_missing.py            # 끝까지
    python3 scripts/generate_h1_missing.py --limit 5  # 5장만
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE = os.path.dirname(ROOT)
STOP = os.path.join(WORKSPACE, "STOP_IMAGES")
CATALOG = os.path.join(ROOT, "src/data/images/catalog.json")
SKILL = os.path.join(ROOT, ".agents/skills/draw-things-linear-graphic/scripts/generate_linear_graphic.js")
COAUTHOR = "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def registered_keys():
    """등록표에 이미 올라온 열쇠"""
    keys = set()
    for f in glob.glob(os.path.join(ROOT, "src/constants/wordImagesByLetter/*.ts")):
        for m in re.finditer(r'^\s*(?:"([^"]+)"|([A-Za-z_$][\w$]*))\s*:\s*require\(',
                             open(f, encoding="utf-8").read(), re.M):
            keys.add(m.group(1) or m.group(2))
    return keys


def character_scene(scene):
    """장면 속 사람 표현을 지금 기준으로 맞춘다 (generate_images.py 와 같은 규칙)"""
    scene = re.sub(r"\b(?:cute\s+)?(?:slender|skinny)?\s*(?:chibi\s+)?stick\s*man\b",
                   "small slim white pictogram character", scene, flags=re.I)
    scene = re.sub(r"\b(?:cute|chibi|slender|skinny|plump)\s+", "", scene, flags=re.I)
    return re.sub(r"\s{2,}", " ", scene).strip()


def letter_of(stem):
    c = stem[:1].lower()
    return c if "a" <= c <= "z" else "_"


def build_queue():
    """고1 순서대로, 그림 없고 장면 있는 단어"""
    keys = registered_keys()
    cat = json.load(open(CATALOG, encoding="utf-8"))["images"]
    words = json.load(open(os.path.join(ROOT, "src/data/en/words.json"), encoding="utf-8"))
    spellings = json.load(open(os.path.join(ROOT, "src/data/en/levels/high-1.json"), encoding="utf-8"))

    queue, seen = [], set()
    for i, sp in enumerate(spellings):
        cid = (words.get(sp) or {}).get("conceptId") or sp
        if cid in keys or sp in keys or cid in seen:
            continue
        entry = cat.get(cid) or cat.get(sp) or {}
        if not entry.get("scene"):
            continue
        seen.add(cid)
        queue.append({"unit": i // 20 + 1, "word": cid, "scene": entry["scene"]})
    return queue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="이만큼만 그린다 (0 이면 끝까지)")
    args = ap.parse_args()

    queue = build_queue()
    print(f"고1 그릴 단어 {len(queue)}개", flush=True)
    done = failed = skipped = 0

    for it in queue:
        if os.path.exists(STOP):
            print("STOP_IMAGES 파일이 있어 멈춘다", flush=True)
            break
        if args.limit and done >= args.limit:
            break

        word = it["word"]
        # 다른 컴퓨터가 먼저 올렸을 수 있으니 매번 최신을 받아 다시 확인한다
        run(["git", "pull", "--rebase", "origin", "main"])
        if word in registered_keys():
            print(f"[건너뜀] {word} — 이미 등록됨", flush=True)
            skipped += 1
            continue

        letter = letter_of(word)
        rel = f"assets/words/{letter}/{word}.png"
        prompt = f"{word}, {character_scene(it['scene'])}"

        t0 = time.time()
        r = run(["node", SKILL, prompt, "--output", rel, "--seed", "42"])
        if r.returncode != 0 or not os.path.exists(os.path.join(ROOT, rel)):
            print(f"[실패] {word}: {(r.stderr or r.stdout)[-200:]}", flush=True)
            failed += 1
            continue
        sec = time.time() - t0

        run(["python3", os.path.join(ROOT, "scripts/sync_word_images.py")])
        subprocess.run(f"find . .. -name '._*' -type f -delete", cwd=ROOT, shell=True)

        reg = f"src/constants/wordImagesByLetter/{letter}.ts"
        run(["git", "add", rel, reg])
        msg = f"feat: 고1 {it['unit']}단원 {word} 선형그래픽 이미지 생성 및 등록\n\n{COAUTHOR}"
        c = run(["git", "commit", "-m", msg])
        if c.returncode != 0:
            print(f"[실패] {word} 커밋: {c.stdout[-200:]}", flush=True)
            failed += 1
            continue

        run(["git", "pull", "--rebase", "origin", "main"])
        p = run(["git", "push", "origin", "main"])
        if p.returncode != 0:
            print(f"[경고] {word} 올리기 실패 (커밋은 로컬에 있음): {p.stderr[-200:]}", flush=True)

        done += 1
        print(f"[완료 {done}/{len(queue)}] 고1 U{it['unit']} {word} ({sec:.0f}초)", flush=True)

    print(f"끝: 완료 {done}, 건너뜀 {skipped}, 실패 {failed}", flush=True)


if __name__ == "__main__":
    main()
