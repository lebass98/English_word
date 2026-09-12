#!/usr/bin/env python3
"""
Draw Things 실시간 웹 상황판 생성기
- task log 및 word status를 파싱하여 프로젝트 루트의 dashboard.html을 항상 최신 상태로 갱신
- 브라우저에서 열어두면 5초마다 자동 새로고침되어 실시간 현황 및 최신 렌더링 이미지를 한 화면에서 확인
"""

import os
import re
import glob
import datetime

PROJECT_ROOT = "/Volumes/외장하드/App/eng_word/English_word"
WORKSPACE_ROOT = "/Volumes/외장하드/App/eng_word"
DASHBOARD_HTML = os.path.join(WORKSPACE_ROOT, "dashboard.html")
LOG_PATH = "/Users/kmac4_home/.gemini/antigravity-ide/brain/876c99e7-0792-48ed-a965-30555f31e1f4/.system_generated/tasks/task-815.log"

def generate_dashboard():
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 기본값
    current_unit = 9
    unit_total = 20
    completed_words = []
    current_word = {"word": "cough", "id": "m1-174", "meaning": "기침", "scene": ""}
    
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
        for line in lines:
            m_comp = re.search(r"생성 및 저장 완료 \(([\d\.]+)초\) -> .*/([^/]+)\.png", line)
            if m_comp:
                sec = m_comp.group(1)
                w_name = m_comp.group(2)
                if w_name not in [x["word"] for x in completed_words]:
                    completed_words.append({"word": w_name, "time": f"{sec}s"})
            
            m_curr = re.search(r"\[Unit (\d+) - (\d+)/(\d+)\] '([^']+)' \(([^:]+): ([^\)]+)\) 생성 중\.\.\.", line)
            if m_curr:
                current_unit = int(m_curr.group(1))
                current_word = {
                    "word": m_curr.group(4),
                    "id": m_curr.group(5),
                    "meaning": m_curr.group(6),
                    "index": int(m_curr.group(2))
                }

    # UNIT_DATA 동적 임포트
    try:
        from generate_m1_continuous_linear import UNIT_DATA
        current_unit_words = UNIT_DATA.get(current_unit, [])
    except Exception:
        current_unit_words = []

    comp_dict = {x["word"]: x["time"] for x in completed_words}
    done_count = sum(1 for w in current_unit_words if w["word"] in comp_dict)
    percent = (done_count / 20.0) * 100 if current_unit_words else 0.0

    html = f"""<!DOCTYPE html>
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
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
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
      width: {percent}%;
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
      grid-template-columns: repeat(3, 1fr);
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
          <span style="font-size: 32px; font-weight: 800; color: #38bdf8;">{percent:.1f}%</span>
          <span style="font-size: 14px; color: var(--text-muted); margin-left: 4px;">({done_count}/20)</span>
        </div>
      </div>

      <div class="progress-bar-bg">
        <div class="progress-bar-fill"></div>
      </div>

      <div class="unit-history">
        <div class="unit-box">
          <span>Unit 7 (20단어)</span>
          <span style="color: #34d399; font-weight: 700;">✅ 배포 완료</span>
        </div>
        <div class="unit-box">
          <span>Unit 8 (20단어)</span>
          <span style="color: #34d399; font-weight: 700;">✅ 배포 완료</span>
        </div>
        <div class="unit-box" style="border: 1px solid var(--accent);">
          <span>Unit 9 (20단어)</span>
          <span style="color: #818cf8; font-weight: 700;">🔄 {done_count}/20 진행중</span>
        </div>
      </div>
    </div>

    <div class="card current-card">
      <div class="current-label">⚡ 현재 렌더링 중</div>
      <div class="current-word">{current_word['word']}</div>
      <div class="current-meta">{current_word['id']} · {current_word['meaning']}</div>
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
"""

    for idx, item in enumerate(current_unit_words, start=1):
        w = item["word"]
        wid = item["id"]
        mean = item["meaning"]
        
        if w in comp_dict:
            t = comp_dict[w]
            status_html = f'<span class="badge-done">✅ 완료 ({t})</span>'
        elif w == current_word['word']:
            status_html = f'<span class="badge-curr">🔄 렌더링 중...</span>'
        else:
            status_html = f'<span class="badge-wait">⏳ 대기 중</span>'

        html += f"""        <tr>
          <td style="color: var(--text-muted); font-family: 'JetBrains Mono';">{idx}</td>
          <td style="font-family: 'JetBrains Mono';">{wid}</td>
          <td style="font-weight: 700;">{w}</td>
          <td style="color: var(--text-muted);">{mean}</td>
          <td style="font-family: 'JetBrains Mono';">{comp_dict.get(w, "-")}</td>
          <td>{status_html}</td>
        </tr>
"""

    html += """      </tbody>
    </table>
  </div>
</body>
</html>
"""

    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[{now_str}] dashboard.html 생성 완료 -> {DASHBOARD_HTML}")

if __name__ == "__main__":
    generate_dashboard()
