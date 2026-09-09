#!/usr/bin/env bash
# ==========================================================
# 영어 단어 학습 앱 (English_word) 개발 서버 실행 스크립트 (macOS / Linux)
# 웹 브라우저 자동 실행 및 코드 수정 시 자동 새로고침(Fast Refresh) 지원
# ==========================================================

set -e
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

echo ""
echo -e "${CYAN}====================================================${NC}"
echo -e "${BOLD}  영어 단어 학습 앱 (English_word) 로컬 개발 서버${NC}"
echo -e "${CYAN}====================================================${NC}"
echo ""

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
  # 웹 실행에 필수인 react-native-web 설치 여부 검사
  if [ ! -d "node_modules/react-native-web" ] || [ ! -d "node_modules/react-dom" ]; then
    info "웹 지원에 필요한 react-dom / react-native-web 패키지를 설치합니다..."
    npx expo install react-dom react-native-web
    ok "웹 패키지 설치 완료"
  else
    info "의존성 패키지 확인됨"
  fi
fi

# 3) 기존 8081 포트 점유 프로세스 정리
PORT=8081
PIDS=$(lsof -ti:$PORT 2>/dev/null || true)
if [ -n "$PIDS" ]; then
  warn "포트 ${PORT}를 사용 중인 이전 프로세스를 정리합니다..."
  echo "$PIDS" | xargs kill -9 2>/dev/null || true
  sleep 1
  ok "포트 정리 완료"
fi

# 4) 종료 트랩 (Ctrl+C 등 중단 시 프로세스 정리)
cleaned=0
cleanup() {
  [ "$cleaned" = "1" ] && return 0
  cleaned=1
  echo ""
  info "개발 서버를 종료합니다..."
  PIDS=$(lsof -ti:$PORT 2>/dev/null || true)
  [ -n "$PIDS" ] && echo "$PIDS" | xargs kill -9 2>/dev/null || true
  ok "정상적으로 종료되었습니다."
}
trap 'cleanup; exit 0' INT TERM EXIT

# 5) 안내 메시지 출력
echo ""
echo "----------------------------------------------------"
echo -e "  ${BOLD}웹 브라우저 주소 :${NC}  ${GREEN}http://localhost:8081${NC}"
echo -e "  ${BOLD}자동 새로고침   :${NC}  코드 수정 저장 시 실시간 반영 (Fast Refresh)"
echo ""
echo -e "  ${BOLD}[단축키 안내]${NC}"
echo "   - w : 웹 브라우저 열기/다시 열기"
echo "   - r : 앱 다시 불러오기 (Reload)"
echo "   - a : Android 에뮬레이터 또는 기기 연결"
echo "   - i : iOS 시뮬레이터 열기"
echo "   - c : 콘솔 로그 지우기"
echo "   - 종료 : Ctrl + C"
echo "----------------------------------------------------"
echo ""

# 6) 실행 인자 처리 (기본값: --web)
ARGS="$@"
if [ -z "$ARGS" ]; then
  ARGS="--web"
fi

info "Expo 로컬 웹 서버를 시작합니다... (옵션: $ARGS)"
npx expo start $ARGS
