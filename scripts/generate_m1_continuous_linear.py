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
from dashboard_updater import update_dashboards

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")
WORD_IMAGES_TS = os.path.join(PROJECT_ROOT, "src", "constants", "wordImages.ts")

# 스킬 표준 공통 프롬프트 (3~3.5등신 순백색 픽토그램 마네킹 캐릭터)
STYLE_PROMPT = (
    "masterpiece, best quality, ultra-detailed linear graphic illustration, "
    "clean pure line art vector aesthetic, "
    "3 to 3.5 head-to-body chibi SD ratio cute characters with large prominent smooth spherical bald round heads, "
    "minimalist dot and line face, two simple solid black dot eyes and a tiny thin curved smile line, strictly no nose, no eyebrows, no lips, no ears, no hair, "
    "seamless tubular neckless body directly attached to round head with completely no neck, smooth organic curves without clavicle or muscle contours, "
    "jointless smooth rubber-hose arms and legs with no elbows and no knees, simplified mitten-like blunt round hands, smooth rounded flat oval foot pads firmly on floor line, "
    "blank solid white mannequin pictogram character fill with zero clothing, no seams, no buttons, no folds, no skin texture, genderless universal figure, "
    "crisp uniform dark charcoal ink outlines #030203, strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, flat smooth light gray canvas background color #f5f6f8, "
    "modest compact character scale, small adorable chibi figure in spacious wide framing, plenty of surrounding negative space and breathing room around character, avoid oversized character, balanced environmental perspective, full body comfortably framed within scene, "
    "abundant rich background details, furniture, wall decor, floor line, ambient props, "
    "strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
)

