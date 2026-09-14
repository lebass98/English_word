#!/usr/bin/env python3
"""카탈로그 기준으로 단어 그림을 한 장씩 그려 올린다.

여러 컴퓨터(2~3대)가 동시에 그릴 때는 알파벳 범위를 나눠 돌린다. 범위가 겹치지 않으면
그림 파일도 글자별 등록 파일도 겹치지 않아 올릴 때 충돌하지 않는다.

    python3 scripts/generate_images.py --letters a-h                  # 그림 없는 단어만
    python3 scripts/generate_images.py --letters i-p --include-review  # 개정 전 그림(review)도 다시
    python3 scripts/generate_images.py --letters q-z,_ --limit 5 --dry-run

- 대상: 카탈로그에서 어느 과정이든 쓰는 철자 중 첫 글자가 범위 안이고 그림이 없는 것
  (--include-review 면 status 가 review 인 것도). 장면 묘사가 없는 단어는 건너뛰고 끝에 알려 준다
- 한 장마다: 원격 확인(다른 컴퓨터가 먼저 올렸으면 건너뜀) → Draw Things 생성(스킬 스크립트)
  → 글자별 등록 → ._ 정리 → lint → 커밋(그림 + 그 글자 등록 파일) → 받아서 올리기
- README 에는 장마다 적지 않는다. 카탈로그 상태는 끝난 뒤 image_catalog.py 로 다시 만든다
- 멈추기: 저장소 바깥 상위 폴더에 STOP_IMAGES 파일을 만들면 지금 장까지만 하고 멈춘다
- 상황판: 상위 폴더의 LIVE_DASHBOARD.md, dashboard.html (컴퓨터마다 따로 생긴다)
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE = os.path.dirname(ROOT)
CATALOG = os.path.join(ROOT, "src/data/images/catalog.json")
STOP = os.path.join(WORKSPACE, "STOP_IMAGES")
DASH_MD = os.path.join(WORKSPACE, "LIVE_DASHBOARD.md")
DASH_HTML = os.path.join(WORKSPACE, "dashboard.html")
COAUTHOR = "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"

sys.path.insert(0, os.path.join(ROOT, ".agents/skills/draw-things-linear-graphic/scripts"))


def letter_of(word):
    first = word[:1].lower()
    return first if "a" <= first <= "z" else "_"


def parse_letters(spec):
    """"a-h" / "a,c,x-z" / "_" → 글자 집합"""
    letters = set()
    for part in spec.lower().split(","):
        part = part.strip()
        if re.fullmatch(r"[a-z]-[a-z]", part):
            letters.update(chr(c) for c in range(ord(part[0]), ord(part[2]) + 1))
        elif re.fullmatch(r"[a-z_]", part):
            letters.add(part)
        elif part:
            raise SystemExit(f"--letters 형식이 잘못됐습니다: {part!r} (예: a-h, a,c,x-z, _)")
    return letters


def image_path(word):
    return f"assets/words/{letter_of(word)}/{word.replace(' ', '-')}.png"


def character_scene(scene):
    """옛 장면 묘사 속 캐릭터 표현을 지금 스킬 기준으로 바꾼다.

    이 모델은 부정 프롬프트를 거의 따르지 않아 장면 문장 속 낱말이 모양을 정한다.
    막대 인간·SD 마네킹 표현은 날씬한 픽토그램으로 바꾸고 cute·chibi 같은 낱말은 지운다.
    """
    scene = re.sub(
        r"\b(?:small |little |tiny )?(?:cute )?(?:slender )?(?:chibi )?(?:doodle )?"
        r"(?:stick ?m[ae]n|stick figures?|mannequins?|chibi characters?)\b",
        "small slim white pictogram character",
        scene,
        flags=re.I,
    )
    scene = re.sub(r"\b(?:cute|chibi|slender|skinny|plump)\s+", "", scene, flags=re.I)
    return re.sub(r"\s{2,}", " ", scene).strip()


# ── git ─────────────────────────────────────────────────────────────


def sh(cmd, **kw):
    print("$", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT, **kw)


def git_out(*args):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def clear_appledouble():
    """외장하드(exFAT)가 만드는 ._ 파일은 lint 와 rebase 를 멈추게 한다"""
    subprocess.run(["find", ".", "-name", "._*", "-type", "f", "-not", "-path", "./node_modules/*", "-delete"], cwd=ROOT)
    for d in {git_out("rev-parse", "--git-dir"), git_out("rev-parse", "--git-common-dir")}:
        if d:
            subprocess.run(["find", d, "-maxdepth", "2", "-name", "._*", "-type", "f", "-delete"], cwd=ROOT)


def rebasing():
    d = git_out("rev-parse", "--git-dir")
    return bool(d) and (os.path.isdir(os.path.join(ROOT, d, "rebase-merge")) or os.path.isdir(os.path.join(ROOT, d, "rebase-apply")))


def conflicted():
    return [p for p in git_out("diff", "--name-only", "--diff-filter=U").splitlines() if p]


def on_origin(path):
    return subprocess.run(["git", "cat-file", "-e", f"origin/main:{path}"], cwd=ROOT, capture_output=True).returncode == 0


def pull_rebase():
    """받아서 rebase. 성공이면 None, 실제 충돌이면 사유"""
    clear_appledouble()
    sh(["git", "pull", "--rebase", "origin", "main"])
    if rebasing() and not conflicted():
        clear_appledouble()
        sh(["git", "rebase", "--continue"], env={**os.environ, "GIT_EDITOR": "true"})
    if rebasing():
        files = conflicted()
        sh(["git", "rebase", "--abort"])
        return f"pull --rebase 충돌({', '.join(files) or '원인 불명'})"
    return None


def push_with_retry(attempts=3):
    for attempt in range(1, attempts + 1):
        error = pull_rebase()
        if error:
            return error
        if sh(["git", "push", "origin", "main"]).returncode == 0:
            return None
        print(f"push 거절 ({attempt}/{attempts}), 다시 받아서 올린다", flush=True)
    return f"push 가 {attempts}번 거절됨"


# ── 상황판 ─────────────────────────────────────────────────────────

LABEL = {"waiting": "🕒 대기", "rendering": "⏳ 렌더링", "done": "✅ 완료", "failed": "❌ 실패",
         "skipped": "⏭ 다른 컴퓨터가 먼저 올림", "no-scene": "📝 장면 묘사 없음"}


def render_dashboard(state):
    items = state["items"]
    done = sum(1 for it in items if it["status"] == "done")
    total = sum(1 for it in items if it["status"] != "no-scene")
    current = next((it for it in items if it["status"] == "rendering"), None)
    head = (f"# 🎨 단어 그림 생성 상황판 ({state['letters']})\n\n"
            f"> **상태**: {state['phase']}  \n> **갱신**: {state['updated']}  \n"
            f"> **진행**: {done} / {total} (장면 묘사 없음 {len(items) - total})\n\n")
    if current:
        head += f"**지금 렌더링**: `{current['word']}` — {current['scene']}\n\n"
    rows = "| 단어 | 대표 뜻 | 초 | 상태 |\n| :--- | :--- | :---: | :--- |\n" + "".join(
        f"| **{it['word']}** | {it['sense'] or ''} | {it['sec'] or '-'} | {LABEL[it['status']]} |\n"
        for it in items if it["status"] != "no-scene"
    )
    with open(DASH_MD, "w", encoding="utf-8") as f:
        f.write(head + rows)
    trs = "".join(
        f"<tr class='{it['status']}'><td><b>{html.escape(it['word'])}</b></td><td>{html.escape(it['sense'] or '')}</td>"
        f"<td>{it['sec'] or '-'}</td><td>{LABEL[it['status']]}</td></tr>"
        for it in items if it["status"] != "no-scene"
    )
    page = (f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta http-equiv='refresh' content='8'>"
            f"<title>단어 그림 생성 ({html.escape(state['letters'])})</title><style>"
            "body{font:14px/1.5 -apple-system,sans-serif;background:#ecedf1;color:#121826;margin:0;padding:24px}"
            "table{width:100%;max-width:880px;border-collapse:collapse;background:#f1f2f6}"
            "td,th{padding:6px 10px;border-bottom:1px solid #e3e5ea;text-align:left}"
            "tr.rendering{background:#dcf2ea}tr.failed{background:#fde8e8}</style></head><body>"
            f"<h1>단어 그림 생성 ({html.escape(state['letters'])})</h1><p>{html.escape(state['phase'])} · "
            f"<b>{done} / {total}</b> · 갱신 {state['updated']}</p><table><tr><th>단어</th><th>대표 뜻</th>"
            f"<th>초</th><th>상태</th></tr>{trs}</table></body></html>")
    with open(DASH_HTML, "w", encoding="utf-8") as f:
        f.write(page)


def save(state):
    state["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        render_dashboard(state)
    except OSError as e:
        print("상황판 쓰기 실패:", e, flush=True)


# ── 본체 ───────────────────────────────────────────────────────────


def build_queue(letters, include_review):
    images = json.load(open(CATALOG))["images"]
    queue = []
    for word, e in images.items():
        if not e.get("courses") or letter_of(word) not in letters:
            continue
        wanted = e["status"] == "missing" or (include_review and e["status"] == "review")
        if not wanted:
            continue
        queue.append({
            "word": word, "sense": e.get("sense"), "scene": e.get("scene"),
            "redo": e["status"] == "review",
            "status": "waiting" if e.get("scene") else "no-scene", "sec": None,
        })
    queue.sort(key=lambda it: it["word"].lower())
    return queue


def publish(word, state):
    """그림 한 장을 등록·검사·커밋·푸시. 실패하면 사유 문자열"""
    path = image_path(word)
    letter_file = f"src/constants/wordImagesByLetter/{letter_of(word)}.ts"
    if sh(["python3", "scripts/sync_word_images.py"]).returncode != 0:
        return "등록(sync_word_images.py) 실패"
    clear_appledouble()
    lint = sh(["npm", "run", "lint"], capture_output=True, text=True)
    if lint.returncode != 0:
        print((lint.stdout or "")[-3000:], (lint.stderr or "")[-3000:], flush=True)
        return "lint 실패"
    paths = [p for p in (path, letter_file, "src/constants/wordImages.ts")
             if git_out("status", "--porcelain", "--", p)]
    if not paths:
        return None
    sh(["git", "add", "--", *paths], check=True)
    msg = f"feat: 단어 그림 {word} 생성 ({state['letters']})\n\n대표 뜻: {state['sense_of'].get(word) or '-'}\n\n{COAUTHOR}"
    sh(["git", "commit", "-m", msg, "--", *paths], check=True)
    return push_with_retry()


def main():
    parser = argparse.ArgumentParser(description="카탈로그 기준 단어 그림 생성 (알파벳 범위 분담)")
    parser.add_argument("--letters", required=True, help="맡을 첫 글자 범위. 예: a-h / i-p / q-z,_")
    parser.add_argument("--include-review", action="store_true", help="개정 전 그림(review)도 다시 그린다")
    parser.add_argument("--limit", type=int, default=0, help="이번에 그릴 최대 장 수 (0 = 끝까지)")
    parser.add_argument("--dry-run", action="store_true", help="대상만 출력하고 끝낸다")
    args = parser.parse_args()
    letters = parse_letters(args.letters)

    flat = [n for n in os.listdir(os.path.join(ROOT, "assets/words"))
            if n.endswith(".png") and not n.startswith("._")]
    if flat:
        raise SystemExit(f"assets/words 바로 아래에 옮기지 않은 그림 {len(flat)}장이 있습니다. "
                         "scripts/migrate_images_by_letter.py 를 먼저 돌리세요")

    queue = build_queue(letters, args.include_review)
    todo = [it for it in queue if it["status"] == "waiting"]
    no_scene = [it["word"] for it in queue if it["status"] == "no-scene"]
    print(f"범위 {args.letters}: 그릴 단어 {len(todo)}개 (다시 그리기 {sum(it['redo'] for it in todo)}), 장면 묘사 없음 {len(no_scene)}개")
    print("앞 20개:", [it["word"] for it in todo[:20]])
    if args.dry_run:
        if no_scene:
            print("장면 묘사 없음 앞 30개:", no_scene[:30])
        return 0

    if git_out("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("커밋 안 된 변경이 있습니다. 정리한 뒤 다시 돌리세요")
    error = pull_rebase()
    if error:
        raise SystemExit(error)

    from generate_linear_graphic import generate_linear_image

    state = {"letters": args.letters, "phase": "시작", "items": queue,
             "sense_of": {it["word"]: it["sense"] for it in queue}}
    save(state)
    drawn = 0
    for it in todo:
        if os.path.exists(STOP):
            state["phase"] = f"멈춤 파일({STOP})로 멈춤"
            save(state)
            break
        if args.limit and drawn >= args.limit:
            state["phase"] = f"--limit {args.limit}장 도달"
            save(state)
            break
        word, path = it["word"], image_path(it["word"])
        subprocess.run(["git", "fetch", "-q", "origin"], cwd=ROOT)
        if not it["redo"] and on_origin(path):
            it["status"] = "skipped"
            save(state)
            continue

        it["status"] = "rendering"
        state["phase"] = f"{word} 렌더링"
        save(state)
        os.makedirs(os.path.join(ROOT, os.path.dirname(path)), exist_ok=True)
        t0 = time.time()
        try:
            generate_linear_image(f"{word}, {character_scene(it['scene'])}", os.path.join(ROOT, path), seed=42)
            ok = os.path.getsize(os.path.join(ROOT, path)) > 10000
        except Exception as e:  # Draw Things 오류가 나도 다음 단어로 넘어간다
            print("생성 실패", word, e, flush=True)
            ok = False
        it["sec"] = round(time.time() - t0, 1)
        it["status"] = "done" if ok else "failed"
        save(state)
        if not ok:
            continue
        drawn += 1
        error = publish(word, state)
        if error:
            state["phase"] = f"{word} 올리다 멈춤: {error}. 커밋은 로컬에 있을 수 있음"
            save(state)
            print(state["phase"], flush=True)
            return 1
    else:
        state["phase"] = "모두 끝남"
        save(state)

    print(f"끝: 그림 {drawn}장, 건너뜀 {sum(1 for it in queue if it['status'] == 'skipped')}, "
          f"실패 {sum(1 for it in queue if it['status'] == 'failed')}, 장면 묘사 없음 {len(no_scene)}")
    print("카탈로그 상태를 갱신하려면: python3 scripts/image_catalog.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
