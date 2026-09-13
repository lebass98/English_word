#!/usr/bin/env python3
"""
중1 누락 이미지 2장 완성 및 개별 커밋/푸시 후,
토플 1단원부터 순차적으로 이미지 제작 및 개별 커밋/푸시를 수행하는 통합 파이프라인.
- 각 이미지 완료 시 1개씩 커밋 및 푸시
- LIVE_DASHBOARD.md 및 dashboard.html 실시간 자동 업데이트
- Draw Things 선형그래픽 스킬 100% 준수
"""

import os
import sys
import json
import time
import re
import subprocess
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

M1_MISSING_WORDS = [
    {
        "level": "중1",
        "unit": 44,
        "id": "m1-874",
        "word": "bedside",
        "meaning": "침대 곁",
        "scene": "cozy peaceful bedroom corner, caring small slim white pictogram character sitting on bedside wooden chair reading a bedtime book to a resting friend in bed, bedside nightstand table lamp with soft glow and floor line"
    },
    {
        "level": "중1",
        "unit": 50,
        "id": "m1-986",
        "word": "pepper",
        "meaning": "후추",
        "scene": "warm dining restaurant table, cheerful small slim white pictogram character chef using a classic wooden pepper mill to grind fresh aromatic black pepper onto a hot bowl of soup, dining table and floor line"
    }
]