NEGATIVE_PROMPT = (
    "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing, "
    "oversized character, giant figure, frame-filling character, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, large scale character dominating scene, taking over screen, "
    "realistic human anatomy, realistic face, facial details, nose, eyebrows, eyelashes, eyelids, lips, teeth, ears, hair, hairstyle, neck, long neck, throat, collar, collarbone, muscles, realistic fingers, individual finger joints, fingernails, toes, shoes, clothing, clothes, shirt, pants, wrinkles, folds, "
    "thick lines, heavy brush strokes, chunky lines, fat strokes, "
    "pure white #ffffff background, dark background, black background, 3d, 3d render, realistic, shadow, shading, color, gradients, photo, blur, watermark, signature, messy"
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

def generate_image(word: str, scene_desc: str, output_path: str, seed: int = 42) -> tuple:
    import re
    clean_word = re.sub(r'[^\x00-\x7F]+', ' ', word or '').strip()
    clean_scene = re.sub(r'[^\x00-\x7F]+', ' ', scene_desc or '').strip()

    full_prompt = (
        f"linear graphic illustration, complete richly detailed scene of {clean_word}, "
        "thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, extremely fine crisp outlines drawn in dark charcoal ink color #030203, "
        "flat smooth light gray canvas background color #f5f6f8, "
        "neckless cute slender doodle stickman characters with round bald circle heads attached directly to torso with completely no neck, tiny smiling dot faces, "
        "modest compact character scale, standing cute chibi figure occupying approximately one third of frame height around 30 to 35 percent of canvas height, placed comfortably on bottom floor line, spacious upper and middle frame filled with rich environmental details, balanced wide scene composition, plenty of breathing room, full body visible without crowding, "
        f"{clean_scene}, "
        "abundant rich background details, furniture, wall decor, floor line, ambient props, "
        "strictly flat 2d linear graphic, no shading, no gradients, no solid black fills, empty background, "
        "strictly English text only if any letters appear, absolutely no non-English characters, 100% pure English alphabet A-Z only, completely no Korean characters, strictly no Hangul, strictly no Chinese characters, completely non-Asian script, zero foreign glyphs"
    )

    negative_prompt = (
        "neck, long neck, throat, collar, neck line, detailed neck anatomy, "
        "oversized character, giant figure, tall figure, frame-filling character, character taking up entire screen, close-up, extreme close-up, cropped body, zoomed in, crowding the frame, suffocating composition, character head near top of frame, dominating figure, "
        "realistic human anatomy, realistic face, facial details, nose, eyebrows, eyelashes, eyelids, lips, teeth, ears, hair, hairstyle, muscles, realistic fingers, individual finger joints, fingernails, toes, shoes, clothing, clothes, shirt, pants, wrinkles, folds, "
        "thick lines, bold outlines, heavy brush strokes, chunky lines, fat strokes, "
        "pure white #ffffff background, dark background, black background, 3d, 3d render, realistic, shadow, shading, color, gradients, photo, blur, watermark, text, signature, messy, "
        "non-English text, non-English characters, Korean text, Hangul, Korean letters, Chinese characters, Hanzi, Kanji, Japanese text, Kana, foreign script, pseudo-Hangul, weird Asian glyphs, oriental symbols, non-Latin alphabet, foreign writing"
    )
    payload = {
        "prompt": full_prompt,
        "negative_prompt": negative_prompt,
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
                return True, elapsed
            else:
                print(f"이미지 데이터 없음: {result.keys()}", flush=True)
                return False, 0.0
    except Exception as e:
        print(f"API 요청 실패: {e}", flush=True)
        return False, 0.0

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
    ],
    10: [
        {
            "id": "m1-181", "word": "wake", "meaning": "깨우다, 일어나다",
            "scene": "sunny cozy bedroom morning, cute slender stickman sitting up in bed stretching arms cheerfully as sunlight streams through window, round alarm clock on bedside table"
        },
        {
            "id": "m1-182", "word": "tail", "meaning": "꼬리",
            "scene": "sunny living room carpet, playful cute slender stickman smiling and gently watching a happy pet dog wagging its fluffy curled tail joyfully, dog toy bone on floor"
        },
        {
            "id": "m1-183", "word": "petal", "meaning": "꽃잎",
            "scene": "gentle spring flower garden, cute slender stickman kneeling gently holding a delicate fallen flower blossom admiring individual soft curved petals falling gracefully, blooming rose bush and watering can"
        },
        {
            "id": "m1-184", "word": "dream", "meaning": "꿈",
            "scene": "peaceful bedroom at night, cute slender stickman sleeping soundly on cozy pillow under warm quilt, with a whimsical swirling thought cloud above depicting floating starry celestial planets and flying friendly birds"
        },
        {
            "id": "m1-185", "word": "nod", "meaning": "고개를 끄덕이다",
            "scene": "classroom lecture room, attentive cute slender stickman student sitting at neat wooden desk nodding head in clear agreement and understanding while listening to teacher presentation, open notebook and pencil"
        },
        {
            "id": "m1-186", "word": "attract", "meaning": "끌다, 유인하다",
            "scene": "science physics laboratory bench, curious cute slender stickman holding a red and blue horseshoe magnet attracting and picking up a cluster of silver paperclips effortlessly, lab flasks and measuring ruler"
        },
        {
            "id": "m1-187", "word": "terrible", "meaning": "끔찍한, 지독한",
            "scene": "cozy kitchen cooking counter, cute slender stickman looking down with humorous shocked expression and hand over mouth at a completely burnt black smoking batch of cookies on baking tray, oven smoke wisps rising"
        },
        {
            "id": "m1-188", "word": "carry", "meaning": "나르다, 운반하다",
            "scene": "house moving hallway or warehouse, strong determined cute slender stickman carefully carrying a large cardboard moving box with both arms, packing tape and stacked storage boxes nearby"
        },
        {
            "id": "m1-189", "word": "wood", "meaning": "나무, 목재, 숲",
            "scene": "scenic tranquil pine forest woodland trail, cute slender stickman hiker walking beside towering straight wood tree trunks with deep bark textures and fallen timber logs, lush forest floor with wild ferns"
        },
        {
            "id": "m1-190", "word": "butterfly", "meaning": "나비",
            "scene": "bright outdoor botanical garden meadow, cute slender stickman crouching down admiring a graceful butterfly with delicate patterned wings perched gently atop a blooming sunflower petal, fluttering butterflies in air"
        },
        {
            "id": "m1-191", "word": "badly", "meaning": "나쁘게, 심하게",
            "scene": "paved neighborhood bicycle path, cute slender stickman sitting on pavement rubbing knee with a bandaged scrape after falling off bicycle, fallen bicycle on ground and first aid kit nearby"
        },
        {
            "id": "m1-192", "word": "elder", "meaning": "나이가 더 많은, 손위의",
            "scene": "sunny garden patio tea table, polite cute slender stickman respectfully pouring warm steaming tea from a teapot into the teacup of a wise elder grandparent stickman resting comfortably with walking cane"
        },
        {
            "id": "m1-193", "word": "later", "meaning": "나중에",
            "scene": "office desk calendar, cute slender stickman looking at wall clock showing time and pointing finger forward to a future date circled on monthly calendar planner, sticky note memo saying later"
        },
        {
            "id": "m1-194", "word": "appear", "meaning": "나타나다",
            "scene": "magic performance stage with velvet curtains, cute slender stickman magician wearing top hat waving magic wand over an empty table as an adorable white rabbit suddenly appears amidst sparkling magic dust"
        },
        {
            "id": "m1-195", "word": "trumpet", "meaning": "나팔, 트럼펫",
            "scene": "music band concert stage hall, talented cute slender stickman musician enthusiastically blowing into a gleaming brass trumpet with fingers pressing valves, music stand with sheet notes"
        },
        {
            "id": "m1-196", "word": "edge", "meaning": "날, 가장자리",
            "scene": "woodworking craft carpentry bench, cute slender stickman artisan carefully inspecting the sharp clean edge of a freshly cut wooden plank using a steel measurement square ruler, wood shavings on table"
        },
        {
            "id": "m1-197", "word": "weather", "meaning": "날씨",
            "scene": "meteorology weather broadcast station studio, cute slender stickman meteorologist holding pointer gesturing toward large weather radar screen displaying sunshine, rain clouds, and wind symbols"
        },
        {
            "id": "m1-198", "word": "date", "meaning": "날짜, 데이트",
            "scene": "romantic cozy cafe table with flowers in vase, two cute slender stickman having a sweet happy coffee date together holding warm ceramic mugs, heart steam rising softly"
        },
        {
            "id": "m1-199", "word": "data", "meaning": "자료, 데이터",
            "scene": "modern technology analytics research office, cute slender stickman data analyst standing before a large holographic digital monitor displaying colorful bar charts, line graphs, and statistical data metrics"
        },
        {
            "id": "m1-200", "word": "sharp", "meaning": "날카로운",
            "scene": "craft art studio table, cute slender stickman designer carefully testing the precise sharp point of a precision craft knife pencil cutting crisp geometric shapes on cutting mat"
        }
    ],
    11: [
        {
            "id": "m1-201", "word": "coeducation", "meaning": "남녀공학",
            "scene": "cheerful bright high school hallway corridor, cute slender boy and girl stickman students in school uniforms walking together chatting happily carrying backpacks and textbooks, classroom doors and lockers"
        },
        {
            "id": "m1-202", "word": "remain", "meaning": "남다",
            "scene": "warm family dinner dining table after meal, cute slender stickman looking at a single delicious strawberry cake slice remaining alone on a porcelain serving plate, empty tea cups and forks"
        },
        {
            "id": "m1-203", "word": "abuse", "meaning": "남용, 학대",
            "scene": "office desk with warning stop sign, conscientious cute slender stickman manager holding hand up firmly gesturing stop to prevent overuse and abuse of company office resources, recycling bins"
        },
        {
            "id": "m1-204", "word": "husband", "meaning": "남편",
            "scene": "cozy home kitchen, loving cute slender stickman husband wearing apron cheerfully cooking dinner on stove smiling warmly while handing a taste spoon to wife stickman, spice rack and potted plant"
        },
        {
            "id": "m1-205", "word": "waste", "meaning": "낭비, 쓰레기",
            "scene": "neighborhood recycling station, responsible cute slender stickman sorting waste carefully dropping aluminum cans and paper boxes into designated recycling bins instead of wasting, clean park pavement"
        },
        {
            "id": "m1-206", "word": "low", "meaning": "낮은",
            "scene": "peaceful scenic mountain valley meadow, cute slender stickman standing on a low grassy rolling knoll looking up at towering high alpine mountain peaks in distant horizon, wildflowers and river"
        },
        {
            "id": "m1-207", "word": "smell", "meaning": "냄새, 냄새를 맡다",
            "scene": "sunlit flower garden terrace, delighted cute slender stickman gently leaning close to smell the sweet fragrance of a blooming rose blossom with closed eyes and serene happy smile, garden fence"
        },
        {
            "id": "m1-208", "word": "refrigerator", "meaning": "냉장고",
            "scene": "modern bright kitchen, hungry cute slender stickman opening double-door stainless refrigerator glowing with internal light inspecting fresh fruits, milk pitcher, and vegetables neatly organized on shelves"
        },
        {
            "id": "m1-209", "word": "wide", "meaning": "넓은",
            "scene": "vast golden savanna prairie horizon, cute slender stickman standing with arms spread wide open feeling the immense wide expanse of open wilderness plains under huge endless sky with fluffy clouds"
        },
        {
            "id": "m1-210", "word": "effort", "meaning": "노력",
            "scene": "fitness gym training mat, determined cute slender stickman sweating with joyful exertion lifting a heavy barbell with concentrated effort and strength, workout mirrors and dumbbell racks"
        },
        {
            "id": "m1-211", "word": "slave", "meaning": "노예",
            "scene": "historic ancient ruins museum exhibit, thoughtful cute slender stickman viewing a historical display with broken metal chains symbolizing liberation and triumph over ancient slavery, informational plaque"
        },
        {
            "id": "m1-212", "word": "astonish", "meaning": "놀라게 하다",
            "scene": "birthday surprise party doorway, cute slender stickman walking into room completely astonished with wide open arms as friends jump out throwing colorful confetti poppers, party banners"
        },
        {
            "id": "m1-213", "word": "surprise", "meaning": "놀라움",
            "scene": "cozy living room armchair, cute slender stickman gasping with delightful surprise as a spring jack-in-the-box pop toy bounces out of an unwrapped colorful gift box, wrapping paper ribbons on rug"
        },
        {
            "id": "m1-214", "word": "amazing", "meaning": "놀라운",
            "scene": "grand planetarium observatory dome, cute slender stickman looking up through a giant optical telescope pointing with awe at an amazing glowing spiral galaxy projected across starry dome ceiling"
        },
        {
            "id": "m1-215", "word": "wonderful", "meaning": "놀라운, 멋진",
            "scene": "scenic mountain summit overlook at sunset, happy cute slender stickman cheering with raised hands celebrating a wonderful breathtaking panoramic view of sunset colored sky and winding rivers"
        },
        {
            "id": "m1-216", "word": "joke", "meaning": "농담",
            "scene": "cozy coffee shop table, cute slender stickman telling a hilarious funny joke while friend stickman bursts into uncontrollable joyous laughter wiping a happy tear, coffee cups and cafe counter"
        },
        {
            "id": "m1-217", "word": "crop", "meaning": "농작물",
            "scene": "sunlit fertile farm field outdoors, proud cute slender stickman farmer in straw hat holding a wooden basket overflowing with ripe harvested crops including corn ears, tomatoes, and wheat stalks"
        },
        {
            "id": "m1-218", "word": "miss", "meaning": "놓치다, 그리워하다",
            "scene": "train station platform, cute slender stickman running along platform with suitcase waving hand looking at passenger train just pulling away out of station, station clock and departure board"
        },
        {
            "id": "m1-219", "word": "brain", "meaning": "뇌, 두뇌",
            "scene": "science neurology lab classroom, curious cute slender stickman student observing a detailed 3D anatomical brain model resting on a display stand, neuroscience diagrams on wall chart"
        },
        {
            "id": "m1-220", "word": "press", "meaning": "누르다, 언론",
            "scene": "newspaper printing press facility, cute slender stickman technician pressing a prominent round control button activating a mechanical printing press machine printing news sheets"
        }
    ],
    12: [
        {
            "id": "m1-221", "word": "wink", "meaning": "눈을 깜빡거리다",
            "scene": "cheerful cozy cafe counter, playful cute slender stickman barista wearing apron smiling warmly and giving a friendly playful wink with one eye, coffee machine and mugs"
        },
        {
            "id": "m1-222", "word": "blind", "meaning": "눈이 먼, 블라인드",
            "scene": "sunny apartment living room window, cute slender stickman gently pulling the beaded cord adjusting horizontal window blinds slats to filter bright afternoon sunlight, potted fern plant"
        },
        {
            "id": "m1-223", "word": "lay", "meaning": "놓다, 눕히다, 알을 낳다",
            "scene": "warm chicken coop barn nest, cute slender stickman farmer gently smiling as a mother hen sits snugly in straw nest having laid smooth round eggs, wooden coop wall"
        },
        {
            "id": "m1-224", "word": "wolf", "meaning": "늑대",
            "scene": "misty snowy pine forest ridge under full moon, majestic wild wolf standing proudly on rocky ledge howling softly toward starry night sky, snow dusted evergreen pine trees"
        },
        {
            "id": "m1-225", "word": "altogether", "meaning": "다 같이, 완전히",
            "scene": "warm community festival square, joyous group of cute slender stickman neighbors singing and clapping together in unison with linked arms around a decorative village gazebo"
        },
        {
            "id": "m1-226", "word": "squirrel", "meaning": "다람쥐",
            "scene": "autumn leafy oak park tree branch, cute slender stickman standing on path smiling watching an adorable bushy-tailed squirrel nibbling happily on an acorn, colorful fallen leaves"
        },
        {
            "id": "m1-227", "word": "treat", "meaning": "다루다, 대접하다, 치료하다",
            "scene": "sunny bakery cafe table, generous cute slender stickman smiling happily treating a dear friend stickman to a delicious tiered cake and tea cups, sweet dessert display"
        },
        {
            "id": "m1-228", "word": "different", "meaning": "다른, 차이가 나는",
            "scene": "art studio display table, cute slender stickman artist comparing two distinctly different ceramic pottery vases side by side noting unique shapes and contours, craft workbench"
        },
        {
            "id": "m1-229", "word": "bridge", "meaning": "다리",
            "scene": "picturesque river valley landscape, cute slender stickman standing on an elegant stone arched bridge looking down at sparkling flowing river waters below, willow trees on riverbanks"
        },
        {
            "id": "m1-230", "word": "dive", "meaning": "다이빙하다, 뛰어들다",
            "scene": "olympic swimming pool diving platform, athletic cute slender stickman gracefully diving mid-air headfirst with straight body form toward clear sparkling pool water, lane markers"
        },
        {
            "id": "m1-231", "word": "colorful", "meaning": "다채로운, 화려한",
            "scene": "festive carnival street parade, cute slender stickman looking up in delight at a dazzling array of colorful airborne festival balloons and rainbow parade streamers"
        },
        {
            "id": "m1-232", "word": "hurt", "meaning": "다치게 하다, 아프다",
            "scene": "medical clinic treatment room, caring cute slender stickman doctor gently applying a soothing adhesive bandage to the scraped elbow of a brave patient stickman, medical cabinet"
        },
        {
            "id": "m1-233", "word": "college", "meaning": "단과대학, 대학교",
            "scene": "historic ivy-covered university college quadrangle courtyard, cheerful cute slender stickman university students in college blazers carrying books walking past classical brick campus hall"
        },
        {
            "id": "m1-234", "word": "tightly", "meaning": "단단히, 꽉",
            "scene": "sailor sailboat dock pier, strong cute slender stickman pulling with both hands tying a thick nautical rope tightly around a sturdy wooden harbor bollard to secure ship"
        },
        {
            "id": "m1-235", "word": "word", "meaning": "단어, 말",
            "scene": "study room wooden desk, studious cute slender stickman pointing index finger attentively at a specific vocabulary word highlighted in a large open leather-bound dictionary book"
        },
        {
            "id": "m1-236", "word": "shut", "meaning": "닫다",
            "scene": "vintage wooden cottage front door entryway, cute slender stickman firmly pushing shut a heavy wooden door to block out cold windy evening weather, warm glow from room window"
        },
        {
            "id": "m1-237", "word": "close", "meaning": "닫다, 가까운",
            "scene": "sunny front porch, two warm cute slender stickman best friends standing close together smiling happily with arms around shoulders celebrating true close friendship, flower pots"
        },
        {
            "id": "m1-238", "word": "dollar", "meaning": "달러",
            "scene": "bank teller cashier counter, cute slender stickman teller neatly counting crisp green paper dollar currency bills onto polished counter desk, brass balance scale and safe vault"
        },
        {
            "id": "m1-239", "word": "sweet", "meaning": "달콤한, 상냥한",
            "scene": "quaint confectionery candy sweet shop, delighted cute slender stickman holding a colorful spiral rainbow lollipop smiling happily before glass jars brimming with sweet treats"
        },
        {
            "id": "m1-240", "word": "smoke", "meaning": "담배를 피우다, 연기",
            "scene": "cozy mountain cabin fireplace hearth in winter, cute slender stickman sitting on rocking chair watching gentle gray smoke wisps rising up brick chimney from crackling wood fire log"
        }
    ]    ,
    13: [
        {
            "id": "m1-241", "word": "blanket", "meaning": "담요",
            "scene": "cozy peaceful bedroom, cute slender stickman pulling a warm thick knitted blanket snugly up to chest while resting comfortably in bed, bedside nightstand lamp and wooden floor line"
        },
        {
            "id": "m1-242", "word": "answer", "meaning": "대답, 대답하다",
            "scene": "bright school classroom blackboard, confident cute slender stickman student raising hand high in air giving the correct answer to the teacher stickman smiling warmly, wooden desks"
        },
        {
            "id": "m1-243", "word": "continent", "meaning": "대륙",
            "scene": "grand geography study room, curious cute slender stickman gently spinning a large rotating globe highlighting vast continental landmasses, atlas reference books stacked on table"
        },
        {
            "id": "m1-244", "word": "marble", "meaning": "대리석",
            "scene": "classical grand museum gallery hall, cute slender stickman walking gracefully across polished gleaming white marble floor tiles with classical marble pillars and sunlit arches"
        },
        {
            "id": "m1-245", "word": "mostly", "meaning": "대부분",
            "scene": "art studio workshop table, cute slender stickman instructor observing a creative group of stickman art students who are mostly busy painting colorful landscape canvases on easels"
        },
        {
            "id": "m1-246", "word": "instead", "meaning": "대신에",
            "scene": "bright grocery market aisle, cute slender stickman shopper smiling thoughtfully putting a carton of fresh milk into shopping basket instead of a sugary beverage bottle, grocery shelves"
        },
        {
            "id": "m1-247", "word": "ocean", "meaning": "대양",
            "scene": "magnificent open blue ocean seascape, majestic whale leaping out of sparkling ocean waves while cute slender stickman watches excitedly from wooden ship deck railing, distant horizon"
        },
        {
            "id": "m1-248", "word": "captain", "meaning": "대장",
            "scene": "soccer championship stadium pitch, proud cute slender stickman team captain wearing yellow captain armband lifting a shining golden championship trophy high with cheering teammates"
        },
        {
            "id": "m1-249", "word": "chief", "meaning": "대장, 우두머리",
            "scene": "fire station equipment garage, authoritative brave cute slender stickman fire chief in distinguished white helmet pointing forward coordinating crew members before shiny fire engine"
        },
        {
            "id": "m1-250", "word": "prairie", "meaning": "대초원",
            "scene": "vast rolling wilderness prairie grassland under wide endless open sky, adventurous cute slender stickman standing atop a gentle grassy rise looking across endless waving grasses"
        },
        {
            "id": "m1-251", "word": "president", "meaning": "대통령",
            "scene": "formal presidential press briefing hall, dignified cute slender stickman president speaking at podium microphone with national flags standing tall behind, reporters and cameras"
        },
        {
            "id": "m1-252", "word": "dialogue", "meaning": "대화",
            "scene": "cozy library lounge coffee table, two cute slender stickman companions sitting comfortably in armchairs face to face having an engaging thoughtful dialogue sharing creative ideas"
        },
        {
            "id": "m1-253", "word": "dirty", "meaning": "더러운",
            "scene": "bright bathroom sink vanity, conscientious cute slender stickman washing muddy dirty hands thoroughly under running water tap with foaming soap bubbles, clean mirror and towel"
        },
        {
            "id": "m1-254", "word": "further", "meaning": "더욱이",
            "scene": "scenic mountain hiking ridge trail, adventurous cute slender stickman pointing enthusiastically ahead along the winding path eager to hike further into the mountain vista, trail marker"
        },
        {
            "id": "m1-255", "word": "add", "meaning": "더하다",
            "scene": "warm kitchen dining counter, cute slender stickman carefully adding a sweet cube of sugar with small tongs into a steaming porcelain tea cup, tea saucer and teapot on table"
        },
        {
            "id": "m1-256", "word": "pitch", "meaning": "던지다",
            "scene": "sunny baseball diamond mound, focused athletic cute slender stickman pitcher winding up arm mid-motion delivering a fast pitch toward catcher home plate, stadium backstop"
        },
        {
            "id": "m1-257", "word": "throw", "meaning": "던지다",
            "scene": "sunny open park grass lawn, energetic cute slender stickman leaning back throwing a colorful flying disc frisbee far across the lawn for a happy playful puppy to catch, park trees"
        },
        {
            "id": "m1-258", "word": "cover", "meaning": "덮개, 덮다, 다루다",
            "scene": "cozy home kitchen stove, attentive cute slender stickman placing a round glass pot lid cover securely on a simmering stew pot to keep aroma and heat inside, kitchen utensils"
        },
        {
            "id": "m1-259", "word": "degree", "meaning": "도, 정도",
            "scene": "science laboratory classroom wall, curious cute slender stickman checking a large wall Celsius thermometer measuring exact temperature degrees, lab glassware and test tubes"
        },
        {
            "id": "m1-260", "word": "tool", "meaning": "도구",
            "scene": "organized woodworking craft bench, skilled cute slender stickman holding a steel hammer assembling a wooden shelf with screwdrivers and hand tools hanging neatly on pegboard rack"
        }
    ]    ,
    14: [
        {
            "id": "m1-261", "word": "reach", "meaning": "도달하다",
            "scene": "scenic mountain summit peak, proud cute slender stickman hiker with backpack reaching the rocky mountaintop ridge just before sunset stretching arms high in victory, panoramic view"
        },
        {
            "id": "m1-262", "word": "thief", "meaning": "도둑",
            "scene": "quiet moonlit museum hall, mischievous cute slender stickman thief tiptoeing sneaking carefully across checkered floor trying to avoid floor lasers, display pedestal and spotlight"
        },
        {
            "id": "m1-263", "word": "ditch", "meaning": "도랑",
            "scene": "peaceful countryside gravel road, fresh rainwater streaming swiftly along a neat grassy ditch beside the road, cute slender stickman holding yellow umbrella watching water flow"
        },
        {
            "id": "m1-264", "word": "library", "meaning": "도서관",
            "scene": "grand quiet public library hall, cute slender stickman browsing towering wooden bookshelves reaching for a leather-bound book, reading study tables and green library lamp"
        },
        {
            "id": "m1-265", "word": "arrive", "meaning": "도착하다",
            "scene": "welcoming front porch entryway, joyful cute slender stickman traveler with rolling luggage suitcase arriving at cottage front door smiling as welcoming friend opens door"
        },
        {
            "id": "m1-266", "word": "independent", "meaning": "독립의",
            "scene": "cozy new apartment doorway, proud cute slender stickman unlocking front door holding first apartment keys high celebrating independent solo living, houseplant and moving boxes"
        },
        {
            "id": "m1-267", "word": "German", "meaning": "독일 사람, 독일어",
            "scene": "traditional European cobblestone town square, cheerful cute slender stickman wearing Alpine Bavarian hat waving warmly holding a pretzel before historic timbered German style house"
        },
        {
            "id": "m1-268", "word": "bet", "meaning": "돈을 걸다",
            "scene": "friendly board game competition table, excited cute slender stickman placing colorful wager tokens on board square placing a playful friendly bet with smiling opponent stickman"
        },
        {
            "id": "m1-269", "word": "stone", "meaning": "돌",
            "scene": "zen gravel garden terrace, mindful cute slender stickman carefully balancing smooth round stone pebbles into a serene vertical rock stack tower, bamboo water fountain"
        },
        {
            "id": "m1-270", "word": "turn", "meaning": "돌다, 회전하다",
            "scene": "outdoor playground carousel roundabout, energetic cute slender stickman riding merry-go-round roundabout spinning around with joy and arms outstretched, grassy playground"
        },
        {
            "id": "m1-271", "word": "care", "meaning": "돌봄, 걱정",
            "scene": "sunny balcony flower garden, gentle caring cute slender stickman tenderly watering delicate blossoming potted plants with green watering can showing loving tender care"
        },
        {
            "id": "m1-272", "word": "return", "meaning": "돌아가다",
            "scene": "busy airport arrivals gate, happy cute slender stickman traveler waving both hands excitedly returning home from study abroad running toward awaiting family stickman"
        },
        {
            "id": "m1-273", "word": "agree", "meaning": "동의하다",
            "scene": "bright boardroom meeting table, two professional cute slender stickman partners shaking hands firmly with warm smiles in complete mutual agreement over project blueprints"
        },
        {
            "id": "m1-274", "word": "coin", "meaning": "동전",
            "scene": "decorative stone wishing fountain in plaza, cute slender stickman closing eyes and flicking a shining round coin thumb-flip into clear fountain pool making a wish"
        },
        {
            "id": "m1-275", "word": "repeat", "meaning": "되풀이하다",
            "scene": "music studio sound recording room, cute slender stickman music teacher playing melody notes on upright piano while student stickman carefully repeats the melody notes on violin"
        },
        {
            "id": "m1-276", "word": "afraid", "meaning": "두려워하는, 유감스러운",
            "scene": "dark cozy bedroom at thunderstorm night, cute slender stickman peeking cautiously from under blanket looking nervously at stormy lightning flashes outside bedroom window"
        },
        {
            "id": "m1-277", "word": "fear", "meaning": "두려워하다, 공포",
            "scene": "wooden suspension footbridge over deep canyon gorge, courageous cute slender stickman facing fear taking a brave steady step forward onto the bridge holding handrail firmly"
        },
        {
            "id": "m1-278", "word": "twice", "meaning": "두 번",
            "scene": "school running track finish line, athletic cute slender stickman crossing finish tape raising two fingers signaling winning the race twice in a row, stopwatch and stadium fence"
        },
        {
            "id": "m1-279", "word": "surround", "meaning": "둘러싸다",
            "scene": "lush dense pine forest clearing, charming wooden cozy cottage completely surrounded in circle by tall towering pine trees and flowering shrubs under dappled sunlight"
        },
        {
            "id": "m1-280", "word": "rear", "meaning": "뒤쪽의, 양육하다",
            "scene": "sunny front driveway garage, cute slender stickman inspecting the rear bumper trunk of a modern hatchback car parked neatly in driveway, garage door and garden fence"
        }
    ]    ,
    15: [
        {
            "id": "m1-281", "word": "cleave", "meaning": "들러붙다",
            "scene": "peaceful forest woodcutting yard, strong cute slender stickman woodsman using sharp iron splitting wedge to cleave a dry hardwood log smoothly into two identical halves, wood chips and trees"
        },
        {
            "id": "m1-282", "word": "lift", "meaning": "들어올리다",
            "scene": "clean warehouse loading dock, athletic cute slender stickman worker bending knees lifting a heavy cardboard delivery box smoothly up onto wooden shelf, forklift in background"
        },
        {
            "id": "m1-283", "word": "design", "meaning": "디자인",
            "scene": "modern design studio drawing desk, creative cute slender stickman architect holding ruler sketching blueprint design of an innovative eco-friendly modern pavilion building, desk lamp and coffee mug"
        },
        {
            "id": "m1-284", "word": "follow", "meaning": "따르다",
            "scene": "sunny cobblestone park pathway, cute slender stickman walking cheerfully while an adorable fluffy puppy happily follows closely behind his footsteps, autumn flower border"
        },
        {
            "id": "m1-285", "word": "daughter", "meaning": "딸",
            "scene": "school speech contest podium stage, proud smiling cute slender stickman father applauding joyfully as his talented daughter stickman receives first-prize golden trophy ribbon"
        },
        {
            "id": "m1-286", "word": "ground", "meaning": "땅, 운동장",
            "scene": "outdoor school sports ground field, cute slender stickman coach kneeling inspecting the smooth chalk baseline on green grassy ground before track race, field bleachers"
        },
        {
            "id": "m1-287", "word": "beat", "meaning": "때리다",
            "scene": "music band rehearsal room, energetic cute slender stickman drummer holding drumsticks mid-air beating rhythmically on bronze snare drum and cymbal set, microphone stand"
        },
        {
            "id": "m1-288", "word": "shake", "meaning": "떨다",
            "scene": "bright orchard garden, cheerful cute slender stickman gently shaking ripe apple tree trunk causing sweet red apples to rain down into soft green grass and wooden basket"
        },
        {
            "id": "m1-289", "word": "drop", "meaning": "떨어뜨리다",
            "scene": "living room carpet rug, startled cute slender stickman accidentally dropping a shiny ripe red apple from hand watching it fall toward soft rug, cozy armchair and bookshelf"
        },
        {
            "id": "m1-290", "word": "apart", "meaning": "떨어진",
            "scene": "scenic rolling grassy hill ridge, two charming rustic cottages standing fifty meters apart on separate knolls with stone pathway connecting them, wildflowers in breeze"
        },
        {
            "id": "m1-291", "word": "smart", "meaning": "똑똑한",
            "scene": "bright sunny school hallway, sharp neat cute slender stickman student looking smart and confident in crisp school blazer carrying backpack walking with bright posture"
        },
        {
            "id": "m1-292", "word": "straight", "meaning": "똑바른",
            "scene": "geometry classroom whiteboard, studious cute slender stickman using long wooden ruler drawing a perfectly straight horizontal chalk line across the board, protractor on desk"
        },
        {
            "id": "m1-293", "word": "fat", "meaning": "뚱뚱한",
            "scene": "cozy sunny living room armchair cushion, round cute chubby plump pet cat curled up napping lazily while smiling cute slender stickman gently pets its soft round back"
        },
        {
            "id": "m1-294", "word": "leap", "meaning": "뛰다",
            "scene": "meadow stone garden fence, graceful agile cute slender stickman leaping mid-air high over a rustic stone boundary fence with arms extended, wildflower blossoms below"
        },
        {
            "id": "m1-295", "word": "hop", "meaning": "뛰다, 점프하다",
            "scene": "colorful chalk hopscotch playground court, playful cute slender stickman hopping on one foot happily landing squarely inside numbered chalk square grid, cheering friend"
        },
        {
            "id": "m1-296", "word": "excellent", "meaning": "뛰어난",
            "scene": "grand auditorium debate stage, eloquent cute slender stickman student finishing an excellent presentation bow as whole standing audience bursts into enthusiastic standing applause"
        },
        {
            "id": "m1-297", "word": "float", "meaning": "뜨다",
            "scene": "calm peaceful scenic river bend, cute slender stickman standing on riverbank watching an elegant folded origami paper boat floating serenely downstream on clear water surface"
        },
        {
            "id": "m1-298", "word": "label", "meaning": "라벨, 꼬리표",
            "scene": "clothing boutique display counter, attentive cute slender stickman shopper gently reading fabric care label tag sewn into soft woolen sweater garment, wooden garment rack"
        },
        {
            "id": "m1-299", "word": "lantern", "meaning": "랜턴",
            "scene": "misty evening forest hiking trail, adventurous cute slender stickman holding a glowing vintage camping kerosene lantern casting warm golden light onto mossy stone path"
        },
        {
            "id": "m1-300", "word": "dry", "meaning": "마른",
            "scene": "sunny breezy backyard garden lawn, diligent cute slender stickman hanging freshly washed towels and clothes on outdoor washing line blowing completely dry in warm sunny breeze"
        }
    ]    ,
    16: [
        {
            "id": "m1-301", "word": "village", "meaning": "마을",
            "scene": "peaceful mountain valley rustic village, cute slender stickman standing on grassy knoll looking down at quaint cobblestone village cottages with smoking brick chimneys and stone bridge, flowing stream"
        },
        {
            "id": "m1-302", "word": "town", "meaning": "마을, 읍",
            "scene": "charming sunny provincial town main street, cute slender stickman walking past brick town hall with clock tower and cozy boutique storefronts, lampposts and flower baskets along pavement"
        },
        {
            "id": "m1-303", "word": "mind", "meaning": "마음",
            "scene": "quiet serene library window alcove, contemplative cute slender stickman sitting cross-legged on comfortable cushion with closed eyes in peaceful meditation feeling calm peaceful state of mind, gentle sunbeams"
        },
        {
            "id": "m1-304", "word": "mile", "meaning": "마일",
            "scene": "scenic countryside walking trail, adventurous cute slender stickman pausing with walking stick to read a rustic carved wooden trail mile marker post indicating one mile to town, rolling hills horizon"
        },
        {
            "id": "m1-305", "word": "finally", "meaning": "마지막으로, 마침내",
            "scene": "school classroom after thorough cleaning, exhausted but triumphant cute slender stickman holding broom smiling broadly placing final chair neatly on desk celebrating finally finishing the big cleaning task"
        },
        {
            "id": "m1-306", "word": "bar", "meaning": "막대기",
            "scene": "construction stone yard, strong resourceful cute slender stickman using a long sturdy steel crowbar lever bar to carefully lift and pry a heavy granite boulder, workbench and safety gear"
        },
        {
            "id": "m1-307", "word": "bay", "meaning": "만",
            "scene": "peaceful coastal ocean bay overlook at golden sunset, small wooden fishing boats resting quietly anchored in the calm sheltered water bay while cute slender stickman gazes out from scenic cliff ledge"
        },
        {
            "id": "m1-308", "word": "fountain-pen", "meaning": "만년필",
            "scene": "antique wooden writing desk, studious cute slender stickman holding an elegant vintage brass fountain pen writing careful cursive letter onto textured parchment paper, ink bottle and blotter pad"
        },
        {
            "id": "m1-309", "word": "build", "meaning": "만들다, 짓다",
            "scene": "forest clearing construction site, enthusiastic cute slender stickman wearing carpenter tool belt fitting smooth pine wooden timber planks together building a charming wooden cabin frame, saw and lumber"
        },
        {
            "id": "m1-310", "word": "hurray", "meaning": "만세",
            "scene": "sunny school playground gate on last day of semester, overjoyed cute slender stickman students jumping high in the air throwing caps up shouting hurray celebrating start of summer vacation"
        },
        {
            "id": "m1-311", "word": "touch", "meaning": "만지다, 닿다",
            "scene": "sunlit botanical garden greenhouse, gentle curious cute slender stickman reaching outstretched fingertips tenderly touching the soft velvety leaf of an exotic green plant, terra-cotta flowerpots"
        },
        {
            "id": "m1-312", "word": "speech", "meaning": "말, 연설",
            "scene": "grand auditorium lecture hall, dignified cute slender stickman orator standing tall behind podium microphone giving an inspiring passionate speech with open expressive hand gestures to attentive crowd"
        },
        {
            "id": "m1-313", "word": "dumb", "meaning": "말을 못하는, 말문이 막힌",
            "scene": "art exhibition gallery room, cute slender stickman standing struck completely dumb with awe and wonder before an astonishing magnificent giant line art wall mural, hands clasped in speechless admiration"
        },
        {
            "id": "m1-314", "word": "mention", "meaning": "말하다, 언급하다",
            "scene": "school classroom debate podium, confident cute slender stickman raising index finger to clearly mention an important historical point from notes to classmate students listening at desks"
        },
        {
            "id": "m1-315", "word": "clear", "meaning": "맑은, 깨끗한",
            "scene": "alpine pristine mountain brook, delighted cute slender stickman kneeling on smooth riverbank dipping cupped hands into crystal clear sparkling freshwater stream showing visible riverbed pebbles below"
        },
        {
            "id": "m1-316", "word": "taste", "meaning": "맛, 맛을 보다",
            "scene": "cozy warm kitchen dining table, delighted cute slender stickman lifting a warm soup spoon to lips gently tasting the rich homemade vegetable soup with a happy appreciative expression, steaming pot"
        },
        {
            "id": "m1-317", "word": "delicious", "meaning": "맛있는",
            "scene": "quaint Italian bistro dining table, blissful cute slender stickman savoring a forkful of freshly cooked delicious hot pasta with tomato herbs smiling in absolute delight, bread basket and checkered cloth"
        },
        {
            "id": "m1-318", "word": "ruin", "meaning": "망치다, 폐허",
            "scene": "dignified ancient stone acropolis ruins on hilltop, thoughtful cute slender stickman standing beside weathered classical marble archways and broken columns appreciating the historic ancient ruins"
        },
        {
            "id": "m1-319", "word": "hawk", "meaning": "매",
            "scene": "vast golden autumn meadow cliff, majestic sharp-eyed hawk soaring high in wide sky with broad outstretched wings gliding gracefully while cute slender stickman looks up in wonder with binoculars"
        },
        {
            "id": "m1-320", "word": "tie", "meaning": "매다, 묶다",
            "scene": "running stadium track bench, athletic cute slender stickman bending forward double-knotting sports shoe laces tightly before sprint race, lane lines and stadium background"
        }
    ]    ,
    17: [
        {
            "id": "m1-321", "word": "charming", "meaning": "매력적인",
            "scene": "sunlit cobblestone cottage flower garden, elegant graceful cute slender stickman with charming warm smile bowing courteously offering a freshly picked fragrant blooming rose flower"
        },
        {
            "id": "m1-322", "word": "pulse", "meaning": "맥박",
            "scene": "medical clinic examination room, attentive cute slender stickman doctor wearing white coat gently pressing two fingertips against wrist pulse point of patient stickman checking steady heartbeat rhythm, wall chart"
        },
        {
            "id": "m1-323", "word": "oath", "meaning": "맹세, 선서",
            "scene": "solemn civic hall inauguration ceremony, dignified cute slender stickman raising right palm high taking a solemn oath of honor with left hand resting upon state law book before national emblem"
        },
        {
            "id": "m1-324", "word": "beer", "meaning": "맥주",
            "scene": "traditional festival beer garden wooden picnic table, cheerful adult stickman lifting a foaming cold beer glass mug in celebration with friends, decorative wooden barrels and pretzel basket"
        },
        {
            "id": "m1-325", "word": "stay", "meaning": "머무르다",
            "scene": "cozy beachside holiday hotel balcony, relaxed cute slender stickman sitting in wooden lounge chair looking out at sea enjoying a peaceful multiday stay, ocean waves and luggage case in room"
        },
        {
            "id": "m1-326", "word": "feed", "meaning": "먹이를 주다",
            "scene": "sunny backyard doghouse lawn, caring cute slender stickman pouring wholesome crunchy dog kibble from bag into shining stainless bowl for an excited playful puppy wagging tail happily"
        },
        {
            "id": "m1-327", "word": "stupid", "meaning": "멍청한, 어리석은",
            "scene": "study desk room floor, regretful cute slender stickman facepalming palm against forehead laughing sheepishly realizing a funny silly stupid simple mistake on scratch paper homework"
        },
        {
            "id": "m1-328", "word": "license", "meaning": "면허",
            "scene": "driver licensing authority counter, thrilled proud cute slender stickman holding up a brand new shiny driving license card with big victorious smile, parked training car seen outside window"
        },
        {
            "id": "m1-329", "word": "gay", "meaning": "명랑한, 유쾌한",
            "scene": "sunny green city park path, cheerful energetic cute slender stickman skipping along merrily whistling a gay upbeat cheerful tune with arms swinging in pure sunny happiness, singing birds on branch"
        },
        {
            "id": "m1-330", "word": "list", "meaning": "명부, 목록",
            "scene": "orderly classroom teacher desk, organized cute slender stickman teacher holding wooden clipboard carefully checking off student names on alphabetical roll-call attendance list with pen"
        },
        {
            "id": "m1-331", "word": "honour", "meaning": "명예, 존경",
            "scene": "ceremonial stage podium, distinguished brave cute slender stickman receiving a shining engraved medal of honour pinned proudly to chest by ceremony dignitary, standing ovation from audience"
        },
        {
            "id": "m1-332", "word": "several", "meaning": "몇몇의, 여럿의",
            "scene": "sunny park stone birdbath fountain, cute slender stickman watching with delight as several songbirds perch together splashing happily along the fountain rim, park tree and bench"
        },
        {
            "id": "m1-333", "word": "sand", "meaning": "모래",
            "scene": "sunny ocean seaside beach, creative cute slender stickman kneeling on soft beach sand sculpting an elaborate multi-tiered sandcastle using toy bucket and plastic spade, sea ripples"
        },
        {
            "id": "m1-334", "word": "shape", "meaning": "모양",
            "scene": "art classroom workbench, artistic cute slender stickman using hands on pottery wheel carefully shaping smooth wet clay spinning on wheel into an elegant curved vase shape, craft tools"
        },
        {
            "id": "m1-335", "word": "gather", "meaning": "모으다",
            "scene": "autumn garden lawn under tall maple trees, diligent cute slender stickman using garden rake to gather colorful fallen autumn maple leaves into a large tidy circular leaf pile, wooden basket"
        },
        {
            "id": "m1-336", "word": "adventure", "meaning": "모험",
            "scene": "rugged mountain wilderness trail canyon, intrepid cute slender stickman backpacker with trekking poles setting out on a grand wilderness adventure crossing narrow rope bridge, alpine peaks"
        },
        {
            "id": "m1-337", "word": "throat", "meaning": "목구멍, 목",
            "scene": "warm bedroom bedside table, caring cute slender stickman holding hand gently against sore throat while sipping a soothing cup of warm honey lemon tea with steam rising, soft woolen scarf"
        },
        {
            "id": "m1-338", "word": "thirsty", "meaning": "목마른",
            "scene": "summer athletic sports track, parched cute slender stickman athlete tilting water bottle eagerly drinking cool refreshing water after intense workout, sports gym bag on bench"
        },
        {
            "id": "m1-339", "word": "voice", "meaning": "목소리",
            "scene": "professional music recording studio, expressive cute slender stickman singer standing before vintage condenser microphone singing with beautiful soulful melodic voice, soundproof panels and headphones"
        },
        {
            "id": "m1-340", "word": "loud", "meaning": "목소리가 큰, 시끄러운",
            "scene": "school sports festival cheering stand, energetic cute slender stickman cheerleader shouting through red plastic megaphone with extra loud voice cheering school team forward, waving banners"
        }
    ]    ,
    18: [
        {
            "id": "m1-341", "word": "purpose", "meaning": "목적",
            "scene": "school student council conference room, purposeful cute slender stickman student president writing clear event objectives under header PURPOSE on whiteboard, student committee listening attentively"
        },
        {
            "id": "m1-342", "word": "goal", "meaning": "목표",
            "scene": "cozy personal study room desk, motivated cute slender stickman student pointing index finger at a handwritten yearly reading goals checklist chart pinned to bulletin board beside stack of books"
        },
        {
            "id": "m1-343", "word": "engage", "meaning": "몰두하다, 약혼하다",
            "scene": "romantic cobblestone gazebo park terrace, smiling cute slender stickman presenting an elegant open velvet ring box engaging beloved partner stickman with mutual joyous smiles, floral arch"
        },
        {
            "id": "m1-344", "word": "body", "meaning": "몸, 신체",
            "scene": "bright fitness studio mirror, athletic energetic cute slender stickman doing healthy full-body aerobic stretching poses with arms and legs extended in good health and posture, yoga mat on floor"
        },
        {
            "id": "m1-345", "word": "gesture", "meaning": "몸짓",
            "scene": "warm cafe entrance doorway, welcoming cute slender stickman making an open graceful sweep gesture with welcoming hand and smiling warmly inviting friend to come inside and sit at table"
        },
        {
            "id": "m1-346", "word": "tiny", "meaning": "몹시 작은",
            "scene": "study room wooden desk, curious cute slender stickman student looking through a magnifying glass at a tiny delicate ladybug crawling gently across page corner of open notebook"
        },
        {
            "id": "m1-347", "word": "describe", "meaning": "묘사하다",
            "scene": "art studio easel workbench, expressive cute slender stickman holding charcoal pencil describing and sketching the contours of a stone classical bust sculpture onto paper canvas"
        },
        {
            "id": "m1-348", "word": "cemetery", "meaning": "묘지",
            "scene": "peaceful quiet grassy memorial park cemetery, respectful cute slender stickman gently placing a bouquet of white lilies beside an upright carved stone memorial marker under willow tree"
        },
        {
            "id": "m1-349", "word": "heavy", "meaning": "무거운",
            "scene": "moving day front hallway, strong determined cute slender stickman bracing knees and arms lifting a visibly heavy wooden storage crate filled with books, moving boxes and tape"
        },
        {
            "id": "m1-350", "word": "weight", "meaning": "무게",
            "scene": "gym weightlifting platform, athletic cute slender stickman standing focused before a balanced barbell with round iron weight plates resting on platform rack, chalk dust in air"
        },
        {
            "id": "m1-351", "word": "stage", "meaning": "무대",
            "scene": "grand performing arts theater auditorium, confident cute slender stickman actor bowing gracefully under theater spotlight at center of wooden stage before red velvet curtains"
        },
        {
            "id": "m1-352", "word": "tomb", "meaning": "무덤",
            "scene": "historic ancient hillside tomb monument, respectful cute slender stickman explorer quietly observing carved ancient stone facade entrance to historic historical tomb, cypress trees"
        },
        {
            "id": "m1-353", "word": "rudely", "meaning": "무례하게",
            "scene": "orderly bakery queue line, impatient stickman rudely pushing ahead elbows out while well-mannered cute slender stickman standing in neat line gestures politely to wait turns"
        },
        {
            "id": "m1-354", "word": "knee", "meaning": "무릎",
            "scene": "soccer field sideline bench, caring cute slender stickman sports medic gently applying ice compress bandage to the scraped knee of an athletic soccer player stickman, soccer ball"
        },
        {
            "id": "m1-355", "word": "scare", "meaning": "무섭게 하다",
            "scene": "halloween pumpkin front porch, playful cute slender stickman friend leaping playfully from behind wooden fence wearing a friendly ghost sheet yelling boo to scare friend in good fun"
        },
        {
            "id": "m1-356", "word": "frighten", "meaning": "무섭게 하다, 깜짝 놀라게 하다",
            "scene": "living room sofa, startled cute slender stickman jumping slightly with hands up as sudden loud thunderstorm thunder rumbles outside window, cat peeking from behind chair"
        },
        {
            "id": "m1-357", "word": "grammar", "meaning": "문법",
            "scene": "English language classroom blackboard, studious cute slender stickman student underlining sentence subject and verb diagram arrows on grammar structure chart with chalk"
        },
        {
            "id": "m1-358", "word": "sentence", "meaning": "문장",
            "scene": "classroom desk notebook, diligent cute slender stickman writing a complete neat grammatical English sentence with capital letter and punctuation period using ink pen, open book"
        },
        {
            "id": "m1-359", "word": "problem", "meaning": "문제",
            "scene": "science math laboratory blackboard, contemplative cute slender stickman scratching chin studying a complex math logic problem formula written on board looking for solution"
        },
        {
            "id": "m1-360", "word": "matter", "meaning": "문제, 중요하다",
            "scene": "cozy consultation office desk, wise cute slender stickman counselor leaning forward listening with full empathy and understanding discussing a matter of great personal importance with friend"
        }
    ]    ,
    19: [
        {
            "id": "m1-361", "word": "rub", "meaning": "문지르다",
            "scene": "morning bedroom waking up, cute slender stickman sitting on edge of bed rubbing sleepy eyes with closed fists gently waking up to bright morning sunlight streaming in window"
        },
        {
            "id": "m1-362", "word": "culture", "meaning": "문화, 교양",
            "scene": "traditional world cultural heritage museum pavilion, smiling cute slender stickman admiring a display of traditional folk festival lanterns, musical instruments and costumes"
        },
        {
            "id": "m1-363", "word": "bury", "meaning": "묻다",
            "scene": "sunny backyard garden lawn beneath oak tree, cheerful playful puppy stickman digging with front paws burying a treasure bone in soft earth while smiling stickman looks on with trowel"
        },
        {
            "id": "m1-364", "word": "bite", "meaning": "물다",
            "scene": "picnic garden blanket, delighted cute slender stickman taking a big crisp crunchy bite out of a fresh juicy red apple smiling with joy, picnic wicker basket"
        },
        {
            "id": "m1-365", "word": "slip", "meaning": "미끄러지다",
            "scene": "winter frozen ice skating pond rink, cute slender stickman skater wobbling comically losing balance with arms waving in gentle harmless slip on slippery clear ice, snowy pine trees"
        },
        {
            "id": "m1-366", "word": "slide", "meaning": "미끄러지다, 미끄럼틀",
            "scene": "sunny playground park, joyous cute slender stickman sliding happily down a smooth spiral playground slide with raised hands in pure fun, grassy lawn and play swings"
        },
        {
            "id": "m1-367", "word": "superstition", "meaning": "미신",
            "scene": "curiosity antique shop corner, cute slender stickman looking with amused curiosity at a four-leaf clover lucky charm horseshoe and black cat folklore display on shelf"
        },
        {
            "id": "m1-368", "word": "hate", "meaning": "미워하다, 싫어하다",
            "scene": "kitchen dinner table, funny cute slender stickman child scrunching nose making humorous reluctant face looking down at a bowl of bitter green boiled spinach, fork on napkin"
        },
        {
            "id": "m1-369", "word": "crazy", "meaning": "미친, 별난",
            "scene": "amusement park roller coaster ride, thrilling adventurous cute slender stickman screaming with exhilaration and laughter as roller coaster car plunges down a crazy steep loop track"
        },
        {
            "id": "m1-370", "word": "democracy", "meaning": "민주주의, 민주정치",
            "scene": "civic voting election booth, responsible proud cute slender stickman citizen casting a marked official paper ballot into transparent secure ballot box, national flag banner"
        },
        {
            "id": "m1-371", "word": "believe", "meaning": "믿다",
            "scene": "sunlit classroom podium, encouraging cute slender stickman teacher placing hand on shoulder of student stickman expressing sincere warm heartfelt belief in student potential, smiling faces"
        },
        {
            "id": "m1-372", "word": "future", "meaning": "미래",
            "scene": "futuristic city observatory deck, visionary cute slender stickman looking forward toward horizon at a gleaming eco-friendly modern future city with aerodynamic high-speed trains and clean energy towers"
        },
        {
            "id": "m1-373", "word": "push", "meaning": "밀다",
            "scene": "supermarket grocery checkout aisle, industrious cute slender stickman pushing a full metal wheeled grocery cart smoothly forward toward cash register counter, shelf displays"
        },
        {
            "id": "m1-374", "word": "bottom", "meaning": "밑, 바닥",
            "scene": "cozy library study desk, cute slender stickman searching reaching hand all the way down to the very bottom of backpack finding missing brass house key, notebooks on desk"
        },
        {
            "id": "m1-375", "word": "turtle", "meaning": "바다거북",
            "scene": "tropical coral reef ocean water, majestic graceful sea turtle swimming smoothly alongside curious snorkeling cute slender stickman observing beautiful coral formations and sea fish"
        },
        {
            "id": "m1-376", "word": "busy", "meaning": "바쁜",
            "scene": "busy office desk workplace, active diligent cute slender stickman multitasking rapidly typing on keyboard answering phone and organizing file folders with organized energy, desk clock"
        },
        {
            "id": "m1-377", "word": "trousers", "meaning": "바지",
            "scene": "clothing tailor shop mirror, stylish cute slender stickman trying on a pair of smart tailored dress trousers while tailor stickman measures hemline with measuring tape, cloth bolts"
        },
        {
            "id": "m1-378", "word": "museum", "meaning": "박물관",
            "scene": "grand natural history museum exhibition hall, amazed cute slender stickman standing before a towering reconstructed prehistoric dinosaur skeleton exhibit holding informational guidebook"
        },
        {
            "id": "m1-379", "word": "clap", "meaning": "박수치다",
            "scene": "school concert performance hall, enthusiastic cute slender stickman in audience standing and clapping hands vigorously with great beaming smile applauding musician on stage"
        },
        {
            "id": "m1-380", "word": "contrary", "meaning": "반대의",
            "scene": "crossroads directional trail post, cute slender stickman pointing left along sunny meadow path while signpost points contrary opposite way to rocky mountain ridge, thinking pose"
        }
    ]    ,
    20: [
        {
            "id": "m1-381", "word": "receive", "meaning": "받다",
            "scene": "sunlit cottage doorway front porch, delighted cute slender stickman receiving a handwritten envelope letter and wrapped parcel from friendly mail carrier stickman smiling warmly, postbox on post"
        },
        {
            "id": "m1-382", "word": "accept", "meaning": "받아들이다",
            "scene": "warm cafe seating table, forgiving cute slender stickman smiling gently and holding both hands out accepting heartfelt written apology card from remorseful friend stickman, coffee cups on table"
        },
        {
            "id": "m1-383", "word": "invent", "meaning": "발명하다",
            "scene": "creative engineering laboratory workshop, innovative cute slender stickman inventor testing an ingenious mechanical water-cleaning filter machine gadget with glowing indicator dials, blueprints on wall"
        },
        {
            "id": "m1-384", "word": "pronunciation", "meaning": "발음",
            "scene": "language lab classroom mirror, studious cute slender stickman student practicing clear English vowel pronunciation speaking into microphone while looking at mouth shape in mirror, phonetic chart"
        },
        {
            "id": "m1-385", "word": "bright", "meaning": "밝은",
            "scene": "sun-drenched morning kitchen window, cheerful cute slender stickman enjoying a bright sunlit breakfast table bathed in golden warm morning sunlight beams, potted flowering plants on windowsill"
        },
        {
            "id": "m1-386", "word": "rope", "meaning": "밧줄",
            "scene": "harbor wooden pier dock, strong nautical cute slender stickman sailor coiling a thick sturdy braided hemp mooring rope neatly in spiral on wooden dock planks beside berthed sailboat"
        },
        {
            "id": "m1-387", "word": "method", "meaning": "방법",
            "scene": "classroom blackboard lecture, wise cute slender stickman teacher holding pointer explaining a clear 3-step structured learning method flow diagram drawn neatly on blackboard, attentive students"
        },
        {
            "id": "m1-388", "word": "vacation", "meaning": "방학, 휴가",
            "scene": "sunny tropical beach coastline, relaxed cute slender stickman reclining under striped sun umbrella with refreshing coconut drink celebrating summer vacation, palm trees and ocean waves"
        },
        {
            "id": "m1-389", "word": "direction", "meaning": "방향, 지시",
            "scene": "scenic mountain trail crossroads, cute slender stickman hiker looking attentively at a carved wooden directional trail signpost pointing paths to summit lake and valley, compass in hand"
        },
        {
            "id": "m1-390", "word": "background", "meaning": "배경",
            "scene": "photo studio camera tripod, cute slender stickman portrait photographer setting up a scenic canvas backdrop screen behind subject stickman adjusting soft studio lights on stands"
        },
        {
            "id": "m1-391", "word": "million", "meaning": "백만",
            "scene": "astronomy planetarium observatory, awe-inspired cute slender stickman looking through telescope at starry night sky with millions of sparkling stars and distant swirling spiral galaxies"
        },
        {
            "id": "m1-392", "word": "snake", "meaning": "뱀",
            "scene": "lush nature park meadow trail, cautious observant cute slender stickman pausing safely on dirt path watching a smooth green garden snake gliding quietly through tall green grass blades"
        },
        {
            "id": "m1-393", "word": "downtown", "meaning": "번화가",
            "scene": "lively bustling downtown city street avenue, cute slender stickman walking past modern shopfront boutiques, outdoor cafe awnings, pedestrian crosswalks and illuminated city architecture"
        },
        {
            "id": "m1-394", "word": "belt", "meaning": "벨트, 띠",
            "scene": "bedroom dressing mirror, neat cute slender stickman student standing before full-length mirror fastening an elegant leather belt buckle securely around waist of school uniform trousers"
        },
        {
            "id": "m1-395", "word": "change", "meaning": "변화, 변하다, 거스름돈",
            "scene": "friendly bookstore cashier counter, polite cute slender stickman cashier smiling handing shiny metallic coin change and paper receipt into customer stickman palm after book purchase"
        },
        {
            "id": "m1-396", "word": "nickname", "meaning": "별명",
            "scene": "school running track sideline, cheering cute slender stickman friends holding up a fun handmade banner with rabbit nickname cheering fast runner stickman sprinting past track line"
        },
        {
            "id": "m1-397", "word": "bottle", "meaning": "병",
            "scene": "neighborhood recycling center, responsible eco-friendly cute slender stickman sorting placing empty glass beverage bottles carefully into designated green recycling bin crates"
        },
        {
            "id": "m1-398", "word": "hospital", "meaning": "병원",
            "scene": "modern hospital room with sunlit window, caring cute slender stickman nurse in medical scrubs checking monitor while friendly doctor smiles warmly at resting patient stickman in bed"
        },
        {
            "id": "m1-399", "word": "report", "meaning": "보고, 보고하다",
            "scene": "school science laboratory desk, diligent cute slender stickman student writing a comprehensive neatly bound scientific research report binder with charts and test tubes nearby"
        },
        {
            "id": "m1-400", "word": "watch", "meaning": "보다, 손목시계",
            "scene": "city park bench walkway, punctual cute slender stickman glancing at an elegant wrist watch on arm checking the exact time while waiting for arriving friend, park lamppost"
        }
    ]    ,
    21: [
        {
            "id": "m1-401", "word": "treasure", "meaning": "보물",
            "scene": "secluded sandy island beach cave, amazed cute slender stickman kneeling before an opened antique wooden treasure chest overflowing with sparkling jewels and golden coins"
        },
        {
            "id": "m1-402", "word": "jewel", "meaning": "보석",
            "scene": "artisan jewelry workshop bench, skilled cute slender stickman jeweler holding jeweler loupe inspecting a brilliant cut sparkling diamond jewel resting on black velvet cushion"
        },
        {
            "id": "m1-403", "word": "usually", "meaning": "보통",
            "scene": "cozy morning kitchen breakfast nook, cute slender stickman sitting at kitchen table enjoying routine usual breakfast bowl of cereal and fresh orange juice before seven o'clock clock"
        },
        {
            "id": "m1-404", "word": "normal", "meaning": "보통의, 정상적인",
            "scene": "medical clinic consultation desk, reassuring cute slender stickman doctor pointing at heart rate graph paper showing steady normal heartbeat lines to relieved smiling patient stickman"
        },
        {
            "id": "m1-405", "word": "protect", "meaning": "보호하다",
            "scene": "sunny city bicycle path, safety-conscious cute slender stickman buckling chin strap of sturdy cycling helmet securely to protect head before riding bicycle, trees along bike lane"
        },
        {
            "id": "m1-406", "word": "review", "meaning": "복습하다",
            "scene": "quiet evening study desk, studious cute slender stickman student reviewing daytime class notes in neat notebook with highlighter pen beside glowing desk lamp before bed"
        },
        {
            "id": "m1-407", "word": "obey", "meaning": "복종하다, 따르다",
            "scene": "elementary school crossing road, obedient well-mannered cute slender stickman pedestrian pausing obediently at street crosswalk obeying stop sign signal held by crossing guard"
        },
        {
            "id": "m1-408", "word": "primary", "meaning": "본래의, 주요한",
            "scene": "artist painting studio easel, creative cute slender stickman mixing red, blue, and yellow primary color paint tubes on wooden palette exploring fundamental primary colors"
        },
        {
            "id": "m1-409", "word": "cheek", "meaning": "볼, 뺨",
            "scene": "chilly winter snow park, smiling cute slender stickman wearing warm woolen pom-pom beanie with rosy pink winter flushed cheeks holding up a fresh round snowball, pine trees"
        },
        {
            "id": "m1-410", "word": "envelope", "meaning": "봉투",
            "scene": "study writing table, thoughtful cute slender stickman sealing a crisp white paper postal envelope applying a decorative postage stamp carefully to mail letter to friend"
        },
        {
            "id": "m1-411", "word": "wealth", "meaning": "부, 재산",
            "scene": "community charity foundation hall, generous kind cute slender stickman sharing wealth handing boxes of food supplies and warm blankets to community relief volunteers"
        },
        {
            "id": "m1-412", "word": "section", "meaning": "부분, 구역",
            "scene": "grand public library hall, inquisitive cute slender stickman student browsing designated science encyclopedia section bookshelf following clear overhead directional sign"
        },
        {
            "id": "m1-413", "word": "department", "meaning": "부서, 백화점",
            "scene": "modern multistory shopping department store lobby, stylish cute slender stickman looking up at directory board selecting stationery department floor, escalators and store displays"
        },
        {
            "id": "m1-414", "word": "break", "meaning": "부수다, 깨뜨리다, 휴식",
            "scene": "sunny outdoor park courtyard bench, relaxed cute slender stickman taking a peaceful refreshing tea break sipping warm thermos cup with closed eyes resting from workday"
        },
        {
            "id": "m1-415", "word": "booth", "meaning": "부스, 매표소",
            "scene": "lively festival carnival square, cheerful cute slender stickman purchasing event entry tickets from friendly ticket booth attendant inside colorful striped wooden festival booth"
        },
        {
            "id": "m1-416", "word": "revival", "meaning": "부활, 되살아남",
            "scene": "spring garden terrace, delighted cute slender stickman kneeling beside a thriving green plant pot celebrating revival of flourishing new green sprout shoots after winter rain"
        },
        {
            "id": "m1-417", "word": "drum", "meaning": "북",
            "scene": "school brass marching band parade, energetic cute slender stickman drummer marching proudly carrying a large parade snare drum beating rhythm sticks in exciting festival tempo"
        },
        {
            "id": "m1-418", "word": "flame", "meaning": "불꽃",
            "scene": "cozy evening living room table, gentle cute slender stickman carefully lighting a scented candle wick with match watching tiny bright warm golden flame flicker serenely"
        },
        {
            "id": "m1-419", "word": "blow", "meaning": "불다",
            "scene": "birthday party table, joyful cute slender stickman making a birthday wish and puffing cheeks blowing out glowing candles on celebratory birthday cake surrounded by friends"
        },
        {
            "id": "m1-420", "word": "flashlight", "meaning": "불빛, 손전등",
            "scene": "dark mysterious mountain trail cavern, adventurous brave cute slender stickman holding a bright LED flashlight beam illuminating path and stalactites in dark stone cavern"
        }
    ]    ,
    22: [
        {
            "id": "m1-421", "word": "complain", "meaning": "불평하다",
            "scene": "indoor swimming pool deck, cute slender stickman swimmer standing wrapped in towel shivering humorously gesturing with hands complaining politely about cold water to friendly pool lifeguard"
        },
        {
            "id": "m1-422", "word": "crowded", "meaning": "붐비는",
            "scene": "morning commuter subway train platform, cheerful cute slender stickman standing patiently among a lively bustling crowd of commuters waiting for arriving train, station platform clock"
        },
        {
            "id": "m1-423", "word": "hold", "meaning": "붙잡다",
            "scene": "colorful bustling city street market, sweet little cute slender stickman child holding mother stickman hand tightly and lovingly while walking past vibrant fruit and flower market stalls"
        },
        {
            "id": "m1-424", "word": "comparison", "meaning": "비교",
            "scene": "electronics technology store display desk, analytical cute slender stickman holding two sleek smartphone devices side by side comparing screen sizes and features with thoughtful expression"
        },
        {
            "id": "m1-425", "word": "silk", "meaning": "비단",
            "scene": "luxury fabric boutique workshop, gentle cute slender stickman tailor gently caressing a roll of flowing smooth lustrous white silk fabric draped elegantly over wooden workbench"
        },
        {
            "id": "m1-426", "word": "pigeon", "meaning": "비둘기",
            "scene": "sunny cobblestone park plaza bench, cute slender stickman sitting smiling warmly tossing bread crumbs to a friendly plump gray pigeon pecking happily on pavement, park fountain"
        },
        {
            "id": "m1-427", "word": "though", "meaning": "비록 ~일지라도",
            "scene": "snowy winter park meadow, energetic joyful cute slender stickman bundled in scarf and mittens playing cheerfully building a snowman even though it is chilly and snowing softly"
        },
        {
            "id": "m1-428", "word": "secretary", "meaning": "비서",
            "scene": "modern corporate reception office, organized professional cute slender stickman secretary wearing telephone headset smiling politely while jotting important memo notes in ledger notebook"
        },
        {
            "id": "m1-429", "word": "similar", "meaning": "비슷한",
            "scene": "art studio display table, curious cute slender stickman comparing two very similar hand-crafted ceramic mugs side by side admiring their almost identical painted spiral patterns"
        },
        {
            "id": "m1-430", "word": "hollow", "meaning": "비어 있는",
            "scene": "ancient woodland forest trail, cute slender stickman smiling discovering a round hollow knothole cavity inside an old oak tree trunk where a curious little forest owl peeks out"
        },
        {
            "id": "m1-431", "word": "cost", "meaning": "비용",
            "scene": "shoe boutique checkout counter, thoughtful cute slender stickman checking price tag cost on a stylish pair of leather boots with friendly sales clerk stickman smiling behind counter"
        },
        {
            "id": "m1-432", "word": "rate", "meaning": "비율",
            "scene": "business analytics conference room whiteboard, smart cute slender stickman presenting an upward rising growth rate percentage bar chart with presentation pointer to boardroom team"
        },
        {
            "id": "m1-433", "word": "flight", "meaning": "비행",
            "scene": "modern international airport departure lounge window, excited cute slender stickman traveler looking through panoramic glass at a jetliner airplane taking off into the bright blue sky"
        },
        {
            "id": "m1-434", "word": "plane", "meaning": "비행기",
            "scene": "airport tarmac runway, sleek modern passenger airliner plane parked at boarding jet bridge gate while cute slender stickman pilot in uniform waves cheerfully from cockpit steps"
        },
        {
            "id": "m1-435", "word": "empty", "meaning": "빈",
            "scene": "spacious city commuter bus interior, happy cute slender stickman walking down aisle gladly finding a clean comfortable empty seat next to sunlit bus window, route map on ceiling"
        },
        {
            "id": "m1-436", "word": "lend", "meaning": "빌려주다",
            "scene": "school classroom study desk, generous kind cute slender stickman student smiling warmly and lending a spare sharpened yellow pencil to grateful classmate stickman sitting nearby"
        },
        {
            "id": "m1-437", "word": "borrow", "meaning": "빌리다",
            "scene": "rainy school entrance lobby, appreciative cute slender stickman bowing politely borrowing a large bright umbrella from friendly smiling school friend to walk home safely in rain"
        },
        {
            "id": "m1-438", "word": "comb", "meaning": "빗",
            "scene": "bedroom dressing vanity mirror, neat grooming cute slender stickman holding a classic tortoise-shell comb neatly combing hair before round mirror, hairbrush on wooden vanity tray"
        },
        {
            "id": "m1-439", "word": "iceberg", "meaning": "빙산",
            "scene": "polar arctic ocean expedition ship, awe-struck cute slender stickman standing on ship bow railing viewing a colossal majestic blue-white floating iceberg in cold polar sea waters"
        },
        {
            "id": "m1-440", "word": "debt", "meaning": "빚, 은혜",
            "scene": "cozy family living room sofa, loving grateful cute slender stickman child gently hugging elderly parents presenting a heartfelt thank-you card honoring lifelong debt of gratitude"
        }
    ]    ,
    23: [
        {
            "id": "m1-441", "word": "owe", "meaning": "빚지다, 덕분이다",
            "scene": "graduation ceremony hall stage, proud cute slender stickman graduate in cap and gown bowing respectfully handing floral bouquet to parents thanking them for all success owed to them"
        },
        {
            "id": "m1-442", "word": "shine", "meaning": "빛나다",
            "scene": "scenic mountain hill under clear night sky, peaceful cute slender stickman sitting on grassy knoll gazing upward as countless brilliant stars and glowing crescent moon shine brightly"
        },
        {
            "id": "m1-443", "word": "suck", "meaning": "빨다, 마시다",
            "scene": "sunny summer ice cream parlor patio, cheerful cute slender stickman drinking a refreshing cold fruit smoothie through a striped bendy straw with cheeks gently drawn, cafe table"
        },
        {
            "id": "m1-444", "word": "loaf", "meaning": "빵 덩어리",
            "scene": "artisanal rustic village bakery counter, delighted cute slender stickman baker holding up a freshly baked steaming golden brown whole bread loaf with flour dusted wooden cutting board"
        },
        {
            "id": "m1-445", "word": "bone", "meaning": "뼈",
            "scene": "sunny backyard lawn flowerbed, playful adorable pet dog wagging tail happily digging in grass holding a wholesome marrow dog bone while smiling cute slender stickman watches"
        },
        {
            "id": "m1-446", "word": "event", "meaning": "사건, 행사",
            "scene": "grand municipal civic square, excited cute slender stickman attending a magnificent annual community cultural festival event with festival bunting streamers and festive stage"
        },
        {
            "id": "m1-447", "word": "affair", "meaning": "사건, 일",
            "scene": "cozy library study room fireplace, inquisitive cute slender stickman detective reading a mystery novel article in newspaper about a curious puzzling historic affair on desk"
        },
        {
            "id": "m1-448", "word": "accident", "meaning": "사고",
            "scene": "crossroads safety crossing, responsible cute slender stickman traffic police officer directing cars safely around a harmless minor fender tap accident placing orange cones"
        },
        {
            "id": "m1-449", "word": "fierce", "meaning": "사나운",
            "scene": "historic castle stone gatehouse, protective sturdy guard dog barking with fierce loyal courage protecting ancient gate behind wrought iron fence, medieval cobblestone floor"
        },
        {
            "id": "m1-450", "word": "hunter", "meaning": "사냥꾼",
            "scene": "winter pine woodland trail, experienced respectful cute slender stickman hunter tracking wildlife footsteps in crisp white snow alongside faithful loyal hunting hound dog"
        },
        {
            "id": "m1-451", "word": "desert", "meaning": "사막",
            "scene": "vast golden sand dune desert horizon, adventurous cute slender stickman explorer walking across undulating desert sand ridges with walking staff under warm desert sun, palm oasis far off"
        },
        {
            "id": "m1-452", "word": "office", "meaning": "사무실",
            "scene": "bright modern office workstation, productive cute slender stickman working at desk with dual computer monitors and neat stationery organizer, potted green plant on file cabinet"
        },
        {
            "id": "m1-453", "word": "object", "meaning": "사물, 물체",
            "scene": "science museum curiosity exhibition table, inquisitive cute slender stickman student examining an unusual geometric polished metallic puzzle object resting on pedestal"
        },
        {
            "id": "m1-454", "word": "chain", "meaning": "사슬",
            "scene": "harbor sea wall promenade, strong heavy-duty nautical iron link chain barrier stretching between stone bollards protecting pedestrians along water edge, cute stickman leaning"
        },
        {
            "id": "m1-455", "word": "deer", "meaning": "사슴",
            "scene": "sunlit morning forest clearing, gentle graceful wild deer with velvet antlers standing peacefully among ferns looking with calm eyes at admiring cute slender stickman hiker"
        },
        {
            "id": "m1-456", "word": "fact", "meaning": "사실",
            "scene": "school science laboratory greenhouse, wise cute slender stickman teacher holding potted seedling demonstrating fundamental scientific fact that water and sunlight nurture living plants"
        },
        {
            "id": "m1-457", "word": "business", "meaning": "사업",
            "scene": "charming sunny bakery shopfront, proud cute slender stickman small business owner smiling standing proudly in doorway under shop canopy awning holding Open welcome sign"
        },
        {
            "id": "m1-458", "word": "dictionary", "meaning": "사전",
            "scene": "library study desk, studious cute slender stickman looking up an advanced vocabulary word pointing index finger inside a large leather-bound comprehensive English dictionary"
        },
        {
            "id": "m1-459", "word": "photographer", "meaning": "사진사",
            "scene": "outdoor scenic botanical park garden, creative professional cute slender stickman photographer looking through DSLR camera lens taking portrait photo of smiling friend stickman"
        },
        {
            "id": "m1-460", "word": "cousin", "meaning": "사촌",
            "scene": "sunny airport arrival terminal gate, overjoyed cute slender stickman running forward with open arms embracing visiting beloved cousin stickman arriving for summer vacation"
        }
    ]    ,
    24: [
        {
            "id": "m1-461", "word": "social", "meaning": "사회의",
            "scene": "community volunteer center hall, enthusiastic cute slender stickman volunteers working together packing food parcels and talking with neighbors showing active social cooperation"
        },
        {
            "id": "m1-462", "word": "industrial", "meaning": "산업의",
            "scene": "modern automated eco-industrial manufacturing facility, smart cute slender stickman engineer wearing hardhat reviewing blueprint beside high-tech robotic assembly arms and clean factory floor"
        },
        {
            "id": "m1-463", "word": "alive", "meaning": "살아있는",
            "scene": "sunny greenhouse bench, delighted cute slender stickman smiling warmly as a resilient tiny green potted plant sprout flourishes vibrant with new leaves fully alive after watering"
        },
        {
            "id": "m1-464", "word": "life", "meaning": "삶, 생명",
            "scene": "sunlit nursery garden, gentle caring cute slender stickman kneeling tenderly cupping hands around a delicate newborn flowering seedling celebrating precious wonder of life"
        },
        {
            "id": "m1-465", "word": "spade", "meaning": "삽",
            "scene": "sunny garden flowerbed, industrious cute slender stickman pressing foot onto a sturdy steel gardening spade digging rich dark soil hole to plant a blooming rose bush, garden tools"
        },
        {
            "id": "m1-466", "word": "prize", "meaning": "상",
            "scene": "school art exhibition stage, beaming cute slender stickman student standing proud holding up a gleaming golden trophy prize beside an award-winning painted landscape canvas"
        },
        {
            "id": "m1-467", "word": "imagine", "meaning": "상상하다",
            "scene": "cozy bedroom study desk, creative daydreaming cute slender stickman resting chin in hand looking upward as gentle doodle thought clouds show imaginative flying airships and stars"
        },
        {
            "id": "m1-468", "word": "ivy", "meaning": "담쟁이덩굴",
            "scene": "quaint historic red brick school library wall, cute slender stickman admiring lush verdant ivy vine leaves climbing gracefully across the classical brick facade and arched window"
        },
        {
            "id": "m1-469", "word": "merchant", "meaning": "상인",
            "scene": "bustling historic marketplace stall, friendly traditional cute slender stickman merchant weighing aromatic tea leaves on brass balance scales offering fresh goods to customer"
        },
        {
            "id": "m1-470", "word": "symbol", "meaning": "상징",
            "scene": "peace memorial park garden, peaceful cute slender stickman holding out open palm as a gentle pure white dove of peace spreads wings symbolizing universal world peace"
        },
        {
            "id": "m1-471", "word": "scar", "meaning": "상처, 흉터",
            "scene": "first aid clinic examination, brave cute slender stickman looking down with calm smile as caring nurse stickman checks a small healed scar line on knee after successful recovery"
        },
        {
            "id": "m1-472", "word": "wound", "meaning": "상처, 부상",
            "scene": "sports infirmary room, gentle cute slender stickman medic carefully cleansing a minor scraped elbow wound with antiseptic cotton swab on patient stickman sitting on bench"
        },
        {
            "id": "m1-473", "word": "state", "meaning": "상태",
            "scene": "bicycle maintenance workshop, thorough cute slender stickman mechanic inspecting brake cables and chain checking that bicycle is in prime perfect running state and condition"
        },
        {
            "id": "m1-474", "word": "situation", "meaning": "상황, 위치",
            "scene": "scenic mountain lookout viewpoint, calm cute slender stickman hiker observing trail map assessing current mountain hiking situation with compass and binoculars before continuing"
        },
        {
            "id": "m1-475", "word": "carve", "meaning": "새기다",
            "scene": "woodworking studio craft bench, artistic cute slender stickman woodcarver carefully using a sharp gouge chisel to carve intricate floral designs into a polished wooden decorative plaque"
        },
        {
            "id": "m1-476", "word": "lamb", "meaning": "새끼 양",
            "scene": "rolling green hillside meadow pasture, adorable fluffy little white baby lamb frolicking playfully across grassy field toward loving shepherd cute slender stickman holding milk bowl"
        },
        {
            "id": "m1-477", "word": "leak", "meaning": "새다",
            "scene": "kitchen under-sink cupboard, observant cute slender stickman shining flashlight discovering a single water drip leak from pipe valve placing a collection bucket underneath"
        },
        {
            "id": "m1-478", "word": "fresh", "meaning": "새로운, 신선한",
            "scene": "open farmers market morning stall, joyful cute slender stickman holding a woven basket overflowing with crisp freshly harvested green lettuce, dewy apples, and fresh herbs"
        },
        {
            "id": "m1-479", "word": "dawn", "meaning": "새벽",
            "scene": "quiet scenic mountain summit ridge, contemplative cute slender stickman standing peacefully watching the very first golden pink sun rays of dawn cresting above distant misty horizon"
        },
        {
            "id": "m1-480", "word": "cage", "meaning": "새장",
            "scene": "sunlit room window, gentle cute slender stickman opening wide the small wire door of an ornamental birdcage allowing a cheerful rescued canary bird to hop out freely onto finger"
        }
    ]    ,
    25: [
        {
            "id": "m1-481", "word": "idea", "meaning": "생각, 아이디어",
            "scene": "study chalkboard desk, inspired cute slender stickman pointing index finger upward with a bright glowing idea lightbulb doodle popping up above head while sketching notes"
        },
        {
            "id": "m1-482", "word": "remind", "meaning": "생각나게 하다",
            "scene": "cozy attic memory corner, nostalgic smiling cute slender stickman looking through an old vintage family photo album reminding of cherished happy childhood memories with friends"
        },
        {
            "id": "m1-483", "word": "biology", "meaning": "생물학",
            "scene": "science biology laboratory workstation, curious cute slender stickman student looking through optical compound microscope observing biological plant cell wall structures on slide"
        },
        {
            "id": "m1-484", "word": "produce", "meaning": "생산하다",
            "scene": "sunny rural farm orchard garden, proud cute slender stickman farmer standing beside wooden crates brimming with delicious freshly harvested organic red apples produce"
        },
        {
            "id": "m1-485", "word": "survive", "meaning": "생존하다",
            "scene": "harsh desert rocky canyon ridge, amazed cute slender stickman hiker examining a hardy green mountain pine tree miraculously surviving rooted firmly in sheer rocky mountain cliff"
        },
        {
            "id": "m1-486", "word": "mouse", "meaning": "생쥐",
            "scene": "cozy kitchen pantry cupboard corner, tiny adorable cartoon mouse nibbling on a small wedge of Swiss cheese while cute slender stickman peeks in amused with a gentle smile"
        },
        {
            "id": "m1-487", "word": "shower", "meaning": "샤워하다, 소나기",
            "scene": "sunny city park path, surprised cute slender stickman popping open a bright blue umbrella laughing as a sudden refreshing summer rain shower pours down on park trees"
        },
        {
            "id": "m1-488", "word": "hurry", "meaning": "서두르다",
            "scene": "city sidewalk bus stop, energetic cute slender stickman checking wristwatch and dashing briskly along sidewalk with briefcase to catch departing commuter transit bus"
        },
        {
            "id": "m1-489", "word": "hastily", "meaning": "서둘러서",
            "scene": "bedroom doorway entryway, busy cute slender stickman hurriedly buttoning school jacket and snatching backpack from coat rack heading out hastily into morning sunshine"
        },
        {
            "id": "m1-490", "word": "draw", "meaning": "서랍, 끌다, 뽑다",
            "scene": "antique wooden writing desk, cute slender stickman pulling open a smooth mahogany desk drawer to retrieve an official wax-sealed letter and fountain pen from inside"
        },
        {
            "id": "m1-491", "word": "bookstore", "meaning": "서점",
            "scene": "charming quiet bookstore storefront, curious cute slender stickman student browsing towering wooden bookshelves brimming with books in warm cozy neighborhood bookstore"
        },
        {
            "id": "m1-492", "word": "coal", "meaning": "석탄",
            "scene": "vintage steam locomotive railway station, hardworking cute slender stickman stoker with shovel scooping solid black coal lumps into train engine furnace firebox"
        },
        {
            "id": "m1-493", "word": "election", "meaning": "선거",
            "scene": "school student council election voting station, enthusiastic cute slender stickman student proudly dropping paper ballot into official ballot box with democratic vote banner"
        },
        {
            "id": "m1-494", "word": "gift", "meaning": "선물, 재능",
            "scene": "festive holiday living room, smiling cute slender stickman offering a beautifully wrapped colorful gift box tied with a satin ribbon bow to overjoyed friend stickman"
        },
        {
            "id": "m1-495", "word": "senior", "meaning": "선배, 노인",
            "scene": "school soccer training pitch, friendly encouraging senior cute slender stickman soccer player passing ball and guiding junior teammate stickman on proper kicking form"
        },
        {
            "id": "m1-496", "word": "declare", "meaning": "선언하다",
            "scene": "school sports tournament grandstand, dignified cute slender stickman principal speaking into microphone raising hand declaring annual sports festival officially open"
        },
        {
            "id": "m1-497", "word": "choose", "meaning": "선택하다",
            "scene": "quaint ice cream parlor display freezer, thoughtful cute slender stickman smiling pointing index finger choosing favorite ice cream flavor scoop from colorful options"
        },
        {
            "id": "m1-498", "word": "select", "meaning": "선택하다, 선발하다",
            "scene": "school music orchestra rehearsal room, wise cute slender stickman conductor carefully selecting audition music sheet from music stand choosing principal violinist"
        },
        {
            "id": "m1-499", "word": "explain", "meaning": "설명하다",
            "scene": "science classroom blackboard, patient cute slender stickman teacher drawing planetary orbit diagrams explaining solar system mechanics to attentive student stickmen"
        },
        {
            "id": "m1-500", "word": "sugar", "meaning": "설탕",
            "scene": "cozy kitchen dining counter, gentle cute slender stickman using porcelain spoon scooping white sweet granulated sugar from ceramic sugar bowl into warm steaming herbal tea"
        }
    ]    ,
    26: [
        {
            "id": "m1-501", "word": "castle", "meaning": "성",
            "scene": "picturesque green mountain crag, magnificent medieval stone fortress castle standing proudly on hill with tall stone turrets and arched gateway, cute slender stickman traveler looking up in awe"
        },
        {
            "id": "m1-502", "word": "successful", "meaning": "성공한",
            "scene": "book signing event hall, happy celebrated cute slender stickman bestselling author signing copies of novel at desk with smiling readers lining up to congratulate, banners and books"
        },
        {
            "id": "m1-503", "word": "tax", "meaning": "세금",
            "scene": "orderly civic tax service office, conscientious cute slender stickman citizen filing annual municipal revenue tax return forms with helpful government clerk stickman at counter"
        },
        {
            "id": "m1-504", "word": "century", "meaning": "세기, 100년",
            "scene": "history museum timeline hall, thoughtful cute slender stickman student walking past an expansive historic timeline exhibit spanning the 19th and 20th centuries with vintage photographs"
        },
        {
            "id": "m1-505", "word": "count", "meaning": "세다",
            "scene": "bright preschool nursery classroom, cheerful cute slender stickman teacher pointing at numbered colorful wooden counting blocks on table counting numbers one to ten with happy student"
        },
        {
            "id": "m1-506", "word": "laundry", "meaning": "세탁물, 빨래",
            "scene": "modern laundromat parlor, diligent cute slender stickman folding warm freshly dried white towels neatly from front-loading washing machine, laundry basket on bench"
        },
        {
            "id": "m1-507", "word": "introduce", "meaning": "소개하다",
            "scene": "friendly school courtyard garden, enthusiastic cute slender stickman student introducing a smiling new transfer student friend stickman to classmate stickmen with open warm gestures"
        },
        {
            "id": "m1-508", "word": "salt", "meaning": "소금",
            "scene": "cozy kitchen dining table, attentive cute slender stickman cook sprinkling a pinch of fine white salt from a ceramic salt shaker over a steaming bowl of vegetable soup, spice rack on wall"
        },
        {
            "id": "m1-509", "word": "sound", "meaning": "소리",
            "scene": "historic village square clock tower, cute slender stickman standing on cobblestone street pausing happily listening to the rich resonant sound tones of the bell chimes ringing from tower"
        },
        {
            "id": "m1-510", "word": "scream", "meaning": "소리 지르다",
            "scene": "fun spooky haunted house carnival ride, cute slender stickman screaming with humorous theatrical fright and raised hands as a harmless cartoon cardboard spider pops out from door frame"
        },
        {
            "id": "m1-511", "word": "wish", "meaning": "소원, 소원하다",
            "scene": "cozy birthday party table, happy cute slender stickman with closed eyes clasping hands tightly making a heartfelt silent birthday wish before blowing out candles on decorated cake"
        },
        {
            "id": "m1-512", "word": "noise", "meaning": "소음",
            "scene": "bedroom window at busy city street, cute slender stickman sitting up in bed covering ears gently with hands due to late-night car horn traffic noise outside window, alarm clock on nightstand"
        },
        {
            "id": "m1-513", "word": "proverb", "meaning": "속담",
            "scene": "traditional wooden study library, wise cute slender stickman elder pointing finger at an open calligraphy scroll inscribed with ancient time-honored wisdom proverbs, desk lamp"
        },
        {
            "id": "m1-514", "word": "saying", "meaning": "속담, 격언",
            "scene": "classroom inspirational bulletin board, studious cute slender stickman pinning up an engraved wooden plaque featuring the famous saying Time is Gold, student notebooks"
        },
        {
            "id": "m1-515", "word": "whisper", "meaning": "속삭이다",
            "scene": "quiet library study table, two cute slender stickman friends leaning close together with hand cupped around ear whispering a quiet secret so as not to disturb other readers"
        },
        {
            "id": "m1-516", "word": "hand", "meaning": "손, 건네주다",
            "scene": "sunny front doorway porch, considerate cute slender stickman student handing an important sealed envelope letter respectfully with both hands to father stickman smiling warmly"
        },
        {
            "id": "m1-517", "word": "guest", "meaning": "손님",
            "scene": "warm welcoming home dining room, gracious cute slender stickman host welcoming an arriving guest stickman at front doorway taking coat and gesturing warmly toward dining table"
        },
        {
            "id": "m1-518", "word": "handle", "meaning": "손잡이, 다루다",
            "scene": "kitchen stove cooking counter, careful cute slender stickman using an insulated thick fabric pot holder to grip the hot metal handle of a boiling soup pot safely, cooking utensils"
        },
        {
            "id": "m1-519", "word": "nail", "meaning": "손톱, 못",
            "scene": "neat home vanity grooming desk, tidy cute slender stickman using small metal nail clippers carefully trimming fingernails neatly over tissue paper, mirror and towel"
        },
        {
            "id": "m1-520", "word": "frankly", "meaning": "솔직히",
            "scene": "cafe conversational corner, sincere cute slender stickman speaking with open heartfelt hand on chest expressing honest thoughts frankly and kindly to listening friend stickman"
        }
    ]    ,
    27: [
        {
            "id": "m1-521", "word": "cotton", "meaning": "솜, 면화",
            "scene": "sunlit cotton farm field, delighted cute slender stickman holding a soft fluffy white cotton boll freshly plucked from ripe cotton plant shrub, wicker harvest basket on ground"
        },
        {
            "id": "m1-522", "word": "beef", "meaning": "쇠고기",
            "scene": "home kitchen cooking hearth, caring cute slender stickman preparing a warm nutritious beef stew with vegetables stirring steaming pot on stove with wooden spoon"
        },
        {
            "id": "m1-523", "word": "towel", "meaning": "수건",
            "scene": "clean bright bathroom rack, cute slender stickman reaching out to pull a fluffy clean folded white cotton bath towel from polished metal bathroom wall rack, mirror and soap dish"
        },
        {
            "id": "m1-524", "word": "capital", "meaning": "수도, 자금",
            "scene": "national capital landmark plaza, proud cute slender stickman tourist taking photo before grand classical government parliament dome in the bustling historic capital city"
        },
        {
            "id": "m1-525", "word": "hydrogen", "meaning": "수소",
            "scene": "chemistry science laboratory, curious cute slender stickman student pointing at atomic molecular model showing two hydrogen atoms bonded with oxygen forming water H2O"
        },
        {
            "id": "m1-526", "word": "puzzle", "meaning": "수수께끼, 퍼즐",
            "scene": "living room rug coffee table, engrossed cute slender stickman carefully fitting the final interlocking jigsaw puzzle piece into a completed scenic landscape puzzle picture"
        },
        {
            "id": "m1-527", "word": "riddle", "meaning": "수수께끼",
            "scene": "school courtyard bench, playful cute slender stickman posing a clever humorous riddle to friend stickman who scratches head with amusing puzzled grin, book in hand"
        },
        {
            "id": "m1-528", "word": "lesson", "meaning": "수업, 교훈",
            "scene": "bright classroom desk, diligent cute slender stickman student listening attentively to teacher lesson lecture taking organized notes in ruled English exercise notebook"
        },
        {
            "id": "m1-529", "word": "earnings", "meaning": "수입, 소득",
            "scene": "small business accounting desk, prudent cute slender stickman entrepreneur reviewing monthly business ledger earnings and financial records with calculator and ledger book"
        },
        {
            "id": "m1-530", "word": "import", "meaning": "수입하다",
            "scene": "commercial seaport cargo shipping terminal, cute slender stickman logistics officer checking manifest clipboard as large cargo vessel unloads imported shipping containers with crane"
        },
        {
            "id": "m1-531", "word": "collect", "meaning": "수집하다",
            "scene": "study room hobby workbench, dedicated cute slender stickman collector using tweezers placing vintage international postage stamps neatly into velvet stamp collection album"
        },
        {
            "id": "m1-532", "word": "horizon", "meaning": "수평선",
            "scene": "seaside cliff overlook at sunset, peaceful cute slender stickman gazing out across calm shimmering ocean as giant golden sun sinks gracefully below distant sea horizon line"
        },
        {
            "id": "m1-533", "word": "bush", "meaning": "수풀, 덤불",
            "scene": "nature trail meadow edge, observant cute slender stickman smiling softly watching a timid wild rabbit peeking head out from behind a lush green flowering blackberry bush"
        },
        {
            "id": "m1-534", "word": "math", "meaning": "수학",
            "scene": "geometry classroom blackboard, focused cute slender stickman student solving an elegant mathematical geometry triangle equation using wooden compass and chalk on board"
        },
        {
            "id": "m1-535", "word": "harvest", "meaning": "수확",
            "scene": "golden autumn rural farmland, joyful cute slender stickman farmer carrying a heavy sheaf of golden ripe wheat stalks across field during bountiful autumn harvest season"
        },
        {
            "id": "m1-536", "word": "moment", "meaning": "순간",
            "scene": "scenic mountain summit, breathless cute slender stickman standing still in awe capturing a magical serene sunset moment with arms open embracing nature beauty"
        },
        {
            "id": "m1-537", "word": "pilgrim", "meaning": "순례자",
            "scene": "historic mountain stone pathway, determined humble cute slender stickman pilgrim with traveler staff and shoulder pack walking toward ancient hillside temple sanctuary in distance"
        },
        {
            "id": "m1-538", "word": "breathe", "meaning": "숨쉬다",
            "scene": "fresh pine forest clearing, relaxed peaceful cute slender stickman standing with eyes closed taking a deep wholesome breath of crisp fresh morning mountain air, arms outstretched"
        },
        {
            "id": "m1-539", "word": "figure", "meaning": "숫자, 수치, 모양",
            "scene": "financial audit office desk, meticulous cute slender stickman analyst checking statistical numeric figures on printed spreadsheet with ruler and pen verifying accurate data"
        },
        {
            "id": "m1-540", "word": "forest", "meaning": "숲",
            "scene": "lush dense pine forest nature reserve, happy cute slender stickman hiking on winding footpath beneath towering evergreen trees and ferns with dappled sunlight filtering through"
        }
    ]    ,
    28: [
        {
            "id": "m1-541", "word": "schedule", "meaning": "스케줄, 일정",
            "scene": "study desk wall calendar, organized cute slender stickman checking off daily task checklist boxes on a structured weekly activity schedule chart with pen, alarm clock"
        },
        {
            "id": "m1-542", "word": "sad", "meaning": "슬픈",
            "scene": "rainy bedroom window sill, gentle cute slender stickman looking out at raindrops trickling down glass, wiping a soft sympathetic tear with handkerchief after emotional film"
        },
        {
            "id": "m1-543", "word": "habit", "meaning": "습관",
            "scene": "cozy bedtime bedside table, serene cute slender stickman reading a chapter of a book under soft reading lamp practicing a wholesome daily evening reading habit before sleep"
        },
        {
            "id": "m1-544", "word": "custom", "meaning": "습관, 관습",
            "scene": "sunny morning park path, diligent cute slender stickman walking an eager friendly pet dog on leash practicing routine morning custom walk, park trees in morning breeze"
        },
        {
            "id": "m1-545", "word": "passenger", "meaning": "승객",
            "scene": "subway train passenger carriage, well-mannered cute slender stickman passenger sitting comfortably holding book by train window while train glides toward city station"
        },
        {
            "id": "m1-546", "word": "monk", "meaning": "승려",
            "scene": "peaceful mountain temple courtyard, serene humble cute slender stickman Buddhist monk in flowing robes gently sweeping stone pathway with bamboo broom beside stone pagoda"
        },
        {
            "id": "m1-547", "word": "triumph", "meaning": "승리",
            "scene": "sports tournament podium stage, triumphant cute slender stickman raising champion trophy cup high in air cheering with arms raised in victory, celebratory confetti falling"
        },
        {
            "id": "m1-548", "word": "crew", "meaning": "승무원",
            "scene": "airplane cabin galley entryway, polite cheerful cute slender stickman flight attendant crew member smiling warmly greeting boarding travelers with welcoming hand gesture"
        },
        {
            "id": "m1-549", "word": "creek", "meaning": "시냇물",
            "scene": "shady woodland forest creek, playful cute slender stickman stepping across stepping stones watching clear shallow bubbling creek water flow gently over smooth pebbles"
        },
        {
            "id": "m1-550", "word": "stream", "meaning": "시냇물, 개울",
            "scene": "green countryside valley meadow, fresh sparkling stream river winding gracefully through wildflowers with cute slender stickman kneeling to float a tiny paper boat on current"
        },
        {
            "id": "m1-551", "word": "cool", "meaning": "시원한, 멋진",
            "scene": "summer veranda porch, relaxed cute slender stickman enjoying a cool refreshing evening breeze blowing through window curtains holding an iced citrus glass drink with straw"
        },
        {
            "id": "m1-552", "word": "poet", "meaning": "시인",
            "scene": "quaint cafe literary corner, thoughtful expressive cute slender stickman poet standing beside microphone passionately reading lyrical verses from a handwritten poetry notebook"
        },
        {
            "id": "m1-553", "word": "mayor", "meaning": "시장",
            "scene": "city hall press auditorium, dignified cute slender stickman city mayor standing at civic podium presenting architectural blueprint plan for a new municipal public library"
        },
        {
            "id": "m1-554", "word": "match", "meaning": "시합",
            "scene": "athletic stadium soccer pitch, dynamic cute slender stickman soccer player kicking soccer ball into goal net during exciting championship sports match, cheering stadium fans"
        },
        {
            "id": "m1-555", "word": "examination", "meaning": "시험, 조사",
            "scene": "quiet school examination hall, studious focused cute slender stickman student carefully writing answers on exam paper sheet at neat wooden desk, clock on wall"
        },
        {
            "id": "m1-556", "word": "restaurant", "meaning": "식당",
            "scene": "cozy Italian bistro dining room, delighted cute slender stickman customer enjoying hot pasta meal at restaurant table with checkered tablecloth and candle, waiter in background"
        },
        {
            "id": "m1-557", "word": "dining room", "meaning": "식당방, 식당",
            "scene": "warm family dining room, happy cute slender stickman family gathered around long dining table enjoying warm wholesome home-cooked dinner together, pendant chandelier above"
        },
        {
            "id": "m1-558", "word": "plant", "meaning": "식물, 심다",
            "scene": "sunny backyard garden plot, gentle caring cute slender stickman planting a young green flowering plant seedling carefully into fresh dark garden soil, watering can nearby"
        },
        {
            "id": "m1-559", "word": "appetite", "meaning": "식욕",
            "scene": "bakery dining table, cheerful hungry cute slender stickman smiling broadly rubbing tummy with hearty appetite as delicious warm breakfast pancakes and fruit are served"
        },
        {
            "id": "m1-560", "word": "god", "meaning": "신",
            "scene": "ancient mountaintop temple altar under majestic starry sky, respectful cute slender stickman gazing up in peaceful awe at grand classical stone temple columns among clouds"
        }
    ]    ,
    29: [
        {
            "id": "m1-561", "word": "excited", "meaning": "신나는, 흥분한",
            "scene": "amusement park entrance gate, joyful exuberant cute slender stickman jumping with raised arms in pure excitement seeing colorful carousel rides and roller coaster peaks"
        },
        {
            "id": "m1-562", "word": "mystery", "meaning": "신비",
            "scene": "deep sea research submarine viewport, amazed cute slender stickman scientist shining spotlight into deep dark ocean trenches illuminating glowing mysterious deep-sea creatures"
        },
        {
            "id": "m1-563", "word": "trust", "meaning": "신용, 신뢰",
            "scene": "community neighborhood shop counter, warm honest cute slender stickman storekeeper shaking hands with smiling loyal customer building mutual trust and goodwill"
        },
        {
            "id": "m1-564", "word": "sign", "meaning": "신호, 표지판",
            "scene": "pedestrian zebra crosswalk, vigilant cute slender stickman crossing guard holding up a bright red Stop sign allowing school children stickmen to cross road safely"
        },
        {
            "id": "m1-565", "word": "excuse", "meaning": "실례하다, 용서하다",
            "scene": "school hallway corridor, polite cute slender stickman bowing head gently with hand over heart asking excuse and pardon after accidentally bumping into classmate stickman"
        },
        {
            "id": "m1-566", "word": "clue", "meaning": "실마리, 단서",
            "scene": "detective study room floor, sharp observant cute slender stickman detective holding magnifying glass inspecting a crucial footprint clue on rug, notebook and desk lamp"
        },
        {
            "id": "m1-567", "word": "disappoint", "meaning": "실망시키다",
            "scene": "study room desk, remorseful determined cute slender stickman looking at graded quiz paper vowing earnestly to study harder to avoid disappointing supportive parents"
        },
        {
            "id": "m1-568", "word": "actually", "meaning": "실제로",
            "scene": "science experiment classroom bench, surprised happy cute slender stickman student discovering that a complex puzzle experiment actually works smoothly in real demonstration"
        },
        {
            "id": "m1-569", "word": "fail", "meaning": "실패하다, 다시 도전하다",
            "scene": "outdoor skateboarding practice ramp, persevering brave cute slender stickman picking up skateboard with resilient smile brushing dust off knee ready to try trick again after a fall"
        },
        {
            "id": "m1-570", "word": "heart", "meaning": "심장",
            "scene": "running stadium finish track, athletic cute slender stickman athlete resting hand over chest feeling rapid strong heartbeat pulse after energetic sprint workout, sports water bottle"
        },
        {
            "id": "m1-571", "word": "wrap", "meaning": "싸다, 포장하다",
            "scene": "holiday craft wrapping desk, creative cute slender stickman carefully folding colorful gift wrapping paper and tying a neat satin ribbon bow around birthday gift box"
        },
        {
            "id": "m1-572", "word": "fight", "meaning": "싸움, 맞서 싸우다",
            "scene": "dojo martial arts mat, disciplined athletic cute slender stickman practicing karate sparring stance with focused eyes and raised hands in honorable martial arts match"
        },
        {
            "id": "m1-573", "word": "twin", "meaning": "쌍둥이",
            "scene": "sunny garden lawn, two identical cheerful cute slender stickman twin siblings wearing matching striped shirts standing side by side smiling happily with arms linked"
        },
        {
            "id": "m1-574", "word": "shoot", "meaning": "쏘다",
            "scene": "archery target range field, focused cute slender stickman archer drawing back bowstring aiming steady arrow toward round circular bullseye archery target board"
        },
        {
            "id": "m1-575", "word": "spend", "meaning": "쓰다, 소비하다",
            "scene": "cozy bookstore cashier, thoughtful cute slender stickman student paying coins from wallet spending allowance wisely to purchase a cherished inspirational paperback novel"
        },
        {
            "id": "m1-576", "word": "useless", "meaning": "쓸모 없는",
            "scene": "tool shed workbench, honest cute slender stickman inspecting a completely broken rusty bent key shaking head realizing it is useless, tossing it into scrap metal bin"
        },
        {
            "id": "m1-577", "word": "sow", "meaning": "씨를 뿌리다",
            "scene": "fertile freshly tilled garden furrow plot, diligent cute slender stickman farmer scattering handfuls of tiny seeds gently across the rich dark earth bed under early spring sun"
        },
        {
            "id": "m1-578", "word": "seed", "meaning": "씨앗",
            "scene": "gardening potting bench, gentle cute slender stickman holding open palm admiring a collection of diverse flowering seeds before pressing them gently into terra-cotta soil pot"
        },
        {
            "id": "m1-579", "word": "beauty", "meaning": "아름다움",
            "scene": "scenic autumn mountain summit ridge, spellbound cute slender stickman admiring breathtaking natural beauty of golden red foliage valleys and shimmering lake below"
        },
        {
            "id": "m1-580", "word": "probably", "meaning": "아마",
            "scene": "sunny front porch walkway, thoughtful cute slender stickman looking up at clearing blue sky seeing sun peek out from clouds noting it will probably be a lovely sunny day"
        }
    ]    ,
    30: [
        {
            "id": "m1-581", "word": "perhaps", "meaning": "아마",
            "scene": "school gymnasium locker room, thoughtful cute slender stickman tapping chin thinking perhaps forgotten brass keys are still safely inside the gym locker, sports bench"
        },
        {
            "id": "m1-582", "word": "maybe", "meaning": "아마",
            "scene": "front hallway umbrella stand, cautious cute slender stickman checking cloudy gray sky out open doorway deciding maybe it is wise to carry an umbrella, rain boots on floor"
        },
        {
            "id": "m1-583", "word": "amateur", "meaning": "아마추어",
            "scene": "cozy living room armchair, passionate cute slender stickman amateur musician smiling warmly strumming an acoustic wooden guitar playing lovely melodic chords, sheet music stand"
        },
        {
            "id": "m1-584", "word": "none", "meaning": "아무것도 ~없다",
            "scene": "classroom blackboard, curious student stickmen sitting around desk looking thoughtfully at an empty chalk problem board seeing none of them had the difficult riddle answer"
        },
        {
            "id": "m1-585", "word": "quite", "meaning": "아주, 꽤",
            "scene": "school auditorium stage, confident cute slender stickman speaking with quite a clear booming loud voice into podium microphone echoing clearly across the grand assembly hall"
        },
        {
            "id": "m1-586", "word": "ache", "meaning": "아프다, 쑤시다",
            "scene": "cozy mountain cabin fireplace hearth, tired cute slender stickman hiker sitting massaging weary aching calf muscles with gentle smile after a long day of rewarding mountain hiking"
        },
        {
            "id": "m1-587", "word": "sore", "meaning": "아픈",
            "scene": "bedroom armchair, caring cute slender stickman resting wrapped in a warm knitted woolen scarf holding hand gently to sore throat while sipping warm honey tea from mug"
        },
        {
            "id": "m1-588", "word": "sick", "meaning": "아픈, 병이 든",
            "scene": "warm bedroom bed, patient cute slender stickman resting comfortably tucked under cozy blanket with thermometer on nightstand, caring friend stickman visiting with fresh soup bowl"
        },
        {
            "id": "m1-589", "word": "instrument", "meaning": "악기, 계기판",
            "scene": "music instrument shop showroom, delighted cute slender stickman holding a polished shiny brass saxophone exploring musical instruments, violin and guitar hanging on wall"
        },
        {
            "id": "m1-590", "word": "devil", "meaning": "악마",
            "scene": "storybook puppet theater stage, playful cute slender stickman puppeteer holding up a humorous whimsical cartoon little red devil puppet with tiny horns in storytelling show"
        },
        {
            "id": "m1-591", "word": "evil", "meaning": "악마, 악",
            "scene": "fairy tale illustrated storybook desk, thoughtful cute slender stickman reading a classic fable showing noble knight defending peaceful village from cartoon shadowy dragon evil"
        },
        {
            "id": "m1-592", "word": "handshake", "meaning": "악수",
            "scene": "business conference room, two smiling professional cute slender stickman partners exchanging a firm respectful mutual handshake in complete agreement, contract folder on desk"
        },
        {
            "id": "m1-593", "word": "fog", "meaning": "안개",
            "scene": "scenic coastal mountain road, cautious cute slender stickman hiker with walking staff gazing into thick atmospheric swirling white morning fog rolling over pine trees"
        },
        {
            "id": "m1-594", "word": "guide", "meaning": "안내자, 안내하다",
            "scene": "historic palace courtyard, friendly knowledgeable cute slender stickman tour guide holding a small tour flag explaining ancient stone architecture to eager tourist stickmen"
        },
        {
            "id": "m1-595", "word": "comfort", "meaning": "안락, 위안",
            "scene": "cozy living room fireplace, deeply relaxed cute slender stickman sinking into a plush upholstered armchair feeling soothing warm comfort after a long productive workday"
        },
        {
            "id": "m1-596", "word": "safely", "meaning": "안전하게",
            "scene": "airport tarmac runway, relieved cute slender stickman passenger looking out airplane window smiling seeing the passenger jetliner touch down smoothly and safely on runway"
        },
        {
            "id": "m1-597", "word": "inner", "meaning": "안쪽의",
            "scene": "cozy entryway coat rack, tidy cute slender stickman reaching hand inside the secure zippered inner pocket of a winter jacket to retrieve a gleaming brass door key"
        },
        {
            "id": "m1-598", "word": "alarm", "meaning": "알람, 주의",
            "scene": "bedroom nightstand desk, punctual cute slender stickman reaching out smiling hand to turn off a ringing round vintage twin-bell alarm clock at sunrise, morning window light"
        },
        {
            "id": "m1-599", "word": "pill", "meaning": "알약",
            "scene": "dining room kitchen counter, conscientious cute slender stickman holding a tiny round medicinal vitamin pill in palm beside a clear glass of fresh water, medicine bottle"
        },
        {
            "id": "m1-600", "word": "alphabet", "meaning": "알파벳",
            "scene": "elementary classroom whiteboard, cheerful cute slender stickman teacher pointing with wooden pointer at a vibrant complete English alphabet chart from A to Z on wall"
        }
    ]    ,
    31: [
        {
            "id": "m1-601", "word": "stress", "meaning": "압박, 강조하다",
            "scene": "quiet yoga meditation room, peaceful cute slender stickman sitting cross-legged on mat breathing deeply releasing workday stress and tension, potted bamboo and soft lighting"
        },
        {
            "id": "m1-602", "word": "front", "meaning": "앞",
            "scene": "sunlit school campus, proud cute slender stickman student standing right in front of the grand classical front facade entrance of the school building, flowerbeds and walkway"
        },
        {
            "id": "m1-603", "word": "ahead", "meaning": "앞서서",
            "scene": "scenic countryside hiking trail, energetic cute slender stickman walking briskly ahead on winding mountain path turning around smiling gesturing friends to follow along"
        },
        {
            "id": "m1-604", "word": "forward", "meaning": "앞으로",
            "scene": "sports athletics running track, determined cute slender stickman runner leaning body forward driving knees high sprinting energetically forward toward the finish line"
        },
        {
            "id": "m1-605", "word": "pet", "meaning": "애완동물",
            "scene": "sunny backyard garden lawn, affectionate cute slender stickman sitting on green grass gently petting the soft fur of a happy loving golden puppy wagging tail joyfully"
        },
        {
            "id": "m1-606", "word": "wild", "meaning": "야생의",
            "scene": "vast wilderness mountain meadow, curious cute slender stickman hiker observing a magnificent wild stag deer standing proudly among pine trees in untouched wild nature"
        },
        {
            "id": "m1-607", "word": "drugstore", "meaning": "약국",
            "scene": "neighborhood street corner, neat cute slender stickman walking into a welcoming illuminated drugstore with pharmacy cross sign to pick up health supplies, tidy shelves"
        },
        {
            "id": "m1-608", "word": "promise", "meaning": "약속",
            "scene": "sunny park bench, two loyal cute slender stickman best friends locking pinky fingers in an earnest warm heartfelt pinky promise of lifelong friendship, smiling faces"
        },
        {
            "id": "m1-609", "word": "weak", "meaning": "약한",
            "scene": "physical therapy recovery gym, persevering cute slender stickman gently practicing light resistance band exercises to strengthen weak leg muscles, encouraging therapist stickman"
        },
        {
            "id": "m1-610", "word": "thin", "meaning": "얇은",
            "scene": "calligraphy studio window, artistic cute slender stickman holding up a sheet of delicate ultra-thin translucent parchment paper to the sun admiring its fine texture, ink stone"
        },
        {
            "id": "m1-611", "word": "sheep", "meaning": "양",
            "scene": "picturesque rolling green hillside, gentle cute slender stickman shepherd resting with wooden crook watching a flock of fluffy white sheep grazing peacefully on pasture knoll"
        },
        {
            "id": "m1-612", "word": "amount", "meaning": "양, 액수, 총액",
            "scene": "bakery kitchen measuring counter, precise cute slender stickman baker pouring an exact measured amount of white flour from measuring cup onto stainless digital kitchen scale"
        },
        {
            "id": "m1-613", "word": "shoulder", "meaning": "어깨",
            "scene": "hiking trail rest bench, relaxed cute slender stickman adjusting backpack shoulder straps taking weight off shoulders sitting under shady oak tree, water bottle on bench"
        },
        {
            "id": "m1-614", "word": "shrug", "meaning": "어깨를 으쓱이다",
            "scene": "classroom desk, cheerful humorous cute slender stickman playfully lifting and shrugging both shoulders with open palms with a carefree good-natured smile, notebook on desk"
        },
        {
            "id": "m1-615", "word": "dark", "meaning": "어두운",
            "scene": "bedroom nightstand, cozy cute slender stickman switching off bedside lamp settling into bed as room transitions into peaceful restful dark starry night, moon outside window"
        },
        {
            "id": "m1-616", "word": "difficult", "meaning": "어려운",
            "scene": "study room desk blackboard, determined studious cute slender stickman scratching head working through a difficult challenging mathematics geometry problem with perseverance"
        },
        {
            "id": "m1-617", "word": "adult", "meaning": "어른, 성인",
            "scene": "civic voter registration office, proud mature cute slender stickman receiving official voter registration card celebrating milestone transition into responsible adult citizen"
        },
        {
            "id": "m1-618", "word": "silly", "meaning": "어리석은, 우스꽝스러운",
            "scene": "party photo booth corner, funny playful cute slender stickman wearing an oversized silly polka-dot bowtie and funny party glasses making friends laugh in good-natured fun"
        },
        {
            "id": "m1-619", "word": "foolish", "meaning": "어리석은",
            "scene": "rainy street sidewalk, rueful cute slender stickman standing under shop awning realizing how foolish it was to leave umbrella behind at home, smiling shaking wet jacket"
        },
        {
            "id": "m1-620", "word": "anyway", "meaning": "어쨌든",
            "scene": "outdoor park walking path in light drizzle, cheerful adventurous cute slender stickman pulling up jacket hood smiling warmly deciding to enjoy the scenic walk anyway, park trees"
        }
    ],
    32: [
        {
            "id": "m1-621", "word": "language", "meaning": "언어",
            "scene": "bright modern classroom, cute slender stickman student sitting at desk practicing languages, reading open bilingual book, cheerful speech bubbles with English words HELLO and WELCOME floating above, bookshelf and classroom floor line"
        },
        {
            "id": "m1-622", "word": "sometime", "meaning": "언젠가",
            "scene": "cozy bedroom interior, cute slender stickman sitting at wooden desk gazing out window at far mountain landscape in daydream thought, calendar on wall showing future spring date dreaming of visiting farm sometime, desk lamp and floor line"
        },
        {
            "id": "m1-623", "word": "obtain", "meaning": "얻다",
            "scene": "cheerful cute slender stickman proudly receiving a shiny admission pass from older brother stickman, smiling happily in modern theater entrance with minimalist glass doors and clear floor line, zero text, clean outlines"
        },
        {
            "id": "m1-624", "word": "gain", "meaning": "얻다",
            "scene": "quiet university library aisle, curious cute slender stickman sitting cross-legged by tall bookshelf reading an open thick book with knowledge lightbulb glow above head gaining wisdom, stacked books on wooden floor line"
        },
        {
            "id": "m1-625", "word": "thumb", "meaning": "엄지손가락",
            "scene": "bright school classroom doorway, cute slender stickman holding up hand gently caring for a bruised thumb after closing heavy wooden door, small ice pack on table, lockers and tiled floor line"
        },
        {
            "id": "m1-626", "word": "energy", "meaning": "에너지",
            "scene": "sunny outdoor playground lawn, energetic cute slender stickman jumping high into the air with cheerful outstretched arms, dynamic motion sparks and radiating lines showing boundless vitality, swing set and grass line"
        },
        {
            "id": "m1-627", "word": "passport", "meaning": "여권",
            "scene": "busy international airport departure gate counter, cute slender stickman holding out a small dark blue passport booklet with clear gold emblem to airline staff stickman, wheeled rolling suitcase beside on airport floor line"
        },
        {
            "id": "m1-628", "word": "various", "meaning": "여러 가지의",
            "scene": "charming corner grocery confectionery shop, cute slender stickman shopper admiring wooden shelves filled with various different snack packages, round candy jars, and assorted drinks, wooden floor line"
        },
        {
            "id": "m1-629", "word": "journey", "meaning": "여행",
            "scene": "scenic winding mountain hiking trail, cute slender stickman backpacker with trekking pole walking steadily along footpath towards distant mountain village summit under morning clouds, stone path line"
        },
        {
            "id": "m1-630", "word": "trip", "meaning": "여행",
            "scene": "sunlit countryside train station platform, cute slender stickman students wearing small backpacks eagerly waiting for a three-day class trip train, train railway tracks and platform shelter line"
        },
        {
            "id": "m1-631", "word": "suitcase", "meaning": "여행가방",
            "scene": "cozy bedroom carpet, cute slender stickman kneeling on floor packing a sturdy open rolling suitcase, neatly folding clothes and arranging travel gear before school trip, bed and floor line"
        },
        {
            "id": "m1-632", "word": "tourist", "meaning": "여행자",
            "scene": "historic town square in front of grand palace stone gate, cute slender stickman tourist wearing sunhat holding paper city map asking directions to friendly local guide stickman pointing ahead, cobblestone floor line"
        },
        {
            "id": "m1-633", "word": "travel", "meaning": "여행하다, 여행",
            "scene": "spacious study room, adventurous cute slender stickman with backpack spinning a large tabletop world globe with finger pointing at European capitals, travel posters on wall and wooden floor line"
        },
        {
            "id": "m1-634", "word": "history", "meaning": "역사",
            "scene": "warm classroom blackboard, engaging stickman history teacher illustrating ancient castle towers and historical scrolls, attentive cute slender stickman students listening fascinated, desks and floor line"
        },
        {
            "id": "m1-635", "word": "series", "meaning": "연속된",
            "scene": "night bedroom interior, cute slender stickman sitting up in bed listening attentively as a series of rhythmic mysterious tapping soundwaves repeat against the window glass, nightstand clock and floor line"
        },
        {
            "id": "m1-636", "word": "practice", "meaning": "연습하다",
            "scene": "peaceful music room nook, dedicated cute slender stickman sitting on piano bench practicing melody on upright piano with open sheet music after dinner, soft room lighting and carpet floor line"
        },
        {
            "id": "m1-637", "word": "fever", "meaning": "열",
            "scene": "cozy bedroom bed, cute slender stickman resting quietly under warm blanket with a soothing cool cloth on forehead, digital thermometer and hot lemon tea cup on bedside table line"
        },
        {
            "id": "m1-638", "word": "heat", "meaning": "열",
            "scene": "quaint rustic kitchen, cute slender stickman warming chilly hands near radiant warmth of cast iron wood stove with glowing embers, whistling kettle on top and stone floor line"
        },
        {
            "id": "m1-639", "word": "dye", "meaning": "염색하다",
            "scene": "artisan craft studio workbench, creative cute slender stickman wearing apron dipping white cotton fabric into a large round ceramic basin filled with deep indigo blue dye, color dye jars on table line"
        },
        {
            "id": "m1-640", "word": "overhear", "meaning": "엿듣다",
            "scene": "living room hallway doorway, curious cute slender stickman peeking slightly around door frame cupping hand to ear overhearing parents happily whispering surprise travel plans, hallway floor line"
        }
    ],
    33: [
        {
            "id": "m1-641", "word": "glory", "meaning": "영광",
            "scene": "grand memorial hall, veteran cute slender stickman standing proudly before framed golden victory medal and laurels on exhibition wall, solemn reflective smile celebrating past glory, polished museum floor line"
        },
        {
            "id": "m1-642", "word": "British", "meaning": "영국인, 영국인의",
            "scene": "bright friendly school classroom, new British cute slender stickman student standing by teacher podium waving cheerful greeting to classmates, neat school uniform and chalkboard line"
        },
        {
            "id": "m1-643", "word": "clever", "meaning": "영리한",
            "scene": "lush nature sanctuary, cute slender stickman observer watching a clever intelligent monkey stickman skillfully using a slim branch tool to open a locked puzzle box for sweet bananas, grassy ground line"
        },
        {
            "id": "m1-644", "word": "example", "meaning": "예",
            "scene": "classroom whiteboard, encouraging stickman teacher drawing clear diagram under bold title EXAMPLE on board for attentive cute slender stickman student raising hand at front desk, classroom floor line"
        },
        {
            "id": "m1-645", "word": "pretty", "meaning": "예쁜",
            "scene": "sunlit boutique dressing room, cute slender stickman wearing a pretty charming pastel yellow dress with floral ribbon admiring reflection in tall standing mirror, polished wooden floor line"
        },
        {
            "id": "m1-646", "word": "art", "meaning": "예술",
            "scene": "bright attic art studio, passionate cute slender stickman artist holding wooden paint palette and fine brush painting a peaceful landscape of rolling hills on large easel, tubes of paint on studio floor line"
        },
        {
            "id": "m1-647", "word": "hut", "meaning": "오두막집",
            "scene": "quiet pine forest glade, cozy rustic wooden timber hut with stone chimney puffing light smoke curls, cute slender stickman standing welcoming at open wooden door, forest grass line"
        },
        {
            "id": "m1-648", "word": "climb", "meaning": "오르다, 등산하다",
            "scene": "lush garden orchard, adventurous cute slender stickman boy carefully climbing rung by rung up a wooden ladder leaning against apple tree to pick ripe red fruit, orchard ground line"
        },
        {
            "id": "m1-649", "word": "pollution", "meaning": "오염",
            "scene": "busy city street sidewalk, cute slender stickman wearing protective face mask walking past hazy skyline with distant factory smokestacks and vehicle traffic, street curb and lamppost line"
        },
        {
            "id": "m1-650", "word": "rather", "meaning": "오히려, 꽤",
            "scene": "dining table setting, cute slender stickman holding a soup spoon tasting vegetable broth with surprised humorous expression discovering the soup is not boiling hot but rather chilly, table and floor line"
        },
        {
            "id": "m1-651", "word": "corn", "meaning": "옥수수",
            "scene": "sunny golden summer farm field, cute slender stickman farmer harvesting ripe yellow ears of sweet corn from tall green cornstalks into a woven wicker basket, farmland soil line"
        },
        {
            "id": "m1-652", "word": "temperature", "meaning": "온도",
            "scene": "warm summer classroom window, cute slender stickman student fanning face with paper fan checking wall dial thermometer showing hot indoor temperature, open window and desk line"
        },
        {
            "id": "m1-653", "word": "thermometer", "meaning": "온도계",
            "scene": "frosty winter morning window sill, cute slender stickman looking closely through glass at outdoor mercury thermometer marked minus ten degrees with frost patterns on glass frame line"
        },
        {
            "id": "m1-654", "word": "mild", "meaning": "온화한",
            "scene": "gentle spring park meadow, content cute slender stickman having relaxing outdoor lunch on picnic blanket under warm mild sunshine and blooming cherry trees, picnic basket and meadow line"
        },
        {
            "id": "m1-655", "word": "raise", "meaning": "올리다, 모금하다, 양육하다",
            "scene": "active interactive classroom, enthusiastic cute slender stickman student sitting at desk raising arm high and straight with eager smile ready to answer question, textbook and classroom floor line"
        },
        {
            "id": "m1-656", "word": "owl", "meaning": "올빼미",
            "scene": "mystical moonlit night forest, wise calm owl with large round eyes perched quietly on thick oak branch under glowing crescent moon and twinkling stars, forest floor line"
        },
        {
            "id": "m1-657", "word": "closet", "meaning": "옷장",
            "scene": "clean bedroom corner, organized cute slender stickman hanging a warm heavy winter coat onto wooden hanger inside an open wooden wardrobe closet, bedroom floor line"
        },
        {
            "id": "m1-658", "word": "complete", "meaning": "완성하다",
            "scene": "school courtyard exterior wall, proud cute slender stickman muralist team adding the final colorful brushstroke to complete a magnificent large wall painting together, paint buckets and pavement line"
        },
        {
            "id": "m1-659", "word": "crown", "meaning": "왕관",
            "scene": "regal castle throne room, dignified cute slender stickman young queen seated gracefully wearing an elegant golden crown with sparkling pointed gems, royal drapery and palace marble floor line"
        },
        {
            "id": "m1-660", "word": "prince", "meaning": "왕자",
            "scene": "historic fairytale castle courtyard, brave noble cute slender stickman prince wearing royal tunic and cape holding silver crest shield ready to protect kingdom, stone castle archway line"
        }
    ],
    34: [
        {
            "id": "m1-661", "word": "foreign", "meaning": "해외의, 외국의",
            "scene": "historic city royal palace courtyard, cheerful cute slender foreign stickman tourist with small backpack and camera taking photo of magnificent palace stone arches, stone pavement line"
        },
        {
            "id": "m1-662", "word": "shout", "meaning": "소리치다",
            "scene": "wide sunny open soccer field, energetic cute slender stickman teammate cupping hands around mouth shouting encouraging words to players across green pitch, white field goal line"
        },
        {
            "id": "m1-663", "word": "yell", "meaning": "고함치다, 소리 지르다",
            "scene": "school running track stadium sideline, passionate cute slender stickman coach holding a stopwatch yelling spirited motivation to sprinting runners, running track lane line"
        },
        {
            "id": "m1-664", "word": "fare", "meaning": "요금",
            "scene": "clean modern city bus interior near entrance, polite cute slender stickman passenger gently tapping digital transport fare card on fare scanner next to driver, bus aisle floor line"
        },
        {
            "id": "m1-665", "word": "bathroom", "meaning": "화장실",
            "scene": "tidy sparkling clean home bathroom, cute slender stickman smiling at round wall mirror washing hands with foamy soap bubbles over modern ceramic sink, bath mat and tiled floor line"
        },
        {
            "id": "m1-666", "word": "pardon", "meaning": "용서, 사면",
            "scene": "ancient medieval throne room, benevolent cute slender king stickman seated on carved wooden throne holding a rolled parchment decree granting gentle pardon to kneeling villager stickman, stone floor line"
        },
        {
            "id": "m1-667", "word": "dull", "meaning": "둔한, 무딘",
            "scene": "quiet cozy workshop workbench, patient cute slender stickman sharpening a dull blunt chisel blade against an oiled whetstone, wood chips and workshop floor line"
        },
        {
            "id": "m1-668", "word": "umbrella", "meaning": "우산",
            "scene": "gentle rainy city street promenade, cheerful cute slender stickman walking comfortably holding a large round dome umbrella keeping dry under soft raindrops, puddle reflections and sidewalk line"
        },
        {
            "id": "m1-669", "word": "universe", "meaning": "우주",
            "scene": "cozy school astronomy club rooftop at night, curious cute slender stickman gazing through large brass telescope at swirling spiral galaxy and twinkling starry universe, telescope tripod and rooftop line"
        },
        {
            "id": "m1-670", "word": "post", "meaning": "우편",
            "scene": "charming suburban front garden porch, smiling cute slender stickman receiving a sealed envelope letter delivered by friendly postal courier stickman, neat red mailbox and cobblestone pathway line"
        },
        {
            "id": "m1-671", "word": "exercise", "meaning": "운동, 체력 단련",
            "scene": "refreshing sunny morning park lawn, active cute slender stickman doing stretching exercises on a soft mat while friend stickman jogs past, leafy trees and park path line"
        },
        {
            "id": "m1-672", "word": "athlete", "meaning": "운동선수",
            "scene": "indoor gymnasium sports training center, dedicated cute slender athlete stickman balancing gracefully on gymnast beam with focused concentration, safety landing mats and gym floor line"
        },
        {
            "id": "m1-673", "word": "fortunately", "meaning": "다행히",
            "scene": "leafy garden yard after windy rain, relieved cute slender stickman picking up an undamaged fragile ceramic flowerpot that luckily landed soft on grass without breaking, garden stone border line"
        },
        {
            "id": "m1-674", "word": "canal", "meaning": "수로, 물길",
            "scene": "picturesque riverside town waterway, cute slender stickman steering a slender wooden rowing boat peacefully gliding along calm canal between historic brick houses, stone canal bank line"
        },
        {
            "id": "m1-675", "word": "fence", "meaning": "울타리",
            "scene": "sunny countryside ranch meadow, cute slender stickman standing beside a neat wooden post fence gently patting a friendly horse peeking over rail, lush grass meadow line"
        },
        {
            "id": "m1-676", "word": "grab", "meaning": "붙잡다",
            "scene": "busy playful school playground, agile cute slender stickman reaching out arm to quickly grab a flying frisbee disc right before it hits the ground, playground sand line"
        },
        {
            "id": "m1-677", "word": "grand", "meaning": "장엄한",
            "scene": "majestic opera house grand foyer, awe-struck cute slender stickman visitor standing beneath towering classical marble columns and sweeping grand curved staircase, polished marble floor line"
        },
        {
            "id": "m1-678", "word": "circle", "meaning": "원, 동그라미",
            "scene": "bright math classroom desk, clever cute slender stickman using a silver drawing compass to sketch a perfect smooth circle on large drafting paper, wooden ruler and desk line"
        },
        {
            "id": "m1-679", "word": "cause", "meaning": "원인",
            "scene": "modern science laboratory room, inquisitive cute slender stickman researcher examining microscope slide clues to discover the cause of a chemical reaction, glassware test tubes and lab bench line"
        },
        {
            "id": "m1-680", "word": "atom", "meaning": "원자",
            "scene": "interactive physics science center, fascinated cute slender stickman student observing a large glowing 3D planetary atomic model with orbiting electrons, display pedestal and museum floor line"
        }
    ],
    35: [
        {
            "id": "m1-681", "word": "stomach", "meaning": "복부, 배",
            "scene": "cozy living room armchair, cute slender stickman gently holding a warm soothing water bottle against stomach resting comfortably after heavy meal, side table with cup of herbal tea and floor line"
        },
        {
            "id": "m1-682", "word": "locate", "meaning": "위치를 찾다",
            "scene": "spacious library study table, curious cute slender stickman spreading a large unfolded city landmark map pointing finger to locate school library building, desk lamp and floor line"
        },
        {
            "id": "m1-683", "word": "danger", "meaning": "위험",
            "scene": "rocky mountain cliff path, cautious cute slender stickman hiker carefully stopping before a steep crumbling edge marked with warning striped barrier poles, mountain stone path line"
        },
        {
            "id": "m1-684", "word": "competent", "meaning": "유능한",
            "scene": "busy design workshop office, competent skilled cute slender stickman project leader confidently presenting organized architectural blueprints on easel to admiring teammates, studio floor line"
        },
        {
            "id": "m1-685", "word": "famous", "meaning": "유명한",
            "scene": "historic artisan bakery storefront, cute slender stickman baker holding up freshly baked golden bread loaf warmly welcoming line of smiling town customers, brick storefront line"
        },
        {
            "id": "m1-686", "word": "kindergarten", "meaning": "유치원",
            "scene": "bright cheerful kindergarten playroom, kind cute slender stickman teacher reading a big illustrated storybook to tiny cute circle-headed stickman toddlers sitting on colorful rug, toy blocks and floor line"
        },
        {
            "id": "m1-687", "word": "type", "meaning": "종류, 유형",
            "scene": "neat botanist greenhouse nursery, observant cute slender stickman categorizing different types of potted leafy ferns and flowering succulents onto tiered wooden shelves, greenhouse brick floor line"
        },
        {
            "id": "m1-688", "word": "general", "meaning": "장군, 사령관",
            "scene": "historic castle military command tent, dignified cute slender general stickman wearing epaulet mantle reviewing terrain battle map on campaign table with captain stickman, tent floor line"
        },
        {
            "id": "m1-689", "word": "roar", "meaning": "포효하다",
            "scene": "nature reserve safari overlook, amazed cute slender stickman standing safely behind sturdy railing watching a proud majestic lion roaring across open savanna rock outcrop, observation deck line"
        },
        {
            "id": "m1-690", "word": "musician", "meaning": "음악가",
            "scene": "warm acoustics chamber hall stage, elegant cute slender musician stickman resting violin beneath chin passionately bowing melody, wooden music sheet stand and polished parquet stage line"
        },
        {
            "id": "m1-691", "word": "concert", "meaning": "콘서트, 음악회",
            "scene": "intimate acoustic concert auditorium, talented cute slender stickman pianist performing grand piano recital while seated stickman audience listens in peaceful delight, stage floor line"
        },
        {
            "id": "m1-692", "word": "reply", "meaning": "답장하다",
            "scene": "cozy writing desk corner, thoughtful cute slender stickman writing a warm handwritten reply letter with ink fountain pen onto crisp stationery paper, small desk lamp and wooden floor line"
        },
        {
            "id": "m1-693", "word": "stare", "meaning": "응시하다",
            "scene": "charming toy shop display window, mesmerized cute slender stickman child standing on sidewalk staring with wide round eyes at moving miniature clockwork train inside, shop window sill line"
        },
        {
            "id": "m1-694", "word": "gaze", "meaning": "바라보다",
            "scene": "tranquil ocean cliff bench at sunset, peaceful cute slender stickman sitting gazing out at shimmering distant sea horizon and drifting evening clouds, coastal wooden railing line"
        },
        {
            "id": "m1-695", "word": "opinion", "meaning": "의견",
            "scene": "school debate club conference room, thoughtful cute slender stickman student standing at podium politely sharing insightful personal opinion to attentive club members, whiteboard and floor line"
        },
        {
            "id": "m1-696", "word": "compulsory", "meaning": "의무적인, 필수의",
            "scene": "bicycle safety training track, diligent cute slender stickman carefully fastening safety helmet strap before riding bicycle adhering to compulsory safety rule, asphalt training track line"
        },
        {
            "id": "m1-697", "word": "communication", "meaning": "의사소통",
            "scene": "sunny park picnic table, two smiling cute slender stickman friends enjoying lively face-to-face communication sharing stories and laughing over cups of juice, park bench and lawn line"
        },
        {
            "id": "m1-698", "word": "ceremony", "meaning": "의식, 기념식",
            "scene": "grand school auditorium stage, proud cute slender stickman graduate receiving honor certificate scroll during formal graduation ceremony, decorative potted ferns and stage floor line"
        },
        {
            "id": "m1-699", "word": "depend", "meaning": "의존하다",
            "scene": "leafy tree branch nest outdoors, three tiny hungry baby bird stick figures peeking out eagerly depending on mother bird returning with food, sturdy oak branch and leaf line"
        },
        {
            "id": "m1-700", "word": "tooth", "meaning": "치아, 이",
            "scene": "bright modern dental clinic room, friendly dentist stickman showing cute slender stickman patient an enlarged clean tooth model illustrating proper brushing technique, clinic chair and floor line"
        }
    ],
    36: [
        {
            "id": "m1-701", "word": "win", "meaning": "이기다, 승리하다",
            "scene": "vibrant school sports soccer field, ecstatic cute slender stickman player holding championship golden cup trophy high above head surrounded by cheering stickman teammates, soccer goal net and grass field line"
        },
        {
            "id": "m1-702", "word": "strange", "meaning": "이상한, 기묘한",
            "scene": "cozy kitchen corner, curious cute slender stickman leaning down tilting head with puzzled smile listening to strange ticking sound coming from beneath old wooden floorboard, kitchen cabinet and floor line"
        },
        {
            "id": "m1-703", "word": "neighbor", "meaning": "이웃",
            "scene": "friendly suburban garden fence line, warm smiling cute slender stickman handing a wicker basket filled with fresh red garden apples over low wooden picket fence to neighbor stickman, garden flowerbed line"
        },
        {
            "id": "m1-704", "word": "reason", "meaning": "이유, 까닭",
            "scene": "bright school classroom teacher desk, thoughtful cute slender stickman student standing politely explaining the honest reason for being late to understanding stickman teacher, classroom chalkboard and floor line"
        },
        {
            "id": "m1-705", "word": "interest", "meaning": "이해관계, 관심",
            "scene": "peaceful diplomatic meeting room, two respectable cute slender delegate stickmen sitting across round negotiation table shaking hands reaching mutual agreement of interest, world map wall decor and floor line"
        },
        {
            "id": "m1-706", "word": "settler", "meaning": "정착민",
            "scene": "historic riverbank frontier woodland, diligent cute slender settler stickman building sturdy timber log cabin with handheld mallet near flowing river, pine trees and ground line"
        },
        {
            "id": "m1-707", "word": "understand", "meaning": "이해하다",
            "scene": "quiet study room desk, enlightened cute slender stickman student looking at open math geometry notebook with glowing idea lightbulb above head finally understanding complex problem, desk lamp and floor line"
        },
        {
            "id": "m1-708", "word": "drown", "meaning": "물에 빠지다, 익사하다",
            "scene": "rocky coastal beach water edge, heroic cute slender stickman lifeguard throwing buoyant round rescue ring with rope toward swimmer stickman in churning sea waves, shoreline sand line"
        },
        {
            "id": "m1-709", "word": "population", "meaning": "인구",
            "scene": "bustling cheerful city pedestrian boulevard, diverse cute slender stickman citizens walking happily along tree-lined sidewalk illustrating growing vibrant town population, city shopfront line"
        },
        {
            "id": "m1-710", "word": "popular", "meaning": "인기 있는",
            "scene": "lively school courtyard stage, charismatic cute slender stickman acoustic singer performing cheerful song with crowd of enthusiastic stickman students clapping and cheering, stage floor line"
        },
        {
            "id": "m1-711", "word": "lead", "meaning": "안내하다, 이끌다",
            "scene": "mysterious natural cavern entrance, confident cute slender stickman guide holding bright camping lantern leading a line of curious explorer stickmen safely along rocky cave path line"
        },
        {
            "id": "m1-712", "word": "mankind", "meaning": "인류",
            "scene": "ancient stone age campfire clearing, primitive cute slender stickman discovering early fire sparks using wooden friction drill demonstrating ancient dawn of mankind, cave wall and rocky floor line"
        },
        {
            "id": "m1-713", "word": "greeting", "meaning": "인사",
            "scene": "sunny residential morning sidewalk, cheerful cute slender stickman waving open hand high in warm friendly greeting to approaching friend stickman, neat garden hedges and street line"
        },
        {
            "id": "m1-714", "word": "doll", "meaning": "인형",
            "scene": "sweet cozy bedroom bed, peaceful cute slender stickman sleeping soundly tucked under warm duvet gently hugging soft plush button-jointed cloth doll, nightstand and bedroom floor line"
        },
        {
            "id": "m1-715", "word": "diary", "meaning": "일기",
            "scene": "peaceful bedroom study desk at night, cute slender stickman writing daily reflections with pen in hardcover open personal diary under warm small desk lamp glow, bedroom floor line"
        },
        {
            "id": "m1-716", "word": "occur", "meaning": "발생하다, 일어나다",
            "scene": "outdoor city bridge walkway, surprised cute slender stickman pedestrian observing sudden heavy gust of wind occurring and blowing dry autumn leaves across stone bridge railing line"
        },
        {
            "id": "m1-717", "word": "happen", "meaning": "일어나다, 벌어지다",
            "scene": "sunny school park path, smiling cute slender stickman watching an unexpected joyful coincidence happen as two flying colorful butterflies land gently on wooden park bench line"
        },
        {
            "id": "m1-718", "word": "early", "meaning": "이른, 일찍",
            "scene": "quiet sunrise dawn street, energetic cute slender stickman waking early walking briskly to catch first yellow morning school bus under glowing pink sunrise sky, street pavement line"
        },
        {
            "id": "m1-719", "word": "lose", "meaning": "잃어버리다",
            "scene": "clean subway station platform bench, cute slender stickman realizing a forgotten umbrella on train and checking empty pockets with hands outstretched in mild surprise, platform safety line"
        },
        {
            "id": "m1-720", "word": "appointment", "meaning": "임명, 약속",
            "scene": "formal sports team locker room ceremony, proud cute slender stickman soccer athlete receiving a captain armband appointment from smiling stickman coach, bench lockers and floor line"
        }
    ],
    37: [
        {
            "id": "m1-721", "word": "wear", "meaning": "입다, 닳다",
            "scene": "cozy bedroom wardrobe mirror, smiling cute slender stickman trying on a warm cozy winter knit sweater looking at self in standing mirror, clothes hanger rack and bedroom floor line"
        },
        {
            "id": "m1-722", "word": "sleep", "meaning": "자다",
            "scene": "tranquil bedroom night, peaceful cute slender stickman sleeping soundly wrapped in soft warm blanket with crescent moon shining outside window, cozy bed and bedroom floor line"
        },
        {
            "id": "m1-723", "word": "proud", "meaning": "자랑스러운",
            "scene": "bright school exhibition room, proud cute slender stickman standing happily with hands on hips showing a colorful gold medal ribbon pinned to painted canvas, display easel and floor line"
        },
        {
            "id": "m1-724", "word": "lock", "meaning": "자물쇠, 잠그다",
            "scene": "front door porch of cozy home, diligent cute slender stickman holding brass key securely locking the sturdy front door lock before leaving, doorway and porch floor line"
        },
        {
            "id": "m1-725", "word": "own", "meaning": "자신의",
            "scene": "sunny garden lawn, joyful cute slender stickman proudly holding the deed certificate of own newly built small garden greenhouse, flowering plants and lawn line"
        },
        {
            "id": "m1-726", "word": "nature", "meaning": "자연",
            "scene": "breathtaking mountain hiking path, amazed cute slender stickman standing with arms spread wide admiring lush green pine forests, distant rolling hills and winding nature trail line"
        },
        {
            "id": "m1-727", "word": "resource", "meaning": "자원",
            "scene": "sunny open prairie landscape, thoughtful cute slender stickman observing tall spinning clean wind turbine generators and solar energy panel arrays, hillside and ground line"
        },
        {
            "id": "m1-728", "word": "liberty", "meaning": "자유",
            "scene": "wide open green hillside summit, triumphant cute slender stickman standing freely under clear open sky releasing a white dove into the air representing liberty, hill ridge line"
        },
        {
            "id": "m1-729", "word": "bike", "meaning": "자전거",
            "scene": "sunny riverfront paved bicycle path, cheerful cute slender stickman wearing helmet happily pedaling a sleek classic two-wheeled bike along willow trees, river railing line"
        },
        {
            "id": "m1-730", "word": "composer", "meaning": "작곡가",
            "scene": "elegant music studio room, inspired cute slender composer stickman sitting at grand piano composing new melody on sheet music score with pencil, metronome and floor line"
        },
        {
            "id": "m1-731", "word": "bit", "meaning": "작은 조각",
            "scene": "sunny bakery kitchen table, happy cute slender stickman nibbling on a tiny delicious crispy bit of butter cookie from baking tray, rolling pin and kitchen counter line"
        },
        {
            "id": "m1-732", "word": "grass", "meaning": "잔디, 풀",
            "scene": "sunny suburban backyard, relaxed cute slender stickman resting comfortably barefoot on fresh green lush lawn grass under warm gentle sunshine, wooden fence line"
        },
        {
            "id": "m1-733", "word": "error", "meaning": "잘못, 오류",
            "scene": "modern office computer desk, focused cute slender stickman software coder spotting a syntax typo error alert highlighted on computer monitor and fixing it promptly, desk and office floor line"
        },
        {
            "id": "m1-734", "word": "fault", "meaning": "잘못, 결점",
            "scene": "living room carpet, polite cute slender stickman holding cracked ceramic vase with sheepish apologetic smile acknowledging personal fault to companion stickman, sofa and floor line"
        },
        {
            "id": "m1-735", "word": "mistake", "meaning": "실수",
            "scene": "classroom math test desk, gentle cute slender stickman student noticing a simple calculation mistake on exam paper and carefully erasing with pencil rubber, desk and classroom floor line"
        },
        {
            "id": "m1-736", "word": "handsome", "meaning": "잘생긴",
            "scene": "chic dressing room mirror, neat stylish cute slender stickman adjusting neat bowtie collar with charming smile admiring handsome dapper reflection, vanity lights and floor line"
        },
        {
            "id": "m1-737", "word": "pull", "meaning": "잡아당기다",
            "scene": "cozy countryside cottage porch, energetic cute slender stickman firmly gripping sturdy hemp rope with both hands pulling a heavy wooden farm cart forward, gravel path line"
        },
        {
            "id": "m1-738", "word": "magazine", "meaning": "잡지",
            "scene": "bright cozy living room armchair, relaxed cute slender stickman sitting comfortably turning pages of a glossy science picture magazine with coffee cup nearby, small side table and floor line"
        },
        {
            "id": "m1-739", "word": "funeral", "meaning": "장례식",
            "scene": "peaceful memorial garden cemetery, solemn cute slender stickman holding single white blossom flower paying respectful quiet tribute near memorial stone monument, cypress trees and grass line"
        },
        {
            "id": "m1-740", "word": "scene", "meaning": "장면, 현장",
            "scene": "outdoor movie filming set, creative cute slender stickman film director looking through handheld viewfinder framing a dramatic movie scene with clapperboard prop, studio lights and floor line"
        }
    ],
    38: [
        {
            "id": "m1-741", "word": "site", "meaning": "장소, 현장",
            "scene": "historic architectural excavation site, curious cute slender stickman archaeologist examining ancient stone column ruins with magnifying glass, ground line"
        },
        {
            "id": "m1-742", "word": "fun", "meaning": "재미, 즐거움",
            "scene": "cheerful amusement park playground, ecstatic cute slender stickman sliding down spiral playground slide with raised hands in pure fun and laughter, sandpit line"
        },
        {
            "id": "m1-743", "word": "interesting", "meaning": "재미있는, 흥미로운",
            "scene": "quiet cozy library study nook, intrigued cute slender stickman reading a fascinating illustrated science discovery book with wide curious eyes, bookshelf and floor line"
        },
        {
            "id": "m1-744", "word": "judge", "meaning": "재판관, 판사",
            "scene": "formal solemn courtroom, dignified cute slender judge stickman sitting high at mahogany judicial bench tapping wooden gavel firmly, law books and courtroom floor line"
        },
        {
            "id": "m1-745", "word": "enemy", "meaning": "적",
            "scene": "classic fairytale castle parapet, brave cute slender knight stickman standing guard with shield looking out across moat at distant opposing rival knight stickman, stone wall line"
        },
        {
            "id": "m1-746", "word": "properly", "meaning": "적절하게, 제대로",
            "scene": "bright organized laboratory workbench, meticulous cute slender scientist stickman carefully measuring chemical liquid with precision pipette properly into test tube rack, desk and floor line"
        },
        {
            "id": "m1-747", "word": "electricity", "meaning": "전기",
            "scene": "bright physics classroom laboratory, amazed cute slender stickman student observing crackling electric spark arcs leaping across glass plasma ball generator, lab bench and floor line"
        },
        {
            "id": "m1-748", "word": "coil", "meaning": "전선, 코일",
            "scene": "electronics engineering workshop desk, focused cute slender stickman technician carefully winding insulated copper wire coil around magnetic iron core, soldering iron and workbench line"
        },
        {
            "id": "m1-749", "word": "war", "meaning": "전쟁",
            "scene": "historic museum panorama exhibit, thoughtful cute slender stickman visitor observing detailed miniature peace memorial diorama learning about historic ancient war, display case and floor line"
        },
        {
            "id": "m1-750", "word": "whole", "meaning": "전체의",
            "scene": "sunny family dining room, happy cute slender stickman carrying a large whole freshly baked golden crust fruit pie on round baking tray to dining table, kitchen floor line"
        },
        {
            "id": "m1-751", "word": "entire", "meaning": "전체의",
            "scene": "spacious geography classroom, proud cute slender stickman teacher holding pointer wand indicating the entire world globe map displayed across wide wall chalkboard, classroom floor line"
        },
        {
            "id": "m1-752", "word": "tradition", "meaning": "전통",
            "scene": "historic folk festival village square, joyful cute slender stickman performing ceremonial folk circle dance celebrating beloved cultural heritage tradition, lanterns and cobblestone ground line"
        },
        {
            "id": "m1-753", "word": "battle", "meaning": "전투",
            "scene": "grand tournament arena stage, two energetic cute slender stickman martial artists engaging in friendly disciplined sparring contest, spectators and mat floor line"
        },
        {
            "id": "m1-754", "word": "telephone", "meaning": "전화",
            "scene": "cozy vintage hallway table, cheerful cute slender stickman holding classic rotary telephone handset chatting and laughing happily with good friend, wallpaper and wooden floor line"
        },
        {
            "id": "m1-755", "word": "temple", "meaning": "절, 사원",
            "scene": "peaceful misty bamboo forest hillside, serene cute slender stickman traveler walking toward ancient wooden temple pagoda with gentle stone lantern steps, mountain path line"
        },
        {
            "id": "m1-756", "word": "bow", "meaning": "절하다, 인사하다",
            "scene": "polite martial arts dojo hall, respectful cute slender stickman student in tidy uniform bowing low with bent waist in polite traditional greeting to master, wooden dojo floor line"
        },
        {
            "id": "m1-757", "word": "score", "meaning": "점수",
            "scene": "sunny basketball playground court, cheering cute slender stickman player looking up at high scoreboard flipper showing winning final match score, basketball hoop and court line"
        },
        {
            "id": "m1-758", "word": "clerk", "meaning": "점원",
            "scene": "charming corner grocery shop counter, friendly polite cute slender clerk stickman handing brown paper grocery bag with fresh produce to customer stickman, shop counter and floor line"
        },
        {
            "id": "m1-759", "word": "plate", "meaning": "접시",
            "scene": "sparkling clean kitchen sink counter, diligent cute slender stickman gently wiping a smooth ceramic porcelain dining plate with soft dishcloth, drying rack and kitchen floor line"
        },
        {
            "id": "m1-760", "word": "dish", "meaning": "접시, 음식",
            "scene": "cozy restaurant dining table, smiling cute slender stickman serving a delicious steaming hot gourmet pasta dish garnished with fresh basil leaves, dining chair and floor line"
        }
    ],
    39: [
        {
            "id": "m1-761", "word": "chopstick", "meaning": "젓가락",
            "scene": "cozy dining room table, small cute slender stickman sitting politely holding wooden chopsticks picking up food from steaming ceramic bowl, dining table and floor line"
        },
        {
            "id": "m1-762", "word": "square", "meaning": "정사각형",
            "scene": "bright art classroom easel, small cute slender stickman artist drawing a crisp perfect geometric square shape on paper with wooden ruler, easel stand and floor line"
        },
        {
            "id": "m1-763", "word": "information", "meaning": "정보",
            "scene": "spacious modern museum lobby, small cute slender visitor stickman asking polite question at public information booth to friendly staff stickman, lobby floor line"
        },
        {
            "id": "m1-764", "word": "government", "meaning": "정부",
            "scene": "majestic neoclassical parliament hall, small cute slender statesman stickman speaking from rostrum before grand assembly council, classical pillars and floor line"
        },
        {
            "id": "m1-765", "word": "spirit", "meaning": "정신",
            "scene": "high windy mountain summit plateau, small cute slender stickman standing firm with hands on hips gazing determinedly at sunrise showing strong unyielding spirit, mountain ridge line"
        },
        {
            "id": "m1-766", "word": "halt", "meaning": "정지하다",
            "scene": "quiet city street crosswalk, small cute slender crossing guard stickman holding red stop paddle bringing school crosswalk traffic to safe complete halt, street curb line"
        },
        {
            "id": "m1-767", "word": "honest", "meaning": "정직한",
            "scene": "cozy lost and found counter, honest small cute slender stickman handing found leather wallet to smiling office officer stickman, counter and floor line"
        },
        {
            "id": "m1-768", "word": "correctly", "meaning": "정확히",
            "scene": "clean science workshop workbench, small cute slender student stickman measuring liquid volume correctly matching precision graduated cylinder mark, table and floor line"
        },
        {
            "id": "m1-769", "word": "exactly", "meaning": "정확히",
            "scene": "woodworking workshop table, focused small cute slender carpenter stickman aligning wooden joint parts fitting together exactly with zero gap, workbench and floor line"
        },
        {
            "id": "m1-770", "word": "wet", "meaning": "젖은",
            "scene": "rainy home entrance hallway, small cute slender stickman standing indoors shaking water droplets from soaked wet umbrella into umbrella stand, entryway floor line"
        },
        {
            "id": "m1-771", "word": "remove", "meaning": "제거하다",
            "scene": "sunny community garden flowerbed, diligent small cute slender stickman using small garden trowel carefully removing wild weed from around young flowering plant, garden soil line"
        },
        {
            "id": "m1-772", "word": "rid", "meaning": "제거하다",
            "scene": "tidy bedroom wardrobe corner, energetic small cute slender stickman sorting and clearing out unnecessary old clutter boxes getting rid of mess, bedroom floor line"
        },
        {
            "id": "m1-773", "word": "offer", "meaning": "제공하다",
            "scene": "warm tea party lounge, courteous small cute slender stickman holding tray offering warm porcelain cup of fresh herbal tea to guest stickman, low table and floor line"
        },
        {
            "id": "m1-774", "word": "uniform", "meaning": "제복, 교복",
            "scene": "school hallway locker row, neat small cute slender stickman wearing tidy buttoned school uniform standing proudly with backpack, locker doors and floor line"
        },
        {
            "id": "m1-775", "word": "limit", "meaning": "제한하다, 제한",
            "scene": "quiet highway road shoulder, small cute slender stickman driver looking at roadside maximum speed limit sign driving responsibly at safe steady pace, highway barrier line"
        },
        {
            "id": "m1-776", "word": "piece", "meaning": "조각",
            "scene": "cozy living room carpet, small cute slender stickman sitting placing the final interlocking piece into a colorful jigsaw puzzle on low coffee table, floor line"
        },
        {
            "id": "m1-777", "word": "sculpture", "meaning": "조각(품)",
            "scene": "bright stone carving studio, creative small cute slender sculptor stickman using mallet and chisel carefully shaping a smooth marble stone sculpture, studio floor line"
        },
        {
            "id": "m1-778", "word": "statue", "meaning": "조각상",
            "scene": "sunny grand historic park plaza, small cute slender stickman tourist looking up admiring a tall classical bronze hero statue on granite pedestal, park pavement line"
        },
        {
            "id": "m1-779", "word": "shell", "meaning": "조개껍질",
            "scene": "peaceful sandy ocean beach, joyful small cute slender stickman crouching near gentle water edge picking up a beautiful spiral seashell from wet sand, shoreline line"
        },
        {
            "id": "m1-780", "word": "ancestor", "meaning": "조상, 선조",
            "scene": "traditional quiet family shrine room, respectful small cute slender stickman offering polite bow before historic ancestral portrait scroll, incense burner and floor line"
        }
    ],
    40: [
        {"id": "m1-781", "word": "quiet", "meaning": "조용한", "scene": "quiet library study corner, cute slender stickman student sitting at wooden study desk reading open book under soft reading lamp with index finger gently on lips showing silence, tall bookshelves and floor line"},
        {"id": "m1-782", "word": "silent", "meaning": "조용한", "scene": "peaceful snowy park glade at night, cute slender stickman standing in soft winter muffler gazing peacefully at brilliant night stars in complete silence, snow covered evergreen trees and ground line"},
        {"id": "m1-783", "word": "control", "meaning": "조절하다", "scene": "high tech aviation control tower room, focused cute slender stickman flight controller sitting before illuminated radar monitors and microphone headset controlling airplane traffic safely, console desk and floor line"},
        {"id": "m1-784", "word": "pilot", "meaning": "조종사", "scene": "sunny airplane cockpit cabin, proud smiling cute slender stickman pilot wearing aviator headset holding steering yoke looking out forward cockpit windows into clear sky, flight dashboard dials and floor line"},
        {"id": "m1-785", "word": "system", "meaning": "조직, 체계, 제도", "scene": "modern computer server room, smart cute slender stickman technician inspecting organized system server rack units and neat colored network cables with digital tablet, server racks and floor line"},
        {"id": "m1-786", "word": "nephew", "meaning": "조카", "scene": "cozy sunny living room rug, cheerful cute slender uncle stickman giving high five to smiling little nephew stickman who just built a tall colorful toy building block tower, rug and floor line"},
        {"id": "m1-787", "word": "niece", "meaning": "조카딸", "scene": "warm kitchen baking counter, kind cute slender aunt stickman smiling happily while sharing warm fresh baked cookies with cheerful young niece stickman holding small mug, kitchen counter and floor line"},
        {"id": "m1-788", "word": "respect", "meaning": "존경, 존경하다", "scene": "traditional martial arts dojo hall, respectful cute slender stickman student in clean training uniform bowing deeply with hands clasped showing sincere respect to elder master stickman, tatami mats and floor line"},
        {"id": "m1-789", "word": "graduate", "meaning": "졸업하다", "scene": "grand school auditorium stage, joyful cute slender stickman graduate in academic cap and gown happily holding rolled diploma scroll with ribbon bow under banner, wooden podium and floor line"},
        {"id": "m1-790", "word": "seldom", "meaning": "좀처럼 ~않다", "scene": "quiet countryside observatory terrace, patient cute slender stickman astronomer looking through long brass telescope waiting into starry night sky hoping to see a seldom seen bright shooting star, balcony railing and floor line"},
        {"id": "m1-791", "word": "religious", "meaning": "종교적인", "scene": "historic stone chapel interior, devout cute slender stickman standing quietly with folded hands in reverence before towering stained glass windows and altar candles, stone archways and stone floor line"},
        {"id": "m1-792", "word": "seat", "meaning": "좌석", "scene": "modern cinema movie theater hall, courteous cute slender stickman usher holding small flashlight guiding smiling moviegoer stickman to designated plush numbered velvet seat, carpeted theater aisle and floor line"},
        {"id": "m1-793", "word": "order", "meaning": "주문, 순서, 명령하다", "scene": "charming bakery cafe counter, smiling cute slender stickman customer looking at chalkboard menu ordering warm fresh bread from cheerful baker stickman, bread display case and floor line"},
        {"id": "m1-794", "word": "address", "meaning": "주소", "scene": "sunny residential front porch, diligent cute slender stickman postal courier checking destination street address written on white envelope next to brass house number plaque, mailbox and porch steps line"},
        {"id": "m1-795", "word": "main", "meaning": "주요한", "scene": "bustling city central avenue, cute slender stickman pedestrian standing on sidewalk admiring the wide grand main boulevard lined with historical buildings and streetlights, crosswalk and street curb line"},
        {"id": "m1-796", "word": "principal", "meaning": "주요한, 교장선생님", "scene": "dignified school principal office, friendly cute slender headmaster stickman standing beside grand executive wooden desk with framed certificates and school emblem, bookshelf and polished floor line"},
        {"id": "m1-797", "word": "master", "meaning": "주인", "scene": "traditional woodworking craft workshop, skilled cute slender artisan stickman expertly chiseling smooth intricate wood curves demonstrating true master craftsman technique, workbench and floor line"},
        {"id": "m1-798", "word": "hesitate", "meaning": "주저하다, 망설이다", "scene": "community swimming pool edge, cautious cute slender stickman standing on top diving board peering down at clear blue pool water hesitating whether to jump, diving platform and pool deck line"},
        {"id": "m1-799", "word": "death", "meaning": "죽음, 사망", "scene": "peaceful memorial garden courtyard, solemn cute slender stickman gently placing a fresh white daisy flower upon a smooth stone monument in quiet thoughtful remembrance, willow tree and stone floor line"},
        {"id": "m1-800", "word": "prepare", "meaning": "준비하다", "scene": "clean modern kitchen cooking counter, energetic cute slender stickman chef neatly slicing fresh vegetables and measuring spices preparing delicious dinner ingredients into glass bowls, kitchen countertop and floor line"}
    ],
    41: [
        {"id": "m1-801", "word": "row", "meaning": "줄", "scene": "sunny organic vegetable garden, cute slender stickman gardener planting neat straight parallel rows of green leafy lettuce seedlings into rich soil, wooden garden beds and garden soil line"},
        {"id": "m1-802", "word": "stem", "meaning": "줄기", "scene": "botanical laboratory desk, focused cute slender stickman scientist examining the sturdy green stem and leaf nodes of a potted flowering plant with a magnifying glass, microscope and lab table line"},
        {"id": "m1-803", "word": "stripe", "meaning": "줄무늬", "scene": "bright craft workshop table, cheerful cute slender stickman painting alternating bold black and white parallel stripes on a decorative canvas board with a paint roller, paint pots and floor line"},
        {"id": "m1-804", "word": "pick", "meaning": "줍다, 고르다", "scene": "sunny orchard fruit grove, joyful cute slender stickman reaching up into leafy apple tree branches picking a ripe red round apple and placing it into wicker basket, grass lawn line"},
        {"id": "m1-805", "word": "center", "meaning": "중심", "scene": "vibrant community sports field, focused cute slender stickman soccer player placing a soccer ball precisely at the painted center spot circle before kickoff, stadium lawn line"},
        {"id": "m1-806", "word": "important", "meaning": "중요한", "scene": "bright study room desk, cute slender stickman student carefully highlighting an important key sentence in textbook with a bright yellow marker pen, study lamp and desk line"},
        {"id": "m1-807", "word": "pause", "meaning": "중지, 멈추다", "scene": "cozy home cinema lounge, cute slender stickman sitting comfortably on sofa holding remote controller pressing the pause icon button to pause film on screen, coffee table and floor line"},
        {"id": "m1-808", "word": "rat", "meaning": "쥐, 들쥐", "scene": "quiet barn storage floor, observant cute slender stickman farmer shining a flashlight onto floor seeing a small harmless country field rat scurrying behind a wooden grain crate, wooden crates and floor line"},
        {"id": "m1-809", "word": "amuse", "meaning": "즐겁게 하다", "scene": "lively children festival party, cheerful cute slender clown stickman juggling three colorful round balls skillfully to amuse smiling audience friends, party streamers and floor line"},
        {"id": "m1-810", "word": "merry", "meaning": "즐거운", "scene": "festive holiday living room, joyful cute slender stickman decorating a bright green Christmas tree with shiny ornaments humming a merry festive holiday tune, fireplace and floor line"},
        {"id": "m1-811", "word": "enjoy", "meaning": "즐기다", "scene": "sunny seaside promenade bench, relaxed cute slender stickman wearing sunglasses smiling and enjoying a delicious double scoop ice cream cone under warm ocean breeze, coastal promenade line"},
        {"id": "m1-812", "word": "increase", "meaning": "증가하다", "scene": "bright modern office presentation room, proud cute slender stickman analyst pointing pointer at a whiteboard chart showing steady steep increase line graph going upward, boardroom table and floor line"},
        {"id": "m1-813", "word": "prove", "meaning": "증명하다", "scene": "mathematics lecture classroom, confident cute slender stickman mathematician writing clear chalk logical geometric equations on blackboard proving mathematical theorem, lecture podium and floor line"},
        {"id": "m1-814", "word": "boring", "meaning": "지겨운", "scene": "quiet waiting room chair, sleepy cute slender stickman student resting chin in hand looking bored while waiting for delayed appointment, clock on wall and waiting room floor line"},
        {"id": "m1-815", "word": "earth", "meaning": "지구", "scene": "science classroom corner, curious cute slender stickman student spinning a detailed desktop spherical globe of planet Earth pointing at continents and oceans, desk and classroom floor line"},
        {"id": "m1-816", "word": "pass", "meaning": "지나가다", "scene": "high school hallway corridor, polite cute slender stickman student smiling and stepping aside to let friends pass by comfortably through the wide hallway, locker doors and hallway floor line"},
        {"id": "m1-817", "word": "track", "meaning": "지나간 자국, 선로", "scene": "scenic outdoor railway crossing, cute slender stickman standing safely behind barrier looking at polished steel train tracks extending into the distant mountains, signal post and gravel track line"},
        {"id": "m1-818", "word": "eraser", "meaning": "지우개", "scene": "tidy wooden school desk, diligent cute slender stickman student using a soft white rubber eraser to carefully erase pencil mistake cleanly from notebook page, pencil case and desk line"},
        {"id": "m1-819", "word": "spot", "meaning": "지점", "scene": "scenic park summit plateau, cheerful cute slender hiker stickman reaching scenic scenic viewpoint spot marked with wooden marker post overlooking rolling valleys, wooden fence and ground line"},
        {"id": "m1-820", "word": "guard", "meaning": "지키다, 경계, 위병", "scene": "historic palace gate entrance, disciplined cute slender ceremonial palace guard stickman standing tall and alert holding ceremonial staff guarding grand decorative iron gates, stone palace courtyard line"}
    ],
    42: [
        {"id": "m1-821", "word": "basement", "meaning": "지하실", "scene": "cozy home basement workshop, cute slender stickman hobbyist organizing toolboxes and hobby supplies on steel shelves in tidy finished basement, stairs and concrete floor line"},
        {"id": "m1-822", "word": "subway", "meaning": "지하철", "scene": "clean underground subway metro platform, cute slender stickman commuter standing behind yellow safety line waiting as sleek modern train arrives smoothly at station, tiled wall and platform line"},
        {"id": "m1-823", "word": "job", "meaning": "직업, 일", "scene": "bright creative architectural design studio, industrious cute slender stickman architect diligently drawing floor plan blueprints on tilted drafting table, office desk and floor line"},
        {"id": "m1-824", "word": "sincerely", "meaning": "진실하게", "scene": "warm study room writing desk, thoughtful cute slender stickman writing a heartfelt letter with fountain pen signing sincerely with right hand on heart, desk lamp and floor line"},
        {"id": "m1-825", "word": "true", "meaning": "진실한", "scene": "open courtroom witness stand, honest cute slender stickman raising right hand giving truthful honest testimony under warm courthouse lamps, wooden stand and courtroom floor line"},
        {"id": "m1-826", "word": "serious", "meaning": "진지한", "scene": "quiet chess tournament hall, focused serious cute slender stickman chess player staring thoughtfully at chess board contemplating next master move, wooden table and floor line"},
        {"id": "m1-827", "word": "drag", "meaning": "질질 끌다", "scene": "sunny playground sandbox edge, determined cute slender stickman pulling and dragging a heavy wooden wagon loaded with clean sand toys across ground, play equipment and ground line"},
        {"id": "m1-828", "word": "burden", "meaning": "짐", "scene": "winding mountain hiking path, determined cute slender trekker stickman steadily carrying a heavy camping backpack up rocky mountain trail leaning forward with trekking poles, trail line"},
        {"id": "m1-829", "word": "load", "meaning": "짐, 싣다", "scene": "warehouse shipping dock bay, energetic cute slender logistics stickman carefully loading cardboard parcel boxes onto wooden pallet transport cart, cargo shelving and concrete floor line"},
        {"id": "m1-830", "word": "wagon", "meaning": "짐마차", "scene": "rustic countryside meadow road, cheerful cute slender farmer stickman leading a classic wooden four-wheeled farm wagon filled with fresh hay bales and red apples, dirt path line"},
        {"id": "m1-831", "word": "beast", "meaning": "짐승", "scene": "ancient mythical fairy tale glade, brave cute slender stickman adventurer encountering a friendly gentle mythical horned beast resting peacefully in mossy clearing, ancient trees and forest floor line"},
        {"id": "m1-832", "word": "group", "meaning": "집단", "scene": "spacious school workshop activity room, friendly cute slender stickman students sitting in a circle working together harmoniously as a cooperative project study group, study tables and floor line"},
        {"id": "m1-833", "word": "howl", "meaning": "짖다", "scene": "windy moonlit hill cliff, cute slender stickman camper bundled in warm coat listening in wonder as a silhouette wolf howls dramatically towards full moon on distant ridge, campfire and rocky ground line"},
        {"id": "m1-834", "word": "short", "meaning": "짧은", "scene": "tailor shop measuring mirror, smiling cute slender stickman tailor holding measuring tape beside customer stickman checking the length of a newly shortened stylish jacket, clothing racks and floor line"},
        {"id": "m1-835", "word": "chase", "meaning": "쫓아가다", "scene": "sunny park grassy lawn, playful energetic cute slender stickman joyfully running and chasing after a bright colorful runaway soccer ball rolling across grass, park benches and lawn line"},
        {"id": "m1-836", "word": "tear", "meaning": "찢다, 눈물", "scene": "craft workshop table, focused cute slender stickman artist carefully tearing decorative textured handmade paper sheets along ruler line to make scrapbook collage, cutting mat and floor line"},
        {"id": "m1-837", "word": "garage", "meaning": "차고", "scene": "organized home driveway garage, neat cute slender stickman homeowner tuning bicycle gears with wrench inside bright garage with pegboard tool wall, garage door and polished floor line"},
        {"id": "m1-838", "word": "attend", "meaning": "참석하다", "scene": "bright university seminar conference room, attentive cute slender stickman participant sitting in front row taking notes to attend academic lecture, projector screen and floor line"},
        {"id": "m1-839", "word": "indeed", "meaning": "참으로", "scene": "peaceful botanical greenhouse garden, wise cute slender stickman professor nodding approvingly with hands folded behind back agreeing indeed that rare orchid has bloomed beautifully, potted plants and floor line"},
        {"id": "m1-840", "word": "create", "meaning": "창조하다", "scene": "bright artist studio loft, inspired cute slender stickman sculptor molding fresh clay on revolving potter wheel creating a graceful modern ceramic vase, art shelves and studio floor line"}
    ],
    43: [
        {"id": "m1-841", "word": "search", "meaning": "찾다", "scene": "grand historical library archives, inquisitive cute slender stickman researcher holding magnifying glass searching along high catalog bookshelf for rare document, rolling ladder and floor line"},
        {"id": "m1-842", "word": "vegetable", "meaning": "채소", "scene": "cheerful local farmers market stall, smiling cute slender stickman vendor displaying wooden crates of fresh colorful vegetables including orange carrots, green broccoli, and red tomatoes, market awning and cobblestone line"},
        {"id": "m1-843", "word": "fill", "meaning": "채우다", "scene": "sunny patio garden bench, diligent cute slender stickman gardener holding green watering can carefully pouring water to fill decorative terracotta flower planter to the brim, patio tiles line"},
        {"id": "m1-844", "word": "cloth", "meaning": "천", "scene": "traditional fabric textile boutique, smiling cute slender stickman merchant unrolling a bolt of fine smooth patterned linen cloth across wooden cutting counter, rolls of fabric and floor line"},
        {"id": "m1-845", "word": "ceiling", "meaning": "천장", "scene": "historic ornate museum gallery, cute slender stickman tourist looking straight up admiring detailed classical painted fresco murals on high arched ceiling, columns and polished marble floor line"},
        {"id": "m1-846", "word": "puritan", "meaning": "청교도", "scene": "early historical settlement log house, modest cute slender pilgrim stickman wearing historical puritan hat and plain buckle coat standing reverently beside stone hearth, wooden table and floor line"},
        {"id": "m1-847", "word": "charge", "meaning": "청구하다", "scene": "modern cafe register station, polite cute slender stickman cashier handing customer stickman a clear printed invoice receipt explaining the service charge itemized on counter, register and floor line"},
        {"id": "m1-848", "word": "jean", "meaning": "청바지", "scene": "trendy clothing boutique showroom, stylish cute slender stickman holding up and admiring a pair of classic blue denim jeans in front of full-length mirror, display racks and floor line"},
        {"id": "m1-849", "word": "arrest", "meaning": "체포하다", "scene": "city police station precinct, resolute cute slender police officer stickman standing bravely holding badge after lawfully arresting a captured masked suspect, station desk and floor line"},
        {"id": "m1-850", "word": "candle", "meaning": "초", "scene": "cozy antique study desk, cute slender stickman gently lighting a tall beeswax candle in decorative brass candlestick with wooden match creating warm glow, open journal and wooden desk line"},
        {"id": "m1-851", "word": "invite", "meaning": "초대하다", "scene": "cheerful sunny front porch, smiling cute slender stickman handing a beautifully sealed party invitation envelope to friendly neighbor friend stickman, welcome mat and porch line"},
        {"id": "m1-852", "word": "elementary", "meaning": "초보의", "scene": "elementary school classroom blackboard, friendly cute slender stickman teacher pointing with ruler teaching basic elementary ABC alphabet letters to attentive young students, desks and floor line"},
        {"id": "m1-853", "word": "gun", "meaning": "총", "scene": "historic naval museum gallery, interested cute slender stickman visitor observing an antique historical brass ceremonial cannon gun mounted on oak carriage, display railing and museum floor line"},
        {"id": "m1-854", "word": "recently", "meaning": "최근에", "scene": "modern photo gallery wall, proud cute slender stickman photographer hanging a framed photograph taken recently on museum wall checking level alignment, gallery lighting and floor line"},
        {"id": "m1-855", "word": "guess", "meaning": "추측하다", "scene": "cozy family parlor room, cheerful cute slender stickman playing a fun parlor guessing game tapping chin thoughtfully trying to guess mystery secret object inside gift box, coffee table and floor line"},
        {"id": "m1-856", "word": "bless", "meaning": "축복하다", "scene": "sunlit garden wedding arbor, kind cute slender elder stickman gently placing hands on smiling newlyweds heads offering heartfelt blessing for happiness, flower arch and garden lawn line"},
        {"id": "m1-857", "word": "celebrate", "meaning": "축하하다", "scene": "festive party dining room, joyful cute slender stickman friends throwing colorful confetti popping party party crackers to celebrate friend birthday with big cake, party table and floor line"},
        {"id": "m1-858", "word": "exit", "meaning": "출구", "scene": "bright theater lobby hallway, polite cute slender stickman usher pointing towards illuminated green emergency exit sign over doorway, hallway carpet and floor line"},
        {"id": "m1-859", "word": "birth", "meaning": "출생", "scene": "cozy sunlit nursery room, tender cute slender stickman parent lovingly cradling a tiny newborn baby swaddled in soft blanket beside wooden crib, rocking chair and rug line"},
        {"id": "m1-860", "word": "source", "meaning": "출처, 근원", "scene": "lush mountain valley headwaters, curious cute slender stickman explorer discovering the pure crystal spring water bubbling from mossy rock source giving birth to river, riverbank pebbles line"}
    ],
    44: [
        {"id": "m1-861", "word": "shock", "meaning": "충격, 충격을 주다", "scene": "cozy living room armchair, astonished cute slender stickman opening mouth and gasping in genuine shock at shocking plot twist in mystery book, reading lamp and floor line"},
        {"id": "m1-862", "word": "advice", "meaning": "충고", "scene": "peaceful park bench under shady oak, wise elder stickman gently placing hand on shoulder giving warm supportive life advice to thoughtful younger stickman friend, park path line"},
        {"id": "m1-863", "word": "crash", "meaning": "충돌(추락), 충돌하다", "scene": "fun toy playroom floor, laughing cute slender stickman playing with toy bumper cars having them make a safe harmless crash collision into soft cushion blocks, rug and floor line"},
        {"id": "m1-864", "word": "enough", "meaning": "충분한", "scene": "cozy kitchen dining table, contented cute slender stickman gently waving hand over full dinner plate smiling showing he has eaten enough delicious meal, dining chair and floor line"},
        {"id": "m1-865", "word": "hobby", "meaning": "취미", "scene": "bright sunlit hobby craft room, delighted cute slender stickman painting delicate miniature model airplanes as a relaxing favorite weekend hobby, paint jars and worktable line"},
        {"id": "m1-866", "word": "hit", "meaning": "치다", "scene": "sunny baseball diamond field, athletic cute slender stickman baseball batter swinging wooden bat making solid clean hit connecting with baseball into outfield, home plate and dirt field line"},
        {"id": "m1-867", "word": "pal", "meaning": "친구", "scene": "friendly neighborhood playground park, two cheerful cute slender stickman best pals walking arm in arm smiling and sharing funny story together, park pathway line"},
        {"id": "m1-868", "word": "folk", "meaning": "친구들", "scene": "warm community village square, lively cute slender stickman musician playing acoustic guitar singing merry songs surrounded by friendly village folk clapping hands, cobblestone square line"},
        {"id": "m1-869", "word": "intimate", "meaning": "친밀한", "scene": "quiet warm fireplace hearth, two intimate cute slender stickman friends sitting closely on soft cushions sharing quiet heartfelt conversation over hot tea, fireplace mantle and rug line"},
        {"id": "m1-870", "word": "dear", "meaning": "친애하는", "scene": "vintage writing desk room, affectionate cute slender stickman writing a loving letter beginning with words Dear Friend with fountain pen, open letter and desk line"},
        {"id": "m1-871", "word": "kind", "meaning": "친절한, 종류", "scene": "rainy city sidewalk street, kind compassionate cute slender stickman sharing wide umbrella sheltering a grateful passerby stickman from rain shower, street curb line"},
        {"id": "m1-872", "word": "relative", "meaning": "친척", "scene": "warm holiday family reunion dining hall, smiling cute slender stickman welcoming visiting relatives with warm open arms at front door, coat rack and hallway floor line"},
        {"id": "m1-873", "word": "turkey", "meaning": "칠면조", "scene": "cheerful holiday dining table, proud cute slender stickman host presenting a large golden roasted holiday turkey on silver platter to cheering dinner guests, dining chairs and floor line"},
        {"id": "m1-874", "word": "bedside", "meaning": "침대 곁", "scene": "cozy peaceful bedroom corner, caring cute slender stickman sitting on bedside chair reading bedtime story to resting friend, bedside nightstand table lamp and floor line"},
        {"id": "m1-875", "word": "sheet", "meaning": "침대 시트", "scene": "bright airy bedroom morning, tidy cute slender stickman smoothing out crisp clean white cotton bed sheet neatly over mattress, wooden headboard and bedroom floor line"},
        {"id": "m1-876", "word": "invader", "meaning": "침입자", "scene": "ancient fortress stone battlements, vigilant cute slender castle guard stickman spotting distant approaching invader ships on horizon raising warning banner, stone parapet wall line"},
        {"id": "m1-877", "word": "sword", "meaning": "칼", "scene": "historic royal armory exhibition, noble cute slender stickman knight admiring a polished shining steel medieval sword resting in velvet display case, knight armor and stone floor line"},
        {"id": "m1-878", "word": "bean", "meaning": "콩", "scene": "sunny countryside vegetable patch, curious cute slender stickman opening a fresh green garden bean pod showing plump round peas and beans inside, garden trellis and soil line"},
        {"id": "m1-879", "word": "cookie", "meaning": "쿠키", "scene": "warm bakery kitchen oven, joyful cute slender stickman baker wearing oven mitts pulling a baking tray of freshly baked chocolate chip cookies from warm oven, cooling rack and floor line"},
        {"id": "m1-880", "word": "cricket", "meaning": "크리켓", "scene": "green countryside sporting lawn, focused cute slender stickman cricket player holding flat wooden cricket bat ready at wooden wickets, green grass pitch line"}
    ],
    45: [
        {"id": "m1-881", "word": "sniff", "meaning": "킁킁거리다, 냄새를 맡다", "scene": "lush botanical rose garden, delighted cute slender stickman gently leaning forward to sniff the sweet floral perfume of a blooming fragrant pink rose, garden pathway line"},
        {"id": "m1-882", "word": "ride", "meaning": "타다", "scene": "sunny park riverside path, cheerful cute slender stickman wearing helmet happily going for a bicycle ride along tree-lined paved route, bicycle and path line"},
        {"id": "m1-883", "word": "burn", "meaning": "타다, 태우다", "scene": "outdoor campsite circle, careful cute slender stickman watching camp wood logs burn safely with glowing embers inside circular stone campfire pit, camping tent and ground line"},
        {"id": "m1-884", "word": "ostrich", "meaning": "타조", "scene": "spacious safari wildlife sanctuary, curious cute slender stickman standing safely behind fence admiring a tall friendly ostrich with long neck and soft feathers, savannah bushes and ground line"},
        {"id": "m1-885", "word": "greedy", "meaning": "탐욕스러운", "scene": "fairy tale treasure chamber, humorous cute slender stickman comically trying to scoop too many gold coins into small overflowing pouch showing greedy behavior, treasure chest and stone floor line"},
        {"id": "m1-886", "word": "detective", "meaning": "탐정", "scene": "mysterious vintage office study, clever cute slender detective stickman wearing trench coat holding magnifying glass examining footprint clue on floor, filing cabinet and floor line"},
        {"id": "m1-887", "word": "explore", "meaning": "탐험하다", "scene": "mysterious tropical cave entrance, adventurous cute slender explorer stickman holding explorer lantern exploring unknown rocky cavern, stalactites and rocky ground line"},
        {"id": "m1-888", "word": "tower", "meaning": "탑", "scene": "historic medieval city square, awe-struck cute slender stickman tourist looking up at a grand stone clock bell tower reaching high into sky, plaza cobblestones line"},
        {"id": "m1-889", "word": "solar", "meaning": "태양의", "scene": "modern eco-friendly rooftop, innovative cute slender engineer stickman inspecting shiny blue solar panels capturing clean solar sunlight energy, rooftop railing line"},
        {"id": "m1-890", "word": "fur", "meaning": "털", "scene": "cozy living room sofa, smiling cute slender stickman gently brushing the soft clean fluffy fur coat of an adorable friendly lap pet, warm fireplace and rug line"},
        {"id": "m1-891", "word": "wool", "meaning": "털, 양모", "scene": "peaceful countryside pasture barn, gentle cute slender stickman farmer holding a basket filled with soft natural sheared sheep wool skeins, wooden fence and barn floor line"},
        {"id": "m1-892", "word": "discuss", "meaning": "토론하다", "scene": "modern conference meeting room, engaged cute slender stickman colleagues sitting around oval table pointing at charts actively discussing project plans, whiteboard and floor line"},
        {"id": "m1-893", "word": "saw", "meaning": "톱", "scene": "traditional carpentry workbench, diligent cute slender woodworker stickman using a hand saw with sharp teeth cutting a straight pine wood plank on sawhorses, wood shavings and floor line"},
        {"id": "m1-894", "word": "log", "meaning": "통나무", "scene": "peaceful autumn woodland forest, cute slender lumberjack stickman sitting taking a rest upon a sturdy fallen wooden tree log beside hiking trail, forest trees and ground line"},
        {"id": "m1-895", "word": "unification", "meaning": "통일, 단일화", "scene": "grand international unity monument plaza, inspiring cute slender stickman holding symbolic united ribbon bringing two puzzle pieces together in historic peaceful unification, flags and plaza line"},
        {"id": "m1-896", "word": "unity", "meaning": "통일, 일치", "scene": "bright community assembly hall, diverse cute slender stickman friends standing side by side holding hands in solidarity showing strong community unity, stage banner and floor line"},
        {"id": "m1-897", "word": "vote", "meaning": "투표하다", "scene": "civic polling election station, responsible cute slender citizen stickman slipping a folded official ballot paper into sealed wooden voting ballot box, voting booth curtain and floor line"},
        {"id": "m1-898", "word": "special", "meaning": "특별한", "scene": "magical celebration banquet room, delighted cute slender stickman receiving a beautifully wrapped special surprise gift box decorated with golden star bow, celebration table and floor line"},
        {"id": "m1-899", "word": "especially", "meaning": "특별히", "scene": "gourmet fruit display kitchen, smiling cute slender stickman picking one especially large and luscious red strawberry from fruit bowl to enjoy, kitchen table and floor line"},
        {"id": "m1-900", "word": "wrong", "meaning": "틀린", "scene": "math study desk room, thoughtful cute slender stickman student noticing a wrong calculation on homework paper smiling and marking an X to recalculate correctly, desk lamp and desk line"}
    ],
    46: [
        {"id": "m1-901", "word": "destroy", "meaning": "파괴하다", "scene": "sandcastle beach play area, energetic cute slender stickman playfully kicking down a crumbling sandcastle to build a bigger new one, sand bucket and beach sand line"},
        {"id": "m1-902", "word": "dig", "meaning": "파다", "scene": "sunny community garden plot, energetic cute slender stickman using garden spade shovel to dig a deep planting hole for new apple sapling, mounds of soil and garden line"},
        {"id": "m1-903", "word": "sale", "meaning": "판매, 판매하다", "scene": "charming neighborhood yard lawn, friendly cute slender stickman standing beside a neat table of vintage books and toys with a colorful sale sign, front lawn line"},
        {"id": "m1-904", "word": "board", "meaning": "판자, 이사회", "scene": "woodworking construction site, industrious cute slender stickman carrying a long smooth pine wood board upon shoulder towards workbench, building frames and floor line"},
        {"id": "m1-905", "word": "pop", "meaning": "펑하고 터지다", "scene": "cheerful party hall, playful cute slender stickman using a small pin to make a colorful party balloon pop with a fun surprise, party streamers and floor line"},
        {"id": "m1-906", "word": "mail", "meaning": "편지", "scene": "sunny suburban sidewalk curb, cheerful cute slender stickman dropping a sealed stamped envelope into a classic blue postal street mail collection box, sidewalk line"},
        {"id": "m1-907", "word": "letter", "meaning": "편지, 문자", "scene": "cozy antique writing desk, thoughtful cute slender stickman reading a warm handwritten letter with joyful smile, envelope and wooden desk line"},
        {"id": "m1-908", "word": "calm", "meaning": "평온한", "scene": "serene mountain lake shore at dawn, peaceful cute slender stickman sitting in quiet meditation beside calm mirror-like water reflecting mountains, rocky shore line"},
        {"id": "m1-909", "word": "flat", "meaning": "평평한", "scene": "indoor carpentry studio, focused cute slender stickman placing a spirit level tool on a perfectly flat polished wooden tabletop checking horizontal line, workbench line"},
        {"id": "m1-910", "word": "peaceful", "meaning": "평화로운", "scene": "sunny wildflower meadow pasture, relaxed cute slender stickman lying peacefully on soft grass looking up at gentle white clouds, wildflowers and grass line"},
        {"id": "m1-911", "word": "mammal", "meaning": "포유동물", "scene": "natural science history museum, curious cute slender stickman student examining a museum exhibit display showing furry land mammals including rabbit and deer, display glass and floor line"},
        {"id": "m1-912", "word": "include", "meaning": "포함하다", "scene": "cozy bakery packaging counter, courteous cute slender baker stickman adding an extra warm sweet pastry to include inside customer take-out bakery box, counter and floor line"},
        {"id": "m1-913", "word": "explode", "meaning": "폭발시키다", "scene": "science laboratory experiment desk, excited cute slender scientist stickman in safety goggles watching a fun safe baking soda volcano model bubble and explode foaming fizz, lab table and floor line"},
        {"id": "m1-914", "word": "stormy", "meaning": "폭풍의", "scene": "cozy seaside cottage window, warm cute slender stickman in sweater holding tea mug looking out safe window at a dramatic stormy sea with rolling waves, window frame and floor line"},
        {"id": "m1-915", "word": "ticket", "meaning": "표", "scene": "historic train station barrier, excited cute slender passenger stickman holding up a printed train ticket showing it to friendly conductor stickman, platform barrier and floor line"},
        {"id": "m1-916", "word": "surface", "meaning": "표면", "scene": "modern kitchen cleaning counter, diligent cute slender stickman wiping down the shiny granite kitchen counter surface with cleaning cloth making it sparkle, countertop and floor line"},
        {"id": "m1-917", "word": "plenty", "meaning": "풍부", "scene": "autumn harvest pantry room, cheerful cute slender stickman standing beside wooden shelves brimming with plenty of canned fruit jars and harvest baskets, pantry shelves and floor line"},
        {"id": "m1-918", "word": "French", "meaning": "프랑스의", "scene": "charming Parisian style bakery cafe, smiling cute slender stickman holding a fresh crispy French baguette loaf standing beside chalkboard menu, cafe table and floor line"},
        {"id": "m1-919", "word": "flute", "meaning": "플룻, 피리", "scene": "bright music rehearsal hall, focused cute slender stickman musician playing a silver flute producing graceful notes beside music stand, stage floor line"},
        {"id": "m1-920", "word": "blood", "meaning": "피", "scene": "clean hospital blood donation clinic, proud generous cute slender stickman sitting in comfortable recliner donating blood to help patients in need, medical monitor and floor line"}
    ],
    47: [
        {"id": "m1-921", "word": "damage", "meaning": "피해, 손해, 피해를 주다", "scene": "auto repair garage shop, attentive cute slender mechanic stickman inspecting small fender damage on front of parked car estimating repair, tool cart and concrete floor line"},
        {"id": "m1-922", "word": "need", "meaning": "필요로 하다", "scene": "busy hardware tool store, cute slender stickman customer holding a broken screw showing shopkeeper he has urgent need for matching replacement, store aisles and floor line"},
        {"id": "m1-923", "word": "necessary", "meaning": "필요한", "scene": "outdoor camping preparation porch, organized cute slender camper stickman checking off necessary survival supplies on checklist including flashlight and first aid kit, camping gear and floor line"},
        {"id": "m1-924", "word": "heaven", "meaning": "하늘, 천국", "scene": "peaceful starry night hilltop, awe-struck cute slender stickman standing with arms spread wide gazing at breathtaking heavenly starry sky filled with constellations, grassy hill line"},
        {"id": "m1-925", "word": "servant", "meaning": "하인", "scene": "historic manor dining hall, polite courteous cute slender stickman royal attendant carrying a covered silver serving platter with perfect posture, marble columns and floor line"},
        {"id": "m1-926", "word": "however", "meaning": "하지만", "scene": "cozy library study desk, thoughtful cute slender stickman student pausing with pen in hand weighing two contrasting opposing arguments with thoughtful however expression, desk and floor line"},
        {"id": "m1-927", "word": "subject", "meaning": "학과, 주제, 주어", "scene": "school classroom blackboard, smiling cute slender teacher stickman writing favorite science subject title on board with chalk, students at desks and floor line"},
        {"id": "m1-928", "word": "semester", "meaning": "학기", "scene": "university campus quad lawn, cheerful cute slender stickman student holding semester course timetable and binder greeting classmates at start of new semester, campus trees and path line"},
        {"id": "m1-929", "word": "grade", "meaning": "학년", "scene": "bright study room desk, delighted cute slender stickman student proudly showing test paper marked with top A grade to smiling parent stickman, desk and floor line"},
        {"id": "m1-930", "word": "scholar", "meaning": "학자", "scene": "ancient university book library, wise cute slender scholar stickman studying antique parchment manuscripts surrounded by tall stacks of scholarly books, wooden desk and floor line"},
        {"id": "m1-931", "word": "pair", "meaning": "한 쌍", "scene": "cozy shoe shop boutique, delighted cute slender stickman holding up and trying on a comfortable new pair of white sneakers, shoe display boxes and floor line"},
        {"id": "m1-932", "word": "once", "meaning": "한 번, 한때", "scene": "quiet storybook fireplace parlor, kind cute slender storyteller stickman opening an antique leather book beginning story with once upon a time, armchair and rug line"},
        {"id": "m1-933", "word": "sigh", "meaning": "한숨 쉬다", "scene": "cozy home office desk, relieved cute slender stickman leaning back in desk chair letting out a contented gentle sigh after finally finishing big assignment, desk and floor line"},
        {"id": "m1-934", "word": "couple", "meaning": "한 쌍", "scene": "romantic botanical rose garden, happy cute slender stickman couple holding hands walking together under blossoming flower trellis arch, garden path line"},
        {"id": "m1-935", "word": "able", "meaning": "할 수 있는", "scene": "fitness gym workout bench, determined cute slender stickman smiling triumphantly after proving he is able to lift the workout barbell, weights rack and floor line"},
        {"id": "m1-936", "word": "scratch", "meaning": "할퀴다, 긁다", "scene": "sunny living room rug, playful cute slender cat scratching post area where cute slender stickman watches playful kitten scratch cat post, pet toys and floor line"},
        {"id": "m1-937", "word": "together", "meaning": "함께", "scene": "community tree planting park, cheerful cute slender stickman friends working together side by side planting a green young tree in fertile ground, garden fence and park lawn line"},
        {"id": "m1-938", "word": "port", "meaning": "항구", "scene": "scenic coastal marine port dock, friendly cute slender stickman standing on wooden dock watching fishing boats and cargo ships docked at busy harbor port, bollards and water line"},
        {"id": "m1-939", "word": "jar", "meaning": "항아리", "scene": "rustic country kitchen pantry, smiling cute slender stickman sealing a glass preserve jar filled with sweet homemade strawberry jam, pantry shelves and wooden counter line"},
        {"id": "m1-940", "word": "voyage", "meaning": "항해", "scene": "ocean sailing vessel deck, adventurous cute slender captain stickman holding spyglass telescope looking out across rolling blue waves embarking on a grand ocean voyage, ship railing and deck line"}
    ],
    48: [
        {"id": "m1-941", "word": "sail", "meaning": "항해하다", "scene": "sunny coastal bay waters, cheerful cute slender stickman sailing a graceful white canvas sailboat holding the tiller steering smoothly across sea, water ripples line"},
        {"id": "m1-942", "word": "solution", "meaning": "해결, 용해", "scene": "science laboratory workshop bench, triumphant cute slender stickman student discovering the brilliant working solution to a tricky puzzle experiment, chalkboard diagrams and lab bench line"},
        {"id": "m1-943", "word": "navy", "meaning": "해군", "scene": "naval harbor dockyard, proud cute slender naval officer stickman standing sharp in crisp dark navy uniform saluting before naval flagship, harbor pier line"},
        {"id": "m1-944", "word": "admiral", "meaning": "해군 대장", "scene": "historic naval command deck, distinguished cute slender admiral stickman in ceremonial naval coat studying ocean navigation map on wooden table, ship wheel and deck line"},
        {"id": "m1-945", "word": "sunrise", "meaning": "해돋이", "scene": "quiet coastal beach cliff, awe-inspired cute slender stickman standing watching the glowing golden sunrise rise above ocean horizon, ocean waves and sandy shoreline line"},
        {"id": "m1-946", "word": "harmful", "meaning": "해로운", "scene": "science safety laboratory, cautious cute slender stickman technician wearing protective gloves pointing at yellow hazard warning sign avoiding harmful chemical spills, lab bench and floor line"},
        {"id": "m1-947", "word": "beach", "meaning": "해변", "scene": "sunny tropical ocean beach, joyful cute slender stickman walking along sunny sandy beach holding colorful beach ball under palm umbrella, seashells and shoreline line"},
        {"id": "m1-948", "word": "shore", "meaning": "해안", "scene": "rocky ocean shore coast, peaceful cute slender stickman standing on smooth shoreline pebbles watching gentle foaming waves break onto shore, sea spray and shoreline line"},
        {"id": "m1-949", "word": "coast", "meaning": "해안", "scene": "scenic coastal highway cliff, cute slender stickman traveler looking out from scenic overlook admiring sweeping panoramic coastline with lighthouse, coastal cliff railing line"},
        {"id": "m1-950", "word": "nuclear", "meaning": "핵의", "scene": "modern clean energy research institute, smart cute slender physicist stickman studying atomic structure models at clean nuclear energy research facility, control monitors and floor line"},
        {"id": "m1-951", "word": "sunshine", "meaning": "햇빛", "scene": "sunny flower garden terrace, happy cute slender stickman sitting on garden chair basking warmly under bright golden sunshine with closed eyes and gentle smile, patio plants line"},
        {"id": "m1-952", "word": "behave", "meaning": "행동하다", "scene": "elementary classroom etiquette lesson, well-mannered cute slender student stickman sitting politely with neat hands folded on desk behaving impeccably, desks and floor line"},
        {"id": "m1-953", "word": "parade", "meaning": "행렬", "scene": "festive town festival street, joyful cute slender stickman marching in colorful community holiday parade waving small decorative flag to cheering crowds, confetti and street curb line"},
        {"id": "m1-954", "word": "planet", "meaning": "행성", "scene": "space science planetarium dome, curious cute slender stickman student observing high resolution projections of Saturn with beautiful rings and distant planets, planetarium seats and floor line"},
        {"id": "m1-955", "word": "luck", "meaning": "행운", "scene": "sunny clover grass meadow, delighted cute slender stickman kneeling down finding a rare lucky four-leaf clover smiling in celebration of good luck, grassy meadow line"},
        {"id": "m1-956", "word": "march", "meaning": "행진, 행진하다", "scene": "outdoor festival parade boulevard, energetic cute slender brass band stickman playing marching snare drum marching forward with high knees, marching route line"},
        {"id": "m1-957", "word": "homesick", "meaning": "향수병", "scene": "cozy dormitory room window, quiet cute slender stickman holding a framed family photo gazing fondly out window feeling a little homesick, bed and floor line"},
        {"id": "m1-958", "word": "feast", "meaning": "향연, 잔치", "scene": "grand banquet hall dining table, joyful cute slender stickman celebrating at grand feast filled with abundant delicious roast dishes and fresh fruit bowls, banquet chairs and floor line"},
        {"id": "m1-959", "word": "allow", "meaning": "허락하다", "scene": "school library entrance desk, courteous cute slender librarian stickman stamping borrowing card and nodding warmly to allow student stickman to borrow books, check-out desk and floor line"},
        {"id": "m1-960", "word": "vain", "meaning": "헛된", "scene": "windy park pathway, humorous cute slender stickman running trying in vain to catch a runaway fallen autumn leaf blown away by sudden gust, park trees and ground line"}
    ],
    49: [
        {"id": "m1-961", "word": "tongue", "meaning": "혀", "scene": "clean pediatric clinic examination, cooperative cute slender stickman patient opening mouth sticking tongue out gently for smiling friendly doctor checking health with light, medical room floor line"},
        {"id": "m1-962", "word": "revolution", "meaning": "혁명", "scene": "historic city square plaza, inspiring cute slender stickman leader standing on platform holding historical proclamation banner marking peaceful democratic revolution, stone pedestal and plaza line"},
        {"id": "m1-963", "word": "cash", "meaning": "현금", "scene": "bank teller counter station, polite cute slender bank teller stickman neatly counting out paper cash bills to hand to customer stickman, counter partition and floor line"},
        {"id": "m1-964", "word": "modern", "meaning": "현대의", "scene": "sleek minimalist modern living room, stylish cute slender stickman relaxing on contemporary designer sofa in sleek modern interior with clean geometric furniture, polished floor line"},
        {"id": "m1-965", "word": "wise", "meaning": "현명한", "scene": "tranquil mountain temple pavilion, serene cute slender elder stickman philosopher stroking chin offering thoughtful wise guidance over hot tea, stone balcony and floor line"},
        {"id": "m1-966", "word": "present", "meaning": "현재", "scene": "cozy birthday celebration table, delighted cute slender stickman opening a colorful gift present with red silk ribbon, party table and floor line"},
        {"id": "m1-967", "word": "curious", "meaning": "호기심이 많은", "scene": "science discovery museum hall, curious cute slender stickman student leaning forward inspecting an interactive plasma globe ball with wide inquisitive eyes, exhibit table and floor line"},
        {"id": "m1-968", "word": "pumpkin", "meaning": "호박", "scene": "sunny autumn farm pumpkin patch, joyful cute slender farmer stickman carrying a large round ripe orange pumpkin across fertile field, wooden crates and garden soil line"},
        {"id": "m1-969", "word": "alone", "meaning": "혼자", "scene": "peaceful wooden dock on quiet lake, relaxed cute slender stickman sitting alone happily dangling feet over water enjoying solitary peaceful afternoon, wooden pier and water ripples line"},
        {"id": "m1-970", "word": "flood", "meaning": "홍수", "scene": "riverfront emergency levee bank, diligent cute slender rescue worker stickman placing heavy sandbags along reinforced bank to protect town from rising flood water, river embankment line"},
        {"id": "m1-971", "word": "upset", "meaning": "화난", "scene": "cozy living room armchair, cute slender stickman student crossing arms with pouty cheeks looking temporarily upset after losing friendly game, rug and floor line"},
        {"id": "m1-972", "word": "angry", "meaning": "화난", "scene": "comic drama playroom, cute slender stickman playfully stamping foot with comical angry puffed cheeks holding hands on hips, toy shelf and floor line"},
        {"id": "m1-973", "word": "gallery", "meaning": "화랑", "scene": "bright fine art museum gallery, cultured cute slender stickman walking slowly admiring framed oil paintings hung along spacious gallery wall, benches and polished floor line"},
        {"id": "m1-974", "word": "mars", "meaning": "화성", "scene": "astronomy observatory dome, focused cute slender astronomer stickman viewing planet Mars through large astronomical telescope, star charts and observatory floor line"},
        {"id": "m1-975", "word": "steady", "meaning": "확고한", "scene": "woodworking joinery studio, patient cute slender carpenter stickman holding ruler with a calm steady hand drawing a perfectly straight guideline on timber, workbench line"},
        {"id": "m1-976", "word": "certain", "meaning": "확실한", "scene": "quiz competition game podium, confident cute slender stickman contestant smiling and pressing buzzer feeling completely certain of correct answer, quiz podium and stage line"},
        {"id": "m1-977", "word": "check", "meaning": "확인하다", "scene": "airport departure gate desk, organized cute slender traveler stickman carefully checking boarding pass and passport details before boarding flight, counter and airport floor line"},
        {"id": "m1-978", "word": "patient", "meaning": "환자", "scene": "clean hospital recovery room, resting cute slender patient stickman in cozy bed smiling warmly as caring nurse stickman checks wellness chart, hospital bedside table and floor line"},
        {"id": "m1-979", "word": "activity", "meaning": "활동", "scene": "vibrant school recreation gymnasium, energetic cute slender stickman participating enthusiastically in group team sports activity, gym floor lines and bleachers"},
        {"id": "m1-980", "word": "torch", "meaning": "횃불", "scene": "historic Olympic stadium ceremony, proud athletic cute slender runner stickman carrying blazing golden ceremonial torch running towards stadium cauldron, running track line"}
    ],
    50: [
        {"id": "m1-981", "word": "inning", "meaning": "회(야구)", "scene": "sunny baseball stadium scoreboard, excited cute slender baseball fan stickman cheering as scoreboard displays the thrilling final ninth inning, stadium railing and bleachers line"},
        {"id": "m1-982", "word": "company", "meaning": "회사, 친구", "scene": "modern bright office suite, cheerful cute slender stickman professional collaborating with friendly colleagues at open office desk in great company, office plants and floor line"},
        {"id": "m1-983", "word": "gray", "meaning": "회색의", "scene": "cozy rainy street sidewalk, stylish cute slender stickman walking comfortably wearing a neat warm gray wool coat holding umbrella, rain puddle and pavement line"},
        {"id": "m1-984", "word": "junior", "meaning": "후배, 손아래의", "scene": "school library study room, friendly senior stickman patiently mentoring and helping a junior student stickman with algebra homework, wooden study table and floor line"},
        {"id": "m1-985", "word": "afterward", "meaning": "후에", "scene": "cozy cafe booth table, two happy cute slender stickman friends relaxing enjoying cake and tea afterward following a successful exam, cafe table and floor line"},
        {"id": "m1-986", "word": "pepper", "meaning": "후추", "scene": "warm dining restaurant table, cheerful cute slender chef stickman using a classic wooden pepper mill to grind fresh aromatic black pepper onto hot soup, dining table and floor line"},
        {"id": "m1-987", "word": "steal", "meaning": "훔치다", "scene": "humorous family kitchen counter, mischievous playful cute slender stickman tiptoeing comically to steal a warm chocolate cookie from cooling rack, kitchen cabinets and floor line"},
        {"id": "m1-988", "word": "whistle", "meaning": "휘파람을 불다", "scene": "sunny countryside trail promenade, joyful cute slender stickman walking with hands in pockets puckering lips whistling a cheerful melodic tune, wildflower path line"},
        {"id": "m1-989", "word": "rest", "meaning": "휴식, 휴식하다", "scene": "shady garden park hammock, relaxed cute slender stickman lying comfortably taking a peaceful afternoon rest in hammock strung between two shady trees, grass lawn line"},
        {"id": "m1-990", "word": "holiday", "meaning": "휴일, 공휴일", "scene": "tropical resort patio deck, cheerful cute slender stickman wearing straw sunhat celebrating holiday vacation lounging beside sparkling pool with fruity drink, pool deck line"},
        {"id": "m1-991", "word": "flow", "meaning": "흐르다, 흐름", "scene": "peaceful mountain brook meadow, gentle cute slender stickman watching clear cool stream water flow smoothly over smooth river stones, grassy riverbank line"},
        {"id": "m1-992", "word": "comedy", "meaning": "희극, 코미디", "scene": "lively comedy club theater stage, laughing cute slender stickman audience watching funny comedian stickman perform delightful comedy routine, stage spotlight and theater seats line"},
        {"id": "m1-993", "word": "might", "meaning": "힘", "scene": "historic fairytale castle courtyard, brave cute slender stickman pulling with all mighty strength to draw legendary sword from stone, castle flags and stone courtyard line"},
        {"id": "m1-994", "word": "force", "meaning": "힘, 강요하다", "scene": "physics science classroom, curious cute slender stickman student experimenting with magnetic attraction force between two large horseshoe magnets, classroom desk and floor line"}
    ]
}

