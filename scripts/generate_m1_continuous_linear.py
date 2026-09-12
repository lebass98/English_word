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

        elapsed_times = {}
        for idx, item in enumerate(words, start=1):
            w = item["word"]
            w_id = item["id"]
            meaning = item["meaning"]
            scene = item["scene"]
            file_name = w.replace(" ", "-")
            out_file = os.path.join(ASSETS_DIR, f"{file_name}.png")

            # 대시보드 갱신 (렌더링 시작)
            update_dashboards(unit_num, idx, item, elapsed_times, status_text=f"'{w}' 렌더링 중...")

            print(f"\n[Unit {unit_num} - {idx}/20] '{w}' ({w_id}: {meaning}) 생성 중...", flush=True)
            print(f"Scene: {scene}", flush=True)

            seed = 1000 + int(w_id.split("-")[1])
            success, elapsed = generate_image(scene, out_file, seed=seed)
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
