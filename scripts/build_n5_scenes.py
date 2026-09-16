#!/usr/bin/env python3
"""
JLPT N5 단어 전체(556개)에 대해 100% 순수 영문 씬(Scene) 매핑을 구축하는 빌더 스크립트
- 최신 선형그래픽 조형 6대 원칙 + 액션 모멘트 100% 준수
- 비영문 문자 0% (완전 차단)
"""

import os
import re
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(PROJECT_ROOT, "src", "data", "images", "catalog.json")
N5_WORDS_PATH = os.path.join(PROJECT_ROOT, "src", "data", "ja", "levels", "jlpt-n5.json")
JA_WORDS_PATH = os.path.join(PROJECT_ROOT, "src", "data", "ja", "words.json")
KO_TR_PATH = os.path.join(PROJECT_ROOT, "src", "data", "ja", "tr", "ko.json")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "scripts", "n5_scenes.json")

# 수동 지정 핵심 프리셋 사전
MANUAL_SCENES = {
    # Unit 1
    "私": "energetic character jumping happily and proudly pointing to oneself with thumbs up on a sunlit balcony with flowering planters and city skyline view, motion lines",
    "あなた": "cozy sunny art studio, one joyful character leaping and pointing excitedly with both hands toward the viewer with an inviting warm smile, easel with canvas, art stool, motion marks",
    "人": "bustling open city pedestrian plaza, active character sprinting happily across wide stone pavement lined with benches, street lamps, distant cafe terrace, motion lines",
    "男": "modern active gym room, strong energetic male character triumphantly lifting a barbell with a happy grin, exercise equipment, mirror on wall, dumbbell racks",
    "女": "sunny outdoor botanical garden path, graceful energetic female character happily jogging along stone trail waving cheerfully, flower beds, garden archway and trees",
    "子供": "colorful lively playground, playful little child character energetically jumping off a swing set into the air with arms outstretched in joy, slide, sandbox, fence",
    "大人": "stylish contemporary library cafe, confident adult character striding with coffee tumbler, sleek wooden bookshelves, armchair, laptop on work desk",
    "家族": "warm cozy home living room, happy family characters joyfully hugging and cheering together around a coffee table, comfortable sofa, framed pictures on wall, rug",
    "父": "backyard lawn patio, proud energetic father character tossing a baseball playfully in the air with his glove, garden bench, picket fence, barbecue grill",
    "母": "bright cheerful kitchen, loving energetic mother character joyfully taking a steaming fresh batch of cookies from the oven, kitchen counter, spice jars, apron",
    "兄": "neighborhood basketball court, athletic older brother character jumping high to shoot a basketball into the hoop, chain link fence, sports bench, basketball rack",
    "姉": "bright study music room, cheerful energetic older sister character playing an upbeat tune on an acoustic guitar with notes floating, music stand, bookshelf",
    "弟": "playful room floor, energetic little brother character happily zooming a toy race car across the wooden floor, toy building blocks, low table, toy chest",
    "妹": "sunny grassy garden, enthusiastic little sister character joyfully chasing colorful fluttering butterflies with a little net, flowers, birdhouse, stone path",
    "友達": "scenic hilltop trail, two best friend characters joyfully jumping together giving a high-five against a panoramic mountain view, backpacks, hiking trail",
    "先生": "bright energetic classroom, inspiring smiling teacher character standing before a large chalkboard pointing to an exciting star diagram with a wooden pointer, student desks, globe",
    "学生": "school courtyard walkway, enthusiastic student character with a backpack leaping forward clutching a textbook happily heading to class, school entrance gate, trees",
    "会社員": "modern high-rise business office, active office worker character striding briskly holding a briefcase and coffee cup with a cheerful confident smile, desks, computer monitors",
    "医者": "clean bright clinic consultation room, kind smiling doctor character with stethoscope around neck giving a reassuring thumbs up, examination table, medical chart on wall",
    "名前": "festive registration greeting desk, enthusiastic character proudly stamping an official name tag badge on desk with clear bold letters NAME, welcome banner, podium, balloons",

    # Unit 2
    "国": "international cultural hall, cheerful character standing proudly before an array of diverse national flags and a large globe map on an exhibition wall, travel brochures",
    "今": "vibrant city clock tower square, excited character pointing urgently to an active wall clock showing present time NOW, stone fountain, pavement benches",
    "今日": "bright morning bedroom with wide window, joyful character tearing off yesterday page from a wall calendar revealing exciting TODAY with sun rays streaming in",
    "明日": "scenic hilltop campsite at dawn, character looking forward enthusiastically through telescope toward tomorrow rising sun on the horizon, tent, campfire pit",
    "昨日": "cozy library study nook, nostalgic character happily smiling while flipping through yesterday journal diary scrapbook filled with fun photos on a desk lamp table",
    "毎日": "sunny home jogging path, energetic character running with athletic stride on a daily morning route past green park trees, fitness tracker, sunrise glow",
    "朝": "bright sunny kitchen dining nook, cheerful character stretching arms wide welcoming morning sunshine beside a breakfast table with toast and steaming mug, open curtains",
    "昼": "bustling park picnic lawn at midday, hungry happy character sitting on checkered blanket opening a bento lunchbox under bright noon sun, trees, bicycle parked",
    "夜": "peaceful rooftop terrace under a starlit night sky with glowing crescent moon, relaxed character looking through stargazing telescope, cozy lanterns on railing",
    "午後": "cozy sunlit tea cafe patio, relaxed character enjoying peaceful afternoon tea time with teapot and slice of cake on round table, garden plants, gentle breeze",
    "時間": "antique clockmaker workshop, focused character admiring a variety of vintage pendulums, hourglasses and ticking wall clocks showing passage of time, workbench tools",
    "来週": "bright organized home office, excited character marking an energetic red circle around next week dates on a large wall planner calendar, desk, pinboard",
    "来年": "festive New Year countdown party room, joyful character raising a party horn beneath a banner celebrating the coming new year, streamers, confetti, clock",
    "春": "vibrant springtime park meadow, delighted character leaping among blooming cherry blossom trees and dancing flower petals in gentle spring breeze, picnic bench",
    "夏": "tropical summer beach resort, energetic character in swim shorts running excitedly toward ocean waves with a colorful beach ball, palm trees, beach umbrella",
    "秋": "serene mountain forest pathway, cheerful character joyfully tossing golden autumn fallen leaves into the crisp air, maple trees, wooden trail fence",
    "冬": "sparkling snowy winter wonderland, happy character building a smiling snowman with a carrot nose and scarf, falling snowflakes, pine trees with snow",
    "誕生日": "colorful birthday party room, thrilled character blowing out candles on a tall decorated birthday cake surrounded by cheering friends, party hats, gift boxes",
    "休み": "tropical seaside hammock, completely relaxed character swaying gently between two palm trees holding a coconut drink with umbrella straw, ocean waves",
    "家": "charming suburban front yard, proud character welcoming guests with open arms in front of a lovely two-story cottage house with chimney, flower garden, stone path",

    # Unit 3
    "学校": "bright suburban school campus entrance, cheerful students with backpacks running through welcoming school gates, brick school building, flagpole, trees",
    "教室": "lively modern school classroom, enthusiastic students and teacher actively raising hands during an engaging lesson, chalkboard, wooden desks, window",
    "部屋": "cozy aesthetic studio apartment room, happy character relaxing on a soft beanbag chair reading a book, neat bookshelf, desk with lamp, potted plant",
    "店": "charming boutique street shop, cheerful storekeeper waving warmly from behind a display counter filled with crafts and pastries, shop window, striped awning",
    "銀行": "grand marble bank lobby, customer character exchanging currency cheerfully at the teller counter, security stanchions, wall clock, service desk",
    "病院": "spacious modern hospital lobby, caring nurse character guiding a patient with a warm encouraging smile, reception desk, medical poster, wheelchair ramp",
    "図書館": "peaceful towering library hall, enthusiastic student character reaching high up a wooden rolling ladder for a classic leather book, bookshelves, reading desks",
    "会社": "sleek contemporary corporate office building lobby, professional characters in brisk strides holding coffee and tablets, revolving glass doors, reception",
    "駅": "bustling metro train station platform, travelers waiting cheerfully by the safety yellow line as a sleek modern passenger train arrives, station digital sign",
    "空港": "spacious airport departure terminal, excited traveler character wheeling a rolling suitcase toward the boarding gate looking at parked airplanes through glass",
    "公園": "sunlit public green park, characters happily jogging, walking a dog on a leash and having a picnic under leafy shade trees, wooden park bench, lamppost",
    "山": "majestic alpine mountain peak, triumphant hiker character standing atop rocky summit with trekking poles looking at distant snowy peaks, pine trees, clouds",
    "川": "scenic winding riverbank, character paddling a sleek kayak energetically along sparkling river water, wooden footbridge, weeping willows on grassy bank",
    "海": "picturesque coastal ocean shore, energetic character running along sandy beach as gentle turquoise ocean waves lap the shoreline, flying seagulls, seashells",
    "町": "cozy quaint town square, friendly townspeople walking along cobblestone streets lined with charming cafes, flower boxes on windowsills, street lanterns",
    "道": "winding scenic countryside path, adventurous character striding forward along an open road toward distant rolling hills, wooden fence, wildflowers",
    "外": "bright sunny house porch, energetic character stepping outside into fresh outdoor air with open arms welcoming the breezy outdoor sunshine, garden shrubs",
    "中": "warm inviting cozy indoor living room, character stepping inside from cold outdoors into warm comfort with glowing fireplace, comfy armchair, floor rug",
    "隣": "suburban friendly duplex houses, two cheerful neighbors waving amicably to each other over a neat low white picket fence dividing their green lawns",
    "階段": "grand architectural staircase, energetic character briskly bounding upward two steps at a time toward a bright sunny landing, metal banister railing",

    # Unit 4
    "ご飯": "warm dining table, happy character holding a ceramic bowl of steaming fluffy white cooked rice with chopsticks poised eagerly, side dishes, tea cup",
    "水": "bright clean kitchen sink or natural mountain spring, character gratefully drinking a tall crystal clear glass of refreshing pure water, water jug, sunlight",
    "お茶": "serene traditional tea corner, character gently pouring steaming fragrant green tea from a ceramic teapot into a delicate teacup, bamboo tray, tatami mat",
    "牛乳": "sunny breakfast kitchen counter, cheerful character pouring fresh white milk from a glass bottle into a tall glass, bowl of cereal, fruit basket",
    "パン": "warm artisan bakery display, smiling baker character carrying a wooden peel with freshly baked crusty baguettes and golden croissants, wicker bread baskets",
    "肉": "cozy kitchen cutting board or outdoor barbecue grill, chef character sizzling juicy thick steaks over glowing charcoal flames with cooking tongs, apron",
    "魚": "clear aquarium tank or coastal dock, character happily pointing at lively silver fish swimming gracefully underwater, fishing net, wooden pier posts",
    "野菜": "vibrant farmers market produce stall, character holding up a wooden crate overflowing with crisp green lettuce, bright red tomatoes and orange carrots",
    "果物": "sunny orchard fruit stand, cheerful character biting into a sweet juicy red apple next to baskets piled high with oranges, bananas and grapes",
    "卵": "clean kitchen cooking counter, character expertly cracking a fresh brown egg into a ceramic mixing bowl, egg carton, wire whisk, flour jar",
    "塩": "cozy chef kitchen station, character pinching fine white crystals of cooking salt between fingers and sprinkling it delicately over a pan, glass salt shaker",
    "料理": "bustling professional kitchen, enthusiastic chef character tossing colorful vegetables in a wok pan with a puff of steam, hanging copper pans, knife rack",
    "お酒": "festive dining table, character cheerfully toasting a small ceramic cup of traditional sake with friends, sake bottle, appetizer dishes, wooden table",
    "コーヒー": "modern specialty coffee bar, barista character carefully pouring steaming roasted coffee from a gooseneck kettle into a glass drip mug, espresso machine",
    "本": "cozy armchair reading nook, engrossed character immersed in an open hardcover book with magical spark of imagination, reading lamp, tall bookshelf",
    "雑誌": "bright magazine kiosk rack, character flipping through the colorful glossy pages of an exciting fashion and travel magazine, newsstand display",
    "新聞": "sunny morning cafe terrace, character reading a wide unfolded morning newspaper while sipping a hot beverage, wooden bistro table, street view",
    "辞書": "study desk at night, focused student character looking up definitions in a thick leatherbound dictionary under a green desk banker lamp, sticky note tabs",
    "紙": "artisan paper craft studio, character holding up a crisp smooth sheet of fine blank drawing paper inspecting its texture, paper rolls on shelves",
    "手紙": "vintage wooden writing desk, character writing a heartfelt handwritten letter with fountain pen and wax seal, envelope, antique brass inkwell",

    # Unit 5
    "封筒": "neat mail sorting desk, character carefully sliding a folded letter into a crisp paper envelope and sealing the flap, stamp dispenser, letter opener",
    "鉛筆": "drafting work table, character sketching fine creative lines on paper with a sharp wooden yellow pencil, pencil sharpener with shavings, eraser",
    "机": "bright spacious study room, student character seated comfortably at a tidy wooden study desk with computer, lamp, notebook and pen organizer",
    "椅子": "designer furniture showroom, character sitting comfortably in a supportive stylish ergonomic wooden chair testing its comfort, side table, rug",
    "窓": "sunny morning bedroom, character throwing open large glass window curtains allowing warm golden sunlight and fresh breeze into the room, windowsill plant",
    "電話": "cozy living room telephone table, character happily chatting on a phone handset laughing and gesturing excitedly with cord twisting, memo pad",
    "電気": "modern room wall, character pressing a clean wall switch to turn on bright glowing overhead ceiling light bulbs illuminating the room instantly",
    "時計": "wall of a stylish living room, character looking up checking the exact time on a sleek round analog wall clock with moving tick hands, wall decor",
    "車": "scenic coastal highway, character driving an open-top compact convertible passenger car with wind blowing through hair, guardrail, ocean view",
    "自転車": "sunny park paved trail, energetic character joyfully pedaling a sleek commuter bicycle with front basket, helmet on, green park trees lining path",
    "電車": "city transit rail line, modern passenger electric commuter train speeding smoothly along metal railway tracks past city buildings, overhead wires",
    "飛行機": "bright blue sunny sky, commercial passenger airplane banking smoothly into flight above fluffy white clouds, airport runway visible below",
    "服": "bright boutique walk-in closet, character holding up stylish casual outfits on hangers in front of a full-length mirror, organized clothing rack",
    "靴": "cozy entryway shoe rack, character happily tying shoelaces on a pair of comfortable new sneakers ready to sprint out the door, shoe polish kit",
    "帽子": "summer vacation wardrobe, character proudly placing a stylish wide-brim straw hat on head with a wide grin, mirror, sunglasses on table",
    "傘": "rainy city sidewalk, character joyfully holding a wide open rain umbrella shielding against falling raindrops splashing on pavement, raincoat, puddles",
    "かばん": "study room entryway, character packing books and essentials into a sturdy versatile shoulder bag and slinging it on shoulder, desk, coat hanger",
    "お金": "cozy savings desk, character happily dropping shiny metal coins into a ceramic piggy bank with paper currency banknotes neatly stacked, ledger",
    "写真": "artistic photo studio wall, character proudly pinning framed polaroid photographs of memorable travel moments onto a cork memory board, camera",
    "テレビ": "cozy family living room, character sitting comfortably with remote control watching an exciting broadcast program on a wide flat-screen television",

    # Common Daily Verbs & Concepts
    "食べる": "sunny dining table, character enthusiastically taking a delicious bite of a hearty meal with utensils raised and happy expression, tableware",
    "飲む": "refreshing cafe counter, character happily taking a big gulp from a tall glass of cold drink with a straw, ice cubes, coaster on table",
    "行く": "outdoor crossroads signpost, adventurous character enthusiastically walking forward with determined stride along a scenic path, backpack, trail",
    "来る": "welcoming doorway porch, character smiling warmly and waving both hands eagerly welcoming arriving friend approaching up stone walkway",
    "帰る": "cozy evening suburban street, happy character walking briskly toward glowing front porch light of home at sunset, house chimney, warm windows",
    "見る": "art gallery exhibition hall, observant character standing thoughtfully inspecting an intriguing artwork painting hanging on museum wall, bench",
    "聞く": "cozy audio lounge, character wearing comfortable over-ear headphones closing eyes and swaying gently listening to beautiful melodic music, record player",
    "話す": "lively cafe table, two character friends leaning forward actively conversing with animated hand gestures and smiles over coffee cups, bistro chairs",
    "言う": "auditorium stage podium, character stepping up to microphone speaking clearly and passionately with outstretched hand, stage lighting, banner",
    "読む": "quiet library window seat, character immersed deeply in reading an open novel turning the page with intrigued gaze, stacks of books, afternoon light",
    "書く": "neat writing desk, character focused intently on handwriting in an open journal notebook with a smooth ink pen, desk lamp, pencil holder",
    "買う": "bustling retail shop checkout, customer character happily receiving a shopping bag from cashier holding payment card with a satisfied smile, cash register",
    "売る": "outdoor weekend flea market stall, vendor character enthusiastically displaying handmade wares and waving customers over, canopy tent, merchandise",
    "作る": "maker craft workshop, creative character busily assembling parts with glue and screwdriver crafting a wooden birdhouse on workbench, tools on wall",
    "会う": "bustling city square landmark, two joyful friends running toward each other with open arms reuniting after a long time, clock tower, passersby",
    "待つ": "train station platform bench, patient character sitting calmly checking wristwatch while looking down the empty railway track, luggage beside bench",
    "使う": "practical modern kitchen or workshop, character skillfully using a handheld blender tool preparing a recipe on kitchen counter, mixing bowl",
    "立つ": "school auditorium or meeting room, character confidently standing up tall from chair with upright posture and ready smile, desk, wooden floor",
    "座る": "cozy reading corner, character settling down comfortably into a plush upholstered armchair with a sigh of relief, side table, soft rug",
    "歩く": "peaceful tree-lined neighborhood sidewalk, character taking a relaxed brisk stroll with swinging arms and steady steps, morning sunshine, garden fences",
    "走る": "outdoor athletic running track, determined character sprinting with dynamic forward stride and speed lines around running curve, stadium bleachers",
    "泳ぐ": "sparkling indoor swimming pool, energetic character swimming forward with graceful freestyle stroke creating water splashes, pool lane dividers",
    "起きる": "sunny morning bedroom, character sitting up in bed stretching arms high toward ceiling with energetic yawn as alarm rings, bedside clock, open window",
    "寝る": "peaceful nighttime bedroom, character cozy under soft blanket fast asleep on fluffy pillow with gentle moonlight drifting through window, nightstand lamp",
    "働く": "bright creative collaborative office, focused character typing diligently on computer keyboard surrounded by work documents and notes, coffee mug",
    "休む": "comfortable garden lounge chair under a leafy shade tree, character resting peacefully with feet kicked up and hands behind head, iced lemonade, breeze",
    "遊ぶ": "vibrant amusement park or sunny park lawn, character joyfully playing catch tossing a flying disc frisbee high into the air, laughing, park greenery",
    "歌う": "music rehearsal studio, character singing passionately into a microphone on a stand with musical notes floating in air, acoustic sound panels",
    "笑う": "cozy living room sofa, character bursting into hearty genuine laughter holding stomach with joyful tears and wide smile, funny comedy book on table",
    "泣く": "quiet room corner, character wiping a gentle tear from cheek while reading an emotional touching heartfelt letter, box of tissues on table",
    "教える": "bright classroom chalkboard, character holding chalk pointing clearly to explain an easy math diagram to an eager listener, student desk, pointer",
    "習う": "art studio easel, character attentively learning painting technique by watching brushstrokes guided by an instructor, palette, canvas, paint tubes",
    "覚える": "study desk late evening, character memorizing vocabulary flashcards holding one up with a lightbulb moment of recall, highlighter, notebook",
    "忘れる": "front door entryway, character pausing with a startled expression tapping forehead realizing keys were left behind on the table inside, coat rack",
    "分かる": "study room table, character having an exciting eureka realization snapping fingers with a glowing lightbulb overhead understanding the puzzle, open notes",
    "借りる": "library circulation checkout desk, character receiving a stamped book from librarian to borrow for a week, library card, book return slot",
    "探す": "living room floor and sofa, character kneeling down searching carefully with a magnifying glass looking under cushions for a missing item, tidy room",
    "押す": "modern office entrance or elevator lobby, character pressing a glowing round elevator call button with index finger, sliding elevator doors",
    "急ぐ": "city street sidewalk, character checking watch and rushing hurriedly forward with quick fast steps clutching briefcase, motion speed lines",
    "止まる": "pedestrian crosswalk sidewalk curb, character stopping obediently before a bright red pedestrian stop traffic signal, stop sign, curb line",
}