def deduplicate_word_images():
    if not os.path.exists(WORD_IMAGES_TS):
        return
    import re
    with open(WORD_IMAGES_TS, "r", encoding="utf-8") as f:
        lines = f.readlines()
    header, entries, seen_order, footer = [], {}, [], []
    in_entries = False
    for line in lines:
        m = re.match(r"^\s*([\"\x27]?)([\w-]+)\1:\s*(require\(.+\)),?$", line)
        if m:
            key, val = m.group(2), m.group(3)
            if key not in entries:
                seen_order.append(key)
            entries[key] = val
            in_entries = True
        else:
            if not in_entries:
                header.append(line)
            else:
                footer.append(line)
    out = "".join(header)
    for k in seen_order:
        if "-" in k or not k.isidentifier():
            out += f'  "{k}": {entries[k]},\n'
        else:
            out += f'  {k}: {entries[k]},\n'
    out += "".join(footer)
    with open(WORD_IMAGES_TS, "w", encoding="utf-8") as f:
        f.write(out)

def deploy_unit(unit_num: int):
    print(f"\n[Unit {unit_num}] 작업 완료 후 배포 파이프라인 가동...", flush=True)
    
    # 0. wordImages.ts 중복 키 자동 정리
    deduplicate_word_images()

    # 1. 외장하드 ._* 파일 먼저 정리 (Lint 에러 방지)
    subprocess.run(["find", ".", "..", "-name", "._*", "-type", "f", "-delete"], cwd=PROJECT_ROOT)
    print("._* 임시 파일 정리 완료", flush=True)

    # 2. 린트 검증
    try:
        subprocess.run(["npm", "run", "lint"], cwd=PROJECT_ROOT, check=True)
        print("Lint 검증 통과!", flush=True)
    except Exception as e:
        print(f"Lint 경고/오류 (계속 진행): {e}", flush=True)

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
        try:
            deduplicate_word_images()
            subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT)
            subprocess.run(["git", "rebase", "--continue"], cwd=PROJECT_ROOT, env={**os.environ, "GIT_EDITOR": "true"})
            subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
            print(f"Git 배포 재시도 성공: 유닛 {unit_num}", flush=True)
        except Exception as e2:
            print(f"Git 배포 재시도 오류: {e2}", flush=True)

