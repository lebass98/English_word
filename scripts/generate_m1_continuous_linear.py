#!/usr/bin/env python3
"""
Draw Things '선형그래픽' 스킬 기반 중학교 1학년 연속 자동 생성 스크립트
- Unit 7부터 사용자가 중지할 때까지 계속해서 20단어씩 순차 생성 및 Git 배포
- Unit 7 (m1-121 ~ m1-140)
- Unit 8 (m1-141 ~ m1-160)
- Unit 9 (m1-161 ~ m1-180)
- ...
"""

import os
import sys
import json
import time
import base64
import urllib.request
import subprocess
import argparse

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
WORD_IMAGES_TS = os.path.join(PROJECT_ROOT, "src", "constants", "wordImages.ts")

# 스킬 표준 공통 프롬프트
STYLE_PROMPT = (
    "masterpiece, best quality, ultra-detailed linear graphic illustration, "
    "clean pure line art vector aesthetic, "
    "thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, "
    "extremely fine crisp outlines, "
    "neckless cute doodle stickman, perfectly round circle head attached directly to torso with completely no neck, neckless stick figure, "
    "flat smooth light gray canvas background color #f5f6f8, "
    "dark charcoal ink color #030203, "
    "minimalist elegant modern line drawing, delicate continuous contours, "
    "narrative background scene with clear floor line, "
    "completely English scene context, completely no Korean characters, zero text artifacts"
)

NEGATIVE_PROMPT = (
    "shading, shadow, gradient, color, coloring, fill, solid fill, black areas, "
    "thick lines, bold lines, brush strokes, rough sketch, pencil hatching, dirty lines, "
    "grayscale, crosshatching, textured paper, dark background, black background, inverted, "
    "realistic anatomy, human head, realistic face, facial details, eyes, nose, mouth, hair, realistic hands, fingers, "
    "neck, long neck, throat, collar, neck line, detailed neck anatomy, "
    "watermark, signature, text, font, typography, banner text, "
    "Korean text, Hangul, Korean letters, non-English text, broken characters, foreign characters, "
    "3d, render, photorealistic, photo, messy"
)

def update_word_images_ts(word: str, word_id: str):
    if not os.path.exists(WORD_IMAGES_TS):
        return
    with open(WORD_IMAGES_TS, "r", encoding="utf-8") as f:
        content = f.read()

    new_entries = []
    file_name = word.replace(" ", "-")
    if f'"{word}": require(' not in content and f'{word}: require(' not in content:
        new_entries.append(f'  "{word}": require("../../assets/words/{file_name}.png"),')
    if word_id and f'"{word_id}": require(' not in content:
        new_entries.append(f'  "{word_id}": require("../../assets/words/{file_name}.png"),')

    if not new_entries:
        return

    target = "};\n"
    if target in content:
        idx = content.rfind(target)
        updated = content[:idx] + "\n".join(new_entries) + "\n" + content[idx:]
        with open(WORD_IMAGES_TS, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"[{word}] wordImages.ts 등록 완료: {word_id} -> {file_name}.png", flush=True)