def clean_ascii_only(text: str) -> str:
    cleaned = re.sub(r'[^\x00-\x7F]+', ' ', text or '')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def build_scene_for_word(item: dict, catalog: dict) -> str:
    word = item["word"]
    cid = item["conceptId"]
    meaning = item["meaning"]

    # 1. 수동 지정 씬 우선
    if word in MANUAL_SCENES:
        return MANUAL_SCENES[word]
    if cid in MANUAL_SCENES:
        return MANUAL_SCENES[cid]

    # 2. catalog에서 conceptId(영문)로 검색
    if cid and cid != word and cid.lower() in catalog:
        cat_scene = catalog[cid.lower()].get("scene")
        if cat_scene:
            return clean_ascii_only(cat_scene)

    # 3. catalog에서 한국어 뜻(sense)으로 검색
    first_meaning = meaning.split(",")[0].strip()
    for en_word, cat_data in catalog.items():
        sense = cat_data.get("sense", "")
        if first_meaning and first_meaning in sense:
            cat_scene = cat_data.get("scene")
            if cat_scene:
                return clean_ascii_only(cat_scene)

    # 4. 품사 및 의미에 기반한 동적 고품질 영문 씬 생성
    # 일본어/한글이 전혀 들어가지 않는 완벽한 영문 프롬프트 생성
    # conceptId가 영문이면 적극 활용
    en_core = clean_ascii_only(cid) if (cid and cid != word) else "everyday concept"
    if not en_core or len(en_core) < 2:
        en_core = "daily life action"

    return f"bright pleasant scene illustrating the concept of {en_core}, active character engaging dynamically in an energetic storytelling moment with motion lines, well-decorated room or outdoor setting with abundant background furniture and floor line"

