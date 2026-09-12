# 이미지 생성 기본 규칙 (Image Generation Default Rule)

## 기본 원칙 (Default Policy)
이 프로젝트에서 사용자가 "이미지 만들어보자", "이미지 만들어줘", "이미지 제작", "그림 생성" 등 단어나 개념에 대한 이미지 제작을 요청하는 경우, **기본적으로 모두 Draw Things 로컬 API 기반의 '선형그래픽(선화그래픽)' 생성 요청(`draw-things-linear-graphic` 스킬)**으로 간주하고 처리한다.

---

## 필수 준수 표준 (`draw-things-linear-graphic`)

1. **엔드포인트 & 프로토콜**:
   - Draw Things 로컬 API (`http://127.0.0.1:7860/sdapi/v1/txt2img`)
   - Protocol 설정: **HTTP** (gRPC가 아님)

2. **선형그래픽 조형 6대 원칙**:
   - **해상도**: `1024x1024` 네이티브 해상도 직접 생성 (업스케일 금지)
   - **극세선**: `0.05mm` 초극세 바늘선 (`thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke`)
   - **캐릭터**: 목 없는(No-Neck) 머리-몸통 직결 귀여운 스틱맨 (`neckless cute doodle stickman, round head attached directly to torso`)
   - **배경색**: 뉴모피즘 캔버스 테마 톤 `#f5f6f8` (`flat smooth light gray canvas background color #f5f6f8`)
   - **선색**: 딥 차콜 블랙 `#030203` (`dark charcoal ink color #030203`)
   - **씬 구성**: 단일 오브젝트만 두지 않고 바닥선, 가구, 배경 사물 등 풍성한 내러티브 묘사
   - **후처리 배제**: 임계값/필터 인위 적용 금지, 순수 렌더링 파일 저장
   - **언어 배제**: 씬 내 글자는 영문(English)만 허용하며 한글 텍스트는 전면 배제

3. **실시간 대시보드(상황판) 의무**:
   - 이미지 생성 작업 시작 즉시 1차 진행 현황판 출력
   - 단어 렌더링 진행 중 매 2분 주기로 실시간 진행 상황판 갱신
   - 전체 단어 완료 시 최종 집계 완료 상황판 출력

4. **생성 후 자동화 파이프라인**:
   - `assets/words/<단어>.png` 저장
   - `src/constants/wordImages.ts`에 단어명 및 단어 ID(`m1-xxx`, `m2-xxx` 등) 매핑 등록
   - `npm run lint` 코드 검증
   - 외장하드 메타데이터 파일 정리: `find . .. -name '._*' -type f -delete`
   - 한글 커밋 메시지 작성 후 `git pull --rebase origin main && git push origin main`
