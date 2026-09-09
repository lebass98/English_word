#!/usr/bin/env bash
# ==========================================================
# 개발 서버 강제 종료 스크립트 (macOS / Linux)
# start.sh가 정상 종료되지 않았거나 포트가 남아있을 때 사용
# ==========================================================

cd "$(dirname "$0")"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

PORT=8081
found=0

PIDS=$(lsof -ti:$PORT 2>/dev/null || true)
if [ -n "$PIDS" ]; then
  printf "${CYAN}[정보]${NC} 포트 %s 프로세스를 종료합니다.\n" "$PORT"
  echo "$PIDS" | xargs kill -9 2>/dev/null || true
  found=1
fi

# 남은 metro/expo 프로세스 정리
PIDS=$(pgrep -f "expo start" 2>/dev/null || true)
if [ -n "$PIDS" ]; then
  printf "${CYAN}[정보]${NC} 남아 있는 Expo 프로세스를 정리합니다.\n"
  echo "$PIDS" | xargs kill -9 2>/dev/null || true
  found=1
fi

if [ "$found" = "1" ]; then
  printf "${GREEN}[완료]${NC} 개발 서버 프로세스를 모두 종료했습니다.\n"
else
  printf "${CYAN}[정보]${NC} 실행 중인 개발 서버가 없습니다.\n"
fi
