# WordPic — 이미지로 외우는 영어 단어

초6·중1·중2·중3 영어 단어를 연상 이미지와 함께 암기하는 앱.
Expo(React Native) + NativeWind로 모바일 앱 · 모바일 웹 · 반응형 태블릿 웹을 하나의 코드베이스로 지원합니다.

## 실행

```bash
npm run dev      # 웹 자동 새로고침 개발 서버 (브라우저 자동 오픈)
npm start        # Expo 개발 서버 (iOS/Android)
npm run web      # 웹 전용 실행
npm run lint     # ESLint
```

- **Windows 원클릭 실행**: `start.bat` 더블 클릭 (브라우저 자동 오픈 + 코드 저장 시 자동 새로고침)
- **macOS / Linux 실행**: `./start.sh` 실행 (브라우저 자동 오픈 + 코드 저장 시 자동 새로고침)

## 구조

- `app/` — expo-router 라우트 (메인 / 학년별 유닛 / 단어 학습)
- `src/components/` — 공용 컴포넌트 (PillButton, GradeCard, StatCard)
- `src/constants/` — 학년·단어 데이터 로더, 단어 이미지 레지스트리
- `src/data/` — 단어 데이터 (중1 994단어, 중2 1003단어)
- `assets/words/` — 단어별 연상 이미지 (`<단어id>.png`)

## 디자인 규칙

- 전체 UI는 **뉴모피즘** 유지 (버튼 포함). 토큰: `bg-canvas`/`bg-surface`, `shadow-neu`/`shadow-neu-sm`/`shadow-neu-inset`/`shadow-neu-pressed`
- 폰트 크기: 테마 레벨에서 기본 크기를 약 30% 축소하여 컴팩트하고 쾌적한 가독성 확보

## 작업 내역

### 2026-09-09
- Expo + TypeScript + NativeWind(Tailwind) 초기 셋팅, expo-router로 앱/웹 단일 코드베이스 구성
- TanStack Query·Zustand·스토리지 추상화 등 기본 뼈대 추가
- 메인 화면: 헤더·프로필·탭 칩·성취 기록 2×2·학년 선택 카드·하단 네비
- 뉴모피즘 디자인 시스템 확립 (카드·칩·버튼·inset 토큰화), 필 버튼 공용 컴포넌트
- 단어 학습 화면: 플래시카드(뜻 가리기/북마크/거꾸로 학습 토글), 유닛 진행률
- 중학 1학년 단어 994개 데이터 입력(50유닛), 이미지 자리는 placeholder로 비움
- 중학 1학년 1단원 20개 단어 연상 암기 이미지 생성 및 등록
- 학습 학년을 중1~3, 고1~3으로 변경 및 ._ 파일 자동 삭제 훅 추가
- 중학 2학년 단어 1003개 데이터 추가(DAY 01~34, 51개 유닛 분할)
- 중1 1단원 20개 연상 이미지 상단 텍스트(단어, 노란 박스, 별점, 뜻) 제거 및 순수 일러스트 클린업
- 전체 UI 글씨 크기 30% 축소 적용 (tailwind theme.extend.fontSize 및 화면별 위계 정리)

### 2026-09-10
- 학습 화면 `가리기` 버튼이 예문뿐 아니라 한글 뜻까지 함께 가리도록 변경 (가려진 자리를 누르면 바로 표시)
- 이미지 좌우 스와이프로 앞뒤 단어 이동 추가 (그림만 캐러셀처럼 흐르고 단어·발음 영역은 고정)

