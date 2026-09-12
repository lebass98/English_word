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

## 이미지 제작 규칙 (필수 준수)

이 프로젝트에서 사용자가 "이미지 만들어보자", "이미지 만들어줘", "이미지 제작", "그림 생성" 등 단어나 개념에 대한 이미지 제작을 요청하는 경우, **기본적으로 모두 Draw Things 로컬 API 기반의 '선형그래픽(선화그래픽)' 생성 요청(`draw-things-linear-graphic` 스킬)**으로 간주하고 처리한다.

1. **Draw Things 설정**:
   - 로컬 API (`http://127.0.0.1:7860/sdapi/v1/txt2img`), Protocol: **HTTP**
2. **선형그래픽 조형 6대 원칙**:
   - `1024x1024` 네이티브 해상도, 0.05mm 초극세 바늘선 (`thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke`)
   - 목 없는(No-Neck) 머리-몸통 직결 원형 머리 스틱맨 캐릭터
   - 뉴모피즘 캔버스 테마 `#f5f6f8` 배경 + `#030203` 딥 차콜 블랙 선
   - 풍성한 배경 씬(바닥선, 가구, 소품 등 내러티브 묘사)
   - 후처리 효과(필터, 임계값) 배제 원본 보존
   - 씬 내 텍스트는 영문(English)만 사용하며 한글 텍스트 전면 배제
3. **실시간 대시보드(상황판) 의무**:
   - 제작 시작 즉시 1차 현황판 출력
   - 단어 렌더링 진행 중 매 2분 주기로 실시간 상황판 갱신
   - 작업 완료 시 최종 집계 완료 상황판 출력
4. **자동화 파이프라인**:
   - `assets/words/<단어>.png` 저장 -> `src/constants/wordImages.ts` 등록 -> `npm run lint` -> `find . .. -name '._*' -type f -delete` -> 한글 커밋 & push


