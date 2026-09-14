const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const WORDS_DIR = path.join(ROOT, 'assets/words');
const SYNC_SCRIPT = path.join(ROOT, 'scripts/sync_word_images.py');
const README_PATH = path.join(ROOT, 'README.md');

const high2 = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/en/levels/high-2.json'), 'utf8'));
const wordsData = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/en/words.json'), 'utf8'));

const SCENE_PROMPTS = {
  counterpart: "two business branch managers standing in bright modern office shaking hands warmly like matching counterparts, meeting table with laptop, architectural blueprints and office window in background",
  exaggerate: "storyteller standing by camp fire gesturing with widely spread arms dramatically exaggerating giant fish size, two friends seated on log stools listening with wide surprised eyes, tents and pine trees",
  diagnose: "experienced doctor with stethoscope examining medical test report and x-ray on illuminated light box to accurately diagnose patient condition, clinic room, medical equipment, desk",
  authenticity: "art curator in gallery holding magnifying glass carefully examining signature on antique oil painting on wooden easel to verify its authenticity, velvet rope, gallery wall frames",
  passive: "student sitting passively with folded hands at classroom desk observing blackboard while active classmates raise hands enthusiastically, classroom interior, books, window",
  obsess: "student late at night at study desk obsessively checking stack of test score papers under bright desk lamp, clock on wall showing midnight, organized notebooks and sticky notes",
  excessive: "busy city street intersection with excessive noisy car honking and dense traffic, bystander covering ears gently walking on sidewalk, tall buildings, street lamps",
  hybrid: "botanist in sunny greenhouse tending to blooming hybrid potted plant with two distinct flower colors, greenhouse glass ceiling, watering can, wooden work table, plant pots",
  appropriate: "student dressed in appropriate neat graduation gown standing proudly on school auditorium stage receiving diploma certificate, podium, microphone, floral stage decor",
  rational: "analytical student standing in front of whiteboard drawing logical pros and cons decision tree chart to make rational choice, bookshelf, organized office desk"
};

function getConceptPrompt(word) {
  if (SCENE_PROMPTS[word]) return SCENE_PROMPTS[word];
  const item = wordsData[word] || {};
  const example = item.example || `scene illustrating concept of ${word}`;
  const cleanExample = example.replace(/[^\x00-\x7F]/g, ' ').replace(/\s+/g, ' ').trim();
  return `rich narrative scene illustrating ${word}, ${cleanExample}, indoor or outdoor environment with rich ambient details, furniture, floor line`;
}

async function renderWord(word, index, total) {
  const cleanConcept = getConceptPrompt(word);
  const prompt = [
    `linear graphic illustration, complete richly detailed scene of ${cleanConcept}`,
    "thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, extremely fine crisp outlines drawn in dark charcoal ink color #030203",
    "flat smooth light gray canvas background color #f5f6f8",
    "simple white pictogram characters, two small dot eyes and a small smile line, plain white face",
    "the round bald head is drawn as its own complete closed circle outline, and directly below it the narrow torso starts with its own separate small rounded top edge",
    "head and body are two clearly separate shapes that touch only at one small narrow point under the chin, no thick neck",
    "very narrow slim torso only about half as wide as the head, tall soft rounded rectangle body with a flat bottom edge, the whole figure is narrow and about three times taller than it is wide",
    "short slim rounded tube arms drawn with two close parallel outlines ending in small round mitten nubs, held close to the body",
    "short slim rounded tube legs drawn with two close parallel outlines ending in small rounded feet, limbs are narrow but still have visible width and are never a single line",
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
    steps: 8,
    width: 1024,
    height: 1024,
    seed: 42 + index
  };

  console.log(`\n======================================================`);
  console.log(`[${index + 1}/${total}] '${word}' 렌더링 요청 시작...`);
  console.log(`콘셉트: ${cleanConcept}`);
  const t0 = Date.now();

  const res = await fetch("http://127.0.0.1:7860/sdapi/v1/txt2img", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`API HTTP Error: ${res.status} ${res.statusText}`);
  }

  const data = await res.json();
  if (!data.images || data.images.length === 0) {
    throw new Error(`Draw Things 이미지 수신 실패`);
  }

  const fileName = `${word.toLowerCase().replace(/\s+/g, '-')}.png`;
  const targetFile = path.join(WORDS_DIR, fileName);
  const buf = Buffer.from(data.images[0], 'base64');
  fs.writeFileSync(targetFile, buf);

  const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
  console.log(`[완료] '${word}' 저장됨: ${targetFile} (${buf.length} bytes, 소요시간: ${elapsed}초)`);

  // 1. 단어 이미지 레지스트리 동기화
  execSync(`python3 "${SYNC_SCRIPT}"`, { stdio: 'inherit', cwd: ROOT });

  // 2. AppleDouble 메타데이터 삭제
  execSync(`find . -name '._*' -type f -delete`, { cwd: ROOT });

  // 3. README.md 작업 내역 갱신
  updateReadme(word);

  // 4. Git 커밋 및 Push
  console.log(`Git 커밋 및 원격 푸시 동기화 진행 중...`);
  execSync(`git add -A`, { cwd: ROOT });
  execSync(`git commit -m "feat: 고등학교 2학년 단어 ${word} 선형그래픽 이미지 추가 및 등록"`, { cwd: ROOT });
  execSync(`git pull --rebase origin main`, { cwd: ROOT });
  execSync(`git push origin main`, { cwd: ROOT });
  console.log(`[동기화 완료] '${word}' 커밋 및 원격 푸시 성공!`);
}

function updateReadme(word) {
  let content = fs.readFileSync(README_PATH, 'utf8');
  const today = '### 2026-09-14';
  const entryLine = `- 고2 미생성 단어 1장 Draw Things 선형그래픽으로 생성 및 등록 (머리·몸통 분리 개정 스킬 적용)\n  - 대상 단어: ${word}`;
  
  if (content.includes(today)) {
    content = content.replace(today, `${today}\n${entryLine}`);
  } else {
    content = content.replace('## 작업 내역', `## 작업 내역\n\n${today}\n${entryLine}`);
  }
  fs.writeFileSync(README_PATH, content, 'utf8');
}

async function main() {
  const maxCount = parseInt(process.argv[2] || "5", 10);
  const assetFiles = new Set(fs.readdirSync(WORDS_DIR).map(f => f.replace(/\.png$/i, '').toLowerCase()));

  const missingWords = [];
  for (const item of high2) {
    const w = typeof item === 'string' ? item : (item.word || item.id || item.en);
    const normalized = w.toLowerCase().trim();
    const fileKey = normalized.replace(/\s+/g, '-');
    if (!assetFiles.has(normalized) && !assetFiles.has(fileKey)) {
      missingWords.push(w);
    }
  }

  console.log(`총 고2 미생성 단어: ${missingWords.length}개. 이번 배치 실행 예정: ${maxCount}개`);
  const targets = missingWords.slice(0, maxCount);

  for (let i = 0; i < targets.length; i++) {
    try {
      await renderWord(targets[i], i, targets.length);
    } catch (err) {
      console.error(`[오류] 단어 '${targets[i]}' 처리 중 에러:`, err);
    }
  }
  console.log(`\n배치 작업이 모두 완료되었습니다.`);
}

main().catch(console.error);
