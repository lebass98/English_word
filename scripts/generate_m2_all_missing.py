#!/usr/bin/env python3
"""
중2 전체 단원을 1단원부터 훑어 그림이 없는 단어만 선형그래픽으로 만든다.

- 프롬프트는 여기서 따로 쓰지 않고 스킬 스크립트(generate_linear_graphic.py)를 그대로 불러 쓴다.
  그래서 스킬이 개정되면 이 스크립트도 자동으로 최신 규칙을 따른다.
- 단어별 장면은 scripts/m2_missing_scenes.json 에 있다. 없으면 예문으로 장면을 만든다.
- REGENERATE 에 넣은 단어는 그림이 있어도 다시 만든다 (스킬 개정 전 모습으로 만든 그림).
- 한 단원의 누락분이 끝날 때마다: wordImages.ts 등록 -> lint -> ._* 정리 -> README -> 커밋 & 푸시
- 진행 상황은 LIVE_DASHBOARD.md / dashboard.html (dashboard_updater.py 와 같은 위치)에 갱신한다.

    python3 scripts/generate_m2_all_missing.py            # 생성
    python3 scripts/generate_m2_all_missing.py --dry-run  # 대상만 보기
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SKILL_SCRIPTS = os.path.join(PROJECT_ROOT, ".agents", "skills", "draw-things-linear-graphic", "scripts")
sys.path.insert(0, SKILL_SCRIPTS)
from generate_linear_graphic import generate_linear_image  # noqa: E402

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
SYNC_SCRIPT = os.path.join(SCRIPT_DIR, "sync_word_images.py")
README_FILE = os.path.join(PROJECT_ROOT, "README.md")
STATUS_FILE = os.path.join(SCRIPT_DIR, "m2_missing_status.json")
SCENES_FILE = os.path.join(SCRIPT_DIR, "m2_missing_scenes.json")
WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)
DASHBOARD_MD = os.path.join(WORKSPACE_ROOT, "LIVE_DASHBOARD.md")
DASHBOARD_HTML = os.path.join(WORKSPACE_ROOT, "dashboard.html")

# 그림이 있어도 다시 그릴 단어 (비워 두면 없는 그림만 만든다)
REGENERATE = set()


def clean_scene(text):
    """스킬 원칙 3: 캐릭터 모양을 흔드는 낱말을 장면 문장에서 정리한다"""
    text = re.sub(r"[^\x00-\x7F]+", " ", text or "")
    text = re.sub(r"\b(cute\s+)?slender\s+stickman\b|\bstickman\b", "small slim white pictogram character", text, flags=re.I)
    text = re.sub(r"\b(cute|chibi|plump|chubby|slender|skinny)\b", "", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip(" ,")


def get_scene(word, scenes, words_dict):
    if word in scenes:
        return clean_scene(scenes[word])
    example = clean_scene(words_dict.get(word, {}).get("example", ""))
    if example:
        return f"a small slim white pictogram character acting out the sentence: {example}, rich background furniture, props and floor line"
    return f"a small slim white pictogram character showing the meaning of the word {word}, rich props, wall decor and floor line"


def run(cmd, check=True):
    print("$ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=PROJECT_ROOT, check=check)


def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def write_dashboard(targets, done, current, started_at):
    """전체 대상 기준 진행 상황판 (md + 8초 자동 새로고침 html)"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(targets)
    n_done = len(done)
    pct = n_done / total * 100 if total else 100
    bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
    avg = sum(d["elapsed_sec"] for d in done.values()) / n_done if n_done else 0
    remain_min = avg * (total - n_done) / 60 if avg else 0
    run_min = (time.time() - started_at) / 60

    def state(t):
        if t["word"] in done:
            return f"✅ 완료 ({done[t['word']]['elapsed_sec']:.0f}초)"
        if current and t["word"] == current["word"]:
            return "🔄 렌더링 중"
        return "🕒 대기"

    md = [
        "# 🚀 중2 누락 그림 선형그래픽 상황판\n",
        f"> **진행**: `[{bar}] {pct:.1f}% ({n_done}/{total})`  ",
        f"> **현재**: {current['id'] + ' ' + current['word'] + ' (Unit ' + str(current['unit']) + ')' if current else '없음'}  ",
        f"> **경과**: {run_min:.0f}분 · 평균 {avg:.0f}초/장 · 남은 예상 {remain_min:.0f}분  ",
        f"> **마지막 갱신**: {now}\n",
    ]
    if current:
        md.append(f"**현재 장면**: {current['scene']}\n")
    md += ["| Unit | ID | 단어 | 뜻 | 상태 |", "| :-: | :-: | :-: | :-- | :-- |"]
    md += [f"| {t['unit']} | {t['id']} | **{t['word']}** | {t['meaning']} | {state(t)} |" for t in targets]
    with open(DASHBOARD_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    rows = "\n".join(
        f"<tr><td>{t['unit']}</td><td>{t['id']}</td><td><b>{t['word']}</b></td><td>{t['meaning']}</td><td>{state(t)}</td></tr>"
        for t in targets
    )
    cur_html = (
        f"<div class='cur'><div class='lbl'>현재 렌더링</div><div class='w'>{current['word']}</div>"
        f"<div class='m'>{current['id']} · Unit {current['unit']} · {current['meaning']}</div><div class='s'>{current['scene']}</div></div>"
        if current else "<div class='cur'><div class='w'>대기 없음</div></div>"
    )
    html = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta http-equiv="refresh" content="8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>중2 선형그래픽 상황판</title>
<style>body{{font-family:-apple-system,sans-serif;background:#0f1117;color:#f3f4f6;padding:24px;margin:0}}
.bar{{height:16px;background:#212530;border-radius:99px;overflow:hidden;margin:12px 0}}
.fill{{height:100%;width:{pct:.1f}%;background:linear-gradient(90deg,#6366f1,#38bdf8)}}
.cur{{background:#181b24;border:1px solid #6366f1;border-radius:14px;padding:18px;margin:16px 0}}
.lbl{{color:#38bdf8;font-size:12px;font-weight:700}}.w{{font-size:32px;font-weight:800}}.m{{color:#9ca3af}}.s{{color:#9ca3af;font-size:12px;margin-top:8px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}td,th{{padding:8px 10px;border-bottom:1px solid #222;text-align:left}}th{{color:#9ca3af}}</style></head>
<body><h2>🎨 중2 누락 그림 선형그래픽 상황판</h2>
<div>{pct:.1f}% ({n_done}/{total}) · 경과 {run_min:.0f}분 · 평균 {avg:.0f}초/장 · 남은 예상 {remain_min:.0f}분 · 갱신 {now}</div>
<div class="bar"><div class="fill"></div></div>{cur_html}
<table><thead><tr><th>Unit</th><th>ID</th><th>단어</th><th>뜻</th><th>상태</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""
    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html)


def add_readme_entry(unit, words):
    today = f"### {datetime.now().strftime('%Y-%m-%d')}"
    entry = (
        f"- 중2 {unit}단원 빠진 그림 {len(words)}장 선형그래픽으로 생성 및 등록 (머리·몸통 분리 개정 스킬 적용)\n"
        f"  - 대상: {', '.join(words)}\n"
    )
    with open(README_FILE, encoding="utf-8") as f:
        content = f.read()
    marker = "## 작업 내역\n\n"
    if today in content:
        head, tail = content.split(today, 1)
        content = head + today + "\n" + entry + tail.lstrip("\n")
    elif marker in content:
        head, tail = content.split(marker, 1)
        content = head + marker + today + "\n" + entry + "\n" + tail
    else:
        content += f"\n## 작업 내역\n\n{today}\n{entry}"
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def publish_unit(unit, words):
    """단원 누락분 완료 시 파이프라인. 실패하면 예외를 던져 전체를 멈춘다"""
    print(f"\n[Unit {unit}] 등록·검증·배포 시작: {', '.join(words)}", flush=True)
    has_origin = subprocess.run(["git", "remote", "get-url", "origin"], cwd=PROJECT_ROOT, capture_output=True).returncode == 0
    # 다른 기기·세션도 같은 날짜 README 에 줄을 넣으므로, README 를 고치기 전에 먼저 받아
    # 받기와 푸시 사이를 몇 초로 줄인다 (예전엔 커밋 뒤에 받아 README 가 자주 충돌했다)
    if has_origin and run(["git", "pull", "--rebase", "--autostash", "origin", "main"], check=False).returncode != 0:
        raise RuntimeError("pull --rebase 충돌 - 자동 해결하지 않고 중단합니다")
    run([sys.executable, SYNC_SCRIPT])
    run(["npm", "run", "lint"])
    run(["find", ".", "..", "-name", "._*", "-type", "f", "-delete"], check=False)
    add_readme_entry(unit, words)
    run(["git", "add", "-A"])
    msg = (
        f"feat: 중2 {unit}단원 빠진 그림 {len(words)}장 생성 및 등록\n\n"
        f"대상: {', '.join(words)}\n\n"
        "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
    )
    run(["git", "commit", "-m", msg])
    if not has_origin:
        print("[Git] origin 없음 - 커밋까지만 완료", flush=True)
        return
    if run(["git", "push", "origin", "main"], check=False).returncode != 0:
        # 그 몇 초 사이에 누가 올렸으면 한 번 더 받아 올린다
        if run(["git", "pull", "--rebase", "origin", "main"], check=False).returncode != 0:
            raise RuntimeError("pull --rebase 충돌 - 자동 해결하지 않고 중단합니다")
        run(["git", "push", "origin", "main"])
    print(f"[Git] Unit {unit} 푸시 완료", flush=True)


def generate_with_retry(item, attempts=3):
    for n in range(1, attempts + 1):
        t0 = time.time()
        try:
            generate_linear_image(item["scene"], item["file_path"], seed=950 + item["global_idx"] * 19)
            return time.time() - t0
        except Exception as e:  # Draw Things 일시 오류는 잠시 뒤 다시 시도
            print(f"[{item['word']}] 실패 {n}/{attempts}: {e}", flush=True)
            if n < attempts:
                time.sleep(30)
    return None


def main():
    dry_run = "--dry-run" in sys.argv
    with open(os.path.join(PROJECT_ROOT, "src/data/en/levels/middle-2.json"), encoding="utf-8") as f:
        m2_words = json.load(f)
    with open(os.path.join(PROJECT_ROOT, "src/data/en/tr/ko.json"), encoding="utf-8") as f:
        meanings = json.load(f).get("meanings", {})
    with open(os.path.join(PROJECT_ROOT, "src/data/en/words.json"), encoding="utf-8") as f:
        words_dict = json.load(f)
    with open(SCENES_FILE, encoding="utf-8") as f:
        scenes = json.load(f)

    targets = []
    for i, word in enumerate(m2_words):
        path = os.path.join(ASSETS_DIR, word.replace(" ", "-") + ".png")
        if os.path.exists(path) and word not in REGENERATE:
            continue
        targets.append({
            "global_idx": i + 1,
            "unit": i // 20 + 1,
            "id": f"m2-{i + 1}",
            "word": word,
            "meaning": meanings.get(f"m2-{i + 1}", ""),
            "scene": get_scene(word, scenes, words_dict),
            "file_path": path,
        })

    print(f"중2 {len(m2_words)}단어 중 생성 대상 {len(targets)}개", flush=True)
    if dry_run:
        for t in targets:
            print(f"  U{t['unit']} {t['id']} {t['word']}: {t['scene']}")
        return 0

    started_at = time.time()
    done = {}
    status = {"current_unit": None, "current_word": None, "total_targets": len(targets), "completed_words": []}

    for unit in sorted({t["unit"] for t in targets}):
        created = []
        for item in (t for t in targets if t["unit"] == unit):
            status.update(current_unit=unit, current_word=item["word"])
            save_status(status)
            write_dashboard(targets, done, item, started_at)
            print(f"\n[{item['id']}] {item['word']} ({item['meaning']})\nScene: {item['scene']}", flush=True)

            elapsed = generate_with_retry(item)
            if elapsed is None:
                continue
            size_kb = round(os.path.getsize(item["file_path"]) / 1024, 1)
            done[item["word"]] = {"word": item["word"], "id": item["id"], "unit": unit, "elapsed_sec": round(elapsed, 1), "size_kb": size_kb}
            status["completed_words"].append(done[item["word"]])
            save_status(status)
            created.append(item["word"])
            print(f"PROGRESS {len(done)}/{len(targets)} {item['word']} {elapsed:.0f}s", flush=True)

        write_dashboard(targets, done, None, started_at)
        if created:
            publish_unit(unit, created)

    status.update(current_unit=None, current_word=None)
    save_status(status)
    write_dashboard(targets, done, None, started_at)
    failed = [t["word"] for t in targets if t["word"] not in done]
    print(f"\n완료: {len(done)}/{len(targets)} 생성" + (f", 실패: {failed}" if failed else ""), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
