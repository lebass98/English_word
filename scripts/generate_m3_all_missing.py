#!/usr/bin/env python3
"""
중3 전체 단원을 1단원부터 훑어 그림이 없는 단어만 선형그래픽으로 생성 및 배포한다.

- 프롬프트: .agents/skills/draw-things-linear-graphic 스킬 원칙 준수
- 장면(Scene): scripts/m3_missing_scenes.json (100% 영문 전용, SD 3~3.5등신, 풍성한 배경)
- 대시보드: LIVE_DASHBOARD.md 및 dashboard.html 실시간 갱신
- 유닛 완료 시 파이프라인: sync_word_images.py -> npm run lint -> ._* 삭제 -> git commit & push
- 정지: 상위 폴더에 STOP_IMAGES 파일 생성 시 현재 단어 완료 후 안전 종료

    python3 scripts/generate_m3_all_missing.py            # 생성 실행
    python3 scripts/generate_m3_all_missing.py --dry-run  # 대상 목록 미리보기
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
WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)
SKILL_SCRIPTS = os.path.join(WORKSPACE_ROOT, ".agents", "skills", "draw-things-linear-graphic", "scripts")
sys.path.insert(0, SKILL_SCRIPTS)
from generate_linear_graphic import generate_linear_image  # noqa: E402

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
SYNC_SCRIPT = os.path.join(SCRIPT_DIR, "sync_word_images.py")
README_FILE = os.path.join(PROJECT_ROOT, "README.md")
STATUS_FILE = os.path.join(SCRIPT_DIR, "m3_missing_status.json")
SCENES_FILE = os.path.join(SCRIPT_DIR, "m3_missing_scenes.json")

LIVE_DASHBOARD_MD = os.path.join(WORKSPACE_ROOT, "LIVE_DASHBOARD.md")
LIVE_DASHBOARD_HTML = os.path.join(WORKSPACE_ROOT, "dashboard.html")
STOP_FILE = os.path.join(WORKSPACE_ROOT, "STOP_IMAGES")

COAUTHOR = "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"


def letter_of(stem):
    first = stem[:1].lower()
    return first if "a" <= first <= "z" else "_"


def get_image_path(word):
    slug = word.replace(" ", "-")
    letter = letter_of(slug)
    # Check letter folder first, then root folder
    p1 = os.path.join(ASSETS_DIR, letter, slug + ".png")
    p2 = os.path.join(ASSETS_DIR, slug + ".png")
    if os.path.exists(p1):
        return p1
    if os.path.exists(p2):
        return p2
    return p1  # Target path for new images


def clean_scene(text):
    """스킬 원칙 3: 캐릭터 모양을 흔드는 낱말을 장면 문장에서 정리한다"""
    text = re.sub(r"[^\x00-\x7F]+", " ", text or "")
    text = re.sub(r"\b(cute\s+)?slender\s+stickman\b|\bstickman\b", "small slim white pictogram character", text, flags=re.I)
    text = re.sub(r"\b(cute|chibi|plump|chubby|slender|skinny)\b", "", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip(" ,")


def run(cmd, check=True):
    print("$ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=PROJECT_ROOT, check=check)


def update_dashboards(targets, current_item=None, status_map=None, is_stopped=False):
    """LIVE_DASHBOARD.md 및 dashboard.html 실시간 갱신"""
    if status_map is None:
        status_map = {}

    total = len(targets)
    done_count = sum(1 for t in targets if status_map.get(t["word"], {}).get("status") == "done")
    pct = round((done_count / total * 100), 1) if total > 0 else 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_state = "stopped" if is_stopped else ("running" if current_item else "idle")

    # Progress bar (20 blocks)
    filled = int(done_count / total * 20) if total > 0 else 0
    bar = "█" * filled + "░" * (20 - filled)

    # 1. LIVE_DASHBOARD.md
    md_lines = [
        "# 🚀 중3 빠진 그림 채우기 상황판\n",
        f"> **단계**: {run_state}  ",
        f"> **마지막 갱신**: {now_str}  ",
        f"> **범위**: 중3 전체 1200단어 중 빠진 그림 {total}개  \n",
        "```",
        f"[{bar}] {pct}% ({done_count} / {total})",
        "```\n",
        "| 번호 | ID | 단어 | 뜻 | 소요 | 상태 |",
        "| :---: | :---: | :--- | :--- | :---: | :--- |",
    ]

    for idx, item in enumerate(targets, 1):
        info = status_map.get(item["word"], {})
        st = info.get("status", "waiting")
        elapsed = info.get("elapsed", "-")
        size = info.get("size", "")

        if st == "done":
            st_text = f"✅ 완료 ({size})" if size else "✅ 완료"
        elif st == "rendering":
            st_text = "⏳ 렌더링 중"
        elif st == "failed":
            st_text = "❌ 실패"
        else:
            st_text = "🕒 대기 중"

        md_lines.append(f"| {idx} | {item['id']} | **{item['word']}** | {item['meaning']} | {elapsed} | {st_text} |")

    with open(LIVE_DASHBOARD_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    # 2. dashboard.html
    tr_html = []
    for idx, item in enumerate(targets, 1):
        info = status_map.get(item["word"], {})
        st = info.get("status", "waiting")
        elapsed = str(info.get("elapsed", "-"))
        if st == "done":
            tr_html.append(f"<tr class='done'><td>{idx}</td><td>{item['id']}</td><td><b>{item['word']}</b></td><td>{item['meaning']}</td><td>{elapsed}</td><td>✅ 완료</td></tr>")
        elif st == "rendering":
            tr_html.append(f"<tr class='rendering'><td>{idx}</td><td>{item['id']}</td><td><b>{item['word']}</b></td><td>{item['meaning']}</td><td>{elapsed}</td><td>⏳ 렌더링 중</td></tr>")
        elif st == "failed":
            tr_html.append(f"<tr class='failed'><td>{idx}</td><td>{item['id']}</td><td><b>{item['word']}</b></td><td>{item['meaning']}</td><td>{elapsed}</td><td>❌ 실패</td></tr>")
        else:
            tr_html.append(f"<tr class='waiting'><td>{idx}</td><td>{item['id']}</td><td><b>{item['word']}</b></td><td>{item['meaning']}</td><td>{elapsed}</td><td>🕒 대기 중</td></tr>")

    html_content = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta http-equiv="refresh" content="8">
<title>중3 그림 채우기</title><style>
body{{font:14px/1.5 -apple-system,sans-serif;background:#ecedf1;color:#121826;margin:0;padding:24px}}
.wrap{{max-width:880px;margin:auto}} .meter{{height:10px;background:#dfe1e7;border-radius:99px;overflow:hidden}}
.meter i{{display:block;height:100%;width:{pct}%;background:#0EB582}} table{{width:100%;border-collapse:collapse;margin-top:16px;background:#f1f2f6;border-radius:16px;overflow:hidden}}
td,th{{padding:8px 10px;text-align:left;border-bottom:1px solid #e3e5ea}} tr.rendering{{background:#dcf2ea}} tr.failed{{background:#fde8e8}}
.now{{background:#f1f2f6;padding:10px 14px;border-radius:12px;margin:12px 0}} small{{color:#64748b}}
</style></head><body><div class="wrap"><h1>중3 빠진 그림 채우기</h1>
<p>{run_state} · <b>{done_count} / {total} ({pct}%)</b> · <small>갱신 {now_str} (8초마다 새로고침)</small></p>
<div class="meter"><i></i></div>
{f'<div class="now">⏳ 현재 렌더링 중: <b>{current_item["id"]} {current_item["word"]}</b> ({current_item["meaning"]})<br><small>{current_item["scene"]}</small></div>' if current_item else ''}
<table><tr><th>#</th><th>ID</th><th>단어</th><th>뜻</th><th>초</th><th>상태</th></tr>{"".join(tr_html)}</table></div></body></html>"""

    with open(LIVE_DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)


