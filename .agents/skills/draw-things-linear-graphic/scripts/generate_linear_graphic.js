#!/usr/bin/env node
/**
 * Draw Things 로컬 API 기반 '선형그래픽' 이미지 자동 생성 엔진 (Node.js 버전)
 * - 추가 패키지 설치 없이 Node.js 표준 라이브러리(fetch, fs)만으로 즉시 구동됩니다.
 * - 규칙:
 *   1. 초기 선 굵기: 0.05mm 초극세 바늘선
 *   2. 배경 색상코드: #f5f6f8 (소프트 라이트그레이 캔버스)
 *   3. 선 색상코드: #030203 (딥 차콜 블랙 잉크)
 *   4. 내용: 풍성한 씬 (배경 가구, 장식, 소품, 상호작용하는 귀여운 스틱맨들)
 *   5. 후처리: 인위적인 필터/임계값 수정 없이 1024x1024 순수 렌더링 원본 보존
 */

const fs = require('fs');
const path = require('path');

const DEFAULT_API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img";

async function generateLinearImage({
  concept,
  outputPath,
  apiUrl = DEFAULT_API_URL,
  seed = 42,
  width = 1024,
  height = 1024,
  steps = 8
}) {
  // 영문 외 문자 엄격 차단 및 정제 (한글, 한자, 일본어 등 비영문 문자 원천 제거)
  const cleanConcept = (concept || '')
    .replace(/[^\x00-\x7F]/g, ' ') // 비ASCII/비영문 문자 전면 제거
    .replace(/\s+/g, ' ')
    .trim();

  if (!cleanConcept) {
    throw new Error("영문 외 문자만 입력되었거나 유효한 영문 씬 설명(concept)이 없습니다. 오직 순수 영문(English only)만 허용됩니다.");
  }

  const prompt = [
    `linear graphic illustration, complete richly detailed scene of ${cleanConcept}`,
    "3 to 3.5 head-to-body chibi SD ratio cute characters with large prominent smooth spherical bald round heads",
    "minimalist dot and line face, two simple solid black dot eyes and a tiny thin curved smile line, strictly no nose, no eyebrows, no lips, no ears, no hair",
    "seamless tubular neckless body directly attached to round head with completely no neck, smooth organic curves without clavicle or muscle contours",
    "jointless smooth rubber-hose arms and legs with no elbows and no knees, simplified mitten-like blunt round hands, smooth rounded flat oval foot pads firmly on floor line",
    "blank solid white mannequin pictogram character fill with zero clothing, no seams, no buttons, no folds, no skin texture, genderless universal figure",
    "crisp uniform dark charcoal ink outlines #030203, strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, flat smooth light gray canvas background color #f5f6f8",
    "abundant rich background details, furniture, wall decor, floor line, ambient props",
    "strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
  ].join(", ");

  const negativePrompt = [
    "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing",
    "realistic human anatomy, realistic face, facial details, nose, eyebrows, eyelashes, eyelids, lips, teeth, ears, hair, hairstyle, neck, long neck, throat, collar, collarbone, muscles, realistic fingers, individual finger joints, fingernails, toes, shoes, clothing, clothes, shirt, pants, wrinkles, folds",
    "thick lines, heavy brush strokes, chunky lines, fat strokes",
    "pure white #ffffff background, dark background, black background, 3d, 3d render, realistic, shadow, shading, color, gradients, photo, blur, watermark, signature, messy"
  ].join(", ");

  const payload = {
    prompt,
    negative_prompt: negativePrompt,
    steps,
    width,
    height,
    seed
  };

  console.log(`[선형그래픽] Draw Things 요청 중 (API: ${apiUrl}, seed=${seed}, size=${width}x${height})...`);
  const t0 = Date.now();

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`API 요청 실패: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  const images = data.images;
  if (!images || images.length === 0) {
    throw new Error("Draw Things로부터 이미지를 수신하지 못했습니다.");
  }

  const buffer = Buffer.from(images[0], 'base64');
  const targetDir = path.dirname(path.resolve(outputPath));
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, buffer);
  const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
  console.log(`[선형그래픽] 생성 및 저장 완료 (${elapsed}초) -> ${outputPath}`);
  return outputPath;
}

function parseArgs() {
  const args = process.argv.slice(2);
  let concept = '';
  let outputPath = '';
  let apiUrl = DEFAULT_API_URL;
  let seed = 42;
  let width = 1024;
  let height = 1024;
  let steps = 8;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--output' || arg === '-o') {
      outputPath = args[++i];
    } else if (arg === '--url' || arg === '-u') {
      apiUrl = args[++i];
    } else if (arg === '--seed' || arg === '-s') {
      seed = parseInt(args[++i], 10);
    } else if (arg === '--width' || arg === '-w') {
      width = parseInt(args[++i], 10);
    } else if (arg === '--height' || arg === '-H') {
      height = parseInt(args[++i], 10);
    } else if (arg === '--steps') {
      steps = parseInt(args[++i], 10);
    } else if (!concept && !arg.startsWith('-')) {
      concept = arg;
    }
  }

  if (!concept || !outputPath) {
    console.error("사용법: node generate_linear_graphic.js <concept> --output <filepath> [--seed <seed>]");
    process.exit(1);
  }

  return { concept, outputPath, apiUrl, seed, width, height, steps };
}

if (require.main === module) {
  const options = parseArgs();
  generateLinearImage(options).catch(err => {
    console.error(`[오류 발생] ${err.message}`);
    process.exit(1);
  });
}

module.exports = { generateLinearImage };
