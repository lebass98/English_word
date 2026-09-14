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
    "thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, extremely fine crisp outlines drawn in dark charcoal ink color #030203",
    "flat smooth light gray canvas background color #f5f6f8",
    // 사람 모양: 가는 막대 인간이 아니라 도톰한 튜브 팔다리의 순백 픽토그램 (사용자 레퍼런스)
    // 머리와 몸통은 한 덩어리로 잇지 않는다. 이어 그리면 이음새가 두꺼운 목처럼 보인다
    "simple white pictogram characters, two small dot eyes and a small smile line, plain white face",
    "the round bald head is drawn as its own complete closed circle outline, and directly below it the narrow torso starts with its own separate small rounded top edge",
    "head and body are two clearly separate shapes that touch only at one small narrow point under the chin, no thick neck",
    "very narrow slim torso only about half as wide as the head, tall soft rounded rectangle body with a flat bottom edge, the whole figure is narrow and about three times taller than it is wide",
    "short slim rounded tube arms drawn with two close parallel outlines ending in small round mitten nubs",
    "short slim rounded tube legs drawn with two close parallel outlines ending in small rounded feet, limbs are narrow but still have visible width and are never a single line",
    // 익사이팅한 활동: 가만히 서 있는 그림 대신 한창 신나게 움직이는 순간을 그린다 (2026-09-14 사용자 요청)
    // 몸 모양은 그대로 두고 팔다리만 동작에 맞춰 자유롭게 움직인다
    "the characters are caught in the middle of an exciting energetic activity, dynamic action pose full of movement such as running, jumping, leaping, reaching, throwing or climbing",
    "arms and legs move freely with the action while keeping the same slim tube shape, playful adventurous mood, small motion lines and action marks showing speed and excitement, lively storytelling moment",
    "small character in a wide scene, modest compact character scale, standing small figure occupying approximately one third of frame height around 30 to 35 percent of canvas height, placed comfortably on bottom floor line, spacious upper and middle frame filled with rich environmental details, balanced wide scene composition, plenty of breathing room, full body visible without crowding",
    "abundant rich background details, furniture, wall decor, floor line, ambient props",
    "strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, empty background",
    "strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
  ].join(", ");

  const negativePrompt = [
    "stick figure, stickman, matchstick limbs, single-line arms, single-line legs, thin wire limbs, long thin legs",
    "fat body, chubby, plump, round belly, wide bulky torso, blush, rosy cheeks, pink cheeks, cheek marks",
    "thick neck, wide neck, head merged into body, head and torso as one continuous blob, head outline flowing into shoulders",
    "long neck, throat, collar, detailed neck anatomy",
    "oversized character, giant figure, tall figure, frame-filling character, character taking up entire screen, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, suffocating composition, character head near top of frame, dominating figure",
    "realistic human anatomy, realistic face, facial details, nose, eyebrows, eyelashes, eyelids, lips, teeth, ears, hair, hairstyle, muscles, realistic fingers, individual finger joints, fingernails, toes, shoes, clothing, clothes, shirt, pants, wrinkles, folds",
    "thick lines, bold outlines, heavy brush strokes, chunky lines, fat strokes",
    "pure white #ffffff background, dark background, black background, 3d, 3d render, realistic, shadow, shading, color, gradients, photo, blur, watermark, text, signature, messy",
    "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing"
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
