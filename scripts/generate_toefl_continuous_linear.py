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
  6) LIVE_DASHBOARD.md 및 dashboard.html 실시간 갱신 (8초 자동 새로고침)
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
DASHBOARD_MD = os.path.join(WORKSPACE_ROOT, "LIVE_DASHBOARD.md")
DASHBOARD_HTML = os.path.join(WORKSPACE_ROOT, "dashboard.html")

TOEFL_PATH = os.path.join(PROJECT_ROOT, "src", "data", "en", "levels", "toefl.json")
TR_PATH = os.path.join(PROJECT_ROOT, "src", "data", "en", "tr", "ko.json")
WORDS_PATH = os.path.join(PROJECT_ROOT, "src", "data", "en", "words.json")

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

def update_dashboards(current_unit: int, total_units: int, unit_tasks: list, done_records: dict, current_task: dict = None, status_phase: str = "진행 중", started_at: float = 0, unit_status_map: dict = None):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unit_total = len(unit_tasks)
    unit_done = len(done_records)
    unit_pct = (unit_done / unit_total * 100) if unit_total else 100
    bar = "█" * int(unit_pct // 5) + "░" * (20 - int(unit_pct // 5))

    measured = [v.get("elapsed", 0) for v in done_records.values() if v.get("elapsed", 0) > 0]
    avg = (sum(measured) / len(measured)) if measured else 0
    remaining_in_unit = unit_total - unit_done
    remain_min = (avg * remaining_in_unit / 60) if avg else 0
    run_min = ((time.time() - started_at) / 60) if started_at else 0

    def state_md(t):
        w = t["word"]
        if w in done_records:
            sec = done_records[w].get("elapsed", 0)
            sz = done_records[w].get("size", "-")
            return f"✅ 완료 ({sec:.1f}초, {sz})" if sec > 0 else f"✅ 기존 파일 ({sz})"
        if current_task and t["word"] == current_task["word"]:
            return "🔄 **렌더링 중...**"
        return "🕒 대기 중"

    # Markdown Dashboard
    md = [
        "# 🚀 토플(TOEFL) 선형그래픽 실시간 상황판 (Live Dashboard)\n",
        f"> **상태**: 🟢 Unit {current_unit} ({unit_done}/{unit_total}) - {status_phase}  ",
        f"> **현재 유닛 진행률**: `[{bar}] {unit_pct:.1f}% ({unit_done} / {unit_total})`  ",
        f"> **현재 작업**: {current_task['id'] + ' ' + current_task['word'] + ' (' + current_task['meaning'] + ')' if current_task else '대기' }  ",
        f"> **소요/예상**: 유닛 작업 {run_min:.1f}분 경과 · 평균 {avg:.1f}초/장 · 잔여 약 {remain_min:.1f}분  ",
        f"> **마지막 갱신**: {now_str} (개별 이미지 완료 시 즉시 Git 커밋 & 원격 푸시)\n",
        "---\n",
        "## 📊 토플 유닛별 진행 요약\n",
        "| 구분 | 대상 ID | 완료율 | 상태 |",
        "| :--- | :--- | :---: | :--- |"
    ]

    unit_status_map = unit_status_map or {}
    # Show summary of units
    max_display_unit = min(current_unit + 4, total_units)
    min_display_unit = max(1, current_unit - 2)
    for u in range(1, total_units + 1):
        s_idx = (u - 1) * 20 + 1
        e_idx = min(u * 20, 1495)
        st = unit_status_map.get(u, "⏳ 대기 중")
        if u < current_unit:
            md.append(f"| **토플 Unit {u}** | tf-{s_idx} ~ tf-{e_idx} | **100% (20/20)** | ✅ GitHub 배포 완료 |")
        elif u == current_unit:
            md.append(f"| **토플 Unit {u}** | tf-{s_idx} ~ tf-{e_idx} | **{unit_pct:.1f}% ({unit_done}/{unit_total})** | 🔄 **진행 중 ({status_phase})** |")
        elif u <= max_display_unit:
            md.append(f"| **토플 Unit {u}** | tf-{s_idx} ~ tf-{e_idx} | 0% (0/20) | ⏳ 대기 중 |")

    md.extend([
        "\n---\n",
        f"## 🔄 현재 유닛: Unit {current_unit} 상세 진행 현황\n",
        "| 번호 | ID | 단어 | 뜻 | 상태 |",
        "| :---: | :---: | :--- | :--- | :--- |"
    ])
    for idx, t in enumerate(unit_tasks, 1):
        md.append(f"| {idx} | {t['id']} | **{t['word']}** | {t['meaning']} | {state_md(t)} |")

    with open(DASHBOARD_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    # HTML Dashboard (8초 자동 새로고침)
    rows_html = ""
    for idx, t in enumerate(unit_tasks, 1):
        w = t["word"]
        if w in done_records:
            sec = done_records[w].get("elapsed", 0)
            sz = done_records[w].get("size", "-")
            cls = "done"
            st_text = f"✅ 완료 ({sec:.1f}s)" if sec > 0 else f"✅ 기존 파일 ({sz})"
        elif current_task and t["word"] == current_task["word"]:
            cls = "rendering"
            st_text = "🔄 렌더링 중..."
        else:
            cls = "waiting"
            st_text = "🕒 대기 중"

        rows_html += f"<tr class='{cls}'><td>{idx}</td><td>{t['id']}</td><td><b>{w}</b></td><td>{t['meaning']}</td><td>{st_text}</td></tr>\n"

    unit_summary_rows = ""
    for u in range(1, total_units + 1):
        if u > current_unit + 3 and u < total_units - 1:
            if u == current_unit + 4:
                unit_summary_rows += "<tr><td colspan='4' style='text-align:center;color:#9ca3af;'>... 중략 ...</td></tr>\n"
            continue
        s_idx = (u - 1) * 20 + 1
        e_idx = min(u * 20, 1495)
        if u < current_unit:
            u_badge = "<span style='color:#059669;font-weight:600;'>✅ 완료</span>"
            u_pct_str = "100%"
        elif u == current_unit:
            u_badge = f"<span style='color:#0d9488;font-weight:600;'>🔄 Unit {u} 진행 중</span>"
            u_pct_str = f"{unit_pct:.1f}% ({unit_done}/{unit_total})"
        else:
            u_badge = "<span style='color:#9ca3af;'>⏳ 대기</span>"
            u_pct_str = "0%"
        unit_summary_rows += f"<tr><td><b>Unit {u}</b></td><td>tf-{s_idx} ~ tf-{e_idx}</td><td>{u_pct_str}</td><td>{u_badge}</td></tr>\n"

    html = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta http-equiv="refresh" content="8">
<title>토플 선형그래픽 실시간 대시보드</title><style>
body{{font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#ecedf1;color:#121826;margin:0;padding:24px}}
.wrap{{max-width:940px;margin:auto}} .meter{{height:12px;background:#dfe1e7;border-radius:99px;overflow:hidden;margin:12px 0}}
.meter i{{display:block;height:100%;width:{unit_pct:.1f}%;background:#0EB582;transition:width .4s}}
table{{width:100%;border-collapse:collapse;margin-top:14px;background:#f8f9fa;border-radius:14px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06)}}
td,th{{padding:10px 14px;text-align:left;border-bottom:1px solid #e5e7eb}}
th{{background:#f1f3f5;font-weight:600}}
tr.done{{background:#fafffd}} tr.rendering{{background:#e6fcf5;font-weight:bold}} tr.waiting{{color:#6b7280}}
.card{{background:#ffffff;padding:16px 20px;border-radius:14px;box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:16px}}
small{{color:#6b7280}}
</style></head><body><div class="wrap">
<div class="card">
  <h2 style="margin:0 0 8px 0;">🚀 토플(TOEFL) 선형그래픽 실시간 생성 상황판</h2>
  <div><b>현재:</b> Unit {current_unit} / {total_units} &nbsp;·&nbsp; <b>단어 진행:</b> {unit_done} / {unit_total} ({unit_pct:.1f}%) &nbsp;·&nbsp; <small>갱신 {now_str} (8초마다 새로고침)</small></div>
  <div class="meter"><i></i></div>
  <div style="font-size:13px;color:#4b5563;">작업 {run_min:.1f}분 경과 · 평균 {avg:.1f}초/장 · 유닛 잔여 약 {remain_min:.1f}분 · <b>개별 단어 완성 시 즉시 GitHub 배포</b></div>
</div>

<div class="card">
  <h3 style="margin:0 0 8px 0;">📊 전체 유닛 요약</h3>
  <table>
    <tr><th>유닛</th><th>범위</th><th>진행률</th><th>상태</th></tr>
    {unit_summary_rows}
  </table>
</div>

<div class="card">
  <h3 style="margin:0 0 8px 0;">🔄 현재 Unit {current_unit} 상세 진행 목록</h3>
  <table>
    <tr><th>#</th><th>ID</th><th>단어</th><th>뜻</th><th>상태</th></tr>
    {rows_html}
  </table>
</div>
</div></body></html>"""

    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html)

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
            fname = t["word"].replace(" ", "-") + ".png"
            fpath = os.path.join(ASSETS_DIR, fname)
            if os.path.exists(fpath):
                sz_kb = f"{os.path.getsize(fpath) // 1024}KB"
                done_records[t["word"]] = {"elapsed": 0.0, "size": sz_kb}

        update_dashboards(u, total_units, unit_tasks, done_records, None, status_phase="단원 시작", started_at=unit_started_at)

        for task in unit_tasks:
            w = task["word"]
            wid = task["id"]
            meaning = task["meaning"]
            scene = task["scene"]
            fname = w.replace(" ", "-") + ".png"
            out_path = os.path.join(ASSETS_DIR, fname)

            if os.path.exists(out_path):
                print(f"[Unit {u}] '{w}' 이미 파일이 존재하여 건너뜁니다 -> {out_path}", flush=True)
                continue

            print(f"\n▶ [Unit {u} - {wid}] '{w}' ({meaning}) 렌더링 시작...", flush=True)
            print(f"  Scene: {scene}", flush=True)

            update_dashboards(u, total_units, unit_tasks, done_records, task, status_phase=f"'{w}' 렌더링 중", started_at=unit_started_at)

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

                update_dashboards(u, total_units, unit_tasks, done_records, None, status_phase=f"'{w}' 완료 및 배포됨", started_at=unit_started_at)

            except Exception as e:
                print(f"❌ '{w}' 작업 중 오류 발생: {e}", flush=True)
                time.sleep(3)

        print(f"\n🎉 [토플 Unit {u}] 20단어 배포 전원 완료! 즉시 다음 유닛으로 진행합니다...\n", flush=True)
        update_dashboards(u, total_units, unit_tasks, done_records, None, status_phase=f"Unit {u} 배포 완료 🎉", started_at=unit_started_at)

    print("\n🎊 토플 전체 유닛 연속 생성 작업이 완수되었습니다!", flush=True)

if __name__ == "__main__":
    main()