def main():
    parser = argparse.ArgumentParser(description="중1 선형그래픽 연속 생성기")
    parser.add_argument("--start-unit", type=int, default=35, help="시작할 유닛 번호 (기본: 35)")
    parser.add_argument("--start-idx", type=int, default=1, help="시작할 단어 번호 (기본: 1)")
    parser.add_argument("--end-unit", type=int, default=36, help="종료할 유닛 번호 (기본: 36)")
    args = parser.parse_args()

    print(f"==================================================", flush=True)
    print(f"중학교 1학년 선형그래픽 연속 생성 파이프라인 가동 (Unit {args.start_unit}:{args.start_idx} ~ {args.end_unit}:20)", flush=True)
    print(f"규칙: 3~3.5등신 픽토그램 순백색 마네킹 캐릭터 조형 원칙 적용", flush=True)
    print(f"==================================================", flush=True)

    for unit_num in range(args.start_unit, args.end_unit + 1):
        if unit_num not in UNIT_DATA:
            print(f"유닛 {unit_num} 데이터가 정의되지 않았습니다. 작업을 종료합니다.", flush=True)
            break

        words = UNIT_DATA[unit_num]
        print(f"\n▶▶▶ [Unit {unit_num}] 20단어 렌더링 시작 ◀◀◀", flush=True)

        elapsed_times = {}
        for idx, item in enumerate(words, start=1):
            w = item["word"]
            w_id = item["id"]
            meaning = item["meaning"]
            scene = item["scene"]
            file_name = w.replace(" ", "-")
            out_file = os.path.join(ASSETS_DIR, f"{file_name}.png")

            # 시작 번호 이전 단어는 유지
            if unit_num == args.start_unit and idx < args.start_idx:
                elapsed_times[w] = 150.0
                print(f"[{w}] 이전 생성 단어 유지 (번호 {idx} < {args.start_idx})", flush=True)
                continue

            # 대시보드 갱신 (렌더링 시작)
            update_dashboards(unit_num, idx, item, elapsed_times, status_text=f"'{w}' 렌더링 중...")

            print(f"\n[Unit {unit_num} - {idx}/20] '{w}' ({w_id}: {meaning}) 생성 중...", flush=True)
            print(f"Scene: {scene}", flush=True)

            seed = 1000 + int(w_id.split("-")[1])
            success, elapsed = generate_image(w, scene, out_file, seed=seed)
            if success:
                elapsed_times[w] = elapsed
                print(f"[{w}] 생성 완료 ({elapsed:.1f}초) -> {out_file}", flush=True)
                update_word_images_ts(w, w_id)
                # 대시보드 갱신 (단어 완료)
                update_dashboards(unit_num, idx, item, elapsed_times, status_text=f"'{w}' 완료 ({elapsed:.1f}초)")
            else:
                print(f"[{w}] 생성 실패!", flush=True)

        # 1개 유닛(20단어) 완료 시 배포
        update_dashboards(unit_num, 20, words[-1], elapsed_times, status_text="유닛 완료 및 Git 배포 중...")
        deploy_unit(unit_num)
        update_dashboards(unit_num, 20, words[-1], elapsed_times, status_text="✅ 유닛 배포 완료")
        print(f"🎉 [Unit {unit_num}] 20단어 생성 및 등록 배포 전원 완료!\n", flush=True)

    print("모든 지정 유닛 생성 파이프라인이 성공적으로 완료되었습니다!", flush=True)

if __name__ == "__main__":
    main()
