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

### 2026-09-17
- 일본어 JLPT N5 Unit 4 단어 선형그래픽 이미지 제작 및 등록 (ご飯, 水, お茶, 牛乳, パン 외 15개)
- 일본어 JLPT N5 Unit 3 단어 선형그래픽 이미지 제작 및 등록 (学校, 教室, 部屋, 店, 銀行 외 15개)
- 일본어 단어에 한국어 발음 표기 추가 (N5 556단어 전원)
  - 국립국어원 일본어 표기법 기준 자동 변환: か·た행 어두 평음화, っ→ㅅ받침, ん→ㄴ받침, 장음 미표기
  - `scripts/ja_korean_reading.py` 로 생성해 `src/data/ja/tr/ko.json` 의 `readingKo` 에 저장
  - 학습 화면에서 가나 옆에 민트색으로 표시 (わたし 와타시)
- 일본어 JLPT N5 Unit 2 단어 선형그래픽 이미지 제작 및 등록 (国, 今, 今日, 明日, 昨日 외 15개)
- 일본어 JLPT N5 Unit 1 단어 선형그래픽 이미지 제작 및 등록 (私, あなた, 人, 男, 女 외 15개)
- 일본어 N5 556단어 장면을 전부 새로 작성하고 처음부터 다시 생성 시작
  - 기초 단어라 기존 장면(틀 문장·영어 카탈로그 차용)으로는 뜻이 안 드러나, 단어를 대표하는 물건·동작을 문장 맨 앞에 크게 두고 소품까지 상세히 묘사
  - 형용사는 대비 쌍, 시간·색·인사말은 영문 라벨과 말풍선으로 뜻을 못 박음. 색 이름은 모델이 채색하므로 대문자 라벨로만 표기
  - `generate_n5_continuous_linear.py` 가 스킬 스크립트를 직접 쓰도록 바꾸고 `--regenerate`(기존 그림 다시 그리기) 추가
- 토익 27단원부터 그림 82장 생성 후 사용자 요청으로 중단

