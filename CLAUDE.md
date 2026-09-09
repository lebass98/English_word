@AGENTS.md

# 프로젝트 작업 규칙

## Git 작업 및 커밋 규칙 (필수)

작업 완료 시 또는 사용자의 커밋/배포/완료 요청이 있을 때 **묻지 말고** 아래 순서대로 자동 수행한다.

### 1. 커밋 메시지 한글 작성
- 커밋 메시지는 **반드시 한글**로 번역/작성한다.
- 접두사 타입(`feat`, `fix`, `chore`, `docs`, `style`, `refactor` 등)만 영문으로 작성하고 제목과 내용은 한글로 작성한다.
- 제목은 50자 내외로 핵심을 요약하며, 세부 변경 사항이 있을 경우 빈 줄 뒤에 본문을 기재한다.
- 커밋 명령:
  ```bash
  git add -A
  git commit -m "<타입>: <한글 요약>"
  ```

### 2. 풀(Pull) 및 푸시(Push) 동기화
- 원격 저장소(`origin`)가 연결되어 있는 경우, 반드시 최신 상태를 가져오고 푸시한다:
  ```bash
  git pull --rebase origin main
  git push origin main
  ```
- 원격 저장소가 설정되지 않은 경우 커밋까지만 완료하고 사용자에게 알린다.
- `pull --rebase` 중 충돌이 발생하면 임의로 해결하지 말고 즉시 중단 후 사용자에게 알린다.

## `._*` 파일 처리 규칙 (필수)

- 이 프로젝트는 exFAT 외장하드에 있어 macOS가 `._파일명` 형태의 AppleDouble 메타데이터 파일을 자동 생성한다.
- `._*` 파일은 expo-router 라우트 스캔, git 팩 인덱스 등을 깨뜨리므로 **발견 즉시 전부 삭제**한다.
- `.claude/settings.json`의 SessionStart / UserPromptSubmit / PostToolUse 훅이 자동으로 삭제한다. 훅이 놓친 경우 아래 명령으로 수동 정리한다:
  ```bash
  find . .. -name '._*' -type f -delete
  ```
- `._*` 파일은 절대 커밋하지 않는다 (`.gitignore`에 등록됨).