def generate_image(scene_desc: str, output_path: str, seed: int = 42) -> bool:
    full_prompt = f"{scene_desc}, {STYLE_PROMPT}"
    payload = {
        "prompt": full_prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "width": 1024,
        "height": 1024,
        "steps": 8,
        "seed": seed,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
            if "images" in result and len(result["images"]) > 0:
                img_data = base64.b64decode(result["images"][0])
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(img_data)
                elapsed = time.time() - start_time
                print(f"생성 및 저장 완료 ({elapsed:.1f}초) -> {output_path}", flush=True)
                return True
            else:
                print(f"이미지 데이터 없음: {result.keys()}", flush=True)
                return False
    except Exception as e:
        print(f"API 요청 실패: {e}", flush=True)
        return False

# 유닛별 20단어 데이터 딕셔너리
UNIT_DATA = {
    7: [
        {
            "id": "m1-121", "word": "bother", "meaning": "괴롭히다",
            "scene": "cozy study room desk, cute slender stickman student sitting trying to focus on open textbook and notebook while mischievous friend stickman giggles and playfully tickles his ear with a fluffy feather pen to bother him, desk lamp and floor line"
        },
        {
            "id": "m1-122", "word": "relay", "meaning": "교대자, 교대하다",
            "scene": "dynamic athletic running track stadium, energetic cute slender stickman runner sprinting forward seamlessly passing a smooth baton into the outstretched hand of waiting teammate stickman in exciting relay race, lane lines and cheering fence"
        },
        {
            "id": "m1-123", "word": "suburb", "meaning": "교외",
            "scene": "peaceful quiet suburban neighborhood street, cute slender stickman riding bicycle past lovely houses with neat white picket fences and garden trees, distant city skyscraper skyline visible softly on horizon"
        },
        {
            "id": "m1-124", "word": "education", "meaning": "교육",
            "scene": "warm inspiring classroom, cute slender stickman teacher drawing solar system planetary orbit diagrams on large blackboard with chalk, attentive young stickman students sitting at neat wooden desks listening eagerly"
        },
        {
            "id": "m1-125", "word": "traffic", "meaning": "교통",
            "scene": "busy city intersection road with traffic lights, neat line of waiting cars and city bus stopped at red light, cute slender stickman pedestrians walking safely across painted zebra crosswalk, street lamps and city street line"
        },
        {
            "id": "m1-126", "word": "operator", "meaning": "교환수",
            "scene": "telecommunications control room station, cute slender stickman operator wearing headset sitting at console desk skillfully plugging patch cables into telephone switchboard board, glowing indicator dials and audio meters"
        },
        {
            "id": "m1-127", "word": "exchange", "meaning": "교환하다",
            "scene": "cheerful outdoor gift exchange plaza, two smiling cute slender stickman friends standing face to face happily swapping beautifully wrapped gift boxes with big ribbon bows simultaneously, decorative bunting flags"
        },
        {
            "id": "m1-128", "word": "beg", "meaning": "구걸하다, 간청하다",
            "scene": "cozy living room rug, cute slender stickman sitting on sofa holding a treat jar, while an adorable small puppy sits up on hind legs begging politely with front paws together for a delicious biscuit"
        },
        {
            "id": "m1-129", "word": "whisker", "meaning": "구레나룻, 수염",
            "scene": "sunny living room window cushion, cute slender stickman gently smiling and admiring a fluffy friendly cat showing its distinct fine needle whiskers curving delicately from cheeks, warm sunlight and tea mug"
        },
        {
            "id": "m1-130", "word": "roll", "meaning": "구르다",
            "scene": "gentle grassy hill slope outdoors, playful cute slender stickman gleefully rolling a large round ball down the soft green grassy incline chasing after it with open arms, billowing clouds and wildflowers"
        },
        {
            "id": "m1-131", "word": "cloudy", "meaning": "구름이 낀",
            "scene": "peaceful riverside promenade path, cute slender stickman in light coat looking up thoughtfully at sky overcast with thick soft fluffy layers of gray clouds diffusing the sunlight, gentle breeze rustling trees"
        },
        {
            "id": "m1-132", "word": "hole", "meaning": "구멍",
            "scene": "backyard garden flowerbed, cute slender stickman leaning on a garden shovel looking curiously down at a neat round hole in the soil where a cute little mole peeks its tiny head out, stone border and soil mound"
        },
        {
            "id": "m1-133", "word": "bend", "meaning": "구부리다",
            "scene": "craft artisan workshop table, cute slender stickman craftsman with work apron holding a slender flexible bamboo rod with both hands deliberately bending it into a smooth graceful curved arc, clamps and tools on pegboard"
        },
        {
            "id": "m1-134", "word": "save", "meaning": "구하다, 절약하다, 저축하다",
            "scene": "neat wooden study desk, cheerful cute slender stickman happily dropping a shiny round coin into the top slot of a cute ceramic piggy bank to save money, small stack of saved coins and ledger notepad"
        },
        {
            "id": "m1-135", "word": "nation", "meaning": "국가",
            "scene": "grand civic plaza square, proud cute slender stickman citizen standing with hand placed gently on chest looking up at a majestic national flag waving atop a tall flagpole in front of historic national hall, civic monument"
        },
        {
            "id": "m1-136", "word": "international", "meaning": "국제적인",
            "scene": "grand international summit convention hall, diverse cute slender stickman delegates gathering around circular table with row of international flags, shaking hands and sharing documents in friendly global partnership"
        },
        {
            "id": "m1-137", "word": "army", "meaning": "군대, 육군",
            "scene": "orderly military camp parade ground, disciplined cute slender stickman soldiers in formation standing proudly at attention while a commanding officer walks inspecting the ranks, military tents and flag line"
        },
        {
            "id": "m1-138", "word": "soldier", "meaning": "군인, 병사",
            "scene": "peaceful scenic outpost guard station, brave cute slender stickman soldier wearing sturdy helmet and backpack standing upright on duty holding compact binoculars gazing faithfully across valley horizon"
        },
        {
            "id": "m1-139", "word": "firm", "meaning": "굳은, 회사",
            "scene": "sleek modern corporate office conference room, professional cute slender stickman partners in neat business suits shaking hands firmly over a table contract after sealing deal, glass wall overlooking city skyline"
        },
        {
            "id": "m1-140", "word": "hunger", "meaning": "굶주림",
            "scene": "cozy kitchen stove in evening, hungry cute slender stickman holding stomach with funny rumbly expression, eagerly watching steam rising deliciously from a large boiling soup pot on stove holding a soup spoon"
        }
    ],
    8: [
        {
            "id": "m1-141", "word": "palace", "meaning": "궁전",
            "scene": "splendid classical fairy-tale palace facade, cute slender stickman king wearing a delicate round crown walking through grand marble archway courtyard with soaring spires, decorative stone fountain and banners"
        },
        {
            "id": "m1-142", "word": "valuable", "meaning": "귀중한",
            "scene": "antique treasure vault showroom, cute slender stickman jeweler with magnifying loupe gently holding up an exquisite rare glowing gemstone resting on velvet cushion, ornate brass scales and jewel chest"
        },
        {
            "id": "m1-143", "word": "precious", "meaning": "귀중한",
            "scene": "warm family living room, cute slender stickman mother lovingly cradling an adorable tiny baby stickman wrapped in soft swaddle blanket smiling softly, gentle rocking cradle and wall family portraits"
        },
        {
            "id": "m1-144", "word": "rule", "meaning": "규칙, 규정하다, 통치하다",
            "scene": "formal library study room wall, cute slender stickman librarian pointing finger politely to a framed rule chart on wall titled 'LIBRARY RULES' depicting quiet icons, neat bookshelves and study desk"
        },
        {
            "id": "m1-145", "word": "regular", "meaning": "규칙적인",
            "scene": "sunny morning bedroom window, cute slender stickman in pajamas happily stretching arms as round alarm clock rings on bedside table next to weekly routine schedule calendar marked with checkboxes"
        },
        {
            "id": "m1-146", "word": "balance", "meaning": "균형",
            "scene": "outdoor gymnastics balance beam, graceful cute slender stickman balancing poised on one foot with arms outstretched horizontally in perfect poise along narrow wooden beam, soft landing mat below"
        },
        {
            "id": "m1-147", "word": "swing", "meaning": "그네, 흔들다",
            "scene": "sunny neighborhood playground under leafy tree, joyous cute slender stickman swinging high on wooden swing hanging from sturdy oak branch kicking feet toward sky, sandbox and park bench"
        },
        {
            "id": "m1-148", "word": "shade", "meaning": "그늘",
            "scene": "sunny summer meadow, cute slender stickman relaxing sitting peacefully with cold lemonade cup under the cooling dark shadow canopy of a giant leafy green tree shelter, bright scorching sun shining outside"
        },
        {
            "id": "m1-149", "word": "such", "meaning": "그러한",
            "scene": "art museum gallery room, cute slender stickman visitor standing amazed with hand on chin gazing upward at an overwhelmingly magnificent gigantic masterpiece painting hanging on wall, gallery spotlight"
        },
        {
            "id": "m1-150", "word": "otherwise", "meaning": "그렇지 않으면",
            "scene": "hallway front door entryway, cute slender stickman about to step out into rainy day, friend stickman holding out an open umbrella warning him to take it otherwise he will get completely soaked"
        },
        {
            "id": "m1-151", "word": "bowl", "meaning": "그릇",
            "scene": "bright breakfast kitchen counter, cute slender stickman holding a ceramic cereal bowl filled with colorful fruit slices and oatmeal holding wooden spoon, pitcher of fresh milk and fruit basket"
        },
        {
            "id": "m1-152", "word": "paint", "meaning": "그림, 그리다",
            "scene": "sunlit art studio room, cute slender stickman artist wearing beret holding wooden palette and fine paintbrush dabbing strokes onto a canvas easel depicting a mountain landscape, paint tubes on stool"
        },
        {
            "id": "m1-153", "word": "shadow", "meaning": "그림자",
            "scene": "sunset paved city street walkway, cute slender stickman walking forward noticing his own long dramatic dark silhouette shadow cast stretches far behind him across the cobblestone pavement, street lamp"
        },
        {
            "id": "m1-154", "word": "else", "meaning": "그밖에",
            "scene": "quaint bakery checkout counter, friendly cute slender stickman baker holding wrapped loaf of bread smiling and asking customer stickman if they need anything else, glass showcase full of pastries"
        },
        {
            "id": "m1-155", "word": "theater", "meaning": "극장",
            "scene": "classic movie cinema theater hall, audience rows of cute slender stickman spectators sitting in plush velvet seats watching exciting movie projected onto huge glowing cinema screen with popcorn bucket"
        },
        {
            "id": "m1-156", "word": "diligent", "meaning": "근면한, 부지런한",
            "scene": "late night home study desk with warm desk lamp, diligent cute slender stickman sitting focused writing notes into notebook surrounded by neatly organized reference books and coffee mug, starry night outside window"
        },
        {
            "id": "m1-157", "word": "metal", "meaning": "금속",
            "scene": "modern metalsmith forge workshop, cute slender stickman craftsman with protective goggles using tongs holding a gleaming silver metal ingot over sturdy anvil, assortment of steel rods and tools"
        },
        {
            "id": "m1-158", "word": "rapidly", "meaning": "급격하게",
            "scene": "dynamic racing wind tunnel laboratory, cute slender stickman scientist observing a streamlined miniature rocket vehicle shooting forward rapidly leaving speed lines across track, digital velocity speedometer display"
        },
        {
            "id": "m1-159", "word": "machine", "meaning": "기계",
            "scene": "spacious industrial engineering workshop, cute slender stickman mechanic holding a wrench turning a gleaming gear cog inside a complex mechanical machine with turning gears, pistons and pulleys"
        },
        {
            "id": "m1-160", "word": "monument", "meaning": "기념비",
            "scene": "historic memorial plaza park, cute slender stickman tourist standing respectfully looking up at a towering carved marble stone monument obelisk commemorating historical peace, flowers laid at stone base"
        }
    ],
    9: [
        {
            "id": "m1-161", "word": "expect", "meaning": "기대하다, 예상하다",
            "scene": "cozy front porch entryway, cute slender stickman standing waiting eagerly looking down driveway expecting beloved friend arrival holding welcome flower bouquet, mailbox and path"
        },
        {
            "id": "m1-162", "word": "pray", "meaning": "기도하다",
            "scene": "peaceful quiet church chapel or temple room, cute slender stickman kneeling gently with hands clasped together in sincere prayer with bowed head, warm candle flame glowing on altar"
        },
        {
            "id": "m1-163", "word": "record", "meaning": "기록",
            "scene": "sports stadium finish line podium, cute slender stickman referee holding stopwatch looking proudly at digital scoreboard displaying a new world record time, athlete smiling with trophy"
        },
        {
            "id": "m1-164", "word": "giraffe", "meaning": "기린",
            "scene": "sunny African savannah wildlife park, cute slender stickman standing on safe wooden viewing deck offering acacia leaves to a tall gentle giraffe with long graceful neck and spotted pattern, acacia trees"
        },
        {
            "id": "m1-165", "word": "pleasant", "meaning": "기분 좋은",
            "scene": "gentle spring garden bench under flowering cherry tree, cute slender stickman relaxing with eyes closed and gentle smile feeling the pleasant warm sunshine and soft fluttering flower petals"
        },
        {
            "id": "m1-166", "word": "delight", "meaning": "기쁨",
            "scene": "colorful birthday party room, cute slender stickman beaming with pure delight clapping hands excitedly as family brings in a glowing birthday cake with candles, balloons and streamers"
        },
        {
            "id": "m1-167", "word": "joy", "meaning": "기쁨",
            "scene": "lush green hilltop meadow, joyous cute slender stickman jumping high into air with arms wide open in pure exuberant joy, colorful wildflowers, flying songbirds and sunshine"
        },
        {
            "id": "m1-168", "word": "engineer", "meaning": "기사",
            "scene": "modern engineering design laboratory, cute slender stickman engineer wearing hardhat pointing to technical blueprint schematic spread on desk discussing with robotic arm prototype"
        },
        {
            "id": "m1-169", "word": "skill", "meaning": "기술",
            "scene": "pottery studio room, cute slender stickman potter expertly shaping wet clay on spinning pottery wheel with deft nimble fingers into a beautiful balanced vase, finished pottery on wooden shelves"
        },
        {
            "id": "m1-170", "word": "memory", "meaning": "기억",
            "scene": "nostalgic attic room window, cute slender stickman sitting on vintage trunk smiling warmly as he turns pages of an open vintage photo album filled with childhood picture memories, warm ray of light"
        },
        {
            "id": "m1-171", "word": "remember", "meaning": "기억하다",
            "scene": "study desk with glowing lightbulb idea above head, cute slender stickman snapping fingers with bright sudden smile remembering an important answer, open revision notes and textbook"
        },
        {
            "id": "m1-172", "word": "foundation", "meaning": "기초",
            "scene": "building construction site, cute slender stickman construction engineer checking blueprint verifying the sturdy solid concrete foundation blocks laid deep into the ground, level tool and crane in background"
        },
        {
            "id": "m1-173", "word": "base", "meaning": "기초, 기반",
            "scene": "baseball diamond infield field, cute slender stickman baseball runner sliding foot safely onto white square base bag just ahead of tag, baseball field foul lines and dugout"
        },
        {
            "id": "m1-174", "word": "cough", "meaning": "기침",
            "scene": "warm living room armchair, cute slender stickman feeling under the weather coughing into crook of elbow politely holding a warm cup of honey tea, blanket draped and box of tissues on side table"
        },
        {
            "id": "m1-175", "word": "chance", "meaning": "기회, 확률",
            "scene": "carnival game booth, cute slender stickman taking a golden chance aiming dart carefully at balloon target on wall with focused hopeful smile, prize teddy bears hanging from canopy"
        },
        {
            "id": "m1-176", "word": "climate", "meaning": "기후",
            "scene": "geography classroom with globe, cute slender stickman teacher pointing to climate zones map showing desert sun, tropical rain, temperate forest, and polar ice caps on wall chart"
        },
        {
            "id": "m1-177", "word": "route", "meaning": "길",
            "scene": "hiking trailhead wooden trail map sign, cute slender stickman hiker with backpack tracing a winding mountain hiking route path with index finger planning the scenic trek, pine trees and trail marker"
        },
        {
            "id": "m1-178", "word": "feather", "meaning": "깃털",
            "scene": "sunlit wooden desk, cute slender stickman holding a single delicate soft quill feather up to the light admiring its intricate fine barbs, vintage inkwell and parchment letter"
        },
        {
            "id": "m1-179", "word": "deep", "meaning": "깊은",
            "scene": "clear calm coastal ocean waters, cute slender stickman snorkeling looking down into the deep blue underwater abyss with colorful coral reef canyon and swimming sea turtles far below"
        },
        {
            "id": "m1-180", "word": "clean", "meaning": "깨끗한",
            "scene": "sparkling bright kitchen living room, cheerful cute slender stickman with apron holding mop wiping floor until it shines brilliantly with sparkle glints, neat shelves and tidy flower vase"
        }
    ]
}

def deploy_unit(unit_num: int):
    print(f"\n[Unit {unit_num}] 작업 완료 후 배포 파이프라인 가동...", flush=True)
    
    # 1. 린트 검증
    try:
        subprocess.run(["npm", "run", "lint"], cwd=PROJECT_ROOT, check=True)
        print("Lint 검증 통과!", flush=True)
    except Exception as e:
        print(f"Lint 경고/오류 (계속 진행): {e}", flush=True)

    # 2. 외장하드 ._* 파일 정리
    subprocess.run(["find", ".", "..", "-name", "._*", "-type", "f", "-delete"], cwd=PROJECT_ROOT)
    print("._* 임시 파일 정리 완료", flush=True)

    # 3. Git 커밋 & 푸시
    try:
        subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, check=True)
        commit_msg = f"feat: 중1 유닛 {unit_num} 선형그래픽 일러스트 20단어 전원 생성 및 등록 완료"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        print(f"Git 배포 완료: 유닛 {unit_num}", flush=True)
    except Exception as e:
        print(f"Git 커밋/푸시 중 오류: {e}", flush=True)

