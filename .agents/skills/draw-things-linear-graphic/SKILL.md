---
name: draw-things-linear-graphic
description: >-
  Draw Things 로컬 API(http://127.0.0.1:7860)를 활용하여 '선형그래픽' 스타일의 고품질 일러스트 및 단어 이미지를 생성하는 스킬.
  사용자가 '선형그래픽', 극세선 라인아트, 드로우씽즈(Draw Things) 기반 단어/아이콘 이미지 생성을 요청할 때 활성화된다.
  초기 0.05mm 초극세선, 캔버스 배경색 #f5f6f8, 선색 #030203, 풍성한 씬 구성, 후처리 효과 없는 1024x1024 순수 렌더링 출력을 보장한다.
---

# Draw Things 선형그래픽 생성 스킬 (draw-things-linear-graphic)

이 스킬은 **Draw Things** 앱의 로컬 API를 통해 일관된 톤앤매너의 **'선형그래픽'** 일러스트를 생성하는 워크플로우를 정의합니다.

어떤 컴퓨터에서든 이 저장소를 클론(`git pull`)하면 자동으로 인식되며, 외부 파이썬 패키지 설치(Pillow 등) 없이 기본 `python3`만으로 즉시 작동합니다.

---

## 🎨 선형그래픽 6대 핵심 원칙

1. **초극세 바늘선 (0.05mm Hairline)**:
   - 512px 업스케일 방식을 쓰지 않고, **1024×1024 네이티브 해상도**로 직접 생성하여 선 굵기를 초기부터 가장 얇게 렌더링합니다.
   - 프롬프트 키워드: `thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke`, `extremely fine crisp outlines`.
2. **목 없는(No-Neck) 머리-몸통 직접 연결 캐릭터**:
   - 사람/스틱맨 캐릭터는 **목을 절대 생성하지 않고, 동그란 머리가 몸통에 바로 부착**되도록 구성합니다.
   - 긍정 프롬프트: `neckless cute doodle stickman, perfectly round circle head attached directly to torso with completely no neck, neckless stick figure`.
   - 부정 프롬프트: `neck, long neck, throat, collar, neck line, detailed neck anatomy`.
3. **배경 색상코드 `#f5f6f8`**:
   - 뉴모피즘 캔버스 테마와 완벽히 일치하는 소프트 라이트그레이 톤 (`flat smooth light gray canvas background color #f5f6f8`).
4. **선 색상코드 `#030203`**:
   - 순수 칠흑색에 가까운 딥 차콜 블랙 잉크 (`dark charcoal ink color #030203`).
5. **풍성한 씬 (Rich Scene Content)**:
   - 인물 1명만 덩그러니 있는 것이 아니라, 배경 가구, 벽면 장식(시계, 책장, 조명), 바닥선, 소품, 2~4명의 귀여운 원형 머리 스틱맨 동료들의 상호작용을 풍성하게 묘사합니다.
6. **추후 수정 및 효과 일체 배제 (Zero Post-Processing)**:
   - 생성 후 임계값(Threshold), 색상 왜곡, 필터 효과를 인위적으로 주지 않고, 모델 본연의 부드러운 안티에일리어싱을 보존한 **순수 렌더링 원본 파일**을 그대로 저장합니다.
7. **한글 텍스트 전면 배제 및 영문 우선 표기 (English Only / No Korean Text)**:
   - 씬 내부의 간판, 표지판, 칠판, 배너, 서류, 책 표지 등 글자가 들어가는 모든 요소에 **한글은 절대 넣지 않고, 반드시 간결하고 명확한 영문(English text, 예: 'STORE', 'SALE', 'LIBRARY', 'POST', 'BOUND FOR SEOUL')** 만을 사용합니다.
   - 프롬프트 작성 시에도 한글 단어 뜻(예: `(가슴)`, `(가루)`)을 직접 전달하지 않고, **100% 순수 영문 씬 묘사(English prompt only)** 로 작성하여 언어 혼선으로 인한 렌더링 아티팩트와 글자 깨짐을 원천 방지합니다.
   - 부정(Negative) 프롬프트 필수: `Korean text, Hangul, Korean letters, non-English text, broken characters, foreign characters`.


---

## 💻 사전 준비사항 (어떤 컴퓨터에서든 공통)

1. **Draw Things 앱 실행**:
   - Mac 또는 지원 기기에서 `Draw Things` 앱을 실행합니다.
2. **API 서버 켜기**:
   - 설정(Settings)에서 **API Server (Port 7860)**를 활성화합니다.
   - 기본 주소: `http://127.0.0.1:7860` (원격 PC의 경우 해당 IP 지정 가능)
3. **권장 모델**:
   - `z_image_turbo_1.0_q8p.ckpt` (또는 동급 고속 1024x1024 모델, Steps: 8)

---

## 🚀 사용 방법 (실행 명령어)

추가 의존성 설치 없이 환경에 따라 `node` 또는 `python3`로 스크립트를 바로 호출합니다.

```bash
# Node.js 사용 시 (권장, 추가 도구 설치 불필요)
node .agents/skills/draw-things-linear-graphic/scripts/generate_linear_graphic.js \
  "meeting room with colleagues discussing charts on whiteboard" \
  --output assets/words/discuss.png \
  --seed 999

# Python3 사용 시 (Xcode Command Line Tools 등 파이썬 설치 환경)
python3 .agents/skills/draw-things-linear-graphic/scripts/generate_linear_graphic.py \
  "meeting room with colleagues discussing charts on whiteboard" \
  --output assets/words/discuss.png \
  --seed 999
```

### 파라미터 옵션

| 옵션 | 단축키 | 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| `concept` | (필수) | - | 생성할 씬 또는 단어 콘셉트 영문 묘사 |
| `--output` | `-o` | (필수) | 결과 이미지를 저장할 경로 (.png) |
| `--url` | `-u` | `http://127.0.0.1:7860/sdapi/v1/txt2img` | Draw Things API 주소 |
| `--seed` | `-s` | `42` | 생성 랜덤 시드 |
| `--width` | `-w` | `1024` | 가로 해상도 |
| `--height` | `-H` | `1024` | 세로 해상도 |
| `--steps` | - | `8` | 추론 스텝 수 |

---

## 📊 실시간 진행 상황판(Dashboard) 필수 실행 규칙 (필수 준수)

Draw Things를 이용한 이미지 제작 작업 진행 시, 사용자의 별도 요청이 없더라도 **반드시 아래 규칙에 따라 상황판을 실시간으로 표시하고 갱신**해야 합니다:

1. **작업 시작 즉시 현황판 1차 시행**:
   - 다중/단일 이미지 제작이 시작되는 즉시, 전체 대상 단어 목록과 함께 **초기 진행 상황판(Dashboard Table)을 무조건 렌더링**하여 보고합니다.
2. **2분 주기 실시간 현황판 갱신 (반드시 수행)**:
   - 이미지 1장 생성에 약 2분~2분 30초가 소요되므로, **매 2분마다 생성 진행 로그 및 파일 상태를 확인하여 상황판을 실시간으로 갱신**하여 출력합니다.
   - 단어가 완료될 때마다 상태를 즉시 `✅ 완료 (소요시간, 파일크기)`로 전환하고 다음 단어를 `⏳ 렌더링 중`으로 업데이트합니다.
3. **상황판 필수 표기 항목**:
   - 총 단어 수 대비 현재 진행률 프로그레스 바 (예: `[████░░░░░░░░] 35% (7/20)`)
   - 각 단어별 진행 상태: `✅ 완료 (소요 시간, 파일 경로)` / `⏳ 렌더링 중 (진행 중인 씬)` / `🕒 대기 중`
   - 현재 렌더링 중인 단어의 영문 씬(Scene) 묘사
4. **작업 완료 시 최종 완료 상황판 출력**:
   - 모든 단어가 생성 완료되면 최종 집계 상황판과 함께 `wordImages.ts` 등록, 타입체크, 커밋/푸시를 순차 완료합니다.

---

## 🌐 다른 컴퓨터에서 전역(Global) 스킬로 등록하는 법

저장소 프로젝트 외의 다른 폴더나 시스템 전역에서도 이 스킬을 호출하고 싶다면, 아래 한 줄을 실행하여 전역 스킬 디렉토리에 링크/복사할 수 있습니다:

```bash
mkdir -p ~/.gemini/config/skills/
cp -r .agents/skills/draw-things-linear-graphic ~/.gemini/config/skills/
```

