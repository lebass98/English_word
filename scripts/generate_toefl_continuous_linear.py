#!/usr/bin/env python3
"""
토플(TOEFL) 전용 선형그래픽 연속 생성 및 자동 배포 스크립트.
- 지정된 시작 유닛부터 순차적으로 생성 및 1개 완성 시 즉시 개별 Git 커밋 & 원격 푸시
- LIVE_DASHBOARD.md 및 dashboard.html 실시간 자동 업데이트 (8초 새로고침)
- Draw Things 선형그래픽 스킬 100% 준수 (3~3.5등신 순백색 마네킹, 영문 100%, 0.05mm 초극세선, #030203 선, #f5f6f8 배경)

사용법:
    python3 scripts/generate_toefl_continuous_linear.py --start-unit 2 --end-unit 2
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

TOEFL_PRESET_SCENES = {
    # Unit 2
    "accommodate": "large spacious university auditorium hall, welcoming small slim white pictogram usher standing near rows of neat cushioned seats ready to accommodate hundreds of arriving guests, hall entrance and polished floor line",
    "accommodation": "comfortable student guest lodge room, small slim white pictogram traveler settling into cozy tidy accommodation with wooden study desk, bed and warm lamp, room window and floor line",
    "accompanied by": "cozy rain shelter porch, small slim white pictogram standing safely under porch canopy watching rainy squall accompanied by wind gusts dancing across yard, porch railing and stone floor line",
    "accompany": "bright hospital reception foyer, kind small slim white pictogram walking gently beside a nervous family member to accompany them towards the doctor clinic, hall signs and polished floor line",
    "accomplish": "mountain peak sunrise summit, joyful small slim white pictogram hiker planting a cheerful summit flag having accomplished the difficult climb, rocky summit ledge and ground line",
    "accomplished": "grand classical music auditorium, gifted small slim white pictogram concert pianist performing gracefully at a sleek grand piano, stage floor line and warm spotlight",
    "accord": "international diplomacy conference hall, two smiling small slim white pictogram ambassadors holding up signed treaty papers in complete mutual accord, meeting podium and stage line",
    "according to": "science weather broadcast studio, small slim white pictogram presenter holding weather pointer explaining cloud map according to latest satellite meteorological forecast, studio monitor and floor line",
    "account": "modern bank branch counter, polite small slim white pictogram customer receiving a newly printed savings account booklet from bank teller, counter divider and floor line",
    "account for": "environmental ecology laboratory, thoughtful small slim white pictogram researcher pointing at pie chart explaining factors that account for seasonal ecosystem changes, laboratory chalkboard and floor line",
    "accumulate": "winter mountain cabin roof, peaceful small slim white pictogram looking outside window admiring thick soft white snow beginning to accumulate on eaves and fence, wooden windowsill and cabin floor line",
    "accuracy": "astronomy measurement laboratory, meticulous small slim white pictogram scientist adjusting a high precision laser instrument ensuring maximum measurement accuracy, calibration workbench and floor line",
    "accurate": "meteorological weather station, observant small slim white pictogram student comparing an accurate digital temperature sensor with a wall chart, weather station desk and floor line",
    "accustomed to": "sunny desert botanical greenhouse, resilient small slim white pictogram caretaker tending to lush green desert succulents and cactus plants accustomed to intense dry warmth, greenhouse gravel path line",
    "ache": "cozy recovery room sofa, small slim white pictogram resting comfortably with a soft warming compress on tired knee after a long mountain walk, footstool and living room floor line",
    "achieve": "athletic sports stadium finish ribbon, jubilant small slim white pictogram runner crossing marathon finish line having achieved the personal best distance goal, running track lines and bleachers",
    "acquire": "bright language academy study lounge, enthusiastic small slim white pictogram student reading international storybook practicing diligently to acquire fluent conversational skills, bookshelf and table line",
    "acquisition": "cozy home library corner, happy small slim white pictogram book collector placing a valuable new storybook acquisition onto wooden bookshelf, library ladder and rug floor line",
    "active": "sunny morning community park promenade, energetic small slim white pictogram walking briskly with walking sticks enjoying active healthy daily exercise, park trees and walkway line",
    "activity": "vibrant recreation center gym, cheerful small slim white pictogram swimming comfortably in clear indoor lap pool enjoying favorite water sport activity, pool lane markers and tiled deck line"
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

def update_dashboards(all_tasks: list, done_records: dict, current_task: dict = None, status_phase: str = "진행 중", started_at: float = 0):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(all_tasks)
    n_done = len(done_records)
    pct = (n_done / total * 100) if total else 100
    bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))

    elapsed_sum = sum(v.get("elapsed", 0) for v in done_records.values() if v.get("elapsed", 0) > 0)
    measured_count = sum(1 for v in done_records.values() if v.get("elapsed", 0) > 0)
    avg = (elapsed_sum / measured_count) if measured_count else 0
    remaining_tasks = total - n_done
    remain_min = (avg * remaining_tasks / 60) if avg else 0
    run_min = ((time.time() - started_at) / 60) if started_at else 0

    def state_md(t):
        w = t["word"]
        if w in done_records:
            sec = done_records[w].get("elapsed", 0)
            sz = done_records[w].get("size", "-")
            return f"✅ 완료 ({sec:.1f}초, {sz})" if sec > 0 else f"✅ 기존 파일 확인 ({sz})"
        if current_task and t["word"] == current_task["word"]:
            return "🔄 **렌더링 중...**"
        return "🕒 대기 중"

    # Markdown Dashboard
    md = [
        "# 🚀 토플(TOEFL) 선형그래픽 실시간 상황판 (Live Dashboard)\n",
        f"> **단계**: {status_phase}  ",
        f"> **진행률**: `[{bar}] {pct:.1f}% ({n_done} / {total})`  ",
        f"> **현재 작업**: {current_task['level'] + ' ' + current_task['id'] + ' ' + current_task['word'] + ' (' + current_task['meaning'] + ')' if current_task else '대기' }  ",
        f"> **소요/예상**: 총 {run_min:.1f}분 경과 · 평균 {avg:.1f}초/장 · 잔여 {remain_min:.1f}분  ",
        f"> **마지막 갱신**: {now_str} (개별 이미지 완료 시 즉시 Git 커밋 & 원격 푸시)\n",
        "---\n",
        "| 번호 | 단계 | ID | 단어 | 뜻 | 상태 |",
        "| :---: | :---: | :---: | :--- | :--- | :--- |"
    ]
    for idx, t in enumerate(all_tasks, 1):
        md.append(f"| {idx} | {t['level']} (U{t['unit']}) | {t['id']} | **{t['word']}** | {t['meaning']} | {state_md(t)} |")

    with open(DASHBOARD_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    # HTML Dashboard (8초 자동 새로고침)
    rows_html = ""
    for idx, t in enumerate(all_tasks, 1):
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

        rows_html += f"<tr class='{cls}'><td>{idx}</td><td>{t['level']} U{t['unit']}</td><td>{t['id']}</td><td><b>{w}</b></td><td>{t['meaning']}</td><td>{st_text}</td></tr>\n"

    html = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta http-equiv="refresh" content="8">
<title>토플 선형그래픽 실시간 대시보드</title><style>
body{{font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#ecedf1;color:#121826;margin:0;padding:24px}}
.wrap{{max-width:920px;margin:auto}} .meter{{height:12px;background:#dfe1e7;border-radius:99px;overflow:hidden;margin:12px 0}}
.meter i{{display:block;height:100%;width:{pct:.1f}%;background:#0EB582;transition:width .4s}}
table{{width:100%;border-collapse:collapse;margin-top:16px;background:#f8f9fa;border-radius:14px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06)}}
td,th{{padding:10px 14px;text-align:left;border-bottom:1px solid #e5e7eb}}
th{{background:#f1f3f5;font-weight:600}}
tr.done{{background:#fafffd}} tr.rendering{{background:#e6fcf5;font-weight:bold}} tr.waiting{{color:#6b7280}}
.card{{background:#ffffff;padding:16px 20px;border-radius:14px;box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:16px}}
small{{color:#6b7280}}
</style></head><body><div class="wrap">
<div class="card">
  <h2 style="margin:0 0 8px 0;">🚀 토플 선형그래픽 실시간 상황판</h2>
  <div><b>상태:</b> {status_phase} &nbsp;·&nbsp; <b>진행:</b> {n_done} / {total} ({pct:.1f}%) &nbsp;·&nbsp; <small>갱신 {now_str} (8초마다 새로고침)</small></div>
  <div class="meter"><i></i></div>
  <div style="font-size:13px;color:#4b5563;">총 {run_min:.1f}분 경과 · 평균 {avg:.1f}초/장 · 잔여 약 {remain_min:.1f}분 · <b>개별 단어 완성 시 즉시 GitHub 배포</b></div>
</div>
<table>
<tr><th>#</th><th>단계</th><th>ID</th><th>단어</th><th>뜻</th><th>상태</th></tr>
{rows_html}
</table>
</div></body></html>"""

    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html)

