@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

set PORT=8081
set RESTART_DELAY=3
set MAX_FAST_FAILS=5
set ATTEMPT=0
set FAST_FAILS=0

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

REM 3) 안내 메시지 출력
echo.
echo ----------------------------------------------------
echo   웹 브라우저 주소 :  http://localhost:%PORT%
echo   자동 새로고침   :  코드 수정 저장 시 실시간 반영 (Fast Refresh)
echo   자동 재시작     :  서버가 꺼지면 %RESTART_DELAY%초 뒤 다시 실행
echo.
echo   [단축키 안내]
echo    - w : 웹 브라우저 열기/다시 열기
echo    - r : 앱 다시 불러오기 (Reload)
echo    - a : Android 기기/에뮬레이터 연결
echo    - i : iOS 시뮬레이터 열기
echo    - c : 콘솔 화면 지우기
echo    - 완전 종료 : 이 창을 닫거나 Ctrl + C 후 N
echo ----------------------------------------------------
echo.

REM 4) 인자 처리 (기본값: --web)
set ARGS=%*
if "%ARGS%"=="" set ARGS=--web

REM ── 서버 실행 + 자동 재시작 루프 ──────────────────────
:RUN_SERVER
set /a ATTEMPT+=1
call :KILL_PORT

if !ATTEMPT! GTR 1 (
  echo [정보] 개발 서버를 다시 시작합니다 ^(!ATTEMPT!번째 실행^)
) else (
  echo [정보] Expo 로컬 웹 서버를 시작합니다... ^(옵션: %ARGS%^)
)

REM 시작 시각 기록 (즉시 실패 판별용)
for /f "delims=" %%t in ('powershell -NoProfile -Command "[int][double]::Parse((Get-Date -UFormat %%s))"') do set START_TS=%%t

call npx expo start %ARGS%
set EXIT_CODE=!errorlevel!

for /f "delims=" %%t in ('powershell -NoProfile -Command "[int][double]::Parse((Get-Date -UFormat %%s))"') do set END_TS=%%t
set /a RAN_FOR=!END_TS!-!START_TS!

if !EXIT_CODE! EQU 0 (
  echo [정보] 서버가 정상 종료되었습니다.
  goto :FINISH
)

REM 시작하자마자 반복해서 죽으면 무한 재시작을 멈춘다
if !RAN_FOR! LSS 10 (
  set /a FAST_FAILS+=1
) else (
  set FAST_FAILS=0
)

if !FAST_FAILS! GEQ %MAX_FAST_FAILS% (
  echo [오류] 서버가 %MAX_FAST_FAILS%번 연속으로 즉시 종료되었습니다. 자동 재시작을 멈춥니다.
  echo [오류] 위에 표시된 오류 메시지를 먼저 확인하세요.
  goto :FINISH
)

echo [주의] 서버가 예기치 않게 종료되었습니다 ^(종료 코드 !EXIT_CODE!^).
echo [주의] %RESTART_DELAY%초 후 자동으로 다시 시작합니다. 완전히 멈추려면 이 창을 닫으세요.
timeout /t %RESTART_DELAY% /nobreak > nul
goto :RUN_SERVER

:KILL_PORT
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
  taskkill /F /PID %%a > nul 2>&1
)
exit /b 0

:FINISH
echo.
echo [정보] 서버를 종료합니다...
call :KILL_PORT
echo [완료] 정상적으로 종료되었습니다.
endlocal
