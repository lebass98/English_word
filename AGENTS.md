# Expo HAS CHANGED

Read the exact versioned docs at https://docs.expo.dev/versions/v57.0.0/ before writing any code.

## 작업 및 Git 커밋/동기화 규칙 (필수)

사용자의 요청/명령 작업을 완료했을 때 **묻지 말고** 아래 순서대로 자동 수행한다.

### 1. README.md 작업 내역 일별 추가
- 작업 완료 시 `README.md`의 `## 작업 내역` 섹션에 오늘 날짜(예: `### YYYY-MM-DD`)를 확인하고 없으면 신규 생성한다.
- 작업한 핵심 내용을 간략하게 글머리 기호(`-`)로 추가/정리한다.

### 2. 커밋 메시지 한글 작성 및 커밋
- 커밋 메시지는 **반드시 한글**로 번역/작성한다.
- 접두사 타입(`feat`, `fix`, `chore`, `docs`, `style`, `refactor` 등)만 영문으로 작성하고 제목과 내용은 한글로 작성한다.
- 제목은 50자 내외로 핵심을 요약하며, 세부 변경 사항이 있을 경우 본문에 기재한다.
- 커밋 명령:
  ```bash
  git add -A
  git commit -m "<타입>: <한글 요약>"
  ```

### 3. 풀(Pull) 및 푸시(Push) 동기화
- 원격 저장소(`origin`)가 연결되어 있는 경우, 반드시 최신 상태를 가져오고 푸시한다:
  ```bash
  git pull --rebase origin main
  git push origin main
  ```
- 원격 저장소가 설정되지 않은 경우 커밋까지만 완료하고 사용자에게 알린다.
- `pull --rebase` 중 충돌이 발생하면 임의로 해결하지 말고 즉시 중단 후 사용자에게 알린다.