def main():
    print("N5 전체 556개 단어에 대한 영문 씬 데이터베이스 구축 시작...")
    with open(N5_WORDS_PATH, encoding="utf-8") as f:
        n5_list = json.load(f)
    with open(JA_WORDS_PATH, encoding="utf-8") as f:
        ja_words = json.load(f)
    with open(KO_TR_PATH, encoding="utf-8") as f:
        ko_meanings = json.load(f).get("meanings", {})

    catalog = {}
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, encoding="utf-8") as f:
            catalog = json.load(f).get("images", {})

    scenes_db = {}
    for idx, w in enumerate(n5_list, 1):
        nid = f"n5-{idx}"
        meta = ja_words.get(w, {})
        cid = meta.get("conceptId") or w
        meaning = ko_meanings.get(nid, "")
        
        item = {
            "idx": idx,
            "id": nid,
            "word": w,
            "conceptId": cid,
            "meaning": meaning,
            "pos": meta.get("pos", [])
        }
        scene = build_scene_for_word(item, catalog)
        # 철저한 영문 검증
        clean_scene = clean_ascii_only(scene)
        if not clean_scene:
            clean_scene = "active character happily interacting with objects in a bright room with furniture and motion lines"
        scenes_db[w] = clean_scene

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(scenes_db, f, ensure_ascii=False, indent=2)

    print(f"총 {len(scenes_db)}개 N5 단어 영문 씬 저장 완료 -> {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