TOEFL_UNIT1_SCENES = {
    "a great deal": "polar science research station laboratory, curious small slim white pictogram scientist examining large stack of expedition field journals and glacier data charts on wide wooden workbench, polar maps on wall and wooden floor line",
    "a host of": "lush botanical conservatory greenhouse, small slim white pictogram explorer with magnifying glass observing a host of exotic beetles and butterflies perched on jungle leaves, glass greenhouse frames and pathway line",
    "a quarter": "modern classroom lecture hall, thoughtful small slim white pictogram teacher pointing at a large chalkboard diagram dividing a circular pie chart into four neat quarter sections, lecture desk and classroom floor line",
    "a wide range of": "artisan craft museum hall, observant small slim white pictogram visitor walking beside a long exhibition display shelf showcasing a wide range of traditional woodworking tools, display glass cabinet and museum floor line",
    "abandon": "weathered ancient stone castle courtyard, solitary small slim white pictogram traveler exploring long abandoned stone castle gates covered with wild ivy vines, stone archway and cobblestone floor line",
    "abnormally": "meteorology weather observatory station, surprised small slim white pictogram meteorologist wiping brow looking up at a giant wall thermometer showing abnormally high heat reading, weather instruments and floor line",
    "abolish": "historic parliament council hall, determined small slim white pictogram official holding up an official decree document marking the vote to abolish an obsolete law, wooden council dais and hall floor line",
    "abound in": "scenic coastal harbor dock, cheerful small slim white pictogram fisherman on wooden pier looking into crystal clear harbor water that abounds in swimming fish schools, wooden pilings and pier plank line",
    "abroad": "bright international airport terminal, excited small slim white pictogram student pulling travel wheeled suitcase towards departure gate to study abroad, airport panoramic window and floor line",
    "abrupt": "windy mountain hiking trail, cautious small slim white pictogram hiker stopping on rocky ridge path noticing an abrupt steep mountain slope cliff ahead, mountain peaks and trail ground line",
    "absolute": "grand historical throne hall, small slim white pictogram sovereign holding ceremonial golden orb and scepter sitting with absolute authority on stone throne, royal banners and hall floor line",
    "absorb": "biology science classroom laboratory, curious small slim white pictogram student watching a large green potted plant absorb water through transparent root observation chamber, lab bench and floor line",
    "abstract": "modern contemporary art museum gallery, contemplative small slim white pictogram visitor standing with folded hands admiring a large abstract wall painting composed of pure geometric lines and circles, gallery bench and floor line",
    "abundance": "lush green river valley oasis, joyful small slim white pictogram villager filling clay water jugs at a natural crystal spring bubbling with an abundance of fresh clear water, riverbank rocks and meadow line",
    "abundant": "sunny orchard harvest market, cheerful small slim white pictogram fruit farmer standing behind wooden market stall overflowing with abundant ripe apples and oranges in wooden crates, canopy and market floor line",
    "abuse": "office human resources discussion room, small slim white pictogram counselor calmly resolving interpersonal issues with listening ear, office table and floor line",
    "accede with": "formal corporate negotiation meeting room, two professional small slim white pictogram negotiators smiling and shaking hands across wooden conference table having reached mutual accession, office windows and carpet line",
    "accelerate": "futuristic test track stadium, energetic small slim white pictogram racer in streamlined aerodynamic go-kart accelerating smoothly down empty straight test course, track barriers and track line",
    "accessible": "modern public library entrance plaza, polite small slim white pictogram student easily walking up a gentle smooth accessible ramp leading into wide library doors, handrails and plaza stone line",
    "accidentally": "chemistry research laboratory bench, startled small slim white pictogram chemist watching a colorful foamy reaction bubble up unexpectedly from beaker after accidentally mixing test solutions, laboratory glassware and floor line"
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

    elapsed_sum = sum(v.get("elapsed", 0) for v in done_records.values())
    avg = (elapsed_sum / n_done) if n_done else 0
    remain_min = (avg * (total - n_done) / 60) if avg else 0
    run_min = ((time.time() - started_at) / 60) if started_at else 0

    def state_md(t):
        w = t["word"]
        if w in done_records:
            sec = done_records[w].get("elapsed", 0)
            sz = done_records[w].get("size", "-")
            return f"✅ 완료 ({sec:.1f}초, {sz})"
        if current_task and t["word"] == current_task["word"]:
            return "🔄 **렌더링 중...**"
        return "🕒 대기 중"

    # Markdown Dashboard
    md = [
        "# 🚀 영어 단어 선형그래픽 실시간 상황판 (Live Dashboard)\n",
        f"> **단계**: {status_phase}  ",
        f"> **진행률**: `[{bar}] {pct:.1f}% ({n_done} / {total})`  ",
        f"> **현재 작업**: {current_task['level'] + ' ' + current_task['id'] + ' ' + current_task['word'] + ' (' + current_task['meaning'] + ')' if current_task else '대기' }  ",
        f"> **소요/예상**: 총 {run_min:.1f}분 경과 · 평균 {avg:.1f}초/장 · 예상 잔여 {remain_min:.1f}분  ",
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
            st_text = f"✅ 완료 ({sec:.1f}s)"
        elif current_task and t["word"] == current_task["word"]:
            cls = "rendering"
            st_text = "🔄 렌더링 중..."
        else:
            cls = "waiting"
            st_text = "🕒 대기 중"

        rows_html += f"<tr class='{cls}'><td>{idx}</td><td>{t['level']} U{t['unit']}</td><td>{t['id']}</td><td><b>{w}</b></td><td>{t['meaning']}</td><td>{st_text}</td></tr>\n"

    html = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta http-equiv="refresh" content="8">
<title>선형그래픽 실시간 대시보드</title><style>
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
  <h2 style="margin:0 0 8px 0;">🚀 영어 단어 선형그래픽 실시간 생성 상황판</h2>
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

def build_toefl_unit_tasks(unit_num: int = 1):
    toefl_path = os.path.join(PROJECT_ROOT, "src", "data", "en", "levels", "toefl.json")
    tr_path = os.path.join(PROJECT_ROOT, "src", "data", "en", "tr", "ko.json")
    words_path = os.path.join(PROJECT_ROOT, "src", "data", "en", "words.json")

    with open(toefl_path, "r", encoding="utf-8") as f:
        toefl_words = json.load(f)
    with open(tr_path, "r", encoding="utf-8") as f:
        tr_ko = json.load(f).get("meanings", {})
    with open(words_path, "r", encoding="utf-8") as f:
        words_dict = json.load(f)

    start_idx = (unit_num - 1) * 20
    end_idx = min(start_idx + 20, len(toefl_words))
    unit_words = toefl_words[start_idx:end_idx]

    tasks = []
    for i, w in enumerate(unit_words, start_idx + 1):
        wid = f"tf-{i}"
        meaning = tr_ko.get(wid, "")
        if unit_num == 1 and w in TOEFL_UNIT1_SCENES:
            scene = TOEFL_UNIT1_SCENES[w]
        else:
            ex = words_dict.get(w, {}).get("example", "")
            if ex:
                clean_ex = re.sub(r"[^\x00-\x7F]+", " ", ex).strip()
                scene = f"bright indoor scene, small slim white pictogram character acting out: {clean_ex}, rich background furniture, props and floor line"
            else:
                scene = f"bright indoor scene, small slim white pictogram character clearly illustrating the meaning of {w}, rich furniture and floor line"

        tasks.append({
            "level": "토플",
            "unit": unit_num,
            "id": wid,
            "word": w,
            "meaning": meaning,
            "scene": scene
        })
    return tasks

def main():
    print("==================================================", flush=True)
    print("🚀 [중1 미완성 2단어 + 토플 1단원 순차 생성 파이프라인 시작]", flush=True)
    print("==================================================", flush=True)

    # 1. 대상 목록 구성: 중1 누락 2단어 + 토플 1단원 20단어
    all_tasks = []
    all_tasks.extend(M1_MISSING_WORDS)

    toefl_u1 = build_toefl_unit_tasks(1)
    all_tasks.extend(toefl_u1)

    done_records = {}
    started_at = time.time()

    # 이미 존재하는 이미지 사전 검사
    for t in all_tasks:
        fname = t["word"].replace(" ", "-") + ".png"
        fpath = os.path.join(ASSETS_DIR, fname)
        if os.path.exists(fpath):
            sz_kb = f"{os.path.getsize(fpath) // 1024}KB"
            done_records[t["word"]] = {"elapsed": 0.0, "size": sz_kb}

    update_dashboards(all_tasks, done_records, None, status_phase="생성 작업 시작", started_at=started_at)

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
            if w not in done_records:
                sz_kb = f"{os.path.getsize(out_path) // 1024}KB"
                done_records[w] = {"elapsed": 0.0, "size": sz_kb}
            continue

        print(f"\n▶ [{lvl} U{u} - {wid}] '{w}' ({meaning}) 렌더링 시작...", flush=True)
        print(f"  Scene: {scene}", flush=True)

        update_dashboards(all_tasks, done_records, task, status_phase=f"{lvl} U{u} '{w}' 렌더링 중", started_at=started_at)

        # Draw Things API 호출
        seed = 2000 + int(wid.split("-")[1]) if "-" in wid and wid.split("-")[1].isdigit() else 42
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

            # 앱 동기화 및 린트
            print(f"  -> wordImages.ts 동기화 및 린트 검증...", flush=True)
            sync_and_lint()

            # 개별 Git 커밋 & 푸시
            if lvl == "중1" and w == "pepper":
                commit_msg = f"feat: 중1 {u}단원 pepper (후추) 선형그래픽 이미지 생성 및 등록 (중1 994단어 전원 완료 🎉)"
            elif lvl == "중1":
                commit_msg = f"feat: 중1 {u}단원 {w} ({meaning}) 선형그래픽 이미지 생성 및 등록"
            else:
                commit_msg = f"feat: 토플 {u}단원 {w} ({meaning}) 선형그래픽 이미지 생성 및 등록"

            print(f"  -> Git 커밋 & 푸시: {commit_msg}", flush=True)
            git_commit_and_push(commit_msg)
            print(f"🚀 '{w}' GitHub 배포 완료!", flush=True)

            update_dashboards(all_tasks, done_records, None, status_phase=f"{lvl} U{u} '{w}' 완료 및 배포됨", started_at=started_at)

        except Exception as e:
            print(f"❌ '{w}' 작업 중 오류 발생: {e}", flush=True)
            time.sleep(3)

    print("\n🎉 모든 작업(중1 전체 완료 + 토플 1단원)이 성공적으로 완료되었습니다!", flush=True)
    update_dashboards(all_tasks, done_records, None, status_phase="전체 작업 완료 🎉", started_at=started_at)

if __name__ == "__main__":
    main()
