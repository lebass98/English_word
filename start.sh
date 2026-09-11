#!/usr/bin/env bash
# ==========================================================
# 영어 단어 학습 앱 (English_word) 개발 서버 실행 스크립트 (macOS / Linux)
# - 웹 브라우저 자동 실행 및 코드 수정 시 자동 새로고침(Fast Refresh)
# - 서버가 비정상 종료되면 자동으로 다시 시작
# - macOS가 외장하드에 만드는 ._* 파일을 주기적으로 정리
# ==========================================================

set -u
cd "$(dirname "$0")"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { printf "${CYAN}[정보]${NC} %s\n" "$1"; }
ok()    { printf "${GREEN}[완료]${NC} %s\n" "$1"; }
warn()  { printf "${YELLOW}[주의]${NC} %s\n" "$1"; }
fail()  { printf "${RED}[오류]${NC} %s\n" "$1"; }

PORT=8081
RESTART_DELAY=3      # 비정상 종료 후 재시작까지 대기 시간(초)
MIN_UPTIME=10        # 이 시간보다 빨리 죽으면 "즉시 실패"로 간주(초)
MAX_FAST_FAILS=5     # 즉시 실패가 이만큼 연속되면 무한 재시작을 멈춤

echo ""
echo -e "${CYAN}====================================================${NC}"
echo -e "${BOLD}  영어 단어 학습 앱 (English_word)${NC}"
echo -e "${BOLD}  [자동 새로고침 로컬 개발 서버 실행기]${NC}"
echo -e "${CYAN}====================================================${NC}"
echo ""

# ── ._* 파일 정리 함수 ────────────────────────────────────
# macOS가 exFAT 외장하드에 만드는 AppleDouble 파일.
# expo-router가 이걸 라우트로 오인하면 빌드가 깨져 자동 새로고침이 멈춘다.
clean_appledouble() {
  find . -name '._*' -type f -delete 2>/dev/null || true
}

# 1) Node.js 설치 확인
if ! command -v node > /dev/null 2>&1; then
  fail "Node.js가 설치되어 있지 않습니다."
  echo "     https://nodejs.org 에서 Node.js LTS(20 이상)를 설치한 뒤 다시 실행하세요."
  exit 1
fi

NODE_VER=$(node -v)
info "Node.js ${NODE_VER} 확인됨"

# 2) 의존성 패키지 확인 및 설치
if [ ! -d "node_modules" ]; then
  info "의존성 패키지가 없어 새로 설치합니다. 잠시만 기다려주세요..."
  npm install
  npx expo install react-dom react-native-web
  ok "패키지 설치 완료"
else
  if [ ! -d "node_modules/react-native-web" ] || [ ! -d "node_modules/react-dom" ]; then
    info "웹 지원에 필요한 react-dom / react-native-web 패키지를 설치합니다..."
    npx expo install react-dom react-native-web
    ok "웹 패키지 설치 완료"
  else
    info "의존성 패키지 확인됨"
  fi
fi

# 3) 시작 전 정리: ._* 파일 + 포트 점유 프로세스
clean_appledouble
info "._* 임시 파일 정리 완료"

kill_port() {
  local pids
  pids=$(lsof -ti:$PORT 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "$pids" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
}

if [ -n "$(lsof -ti:$PORT 2>/dev/null || true)" ]; then
  warn "포트 ${PORT}를 사용 중인 이전 프로세스를 정리합니다..."
  kill_port
  ok "포트 정리 완료"
fi

# 4) 백그라운드 ._* 청소기 (서버가 도는 동안 계속 정리)
( while true; do sleep 3; clean_appledouble; done ) &
CLEANER_PID=$!

# 5) 종료 트랩 (Ctrl+C 등 중단 시 정리하고 재시작하지 않음)
stopping=0
cleaned=0
cleanup() {
  [ "$cleaned" = "1" ] && return 0
  cleaned=1
  stopping=1
  kill "$CLEANER_PID" 2>/dev/null || true
  echo ""
  info "개발 서버를 종료합니다..."
  kill_port
  clean_appledouble
  ok "정상적으로 종료되었습니다."
}
trap 'cleanup; exit 0' INT TERM
trap 'cleanup' EXIT

# 6) 안내 메시지 출력
echo ""
echo "----------------------------------------------------"
echo -e "  ${BOLD}웹 브라우저 주소 :${NC}  ${GREEN}http://localhost:${PORT}${NC}"
echo -e "  ${BOLD}브라우저 자동 열림:${NC}  서버 구동 시 기본 브라우저 자동 오픈"
echo -e "  ${BOLD}자동 새로고침   :${NC}  코드 수정 저장 시 브라우저 실시간 반영 (Fast Refresh)"
echo -e "  ${BOLD}자동 재시작     :${NC}  서버가 꺼지면 ${RESTART_DELAY}초 뒤 다시 실행"
echo ""
echo -e "  ${BOLD}[단축키 안내]${NC}"
echo "   - w : 웹 브라우저 열기/다시 열기"
echo "   - r : 앱 다시 불러오기 (Reload)"
echo "   - a : Android 에뮬레이터 또는 기기 연결"
echo "   - i : iOS 시뮬레이터 열기"
echo "   - c : 콘솔 로그 지우기"
echo "   - 완전 종료 : Ctrl + C"
echo "----------------------------------------------------"
echo ""

# 7) 실행 인자 처리 (기본값: --web)
ARGS="$*"
if [ -z "$ARGS" ]; then
  ARGS="--web"
fi

# 8) 서버 실행 + 자동 재시작 루프
attempt=0
fast_fails=0

while true; do
  attempt=$((attempt + 1))
  if [ "$attempt" -gt 1 ]; then
    info "개발 서버를 다시 시작합니다 (${attempt}번째 실행)"
  else
    info "자동 새로고침 Expo 로컬 웹 서버를 시작합니다... (옵션: $ARGS)"
    info "3초 후 기본 웹 브라우저가 자동으로 실행됩니다..."
    (
      sleep 3
      if command -v open >/dev/null 2>&1; then
        open "http://localhost:${PORT}" 2>/dev/null || true
      elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:${PORT}" 2>/dev/null || true
      fi
    ) &
  fi

  started_at=$(date +%s)
  # shellcheck disable=SC2086
  npx expo start $ARGS
  exit_code=$?
  ran_for=$(( $(date +%s) - started_at ))

  # Ctrl+C 등으로 사용자가 멈춘 경우 재시작하지 않는다
  if [ "$stopping" = "1" ]; then
    break
  fi

  if [ "$exit_code" -eq 0 ]; then
    info "서버가 정상 종료되었습니다."
    break
  fi

  # 시작하자마자 죽는 상황이 반복되면 무한 재시작을 멈춘다
  if [ "$ran_for" -lt "$MIN_UPTIME" ]; then
    fast_fails=$((fast_fails + 1))
  else
    fast_fails=0
  fi

  if [ "$fast_fails" -ge "$MAX_FAST_FAILS" ]; then
    fail "서버가 ${MAX_FAST_FAILS}번 연속으로 즉시 종료되었습니다. 자동 재시작을 멈춥니다."
    fail "위에 표시된 오류 메시지를 먼저 확인하세요."
    break
  fi

  warn "서버가 예기치 않게 종료되었습니다 (종료 코드 ${exit_code})."
  warn "${RESTART_DELAY}초 후 자동으로 다시 시작합니다. 완전히 멈추려면 Ctrl+C 를 누르세요."
  sleep "$RESTART_DELAY"
  kill_port
  clean_appledouble
done