def build_unit_tasks(start_unit: int, end_unit: int):
    toefl_path = os.path.join(PROJECT_ROOT, "src", "data", "en", "levels", "toefl.json")
    tr_path = os.path.join(PROJECT_ROOT, "src", "data", "en", "tr", "ko.json")
    words_path = os.path.join(PROJECT_ROOT, "src", "data", "en", "words.json")

    with open(toefl_path, "r", encoding="utf-8") as f:
        toefl_words = json.load(f)
    with open(tr_path, "r", encoding="utf-8") as f:
        tr_ko = json.load(f).get("meanings", {})
    with open(words_path, "r", encoding="utf-8") as f:
        words_dict = json.load(f)

    tasks = []
    for u in range(start_unit, end_unit + 1):
        start_idx = (u - 1) * 20
        end_idx = min(start_idx + 20, len(toefl_words))
        unit_words = toefl_words[start_idx:end_idx]

        for i, w in enumerate(unit_words, start_idx + 1):
            wid = f"tf-{i}"
            meaning = tr_ko.get(wid, "")
            if w in TOEFL_PRESET_SCENES:
                scene = TOEFL_PRESET_SCENES[w]
            else:
                ex = words_dict.get(w, {}).get("example", "")
                if ex:
                    clean_ex = re.sub(r"[^\x00-\x7F]+", " ", ex).strip()
                    scene = f"bright indoor scene, small slim white pictogram character acting out: {clean_ex}, rich background furniture, props and floor line"
                else:
                    scene = f"bright indoor scene, small slim white pictogram character clearly illustrating the meaning of {w}, rich furniture and floor line"

            tasks.append({
                "level": "토플",
                "unit": u,
                "id": wid,
                "word": w,
                "meaning": meaning,
                "scene": scene
            })
    return tasks

