#!/usr/bin/env python3
"""
Draw Things 로컬 API 기반 '선형그래픽' 이미지 자동 생성 엔진 (의존성 제로 순수 표준 라이브러리)
- 어떤 컴퓨터에서든 추가 패키지(Pillow 등) 설치 없이 기본 python3만으로 즉시 구동됩니다.
- 규칙:
  1. 초기 선 굵기: 0.05mm 초극세 바늘선 (thinnest possible needle-thin hairline ink stroke)
  2. 배경 색상코드: #f5f6f8 (소프트 라이트그레이 캔버스)
  3. 선 색상코드: #030203 (딥 차콜 블랙 잉크)
  4. 내용: 풍성한 씬 (배경 가구, 장식, 소품, 상호작용하는 귀여운 스틱맨들)
  5. 후처리: 인위적인 필터/임계값 수정 없이 1024x1024 순수 렌더링 원본 보존
"""

import sys
import os
import json
import time
import base64
import urllib.request
import argparse

DEFAULT_API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

def generate_linear_image(
    concept: str,
    output_path: str,
    api_url: str = DEFAULT_API_URL,
    seed: int = 42,
    width: int = 1024,
    height: int = 1024,
    steps: int = 8
):
    # 영문 외 문자 엄격 차단 및 정제 (비영문/비ASCII 문자 전면 제거)
    import re
    clean_concept = re.sub(r'[^\x00-\x7F]+', ' ', concept or '')
    clean_concept = re.sub(r'\s+', ' ', clean_concept).strip()

    if not clean_concept:
        raise ValueError("영문 외 문자만 입력되었거나 유효한 영문 씬 설명(concept)이 없습니다. 오직 순수 영문(English only)만 허용됩니다.")

    prompt = (
        f"linear graphic illustration, complete richly detailed scene of {clean_concept}, "
        "thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, extremely fine crisp outlines drawn in dark charcoal ink color #030203, "
        "flat smooth light gray canvas background color #f5f6f8, "
        # 사람 모양: 가는 막대 인간이 아니라 도톰한 튜브 팔다리의 순백 픽토그램 (사용자 레퍼런스)
        "simple white pictogram characters, round bald head resting directly on top of the body with completely no neck, two small dot eyes and a small smile line, plain white face, "
        "very narrow slim torso only about half as wide as the head, tall soft rounded rectangle body with a flat bottom edge, the whole figure is narrow and about three times taller than it is wide, "
        "short slim rounded tube arms drawn with two close parallel outlines ending in small round mitten nubs, held close to the body, "
        "short slim rounded tube legs drawn with two close parallel outlines ending in small rounded feet, limbs are narrow but still have visible width and are never a single line, "
        "small character in a wide scene, modest compact character scale, standing small figure occupying approximately one third of frame height around 30 to 35 percent of canvas height, placed comfortably on bottom floor line, spacious upper and middle frame filled with rich environmental details, balanced wide scene composition, plenty of breathing room, full body visible without crowding, "
        "abundant rich background details, furniture, wall decor, floor line, ambient props, "
        "strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, empty background, "
        "strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
    )

    negative_prompt = (
        "stick figure, stickman, matchstick limbs, single-line arms, single-line legs, thin wire limbs, long thin legs, "
        "fat body, chubby, plump, round belly, wide bulky torso, blush, rosy cheeks, pink cheeks, cheek marks, "
        "neck, long neck, throat, collar, neck line, detailed neck anatomy, "
        "oversized character, giant figure, tall figure, frame-filling character, character taking up entire screen, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, suffocating composition, character head near top of frame, dominating figure, "
        "realistic human anatomy, realistic face, facial details, nose, eyebrows, eyelashes, eyelids, lips, teeth, ears, hair, hairstyle, muscles, realistic fingers, individual finger joints, fingernails, toes, shoes, clothing, clothes, shirt, pants, wrinkles, folds, "
        "thick lines, bold outlines, heavy brush strokes, chunky lines, fat strokes, "
        "pure white #ffffff background, dark background, black background, 3d, 3d render, realistic, shadow, shading, color, gradients, photo, blur, watermark, text, signature, messy, "
        "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing"
    )


    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "width": width,
        "height": height,
        "seed": seed
    }

    print(f"[선형그래픽] Draw Things 요청 중 (API: {api_url}, seed={seed}, size={width}x{height})...", flush=True)
    t0 = time.time()
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        images = data.get("images", [])
        if not images:
            raise RuntimeError("Draw Things로부터 이미지를 수신하지 못했습니다.")
        raw_bytes = base64.b64decode(images[0])

    # 순수 원본 렌더링 파일 저장 (외부 라이브러리 없이 직접 바이너리 쓰기)
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    with open(output_path, "wb") as f:
        f.write(raw_bytes)

    elapsed = time.time() - t0
    print(f"[선형그래픽] 생성 및 저장 완료 ({elapsed:.1f}초) -> {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Draw Things 선형그래픽 표준 생성 도구")
    parser.add_argument("concept", type=str, help="생성할 장면 또는 단어 콘셉트 영문 설명")
    parser.add_argument("--output", "-o", type=str, required=True, help="저장할 파일 경로 (.png)")
    parser.add_argument("--url", "-u", type=str, default=DEFAULT_API_URL, help="Draw Things API URL (기본: http://127.0.0.1:7860/sdapi/v1/txt2img)")
    parser.add_argument("--seed", "-s", type=int, default=42, help="랜덤 시드 번호 (기본: 42)")
    parser.add_argument("--width", "-w", type=int, default=1024, help="가로 해상도 (기본: 1024)")
    parser.add_argument("--height", "-H", type=int, default=1024, help="세로 해상도 (기본: 1024)")
    parser.add_argument("--steps", type=int, default=8, help="생성 스텝 수 (기본: 8)")
    args = parser.parse_args()

    generate_linear_image(
        concept=args.concept,
        output_path=args.output,
        api_url=args.url,
        seed=args.seed,
        width=args.width,
        height=args.height,
        steps=args.steps
    )

if __name__ == "__main__":
    main()