### 2026-09-11
- 중학교 2학년 Unit 47~51 기존 단어 이미지 83개를 새 연상 일러스트로 전면 교체
- 중학교 2학년 Unit 17·18 단어 40개 연상 이미지 생성 및 학습 카드 매핑 등록
- 중학교 2학년 Unit 16 동사 20개(yell~drag) 연상 이미지 생성 및 학습 카드 매핑 등록
- Draw Things 로컬 API(127.0.0.1:7860) 연결 및 단어 이미지 자동 생성/매핑 스크립트 개선
- 휴가 신청 UI용 SVG 벡터 아이콘 4종 추가 (assets/icons/)
- Draw Things + potrace 연동 AI 생성 기반 초경량 SVG 벡터 변환 파이프라인 구축 (generate_svg_with_drawthings.py)
- 작업 완료 시 README 일별 작업 내역 자동 갱신 및 한글 커밋/푸시/풀 규칙 확립
- 중학교 2학년 Unit 15 (20개 단어: discuss, shrug, sniff 등) Draw Things 기반 연상 이미지 18종 생성 및 wordImages.ts 매핑 등록
- 중2 Unit 15 discuss(토론하다) 연상 이미지 초극세 펜선 및 회의실 씬으로 고도화 재생성
- 선형그래픽 표준 셋팅 확립: 초기 초극세선 셋팅, 배경 #f5f6f8, 선색 #030203, 풍성한 씬 구성 및 후처리 효과 없는 순수 출력 적용 (discuss 반영)
- Draw Things 선형그래픽 전용 에이전트 스킬(draw-things-linear-graphic) 구축 및 저장소 내장 (어느 컴퓨터에서든 git clone/pull 시 즉시 로드)
- Draw Things 로컬 API 연결 검증 및 Node.js 기반 선형그래픽 생성 엔진(generate_linear_graphic.js) 추가, 테스트 이미지(connect.png) 생성 완료
- 중학교 2학년 Unit 15 (2번~20번 단어 19종: shrug~prove) 선형그래픽 스킬 규격(0.05mm 초극세선, 1024x1024, 배경 #f5f6f8, 선색 #030203, 풍성한 씬)으로 전면 재생성 및 교체 적용
- GitHub Actions CI/Deploy 실패 수정: wordImages.ts 내 8개 단어 중복 프로퍼티 키 제거로 TS1117 타입 에러 해결 및 빌드 검증
- Draw Things 선형그래픽 스킬 업데이트: 인물/스틱맨 생성 시 목 없이 머리가 몸통에 바로 연결되는 노넥(No-Neck) 캐릭터 조형 규칙 공식 반영
- 중학교 1학년 Unit 1 (20개 단어 전원: beyond~teenager) 선형그래픽 스킬 규격(0.05mm 초극세선, 1024x1024, 배경 #f5f6f8, 선색 #030203, 노넥 스틱맨, 풍성한 씬)으로 전면 재생성 및 교체 적용
- 배치 파일(start.bat / start.sh)에 자동 새로고침(Fast Refresh) 로컬 웹 서버 실행 및 브라우저 자동 오픈 연동
- package.json 내 npm run dev 개발 서버 스크립트 추가 및 서버 종료 시 비정상 튕김 방지 안내 처리
- 자동 넘김(재생/멈춤) 설정을 zustand persist(AsyncStorage)로 영구 저장 — 단어 이동·뒤로가기·앱 재시작에도 유지
- 메인 화면을 실데이터 기반 "이어하기 홈"으로 전면 재작성 — 가짜 성취기록·프로필·출석뱃지·동작 안 하던 탭/벨 제거
- 학습 기록 영구 저장(zustand persist): entries·lastStudied·dailyLog·nickname, 일별 기록 60일 보관
- 홈 구성: 스트릭 칩 · 이어하기 히어로 카드 · 헷갈리는 단어 복습 · 오늘의 기록 3종 · 내 코스(학습률 실값)
- 단어장(app/wordbook.tsx)·설정(app/settings.tsx) 화면 신설, 하단 네비 3탭 실동작(usePathname 기반)
- 유닛 목록의 "0 / 20"을 실제 외운 개수로 교체하고 유닛별 진행바·완료 표시 추가
- findWord O(1) 색인화 및 unitsOf 캐시로 목록 성능 개선
- SSR(Node) 환경에서 AsyncStorage가 window를 참조해 개발 서버가 죽던 문제 수정(persistStorage 어댑터)
- Draw Things 선형그래픽 스킬 업데이트: 한글 텍스트 전면 배제 및 영문 우선 표기 원칙(원칙 7) 공식화, 100% 영문 프롬프트 구성 및 네거티브 프롬프트 한글 차단 반영
- 중학교 1학년 Unit 2 (20개 단어 전원: sophomore~brown) 선형그래픽 스킬 규격(0.05mm 초극세선, 1024x1024, 배경 #f5f6f8, 선색 #030203, 노넥 스틱맨, 영문 연출)으로 일괄 생성 및 wordImages.ts 매핑 등록
- 중학교 1학년 Unit 3 (20개 단어 전원: decrease~nearly) 선형그래픽 스킬 규격으로 일괄 생성 및 wordImages.ts 매핑 등록, TS1117 중복 키 방지 및 타입체크/웹 빌드 검증 완료
- Draw Things 선형그래픽 스킬 업데이트: 다중 이미지 일괄 생성 시 실시간 진행 상황판(Dashboard Table) 안내 규칙 공식화
- 중학교 1학년 Unit 3 단어 이미지 선형그래픽 생성 작업 중간 반영 (1~12번 12종: decrease~unlike 1024x1024 선형그래픽 생성 완료 및 적용, 잔여 단어 재개 CLI 옵션 추가)

