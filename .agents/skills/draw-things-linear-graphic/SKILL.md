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

## 🎨 선형그래픽 및 3~3.5등신 픽토그램 캐릭터 조형 원칙

1. **전체적인 비율 및 실루엣 (3~3.5등신 SD 비율 & 화면 대비 아담한 캐릭터 크기 축소 & 여백 중심 구도)**:
   - 몸체에 비해 머리가 확연히 큰 **3~3.5등신 SD(Super Deformed) 비율**을 적용해 친근하고 직관적인 인상을 줍니다.
   - 각진 모서리나 해부학적인 골격 굴곡(쇄골, 어깨 각도, 척추 라인 등)을 철저히 배제하고 완만한 곡선 위주로 매끄럽게 이어집니다.
   - **화면 대비 캐릭터 크기 축소 (컴팩트 스케일링 & 여백 확보)**: 캐릭터가 화면을 과도하게 가득 채우거나 거대하게 묘사되지 않도록, 전체적으로 아담하고 작은 컴팩트 스케일(Modest compact scale, small chibi figure)을 엄격히 유지합니다. 인물은 화면의 약 1/3~1/4 수준으로 아담하게 위치하며, 주변에 충분한 시각적 여백(Breathing room, negative space)과 시원한 배경 공간감이 풍성하게 드러나도록 와이드 구도로 연출합니다.
   - 프롬프트 키워드: `3 to 3.5 head-to-body chibi SD ratio cute character, large prominent smooth spherical bald round head, gentle organic curving silhouette, modest compact character scale, small adorable chibi figure in spacious wide framing, plenty of surrounding negative space and breathing room around character, balanced scene composition, full body comfortably framed within scene`.
2. **두상 및 이목구비 (구형 민머리 & 점/선 압축 얼굴)**:
   - **매끄러운 구형 민머리**: 귀, 머리카락, 헤어라인, 턱선이 일절 생략된 매끄러운 원형/구형 두상입니다.
   - **점과 선으로 압축된 이목구비**: 흰자위나 동공 없이 단순한 **두 개의 검은 점(Dot) 눈**과 얇은 호선 형태의 **가벼운 미소선(Smile line) 입** 하나로만 표현합니다. 코, 눈썹, 입술 두께, 치아는 일절 묘사하지 않습니다.
   - 프롬프트 키워드: `smooth spherical bald round head with completely no ears and no hair, minimalist dot and line face, two simple solid black dot eyes and a tiny thin curved smile line, strictly no nose, no eyebrows, no lips, no teeth`.
3. **몸통 및 사지 (목 없는 일체 튜브형 & 관절 생략 & 벙어리장갑 손/패드 발)**:
   - **원통형 일체 몸체**: 목 주름, 가슴 근육, 허리 굴곡 없이 상체와 하체가 일체형 튜브처럼 부드럽게 연결되며 머리에 직접 부착됩니다 (완전한 목 없음 No-Neck).
   - **관절이 생략된 팔다리**: 팔꿈치, 손목, 무릎, 종아리 등의 관절과 근육 굴곡을 생략하고 고무관(Rubber-hose)처럼 매끄럽게 떨어집니다.
   - **간략화된 손과 발**:
     - 손: 손가락 마디, 손톱, 손금 구분 없이 둥글고 뭉툭한 실루엣 (벙어리장갑 Mitten 형태).
     - 발: 발가락, 뒤꿈치, 신발 구분이 없으며 다리 끝에서 둥글고 납작한 타원형 패드 형태로 지면을 지탱합니다.
   - 프롬프트 키워드: `seamless tubular neckless body directly attached to round head with completely no neck, jointless smooth rubber-hose arms and legs with no elbows and no knees, simplified mitten-like blunt round hands, smooth rounded flat oval foot pads firmly touching floor line`.
4. **표면 재질 및 라인 스타일 (평면 순백색 픽토그램 & 균일한 검은색 외곽선)**:
   - **평면 순백색 마감**: 옷, 봉제선, 단추, 주름, 피부 질감이 일절 없는 새하얀 픽토그램/마네킹 형태입니다 (`blank solid white mannequin pictogram body fill`). 성별, 연령, 인종이 드러나지 않는 보편적 형태입니다.
   - **균일한 검은색 외곽선**: 명암(그림자), 색상 그러데이션 없이 균일하고 맑은 딥 차콜 블랙 윤곽선(`#030203`)과 단색 순백색 채움만으로 2D 플랫(2D Flat)하게 완결됩니다.
   - **캔버스 배경 색상코드 `#f5f6f8`**: 뉴모피즘 테마와 일치하는 소프트 라이트그레이 캔버스.
5. **풍성한 배경 씬 (Rich Scene Content)**:
   - 캐릭터 주변에 바닥선, 가구, 벽면 장식, 창문, 소품 등 내러티브 묘사를 균일하고 깔끔한 선화로 풍성하게 배치하여 단어의 상황을 직관적으로 전달합니다.
6. **추후 수정 및 효과 일체 배제 (Zero Post-Processing)**:
   - 생성 후 인위적인 필터, 색상 왜곡, 임계값 조작 없이 모델 본연의 부드러운 안티에일리어싱 1024x1024 원본 파일을 그대로 저장합니다.
7. **영문 외 일체 배제 및 100% 영문 전용 절대 원칙 (Strictly English Only / Zero Non-English Characters)**:
   - **프롬프트 및 씬 설명 내 영문 외 문자 절대 금지**: 단어 뜻, 한국어 메모(예: `(가슴)`, `(가루)`), 한자 등 영문(A-Z, a-z) 및 기본 숫자/기호 이외의 모든 비영문 문자는 프롬프트에 절대 넣지 않으며, 오직 100% 순수 영문 씬 묘사(English prompt only)만 전달합니다.
   - **이미지 씬 내부 텍스트 100% 영문 전용**: 씬 내부의 간판, 포스터, 서류 등에 글자가 노출될 경우 오직 영문 알파벳(A-Z)만 허용하며, 한글/한자/일본어 및 왜곡된 기호 생성을 원천 차단합니다.
   - **부정(Negative) 프롬프트 필수 적용**: `non-English text, Korean text, Hangul, Chinese characters, Hanzi, Kanji, Japanese, foreign characters, oversized character, giant figure, frame-filling character, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, large scale character dominating scene, realistic human anatomy, realistic face, facial details, nose, eyebrows, lips, teeth, ears, hair, neck, muscles, realistic fingers, fingernails, toes, clothes, shirt, pants, wrinkles, shading, gradients, shadow, 3d render`.


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