def add_readme_entry(unit, words):
    today = f"### {datetime.now().strftime('%Y-%m-%d')}"
    entry = (
        f"- 중3 {unit}단원 빠진 그림 {len(words)}장 선형그래픽으로 생성 및 등록 (머리·몸통 분리 개정 스킬 적용)\n"
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
    """단원 누락분 완료 시 파이프라인. 실패하면 중단"""
    print(f"\n[Unit {unit}] 등록·검증·배포 시작: {', '.join(words)}", flush=True)
    has_origin = subprocess.run(["git", "remote", "get-url", "origin"], cwd=PROJECT_ROOT, capture_output=True).returncode == 0
    if has_origin and run(["git", "pull", "--rebase", "--autostash", "origin", "main"], check=False).returncode != 0:
        raise RuntimeError("pull --rebase 충돌 - 자동 해결하지 않고 중단합니다")
    run([sys.executable, SYNC_SCRIPT])
    run(["npm", "run", "lint"])
    run(["find", ".", "..", "-name", "._*", "-type", "f", "-delete"], check=False)
    add_readme_entry(unit, words)
    run(["git", "add", "-A"])
    msg = (
        f"feat: 중3 {unit}단원 빠진 그림 {len(words)}장 생성 및 등록\n\n"
        f"대상: {', '.join(words)}\n\n"
        f"{COAUTHOR}"
    )
    run(["git", "commit", "-m", msg])
    if not has_origin:
        print("[Git] origin 없음 - 커밋까지만 완료", flush=True)
        return
    if run(["git", "push", "origin", "main"], check=False).returncode != 0:
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
        except Exception as e:
            print(f"[{item['word']}] 실패 {n}/{attempts}: {e}", flush=True)
            if n < attempts:
                time.sleep(15)
    return None


def main():
    dry_run = "--dry-run" in sys.argv
    with open(os.path.join(PROJECT_ROOT, "src/data/en/levels/middle-3.json"), encoding="utf-8") as f:
        m3_words = json.load(f)
    with open(os.path.join(PROJECT_ROOT, "src/data/en/tr/ko.json"), encoding="utf-8") as f:
        meanings = json.load(f).get("meanings", {})
    with open(SCENES_FILE, encoding="utf-8") as f:
        scenes = json.load(f)

    targets = []
    for i, word in enumerate(m3_words):
        slug = word.replace(" ", "-")
        letter = letter_of(slug)
        p1 = os.path.join(ASSETS_DIR, letter, slug + ".png")
        p2 = os.path.join(ASSETS_DIR, slug + ".png")
        if os.path.exists(p1) or os.path.exists(p2):
            continue

        target_path = p1
        scene = clean_scene(scenes.get(word, f"a small slim white pictogram character showing the meaning of {word}, rich props and floor line"))
        targets.append({
            "global_idx": i + 1,
            "unit": i // 20 + 1,
            "id": f"m3-{i + 1}",
            "word": word,
            "meaning": meanings.get(f"m3-{i + 1}", ""),
            "scene": scene,
            "file_path": target_path,
        })

    print(f"중3 {len(m3_words)}단어 중 생성 대상 {len(targets)}개", flush=True)
    if dry_run:
        for t in targets:
            print(f"  U{t['unit']:02d} {t['id']} {t['word']}: {t['scene']}")
        return 0

    status_map = {}
    update_dashboards(targets, current_item=None, status_map=status_map)

    done = {}
    for unit in sorted({t["unit"] for t in targets}):
        unit_targets = [t for t in targets if t["unit"] == unit]
        created = []

        for item in unit_targets:
            if os.path.exists(STOP_FILE):
                print("\n[STOP_IMAGES 감지] 사용자가 정지를 요청하여 작업을 안전하게 중단합니다.", flush=True)
                update_dashboards(targets, current_item=None, status_map=status_map, is_stopped=True)
                return 0

            status_map[item["word"]] = {"status": "rendering", "elapsed": "-"}
            update_dashboards(targets, current_item=item, status_map=status_map)
            print(f"\n[{item['id']}] {item['word']} ({item['meaning']})\nScene: {item['scene']}", flush=True)

            elapsed = generate_with_retry(item)
            if elapsed is None:
                status_map[item["word"]] = {"status": "failed", "elapsed": "실패"}
                update_dashboards(targets, current_item=None, status_map=status_map)
                continue

            size_kb = round(os.path.getsize(item["file_path"]) / 1024, 1)
            elapsed_sec = round(elapsed, 1)
            status_map[item["word"]] = {
                "status": "done",
                "elapsed": f"{elapsed_sec}초",
                "size": f"{size_kb}KB"
            }
            done[item["word"]] = {"word": item["word"], "id": item["id"], "unit": unit, "elapsed_sec": elapsed_sec, "size_kb": size_kb}
            created.append(item["word"])
            update_dashboards(targets, current_item=None, status_map=status_map)
            print(f"PROGRESS {len(done)}/{len(targets)} {item['word']} {elapsed_sec}s ({size_kb}KB)", flush=True)

        if created:
            publish_unit(unit, created)

    update_dashboards(targets, current_item=None, status_map=status_map)
    failed = [t["word"] for t in targets if t["word"] not in done]
    print(f"\n전체 완료: {len(done)}/{len(targets)} 생성" + (f", 실패: {failed}" if failed else ""), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
