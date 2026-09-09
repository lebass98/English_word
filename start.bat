@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ====================================================
echo   영어 단어 학습 앱 (English_word) 로컬 개발 서버
echo ====================================================
echo.

REM 1) Node.js 설치 확인
where node > nul 2>&1
if errorlevel 1 (
  echo [오류] Node.js 가 설치되어 있지 않습니다.
  echo        https://nodejs.org 에서 Node.js LTS(20 이상)를 설치한 뒤 다시 실행하세요.
  echo.
  pause
  exit /b 1
)

for /f "delims=" %%v in ('node -v') do set NODE_VER=%%v
echo [정보] Node.js !NODE_VER! 확인됨

REM 2) 의존성 패키지 확인 및 설치
if not exist "node_modules" (
  echo [정보] 의존성 패키지가 없어 새로 설치합니다. 잠시만 기다려주세요...
  call npm install
  call npx expo install react-dom react-native-web
  if errorlevel 1 (
    echo [오류] 패키지 설치에 실패했습니다.
    pause
    exit /b 1
  )
  echo [완료] 패키지 설치 완료
) else (
  if not exist "node_modules\react-native-web" (
    echo [정보] 웹 지원에 필요한 react-dom / react-native-web 패키지를 설치합니다...
    call npx expo install react-dom react-native-web
    echo [완료] 웹 패키지 설치 완료
  ) else (
    echo [정보] 의존성 패키지 확인됨
  )
)

REM 3) 8081 포트 정리 (이전 실행 프로세스 종료)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8081" ^| findstr "LISTENING"') do (
  echo [주의] 포트 8081 을 사용 중인 기존 프로세스(PID: %%a)를 종료합니다...
  taskkill /F /PID %%a > nul 2>&1
)

REM 4) 안내 메시지 출력
echo.
echo ----------------------------------------------------
echo   웹 브라우저 주소 :  http://localhost:8081
echo   자동 새로고침   :  코드 수정 저장 시 실시간 반영 (Fast Refresh)
echo.
echo   [단축키 안내]
echo    - w : 웹 브라우저 열기/다시 열기
echo    - r : 앱 다시 불러오기 (Reload)
echo    - a : Android 기기/에뮬레이터 연결
echo    - i : iOS 시뮬레이터 열기
echo    - c : 콘솔 화면 지우기
echo    - 종료 : 창 닫기 또는 Ctrl + C
echo ----------------------------------------------------
echo.

REM 5) 인자 처리 (기본값: --web)
set ARGS=%*
if "%ARGS%"=="" set ARGS=--web

echo [정보] Expo 로컬 웹 서버를 시작합니다... (옵션: %ARGS%)
call npx expo start %ARGS%

REM 종료 후 정리
echo.
echo [정보] 서버를 종료합니다...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8081" ^| findstr "LISTENING"') do (
  taskkill /F /PID %%a > nul 2>&1
)
echo [완료] 정상적으로 종료되었습니다.
endlocal
