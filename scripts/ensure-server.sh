#!/usr/bin/env bash
# ==========================================================
# 개발 서버가 꺼져 있으면 다시 띄운다.
#
# Claude Code 훅에서 호출된다 (SessionStart / UserPromptSubmit / Stop).
# 작업 도중 서버가 죽거나, 검증하느라 껐다가 다시 켜지 않은 경우를 막는다.
# 이미 떠 있으면 아무것도 하지 않는다.
# ==========================================================

PORT=8081
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"

cd "$ROOT" 2>/dev/null || exit 0

# lsof가 없는 환경(윈도우 등)에서는 조용히 넘어간다
command -v lsof > /dev/null 2>&1 || exit 0

# 이미 포트를 쓰고 있거나 expo 프로세스가 살아 있으면 그대로 둔다.
# (start.sh가 부팅 중이라 아직 포트를 안 열었을 수도 있으므로 둘 다 확인)
if lsof -ti:"$PORT" > /dev/null 2>&1; then
  exit 0
fi
if pgrep -f "expo start" > /dev/null 2>&1 || pgrep -f "start\.sh" > /dev/null 2>&1; then
  exit 0
fi

# 실행 로그는 .expo 아래에 남긴다 (.gitignore에 이미 포함됨)
mkdir -p .expo
nohup ./start.sh --web > .expo/dev-server.log 2>&1 &
disown 2>/dev/null || true

# 훅이 붙잡히지 않도록 바로 빠져나온다
echo '{"systemMessage":"개발 서버가 꺼져 있어 다시 시작했습니다 (http://localhost:8081)"}'
exit 0