def main():
    parser = argparse.ArgumentParser(description="토플 선형그래픽 연속 생성기")
    parser.add_argument("--start-unit", type=int, default=2, help="시작 유닛 (기본 2)")
    parser.add_argument("--end-unit", type=int, default=2, help="종료 유닛 (기본 2)")
    args = parser.parse_args()

    all_tasks = build_unit_tasks(args.start_unit, args.end_unit)
    done_records = {}
    started_at = time.time()

    # 사전 존재하는 파일 확인
    for t in all_tasks:
        fname = t["word"].replace(" ", "-") + ".png"
        fpath = os.path.join(ASSETS_DIR, fname)
        if os.path.exists(fpath):
            sz_kb = f"{os.path.getsize(fpath) // 1024}KB"
            done_records[t["word"]] = {"elapsed": 0.0, "size": sz_kb}

    update_dashboards(all_tasks, done_records, None, status_phase=f"토플 Unit {args.start_unit}~{args.end_unit} 생성 준비 완료", started_at=started_at)

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
            continue

        print(f"\n▶ [{lvl} U{u} - {wid}] '{w}' ({meaning}) 렌더링 시작...", flush=True)
        print(f"  Scene: {scene}", flush=True)

        update_dashboards(all_tasks, done_records, task, status_phase=f"{lvl} U{u} '{w}' 렌더링 중", started_at=started_at)

        seed = 3000 + int(wid.split("-")[1]) if "-" in wid and wid.split("-")[1].isdigit() else 42
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

            update_dashboards(all_tasks, done_records, None, status_phase=f"{lvl} U{u} '{w}' 완료 및 배포됨", started_at=started_at)

        except Exception as e:
            print(f"❌ '{w}' 작업 중 오류 발생: {e}", flush=True)
            time.sleep(3)

    print(f"\n🎉 토플 Unit {args.start_unit}~{args.end_unit} 작업이 성공적으로 완료되었습니다!", flush=True)
    update_dashboards(all_tasks, done_records, None, status_phase="작업 완료 🎉", started_at=started_at)

if __name__ == "__main__":
    main()