def main():
    parser = argparse.ArgumentParser(description="중1 선형그래픽 연속 생성기")
    parser.add_argument("--start-unit", type=int, default=7, help="시작할 유닛 번호 (기본: 7)")
    parser.add_argument("--end-unit", type=int, default=9, help="종료할 유닛 번호 (기본: 9)")
    args = parser.parse_args()

    print(f"==================================================", flush=True)
    print(f"중학교 1학년 선형그래픽 연속 생성 파이프라인 가동 (Unit {args.start_unit} ~ {args.end_unit})", flush=True)
    print(f"==================================================", flush=True)

    for unit_num in range(args.start_unit, args.end_unit + 1):
        if unit_num not in UNIT_DATA:
            print(f"유닛 {unit_num} 데이터가 정의되지 않았습니다. 작업을 종료합니다.", flush=True)
            break

        words = UNIT_DATA[unit_num]
        print(f"\n▶▶▶ [Unit {unit_num}] 20단어 렌더링 시작 ◀◀◀", flush=True)

        for idx, item in enumerate(words, start=1):
            w = item["word"]
            w_id = item["id"]
            meaning = item["meaning"]
            scene = item["scene"]
            file_name = w.replace(" ", "-")
            out_file = os.path.join(ASSETS_DIR, f"{file_name}.png")

            print(f"\n[Unit {unit_num} - {idx}/20] '{w}' ({w_id}: {meaning}) 생성 중...", flush=True)
            print(f"Scene: {scene}", flush=True)

            seed = 1000 + int(w_id.split("-")[1])
            success = generate_image(scene, out_file, seed=seed)
            if success:
                print(f"[{w}] 생성 완료 -> {out_file}", flush=True)
                update_word_images_ts(w, w_id)
            else:
                print(f"[{w}] 생성 실패!", flush=True)

        # 1개 유닛(20단어) 완료 시 배포
        deploy_unit(unit_num)
        print(f"🎉 [Unit {unit_num}] 20단어 생성 및 등록 배포 전원 완료!\n", flush=True)

    print("모든 지정 유닛 생성 파이프라인이 성공적으로 완료되었습니다!", flush=True)

if __name__ == "__main__":
    main()
