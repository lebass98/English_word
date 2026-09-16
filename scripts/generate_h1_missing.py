#!/usr/bin/env python3
"""그림이 없는 단어를 과정 순서대로 한 장씩 그려 올린다.

한 장마다: 원격 확인 → Draw Things 생성 → 글자별 등록 → 커밋 → 받아서 올리기.
카탈로그(src/data/images/catalog.json)는 파생 파일이라 여기서 건드리지 않는다.
다른 컴퓨터와 같은 파일을 고치지 않아 올릴 때 부딪히지 않는다.

멈추기: 저장소 바깥 상위 폴더에 STOP_IMAGES 파일을 만들면 지금 장까지만 하고 멈춘다.

기본 순서는 고1 → 중3 → 고2 → 고3 → 토플이다. 한 장 끝낼 때마다 목록을
다시 세므로, 도중에 장면 묘사를 새로 써 넣으면 그것도 이어서 그린다.

    python3 scripts/generate_h1_missing.py                  # 끝까지
    python3 scripts/generate_h1_missing.py --limit 5        # 5장만
    python3 scripts/generate_h1_missing.py --levels high-1  # 한 과정만
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


def rebase_in_progress():
    return os.path.isdir(os.path.join(ROOT, ".git/rebase-merge")) or \
        os.path.isdir(os.path.join(ROOT, ".git/rebase-apply"))


def sync():
    """최신을 받아 내 커밋 위에 얹는다. 리베이스가 멈춘 채로 두지 않는다.

    멈춘 리베이스를 그대로 두면 저장소가 분리(detached) 상태가 되어
    방금 만든 그림이 작업 폴더에서 사라지고, 올리기는 "behind its remote" 로
    실패하며, 다음 회차가 같은 단어를 또 그린다. 그래서 여기서 끝까지 정리한다.
      - 이미 올라와 내용이 비어 버린 커밋은 건너뛴다
      - 같은 단어 그림이 겹치면 원격 쪽을 남긴다 (사용자 결정)
    정리하지 못하면 리베이스를 되돌리고 False 를 돌려준다.
    """
    env = dict(os.environ, GIT_EDITOR="true")
    run(["git", "pull", "--rebase", "--autostash", "origin", "main"], env=env)

    for _ in range(200):
        if not rebase_in_progress():
            break
        conflicts = [f for f in run(["git", "diff", "--name-only",
                                     "--diff-filter=U"]).stdout.split("\n") if f]
        if conflicts:
            # 리베이스 중에는 --ours 가 원격(받은) 쪽이다
            run(["git", "checkout", "--ours", "--"] + conflicts)
            run(["git", "add", "--"] + conflicts)
            if run(["git", "rebase", "--continue"], env=env).returncode != 0:
                run(["git", "rebase", "--skip"], env=env)
        else:
            run(["git", "rebase", "--skip"], env=env)

    if rebase_in_progress():
        run(["git", "rebase", "--abort"], env=env)
        print("[경고] 리베이스를 정리하지 못해 되돌렸다", flush=True)
        return False
    return True


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


LEVEL_LABEL = {"high-1": "고1", "middle-3": "중3", "high-2": "고2",
               "high-3": "고3", "toefl": "토플", "middle-1": "중1", "middle-2": "중2"}
DEFAULT_LEVELS = ["high-1", "middle-3", "high-2", "high-3", "toefl"]


def build_queue(levels):
    """과정 순서대로, 그림 없고 장면 있는 단어.

    한 장 그릴 때마다 다시 부른다. 그래야 도중에 새로 써 넣은 장면도 집어가고,
    다른 컴퓨터가 먼저 올린 그림은 자동으로 빠진다.
    """
    keys = registered_keys()
    # 카탈로그를 다시 만드는 중이면 잠깐 기다렸다 읽는다.
    # 원자적 쓰기를 넣었지만 다른 도구가 그냥 덮어쓸 수도 있어 한 겹 더 둔다
    for attempt in range(5):
        try:
            cat = json.load(open(CATALOG, encoding="utf-8"))["images"]
            break
        except (json.JSONDecodeError, KeyError):
            if attempt == 4:
                raise
            time.sleep(2)
    words = json.load(open(os.path.join(ROOT, "src/data/en/words.json"), encoding="utf-8"))

    queue, seen = [], set()
    for level in levels:
        path = os.path.join(ROOT, f"src/data/en/levels/{level}.json")
        if not os.path.exists(path):
            continue
        for i, sp in enumerate(json.load(open(path, encoding="utf-8"))):
            cid = (words.get(sp) or {}).get("conceptId") or sp
            if cid in keys or sp in keys or cid in seen:
                continue
            entry = cat.get(cid) or cat.get(sp) or {}
            if not entry.get("scene"):
                continue
            seen.add(cid)
            queue.append({"level": LEVEL_LABEL.get(level, level),
                          "unit": i // 20 + 1, "word": cid, "scene": entry["scene"]})
    return queue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="이만큼만 그린다 (0 이면 끝까지)")
    ap.add_argument("--levels", default=",".join(DEFAULT_LEVELS),
                    help="그릴 과정 순서 (쉼표로 구분)")
    args = ap.parse_args()
    levels = [x.strip() for x in args.levels.split(",") if x.strip()]

    print(f"대상 과정: {' → '.join(LEVEL_LABEL.get(l, l) for l in levels)}", flush=True)
    done = failed = skipped = 0
    streak = 0  # 연달아 실패한 횟수

    while True:
        if os.path.exists(STOP):
            print("STOP_IMAGES 파일이 있어 멈춘다", flush=True)
            break
        if args.limit and done >= args.limit:
            break

        # 다른 컴퓨터가 먼저 올렸을 수 있으니 매번 최신을 받고 목록을 다시 센다.
        # 받아 오지 못한 채로 가면 목록이 어긋나 같은 단어를 또 그리게 되므로 멈춘다
        if not sync():
            print("최신을 받아 오지 못해 멈춘다", flush=True)
            break
        queue = build_queue(levels)
        if not queue:
            print("그릴 단어가 없다", flush=True)
            break
        it = queue[0]
        word = it["word"]

        letter = letter_of(word)
        rel = f"assets/words/{letter}/{word}.png"
        prompt = f"{word}, {character_scene(it['scene'])}"

        t0 = time.time()
        r = run(["node", SKILL, prompt, "--output", rel, "--seed", "42"])
        if r.returncode != 0 or not os.path.exists(os.path.join(ROOT, rel)):
            print(f"[실패] {word}: {(r.stderr or r.stdout)[-200:]}", flush=True)
            failed += 1
            # 같은 단어가 큐 맨 앞에 그대로 남아 있어서 곧바로 다시 시도한다.
            # Draw Things 가 응답을 못 하는 동안에는 그렇게 쉬지 않고 두드리게 되므로
            # 연달아 실패할수록 더 오래 쉬었다가 간다 (최대 5분).
            streak += 1
            wait = min(300, 15 * streak)
            print(f"       {wait}초 쉬었다 다시 시도한다 (연속 실패 {streak}회)", flush=True)
            time.sleep(wait)
            continue
        streak = 0
        sec = time.time() - t0

        run(["python3", os.path.join(ROOT, "scripts/sync_word_images.py")])
        subprocess.run(f"find . .. -name '._*' -type f -delete", cwd=ROOT, shell=True)

        reg = f"src/constants/wordImagesByLetter/{letter}.ts"
        run(["git", "add", rel, reg])
        msg = (f"feat: {it['level']} {it['unit']}단원 {word} 선형그래픽 이미지 생성 및 등록"
               f"\n\n{COAUTHOR}")
        c = run(["git", "commit", "-m", msg])
        if c.returncode != 0:
            print(f"[실패] {word} 커밋: {c.stdout[-200:]}", flush=True)
            failed += 1
            continue

        # 올릴 때도 먼저 최신을 받아 얹는다. 한 번 실패하면 다시 받아 한 번 더 해 본다
        for attempt in range(2):
            if not sync():
                break
            p = run(["git", "push", "origin", "main"])
            if p.returncode == 0:
                break
            if attempt == 1:
                print(f"[경고] {word} 올리기 실패 (커밋은 로컬에 있음): "
                      f"{p.stderr[-200:]}", flush=True)
            else:
                time.sleep(3)

        done += 1
        print(f"[완료 {done}] {it['level']} U{it['unit']} {word} "
              f"({sec:.0f}초, 남은 {len(queue) - 1}개)", flush=True)

    print(f"끝: 완료 {done}, 건너뜀 {skipped}, 실패 {failed}", flush=True)


if __name__ == "__main__":
    main()
