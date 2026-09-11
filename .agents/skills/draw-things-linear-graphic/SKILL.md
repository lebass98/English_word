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

## 🎨 선형그래픽 5대 핵심 원칙

1. **초극세 바늘선 (0.05mm Hairline)**:
   - 512px 업스케일 방식을 쓰지 않고, **1024×1024 네이티브 해상도**로 직접 생성하여 선 굵기를 초기부터 가장 얇게 렌더링합니다.
   - 프롬프트 키워드: `thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke`, `extremely fine crisp outlines`.
2. **배경 색상코드 `#f5f6f8`**:
   - 뉴모피즘 캔버스 테마와 완벽히 일치하는 소프트 라이트그레이 톤 (`flat smooth light gray canvas background color #f5f6f8`).
3. **선 색상코드 `#030203`**:
   - 순수 칠흑색에 가까운 딥 차콜 블랙 잉크 (`dark charcoal ink color #030203`).
4. **풍성한 씬 (Rich Scene Content)**:
   - 인물 1명만 덩그러니 있는 것이 아니라, 배경 가구, 벽면 장식(시계, 책장, 조명), 바닥선, 소품, 2~4명의 귀여운 원형 머리 스틱맨 동료들의 상호작용을 풍성하게 묘사합니다.
5. **추후 수정 및 효과 일체 배제 (Zero Post-Processing)**:
   - 생성 후 임계값(Threshold), 색상 왜곡, 필터 효과를 인위적으로 주지 않고, 모델 본연의 부드러운 안티에일리어싱을 보존한 **순수 렌더링 원본 파일**을 그대로 저장합니다.

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

## 🌐 다른 컴퓨터에서 전역(Global) 스킬로 등록하는 법

저장소 프로젝트 외의 다른 폴더나 시스템 전역에서도 이 스킬을 호출하고 싶다면, 아래 한 줄을 실행하여 전역 스킬 디렉토리에 링크/복사할 수 있습니다:

```bash
mkdir -p ~/.gemini/config/skills/
cp -r .agents/skills/draw-things-linear-graphic ~/.gemini/config/skills/
```
