# WordPic — 이미지로 외우는 영어 단어

초6·중1·중2·중3 영어 단어를 연상 이미지와 함께 암기하는 앱.
Expo(React Native) + NativeWind로 모바일 앱 · 모바일 웹 · 반응형 태블릿 웹을 하나의 코드베이스로 지원합니다.

## 실행

```bash
npm start        # Expo 개발 서버 (iOS/Android)
npm run web      # 웹
npm run lint     # ESLint
```

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
- 중학교 2학년 Unit 17·18 단어 40개 연상 이미지 생성 및 학습 카드 매핑 등록
- 중학교 2학년 Unit 16 동사 20개(yell~drag) 연상 이미지 생성 및 학습 카드 매핑 등록
- Draw Things 로컬 API(127.0.0.1:7860) 연결 및 단어 이미지 자동 생성/매핑 스크립트 개선
- 휴가 신청 UI용 SVG 벡터 아이콘 4종 추가 (assets/icons/)
- Draw Things + potrace 연동 AI 생성 기반 초경량 SVG 벡터 변환 파이프라인 구축 (generate_svg_with_drawthings.py)
- 작업 완료 시 README 일별 작업 내역 자동 갱신 및 한글 커밋/푸시/풀 규칙 확립
- 중학교 2학년 Unit 15 (20개 단어: discuss, shrug, sniff 등) Draw Things 기반 연상 이미지 18종 생성 및 wordImages.ts 매핑 등록
- 중2 Unit 15 discuss(토론하다) 연상 이미지 초극세 펜선 및 회의실 씬으로 고도화 재생성

