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
  const prompt = [
    `linear graphic illustration, complete richly detailed scene of ${concept}`,
    "thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke",
    "extremely fine crisp outlines drawn in dark charcoal ink color #030203",
    "flat smooth light gray canvas background color #f5f6f8",
    "neckless cute slender doodle stickman characters with round bald circle heads attached directly to torso with completely no neck, tiny smiling dot faces",
    "abundant rich background details, furniture, wall decor, floor line, ambient props",
    "strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, empty clean background"
  ].join(", ");

  const negativePrompt = [
    "neck, long neck, throat, collar, neck line, detailed neck anatomy",
    "thick lines, bold outlines, heavy brush strokes, chunky lines, fat strokes",
    "pure white #ffffff background, dark background, black background, 3d, realistic, shadow, shading",
    "color, gradients, photo, blur, watermark, text, signature"
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
