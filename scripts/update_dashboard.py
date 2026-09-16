#!/usr/bin/env python3
"""그림 현황판(상위 폴더의 LIVE_DASHBOARD.md / dashboard.html)을 다시 쓴다.

앱 안의 현황판 화면은 등록표를 그 자리에서 세므로 손댈 것이 없다.
이 파일들은 저장소 밖에서 진행 상황을 훑어보려고 두는 것이라 여기서 채운다.

과정마다 유닛(20단어)별로 그림이 다 채워졌는지 표시한다.

    python3 scripts/update_dashboard.py
"""
import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
WORKSPACE = os.path.dirname(ROOT)
sys.path.insert(0, SCRIPT_DIR)
from generate_h1_missing import registered_keys  # noqa: E402

LEVELS = [("middle-1", "중1"), ("middle-2", "중2"), ("middle-3", "중3"),
          ("high-1", "고1"), ("high-2", "고2"), ("high-3", "고3"),
          ("toefl", "토플")]
UNIT_SIZE = 20


def collect():
    keys = registered_keys()
    words = json.load(open(os.path.join(ROOT, "src/data/en/words.json"),
                           encoding="utf-8"))
    out = []
    for level, label in LEVELS:
        path = os.path.join(ROOT, f"src/data/en/levels/{level}.json")
        if not os.path.exists(path):
            continue
        spellings = json.load(open(path, encoding="utf-8"))
        have = [((words.get(s) or {}).get("conceptId") or s) in keys or s in keys
                for s in spellings]
        units = [have[i:i + UNIT_SIZE] for i in range(0, len(have), UNIT_SIZE)]
        out.append({
            "label": label,
            "total": len(have),
            "made": sum(have),
            "units": [{"no": i + 1, "total": len(u), "made": sum(u)}
                      for i, u in enumerate(units)],
        })
    return out


def bar(made, total, width=20):
    filled = 0 if not total else round(width * made / total)
    pct = 0.0 if not total else made / total * 100
    return f"[{'█' * filled}{'░' * (width - filled)}] {pct:.1f}% ({made} / {total})"


def daily():
    path = os.path.join(ROOT, "src/data/images/dailyCounts.json")
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"days": []}


def write_markdown(courses, day, stamp):
    total = sum(c["total"] for c in courses)
    made = sum(c["made"] for c in courses)
    done_units = sum(1 for c in courses for u in c["units"] if u["made"] == u["total"])
    all_units = sum(len(c["units"]) for c in courses)

    L = ["# 🎨 단어 그림 현황판", "",
         f"> **마지막 갱신**: {stamp}  ",
         f"> **전체**: {made} / {total} 장  ",
         f"> **완성 유닛**: {done_units} / {all_units}  ", "",
         "```", bar(made, total), "```", "",
         "## 과정별", "",
         "| 과정 | 그림 | 남은 그림 | 완성 유닛 | 진행 |",
         "| :--- | ---: | ---: | :---: | :--- |"]
    for c in courses:
        full = sum(1 for u in c["units"] if u["made"] == u["total"])
        left = c["total"] - c["made"]
        L.append(f"| **{c['label']}** | {c['made']} / {c['total']} | "
                 f"{left if left else '—'} | {full} / {len(c['units'])} | "
                 f"{bar(c['made'], c['total'], 12)} |")

    L += ["", "## 유닛별 완료 표시", "",
          "`✅` 다 채운 유닛 · 숫자는 그 유닛에 만든 그림 수 (20단어 기준)", ""]
    for c in courses:
        full = sum(1 for u in c["units"] if u["made"] == u["total"])
        L.append(f"### {c['label']} — 완성 {full} / {len(c['units'])} 유닛")
        L.append("")
        marks = []
        for u in c["units"]:
            mark = "✅" if u["made"] == u["total"] else f"{u['made']}/{u['total']}"
            marks.append(f"{u['no']}:{mark}")
        # 열 개씩 끊어 읽기 좋게 둔다
        for i in range(0, len(marks), 10):
            L.append("　".join(marks[i:i + 10]))
        L.append("")

    days = day.get("days", [])[-14:]
    if days:
        L += ["## 일자별 제작 (최근 14일)", "",
              "| 날짜 | 장수 |", "| :--- | ---: |"]
        L += [f"| {d['date']} | {d['count']} |" for d in days]
        L.append("")

    open(os.path.join(WORKSPACE, "LIVE_DASHBOARD.md"), "w",
         encoding="utf-8").write("\n".join(L))


def write_html(courses, stamp):
    total = sum(c["total"] for c in courses)
    made = sum(c["made"] for c in courses)
    done_units = sum(1 for c in courses for u in c["units"] if u["made"] == u["total"])
    all_units = sum(len(c["units"]) for c in courses)

    rows = []
    for c in courses:
        full = sum(1 for u in c["units"] if u["made"] == u["total"])
        pct = 0 if not c["total"] else c["made"] / c["total"] * 100
        cells = "".join(
            f"<span class='u {'done' if u['made'] == u['total'] else 'part'}' "
            f"title='{c['label']} {u['no']}단원 {u['made']}/{u['total']}'>"
            f"{u['no']}</span>"
            for u in c["units"])
        rows.append(
            f"<section><h2>{c['label']} "
            f"<small>{c['made']} / {c['total']}장 · 완성 유닛 {full}/{len(c['units'])}</small></h2>"
            f"<div class='bar'><i style='width:{pct:.1f}%'></i></div>"
            f"<div class='grid'>{cells}</div></section>")

    html = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>단어 그림 현황판</title><style>
:root{{color-scheme:light}}
body{{margin:0;padding:24px;background:#f5f6f8;color:#0f172a;
font:14px/1.6 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif}}
h1{{font-size:20px;margin:0 0 4px}}
.sub{{color:#64748b;font-size:12px;margin-bottom:20px}}
section{{background:#fff;border-radius:16px;padding:16px 18px;margin-bottom:14px;
box-shadow:0 1px 3px rgba(15,23,42,.08)}}
h2{{font-size:15px;margin:0 0 10px}}
h2 small{{font-weight:400;color:#64748b;margin-left:8px;font-size:12px}}
.bar{{height:8px;border-radius:99px;background:#e2e8f0;overflow:hidden;margin-bottom:12px}}
.bar i{{display:block;height:100%;background:#0eb582}}
.grid{{display:flex;flex-wrap:wrap;gap:4px}}
.u{{min-width:26px;text-align:center;padding:3px 5px;border-radius:7px;
font-size:11px;font-variant-numeric:tabular-nums}}
.u.done{{background:#0eb582;color:#fff}}
.u.part{{background:#e2e8f0;color:#64748b}}
</style></head><body>
<h1>단어 그림 현황판</h1>
<div class="sub">{stamp} 기준 · 전체 {made} / {total}장 · 완성 유닛 {done_units} / {all_units}
　<span style="color:#0eb582">■</span> 다 채운 유닛
　<span style="color:#94a3b8">■</span> 남은 유닛</div>
{''.join(rows)}
</body></html>"""
    open(os.path.join(WORKSPACE, "dashboard.html"), "w",
         encoding="utf-8").write(html)


def main():
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    courses = collect()
    write_markdown(courses, daily(), stamp)
    write_html(courses, stamp)
    for c in courses:
        full = sum(1 for u in c["units"] if u["made"] == u["total"])
        print(f"{c['label']:<4} {c['made']:>5} / {c['total']:<5} "
              f"완성 유닛 {full}/{len(c['units'])}")
    print("현황판 갱신 완료")


if __name__ == "__main__":
    main()
