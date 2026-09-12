#!/usr/bin/env python3
"""Generate Middle School Grade 3 Unit 1 word images with Draw Things."""

import base64
import json
import os
import time
import urllib.request

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "words")

WORDS = [
    ("translation", "a language workshop where one stickman translates a letter at a desk while two friends exchange matching speech cards labeled HELLO and WELCOME, dictionaries, globe, bookshelves, desk lamp"),
    ("underground", "a cutaway underground subway station beneath a busy city street, stickman passengers descending stairs toward a train, tunnel signs, benches, tracks, pipes, buildings and trees above ground"),
    ("rent", "a cozy apartment office where a tenant hands a RENT envelope and key to a smiling landlord, calendar, receipt book, sofa, window, potted plant, shoe rack"),
    ("private", "a quiet bedroom doorway with a clear PRIVATE sign, one stickman gently closing the door while friends respectfully wait outside, desk, diary, bed, lamp, framed pictures"),
    ("union", "a community hall where several diverse stickman friends join hands in a circle around interlocking rings, banner reading TOGETHER, meeting table, chairs, notice board, plants"),
    ("lay", "a picnic garden where a stickman carefully lays a striped blanket flat on the grass while friends arrange a basket and plates, trees, flowers, bench, birds, stepping stones"),
    ("exact", "a precision workshop where a stickman measures a small wooden box with ruler and calipers and marks an exact fit, blueprint table, wall clock, tools, shelves, numbered measurements"),
    ("temperature", "a weather station where two stickmen read a large thermometer beside a window showing sun and snow clouds, weather chart, coat hook, fan, heater, instruments"),
    ("personal", "a school locker area where a stickman organizes a clearly labeled PERSONAL box with diary, headphones and photographs while friends use their own lockers, bench, clock, backpacks"),
    ("disappear", "a small theater stage where a magician stickman lifts an empty top hat as a rabbit vanishes in sparkles, amazed audience friends, curtains, prop table, empty cage, spotlights"),
    ("laboratory", "a busy science laboratory with stickman students examining bubbling flasks and a microscope under a teacher's guidance, safety goggles, test tubes, molecule chart, cabinets, sink"),
    ("league", "a sports clubhouse where four stickman team captains place their club badges around a large LEAGUE trophy, scoreboard, ball rack, jerseys, benches, pennants"),
    ("succeed", "a school invention fair where a stickman celebrates a working model rocket reaching a SUCCESS finish marker, friends applaud, trophy, blueprint desk, tools, banners"),
    ("democracy", "a bright community voting room where stickman citizens place ballots into a VOTE box and discuss ideas at a round table, equal queue, posters, notice board, civic building windows"),
    ("saying", "a cozy classroom where a teacher points to a speech scroll reading PRACTICE MAKES PROGRESS while students discuss its wisdom, books, chalkboard, clock, desks, thought bubbles"),
    ("precious", "a family attic where a stickman carefully holds a precious old photo album close while grandparents smile, keepsake chest, framed memories, rocking chair, lamp, boxes"),
    ("excuse", "a classroom doorway where a late stickman offers a crumpled bus-delay note to the teacher while pointing at a stopped bus outside, clock, desks, backpacks, classmates watching"),
    ("avoid", "a park path where a cyclist carefully steers around a large puddle and warning cone while friends choose a safe dry route, trees, bench, bridge, ducks, direction arrows"),
    ("no longer", "a child's room where a growing stickman sets aside an old tiny bicycle marked BEFORE and proudly rides a larger bicycle marked NOW, height chart, helmet shelf, toys, window"),
    ("narrow", "an old village alley so narrow that two stickman travelers turn sideways to pass between close buildings, hanging lamps, tiny shop fronts, flower pots, bicycle, distant archway"),
]

NEGATIVE_PROMPT = (
    "neck, long neck, throat, collar, neck line, detailed neck anatomy, Korean text, Hangul, "
    "Korean letters, non-English text, broken characters, foreign characters, thick lines, bold outlines, "
    "heavy brush strokes, chunky lines, fat strokes, pure white background, dark background, black background, "
    "3d, photorealistic, color photograph, blur, watermark, signature, poster layout, isolated object"
)


def generate() -> None:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    total = len(WORDS)
    start_at = int(os.environ.get("M3_UNIT1_START_AT", "1"))
    print(f"Middle 3 Unit 1 generation: {total} images", flush=True)

    for index, (word, scene) in enumerate(WORDS, start=1):
        if index < start_at:
            continue
        filename = word.replace(" ", "-") + ".png"
        output_path = os.path.join(ASSETS_DIR, filename)
        prompt = (
            "linear graphic illustration matching a charming educational vocabulary picture, "
            "thinnest possible 0.05mm ultra-delicate needle-thin hairline ink stroke, extremely fine crisp "
            "outlines in dark charcoal ink color #030203, flat smooth light gray canvas background color #f5f6f8, "
            "neckless cute doodle stickman characters with perfectly round bald heads attached directly to torso "
            "with completely no neck, simple dot eyes and friendly expressions, "
            f"{scene}, rich narrative environment with clear floor line and many coherent props, balanced square "
            "composition, strictly flat 2d line art, restrained pale gray accent fills, English text only"
        )
        payload = {
            "prompt": prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "steps": 8,
            "width": 1024,
            "height": 1024,
            "seed": 3100 + index * 37,
        }
        print(f"[{index}/{total}] {word}: {scene}", flush=True)
        started = time.time()
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=900) as response:
            result = json.loads(response.read().decode("utf-8"))
        images = result.get("images", [])
        if not images:
            raise RuntimeError(f"No image returned for {word}")
        with open(output_path, "wb") as output:
            output.write(base64.b64decode(images[0]))
        size_kb = os.path.getsize(output_path) / 1024
        print(f"DONE {word} {time.time() - started:.1f}s {size_kb:.0f}KB {output_path}", flush=True)


if __name__ == "__main__":
    generate()
