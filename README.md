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
- `src/data/` — 단어 데이터 (중1 994단어)
- `assets/words/` — 단어별 연상 이미지 (`<단어id>.png`)

## 디자인 규칙

- 전체 UI는 **뉴모피즘** 유지 (버튼 포함). 토큰: `bg-canvas`/`bg-surface`, `shadow-neu`/`shadow-neu-sm`/`shadow-neu-inset`/`shadow-neu-pressed`
- 최소 폰트 16px(`text-base`), 여백 넉넉하게

## 작업 내역

### 2026-09-09
- Expo + TypeScript + NativeWind(Tailwind) 초기 셋팅, expo-router로 앱/웹 단일 코드베이스 구성
- TanStack Query·Zustand·스토리지 추상화 등 기본 뼈대 추가
- 메인 화면: 헤더·프로필·탭 칩·성취 기록 2×2·학년 선택 카드·하단 네비
- 뉴모피즘 디자인 시스템 확립 (카드·칩·버튼·inset 토큰화), 필 버튼 공용 컴포넌트
- 단어 학습 화면: 플래시카드(뜻 가리기/북마크/거꾸로 학습 토글), 유닛 진행률
- 중학 1학년 단어 994개 데이터 입력(50유닛), 이미지 자리는 placeholder로 비움
- 규칙 추가: 작업 완료 시 커밋→푸시→풀 + README 날짜별 작업 내역 기록
