---
name: draw-things-linear-graphic
description: >-
  Draw Things 로컬 API(http://127.0.0.1:7860)를 활용하여 '선형그래픽' 스타일의 고품질 일러스트 및 단어 이미지를 생성하는 스킬.
  사용자가 '선형그래픽', 극세선 라인아트, 드로우씽즈(Draw Things) 기반 단어/아이콘 이미지 생성을 요청할 때 활성화된다.
  초기 0.05mm 초극세선, 캔버스 배경색 #f5f6f8, 선색 #030203, 풍성한 씬 구성, 후처리 효과 없는 512x512 순수 렌더링 출력을 보장한다.
---

# Draw Things 선형그래픽 생성 스킬 (draw-things-linear-graphic)

이 스킬은 **Draw Things** 앱의 로컬 API를 통해 일관된 톤앤매너의 **'선형그래픽'** 일러스트를 생성하는 워크플로우를 정의합니다.

어떤 컴퓨터에서든 이 저장소를 클론(`git pull`)하면 자동으로 인식되며, 외부 파이썬 패키지 설치(Pillow 등) 없이 기본 `python3`만으로 즉시 작동합니다.

---

## 🎨 선형그래픽 및 날씬한 픽토그램 캐릭터 조형 원칙

> **2026-09-13 개정**: 사용자 레퍼런스(칠판 앞 캐릭터 3명)에 맞춰 사람 모양을 바꿨다.
> 가는 막대 인간(선 한 줄 팔다리)도, 머리가 큰 통통한 SD 캐릭터도 아닌 **좁고 긴 몸통 + 선 두 줄 튜브 팔다리**가 표준이다.
> **같은 날 추가 개정**: 머리와 몸통을 한 덩어리로 이어 그리면 이음새가 두꺼운 목처럼 보여서, **머리는 따로 닫힌 동그라미, 몸통은 그 아래 자기 윗선에서 시작**하도록 바꿨다 (원칙 2).
> 확정 샘플: `assets/words/hydrogen.png` (중1 m1-525) — 머리·몸 구분까지 반영된 표준 모습.

1. **전체 비율 및 실루엣 (좁고 긴 몸 & 화면 높이 약 1/3 & 배경 중심 와이드 구도)**:
   - 몸통 폭은 **머리 폭의 절반 정도**이고, 전체 모습은 **폭보다 세 배쯤 키가 큰** 날씬한 형태입니다. 옆으로 넓거나 통통한 몸은 쓰지 않습니다.
   - 인물 키는 캔버스 높이의 **약 1/3**을 목표로 하고 바닥선에 서 있습니다. 화면 위·중단은 칠판, 선반, 창문, 가구, 도구 같은 배경으로 채우며, 클로즈업이나 화면을 꽉 채우는 구도는 배제합니다.
   - **`cute`, `chibi`, `plump` 같은 낱말은 넣지 않습니다.** 이 모델(z_image_turbo, 8단계)은 부정 프롬프트를 거의 따르지 않아서, 이런 낱말이 들어가면 머리가 커지고 몸이 넓어지며 볼 홍조가 생깁니다. 모양은 긍정 문장으로만 정합니다.
   - 프롬프트 키워드: `small character in a wide scene, modest compact character scale, standing small figure occupying approximately one third of frame height around 30 to 35 percent of canvas height, placed comfortably on bottom floor line, spacious upper and middle frame filled with rich environmental details, balanced wide scene composition, plenty of breathing room, full body visible without crowding`.
2. **두상 및 이목구비 (구형 민머리 & 점/선 얼굴)**:
   - 귀, 머리카락이 없는 매끄러운 원형 민머리를 **따로 닫힌 동그라미 윤곽**으로 그립니다.
   - **머리와 몸통은 한 덩어리로 잇지 않습니다.** 몸통은 머리 바로 아래에서 자기만의 작고 둥근 윗선으로 시작하고, 둘은 턱 밑 좁은 한 점에서만 만납니다. 머리 윤곽이 어깨로 흘러내리듯 이어지면 이음새가 두꺼운 목처럼 보이므로 금지합니다. 길게 드러나는 목도 그리지 않습니다.
   - 두 개의 검은 점 눈과 얇은 미소선 입만 그립니다. 코, 눈썹, 입술, 치아, **볼 홍조**는 그리지 않습니다.
   - 프롬프트 키워드: `simple white pictogram characters, two small dot eyes and a small smile line, plain white face, the round bald head is drawn as its own complete closed circle outline, and directly below it the narrow torso starts with its own separate small rounded top edge, head and body are two clearly separate shapes that touch only at one small narrow point under the chin, no thick neck`.
   - 부정 프롬프트에 `thick neck, wide neck, head merged into body, head and torso as one continuous blob, head outline flowing into shoulders`를 넣습니다. 머리와 몸 사이 구분선은 보여야 하므로 `neck line`은 부정 프롬프트에 넣지 않습니다.
3. **몸통 및 팔다리 (좁고 긴 둥근 직사각형 몸통 & 선 두 줄 튜브 팔다리)**:
   - **몸통**: 머리 폭의 절반 정도로 좁고, 세로로 긴 부드러운 둥근 직사각형이며 밑단이 평평합니다 (단순한 원피스 실루엣).
   - **팔다리**: 짧고 가는 튜브 모양이지만 **선 두 줄로 두께가 보이게** 그립니다. 선 한 줄짜리 막대 팔다리는 금지합니다. 관절은 그리지 않습니다. 팔다리의 **모양**은 그대로 두되, 원칙 8에 따라 **동작에 맞춰 자유롭게 움직입니다** (예전의 "팔은 몸에 붙인다"는 폐지).
   - **손발**: 손은 둥글고 뭉툭한 벙어리장갑 끝, 발은 작고 둥근 발끝입니다.
   - 프롬프트 키워드: `very narrow slim torso only about half as wide as the head, tall soft rounded rectangle body with a flat bottom edge, the whole figure is narrow and about three times taller than it is wide, short slim rounded tube arms drawn with two close parallel outlines ending in small round mitten nubs, held close to the body, short slim rounded tube legs drawn with two close parallel outlines ending in small rounded feet, limbs are narrow but still have visible width and are never a single line`.
   - **장면 묘사 정리**: 단어별 장면에 `cute slender stickman` 같은 표현이 있으면 생성 전에 `small slim white pictogram character`로 바꾸고, 남은 `slender`·`skinny`는 지웁니다. 장면 문장 속 낱말이 캐릭터 설명보다 강하게 작용합니다.
4. **표면 재질 및 라인 스타일 (평면 순백색 픽토그램 & 균일한 검은색 외곽선)**:
   - **평면 순백색 마감**: 옷, 봉제선, 단추, 주름, 피부 질감이 일절 없는 새하얀 픽토그램/마네킹 형태입니다 (`blank solid white mannequin pictogram body fill`). 성별, 연령, 인종이 드러나지 않는 보편적 형태입니다.
   - **균일한 검은색 외곽선**: 명암(그림자), 색상 그러데이션 없이 균일하고 맑은 딥 차콜 블랙 윤곽선(`#030203`)과 단색 순백색 채움만으로 2D 플랫(2D Flat)하게 완결됩니다.
   - **캔버스 배경 색상코드 `#f5f6f8`**: 뉴모피즘 테마와 일치하는 소프트 라이트그레이 캔버스.
5. **풍성한 배경 씬 (Rich Scene Content)**:
   - 캐릭터 주변에 바닥선, 가구, 벽면 장식, 창문, 소품 등 내러티브 묘사를 균일하고 깔끔한 선화로 풍성하게 배치하여 단어의 상황을 직관적으로 전달합니다.
6. **추후 수정 및 효과 일체 배제 (Zero Post-Processing)**:
   - 생성 후 인위적인 필터, 색상 왜곡, 임계값 조작 없이 모델 본연의 부드러운 안티에일리어싱 512x512 원본 파일을 그대로 저장합니다.
7. **영문 외 일체 배제 및 100% 영문 전용 절대 원칙 (Strictly English Only / Zero Non-English Characters)**:
   - **프롬프트 및 씬 설명 내 영문 외 문자 절대 금지**: 단어 뜻, 한국어 메모(예: `(가슴)`, `(가루)`), 한자 등 영문(A-Z, a-z) 및 기본 숫자/기호 이외의 모든 비영문 문자는 프롬프트에 절대 넣지 않으며, 오직 100% 순수 영문 씬 묘사(English prompt only)만 전달합니다.
   - **이미지 씬 내부 텍스트 100% 영문 전용**: 씬 내부의 간판, 포스터, 서류 등에 글자가 노출될 경우 오직 영문 알파벳(A-Z)만 허용하며, 한글/한자/일본어 및 왜곡된 기호 생성을 원천 차단합니다.
   - **부정(Negative) 프롬프트 필수 적용 (영문 전용)**: 아래 원칙 8 뒤 목록 참고.
8. **익사이팅한 활동 장면 (Exciting Action Moment)** — 2026-09-14 사용자 요청으로 추가:
   - 인물이 가만히 서 있거나 물건을 들고 있기만 한 그림 대신, **한창 신나게 움직이는 순간**을 그립니다 (달리기, 점프, 뛰어오르기, 손 뻗기, 던지기, 오르기 등).
   - 몸 **모양**(좁은 몸통, 선 두 줄 튜브 팔다리, 머리·몸통 분리)과 **크기**(화면 높이 약 1/3)는 그대로 두고, 팔다리만 동작에 맞춰 자유롭게 움직입니다. 속도감을 주는 작은 동작선(motion lines)을 곁들입니다.
   - **장면 묘사도 동작 동사로** 씁니다. `a person holding a map` 보다 `a person racing up a hill waving a map toward the peak` 처럼 단어 뜻이 신나는 행동 속에서 드러나게 합니다. 슬프거나 조용한 뜻의 단어도 인물이 뭔가를 적극적으로 하는 장면으로 풉니다.
   - 프롬프트 키워드: `the characters are caught in the middle of an exciting energetic activity, dynamic action pose full of movement such as running, jumping, leaping, reaching, throwing or climbing, arms and legs move freely with the action while keeping the same slim tube shape, playful adventurous mood, small motion lines and action marks showing speed and excitement, lively storytelling moment`.

   영문 전용·구도 부정 프롬프트 목록: `non-English text, Korean text, Hangul, Chinese characters, Hanzi, Kanji, Japanese, foreign characters, dominant character crowding the frame, overwhelming screen, frame-filling figure, suffocating composition, unnatural forced character size, giant figure dominating scenery, oversized character, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, large scale character dominating scene, realistic human anatomy, realistic face, facial details, nose, eyebrows, lips, teeth, ears, hair, neck, muscles, realistic fingers, fingernails, toes, clothes, shirt, pants, wrinkles, shading, gradients, shadow, 3d render`.


---

> **2026-09-16 변경**: 그림 크기를 1024x1024 가 아니라 **512x512** 로 낮췄다 (사용자 요청). 한 장 그리는 시간이 크게 줄어든다.
> 스킬 스크립트의 기본값이 512 이므로, 다른 컴퓨터도 `git pull` 만 하면 같은 크기로 그린다.
> 더 큰 그림이 필요하면 `--width/--height` 로 지정하거나 `IMAGE_SIZE=1024 python3 scripts/generate_images.py ...` 로 돌린다.

## 💻 사전 준비사항 (어떤 컴퓨터에서든 공통)

1. **Draw Things 앱 실행**:
   - Mac 또는 지원 기기에서 `Draw Things` 앱을 실행합니다.
2. **API 서버 켜기**:
   - 설정(Settings)에서 **API Server (Port 7860)**를 활성화합니다.
   - 기본 주소: `http://127.0.0.1:7860` (원격 PC의 경우 해당 IP 지정 가능)
3. **권장 모델**:
   - `z_image_turbo_1.0_q8p.ckpt` (또는 동급 고속 모델, Steps: 8)

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
| `--width` | `-w` | `512` | 가로 해상도 |
| `--height` | `-H` | `512` | 세로 해상도 |
| `--steps` | - | `8` | 추론 스텝 수 |

---

## 📊 진행 보고 규칙

**대시보드·상황판 파일은 만들지 않는다.** `LIVE_DASHBOARD.md`, `dashboard.html` 같은 파일을 만들던 규칙은 폐지했다.

- 진행 보고는 **채팅창에 간결한 1줄**로만 한다. 긴 표를 반복해서 출력하지 않는다.
- 작업이 끝나면 결과를 짧게 요약하고 `wordImages.ts` 등록 → 타입체크 → 커밋/푸시를 이어서 한다.

---

## 🌐 다른 컴퓨터에서 전역(Global) 스킬로 등록하는 법

저장소 프로젝트 외의 다른 폴더나 시스템 전역에서도 이 스킬을 호출하고 싶다면, 아래 한 줄을 실행하여 전역 스킬 디렉토리에 링크/복사할 수 있습니다:

```bash
mkdir -p ~/.gemini/config/skills/
cp -r .agents/skills/draw-things-linear-graphic ~/.gemini/config/skills/
```

