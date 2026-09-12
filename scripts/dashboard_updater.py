import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)
DASHBOARD_MD = os.path.join(WORKSPACE_ROOT, "LIVE_DASHBOARD.md")
DASHBOARD_HTML = os.path.join(WORKSPACE_ROOT, "dashboard.html")

def update_dashboards(current_unit: int, current_idx: int, current_word_info: dict, elapsed_times: dict, status_text: str = "렌더링 진행 중", unit_data: dict = None):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if unit_data is None:
        try:
            from generate_m1_continuous_linear import UNIT_DATA as unit_data
        except Exception:
            unit_data = {}
    unit_words = unit_data.get(current_unit, [])
    done_count = sum(1 for w in unit_words if w["word"] in elapsed_times)
    pct = (done_count / 20.0) * 100

    # 1. Update LIVE_DASHBOARD.md
    md_lines = [
        "# 🚀 Draw Things 선형그래픽 실시간 상황판 (Live Dashboard)\n",
        f"> **상태**: 🟢 Unit {current_unit} ({done_count}/20) - {status_text}  ",
        f"> **마지막 갱신**: {now_str}  ",
        "> **파이프라인**: 매 유닛(20단어) 완료 시마다 자동 앱 적용(`wordImages.ts`) + 린트 검증 + Git 커밋 & 원격 푸시 수행  ",
        "> *(팁: 이 파일을 IDE의 `Markdown Preview (Cmd+K V)`로 열어두시면 실시간으로 리프레시되는 현황을 확인하실 수 있습니다.)*\n",
        "---\n",
        "## 📊 전체 진행 요약\n",
        "| 구분 | 대상 유닛 | 진행 단어 수 | 진행률 | 현재 상태 |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    max_u = max(unit_data.keys()) if unit_data else 13
    for u in range(7, max_u + 1):
        start_id = (u - 1) * 20 + 1
        end_id = u * 20
        if u < current_unit:
            md_lines.append(f"| **중1 Unit {u}** | m1-{start_id} ~ m1-{end_id} | **20 / 20** | **100%** | ✅ GitHub 배포 완료 |")
        elif u == current_unit:
            w_name = current_word_info.get("word", "")
            md_lines.append(f"| **중1 Unit {u}** | m1-{start_id} ~ m1-{end_id} | **{done_count} / 20** | **{pct:.1f}%** | 🔄 **{w_name} 렌더링 중** |")
        else:
            md_lines.append(f"| **중1 Unit {u}** | m1-{start_id} ~ m1-{end_id} | 0 / 20 | 0% | ⏳ 대기 중 |")

    filled_blocks = int(pct // 5)
    empty_blocks = 20 - filled_blocks
    progress_bar = "█" * filled_blocks + "░" * empty_blocks

    md_lines.extend([
        "\n---\n",
        f"## 🔄 현재 유닛: Unit {current_unit} 상세 진행 현황 ({done_count} / 20 완료)\n",
        "```",
        f"[{progress_bar}] {pct:.1f}% ({done_count} / 20 완료)",
        "```\n",
        "| 번호 | ID | 단어 | 한글 의미 | 렌더링 소요 시간 | 상태 |",
        "| :---: | :---: | :---: | :---: | :---: | :---: |"
    ])

    for i, item in enumerate(unit_words, start=1):
        w = item["word"]
        wid = item["id"]
        mean = item["meaning"]
        if w in elapsed_times:
            t_sec = f"{elapsed_times[w]:.1f}초"
            st = f"✅ 완료 (`assets/words/{w}.png`)"
        elif i == current_idx:
            t_sec = "-"
            st = "🔄 **생성 중 (현재 진행 중)**"
        else:
            t_sec = "-"
            st = "⏳ 대기 중"
        md_lines.append(f"| {i} | {wid} | **{w}** | {mean} | {t_sec} | {st} |")

    md_lines.extend([
        "\n---\n",
        "## ⏱️ 자동화 배포 약속",
        f"- **Unit {current_unit} 완료 즉시**: 앱 등록(`wordImages.ts`) -> 린트 검증 -> 임시파일 정리 -> Git 커밋 및 Push가 자동으로 완수되며 다음 유닛으로 연속 진행됩니다.\n"
    ])

    with open(DASHBOARD_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # 2. Update dashboard.html
    html_rows = ""
    for i, item in enumerate(unit_words, start=1):
        w = item["word"]
        wid = item["id"]
        mean = item["meaning"]
        if w in elapsed_times:
            badge = f'<span class="badge-done">✅ 완료 ({elapsed_times[w]:.1f}s)</span>'
            time_str = f"{elapsed_times[w]:.1f}s"
        elif i == current_idx:
            badge = '<span class="badge-curr">🔄 렌더링 중...</span>'
            time_str = "-"
        else:
            badge = '<span class="badge-wait">⏳ 대기 중</span>'
            time_str = "-"
        html_rows += f"""        <tr>
          <td style="color: var(--text-muted); font-family: 'JetBrains Mono';">{i}</td>
          <td style="font-family: 'JetBrains Mono';">{wid}</td>
          <td style="font-weight: 700;">{w}</td>
          <td style="color: var(--text-muted);">{mean}</td>
          <td style="font-family: 'JetBrains Mono';">{time_str}</td>
          <td>{badge}</td>
        </tr>\n"""

    history_boxes = ""
    for u in range(7, max_u + 1):
        if u < current_unit:
            history_boxes += f"""        <div class="unit-box">
          <span>Unit {u} (20단어)</span>
          <span style="color: #34d399; font-weight: 700;">✅ 배포 완료</span>
        </div>\n"""
        elif u == current_unit:
            history_boxes += f"""        <div class="unit-box" style="border: 1px solid var(--accent);">
          <span>Unit {u} (20단어)</span>
          <span style="color: #818cf8; font-weight: 700;">🔄 {done_count}/20 진행중</span>
        </div>\n"""
        else:
            history_boxes += f"""        <div class="unit-box">
          <span>Unit {u} (20단어)</span>
          <span style="color: #6b7280; font-weight: 700;">⏳ 대기중</span>
        </div>\n"""

    curr_w = current_word_info.get("word", "")
    curr_id = current_word_info.get("id", "")
    curr_mean = current_word_info.get("meaning", "")

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🎨 Draw Things 실시간 렌더링 상황판</title>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-canvas: #0f1117;
      --bg-card: #181b24;
      --bg-card-sub: #212530;
      --accent: #6366f1;
      --accent-glow: rgba(99, 102, 241, 0.4);
      --success: #10b981;
      --success-glow: rgba(16, 185, 129, 0.3);
      --warning: #f59e0b;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --border: rgba(255, 255, 255, 0.08);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Pretendard', sans-serif;
      background: var(--bg-canvas);
      color: var(--text-main);
      padding: 24px;
      min-height: 100vh;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 24px;
    }}
    .title-group {{ display: flex; align-items: center; gap: 14px; }}
    .status-badge {{
      background: var(--success-glow);
      color: var(--success);
      border: 1px solid var(--success);
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .pulse-dot {{
      width: 8px;
      height: 8px;
      background: var(--success);
      border-radius: 50%;
      animation: pulse 1.5s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.4; transform: scale(1.3); }}
    }}
    .refresh-hint {{
      font-size: 12px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }}
    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
    }}
    .progress-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-bottom: 12px;
    }}
    .progress-bar-bg {{
      width: 100%;
      height: 16px;
      background: var(--bg-card-sub);
      border-radius: 9999px;
      overflow: hidden;
      margin-bottom: 12px;
    }}
    .progress-bar-fill {{
      height: 100%;
      width: {pct}%;
      background: linear-gradient(90deg, #6366f1, #38bdf8);
      border-radius: 9999px;
      transition: width 0.6s ease;
      box-shadow: 0 0 12px var(--accent-glow);
    }}
    .current-card {{
      background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(24,27,36,0.9));
      border: 1px solid var(--accent);
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
    }}
    .current-label {{
      color: #38bdf8;
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }}
    .current-word {{
      font-size: 36px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 4px;
    }}
    .current-meta {{
      font-size: 16px;
      color: var(--text-muted);
      margin-bottom: 12px;
    }}
    .table-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
      overflow: hidden;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }}
    th {{
      color: var(--text-muted);
      font-size: 13px;
      font-weight: 600;
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
    }}
    td {{
      padding: 12px 14px;
      border-bottom: 1px solid rgba(255,255,255,0.03);
      font-size: 14px;
    }}
    .badge-done {{
      background: rgba(16,185,129,0.15);
      color: #34d399;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
    }}
    .badge-curr {{
      background: rgba(99,102,241,0.25);
      color: #818cf8;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      animation: pulse 1.5s infinite;
    }}
    .badge-wait {{
      color: #6b7280;
      font-size: 12px;
    }}
    .unit-history {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-top: 16px;
    }}
    .unit-box {{
      background: var(--bg-card-sub);
      border-radius: 10px;
      padding: 12px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <div class="header">
    <div class="title-group">
      <h1 style="font-size: 22px; font-weight: 800;">🎨 Draw Things 실시간 렌더링 상황판</h1>
      <div class="status-badge">
        <div class="pulse-dot"></div>
        LIVE RUNNING
      </div>
    </div>
    <div class="refresh-hint">
      마지막 갱신: {now_str} (8초 자동 새로고침)
    </div>
  </div>

  <div class="hero-grid">
    <div class="card">
      <div class="progress-header">
        <div>
          <span style="font-size: 14px; color: var(--text-muted); font-weight: 600;">CURRENT UNIT</span>
          <h2 style="font-size: 28px; font-weight: 800; margin-top: 4px;">중학교 1학년 Unit {current_unit}</h2>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 32px; font-weight: 800; color: #38bdf8;">{pct:.1f}%</span>
          <span style="font-size: 14px; color: var(--text-muted); margin-left: 4px;">({done_count}/20)</span>
        </div>
      </div>

      <div class="progress-bar-bg">
        <div class="progress-bar-fill"></div>
      </div>

      <div class="unit-history">
{history_boxes}
      </div>
    </div>

    <div class="card current-card">
      <div class="current-label">⚡ 현재 렌더링 중</div>
      <div class="current-word">{curr_w}</div>
      <div class="current-meta">{curr_id} · {curr_mean}</div>
      <div style="font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
        평균 렌더링: ~155초 / 단어
      </div>
    </div>
  </div>

  <div class="table-card">
    <h3 style="font-size: 16px; margin-bottom: 14px; font-weight: 700;">📋 Unit {current_unit} 단어별 상세 렌더링 리스트</h3>
    <table>
      <thead>
        <tr>
          <th>번호</th>
          <th>ID</th>
          <th>단어</th>
          <th>의미</th>
          <th>렌더링 소요시간</th>
          <th>상태</th>
        </tr>
      </thead>
      <tbody>
{html_rows}
      </tbody>
    </table>
  </div>
</body>
</html>
"""
    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
