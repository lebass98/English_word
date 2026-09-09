@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo [정보] 개발 서버 프로세스를 종료합니다...

set FOUND=0
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8081" ^| findstr "LISTENING"') do (
  taskkill /F /PID %%a > nul 2>&1
  set FOUND=1
)

if "%FOUND%"=="1" (
  echo [완료] 개발 서버 프로세스를 모두 종료했습니다.
) else (
  echo [정보] 실행 중인 개발 서버가 없습니다.
)
echo.
pause
