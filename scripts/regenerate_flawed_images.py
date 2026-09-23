#!/usr/bin/env python3
"""점검에서 걸러진 그림을 다시 그린다.

무엇이 문제였나:
  - 그림 안에 적힌 영어가 깨져 있다 (appropiirate, THEPLLACED A BAN ...)
  - 한글·한자가 들어가 있다 (규칙상 씬 안 글자는 영문만)
모두 "간판·현수막에 문장을 쓰라"고 시킨 장면에서 나왔다.
모델은 긴 글을 제대로 못 쓰므로, 다시 그릴 때는 글자를 아예 빼고 행동과 소품으로만
뜻을 전한다. 뜻 자체는 단어의 예문에서 뽑아 장면으로 옮긴다.

    python3 scripts/regenerate_flawed_images.py --list          # 대상만 보기
    python3 scripts/regenerate_flawed_images.py --limit 3       # 3장만 시험
    python3 scripts/regenerate_flawed_images.py                 # 전체 재생성
"""

import argparse
import json
import os
import re
import sys
import unicodedata

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
SKILL = os.path.join(ROOT, ".agents/skills/draw-things-linear-graphic/scripts")
sys.path.insert(0, SKILL)

from generate_linear_graphic import generate_linear_image  # noqa: E402

ASSETS = os.path.join(ROOT, "assets/words")
REGEN_LIST = os.path.join(SCRIPT_DIR, "data/regen_list.json")
SCENE_GLOB = os.path.join(SCRIPT_DIR, "*scenes*.json")
# 예전 장면이 없는 낱말은 손으로 써 둔다. 예문을 그대로 넘기면
# "방 안에 캐릭터가 서 있는" 밋밋한 그림으로 수렴해 뜻이 사라진다
HAND_SCENES = os.path.join(SCRIPT_DIR, "data/regen_scenes.json")

# 글자를 부르는 소품 → 글자가 없는 같은 구실의 소품.
# 원본 장면을 통째로 버리면 어렵게 잡아 둔 뜻까지 날아가므로, 소품만 바꿔 끼운다.
PROP_SWAP = [
    (r"\ball in English\b", ""),
    (r"\bin English\b", ""),
    (r"\blabell?ed\b", "marked"),
    (r"\bspelling\b", "shape"),
    (r"\b(cause|result|word|name|title|flash|index)\s+cards?\b", "blank cards"),
    (r"\bcards?\b", "blank cards"),
    (r"\bblank blank\b", "blank"),
    (r"\bplaques?\b", "medal"),
    (r"\bscrolls?\b", "rolled ribbon"),
    (r"\bquotation marks?\b", "small paired ticks"),
    (r"\bquotes?\b", "marked spot"),
    (r"\bquoted\b", "marked"),
    (r"\bpassages?\b", "marked spot"),
    (r"\bessays?\b", "blank sheet"),
    (r"\barticles?\b", "blank sheet"),
    (r"\bnotes?\b", "blank card"),
    (r"\bremarks?\b", "small blank cards"),
    (r"\bcharts?\b", "row of simple bars"),
    (r"\bdiagrams?\b", "simple shapes"),
    (r"\bscripts?\b", "blank sheet"),
    (r"\breferences?\b", "blank card"),
    (r"\blisting\b", "showing"),
    (r"\blisted\b", "shown"),
    (r"\bsentences?\b", "row of blank cards"),
    (r"\bphrases?\b", "row of blank cards"),
    (r"\bchunk of (marks|words)\b", "group of blank cards"),
    (r"\bopinion\b", "thought"),
    (r"\bcaptions?\b", "small blank card"),
    (r"\breceipts?\b", "blank slip"),
    (r"\btickets?\b", "plain slip"),
    (r"\bforms?\b", "blank sheet"),
    (r"\bpages?\b", "blank page"),
    (r"\bposted\b", "pinned"),
    (r"\bwritten\b", "drawn"),
    (r"\bsign\s*board\b", "arrow marker"),
    (r"\bnotice\s*board\b", "pin board with blank cards"),
    (r"\bbulletin\s*board\b", "pin board with blank cards"),
    (r"\b(black|white|chalk)board\b", "blank wall panel"),
    (r"\bboard\b", "blank panel"),
    (r"\bbanners?\b", "linked arms"),
    (r"\bplacards?\b", "raised hands"),
    (r"\bpennants?\b", "ribbon"),
    (r"\bflags?\b", "ribbon"),
    (r"\btreaty paper\b", "handshake"),
    (r"\bprice tags?\b", "coin stack"),
    (r"\btags?\b", "small ribbon"),
    (r"\bposters?\b", "framed picture"),
    (r"\bsigns?\b", "arrow marker"),
    (r"\blabels?\b", "small plain tag"),
    (r"\bmenu\b", "tray of dishes"),
    (r"\bheadlines?\b", "folded paper"),
    (r"\btitles?\b", "folded paper"),
    (r"\bnewspapers?\b", "folded paper"),
    (r"\bdocuments?\b", "blank sheet"),
    (r"\bcertificates?\b", "ribboned blank sheet"),
    (r"\b(task|answer|score)\s*sheets?\b", "blank sheets"),
    (r"\b(rule|note|text)\s*books?\b", "thick book"),
    (r"\b(due|rule|check|to-?do)\s*list\b", "row of small ticks"),
    (r"\blist\b", "row of small ticks"),
    (r"\bwith names on them\b", ""),
    (r"\bstates? the rule\b", "gestures the rule"),
    (r"\breads?\b", "looks at"),
    (r"\bwriting\b", "drawing"),
    (r"\bwrites?\b", "draws"),
    (r"\bwritten\b", "drawn"),
    (r"\btexts?\b", "marks"),
    (r"\bletters?\b", "marks"),
    (r"\bwords?\b", "marks"),
]

# 장면에서 글자를 부르는 낱말. 이 말이 들어가면 모델이 간판에 문장을 쓰려 한다
TEXT_WORDS = re.compile(
    r"\b(sign|signs|signboard|banner|poster|label|labels|board|blackboard|whiteboard|"
    r"chalkboard|billboard|notice|menu|headline|caption|title|letter|letters|word|words|"
    r"text|writing|written|writes|write|reads|reading a book|newspaper|document|slogan)\b",
    re.I,
)

# 글자를 그리지 말라고 붙이는 말. 길면 장면 설명을 밀어내므로 짧게 둔다
NO_TEXT = (
    "a scene with no letters, no words and no writing of any kind anywhere in the picture"
)

# 장면의 핵심을 고를 때 버리는 기능어
STOP = set("""
a an the of to in on at for with and or but is are was were be been being am
that this these those it its as by from has have had do does did will would
can could should may might must not no so if then than there their they them
he she his her you your we our i my me him us who whom which what when where
very more most much many some any each every all both few other another such
""".split())


def letter_of(stem: str) -> str:
    first = stem[:1].lower()
    return first if "a" <= first <= "z" else "_"


def image_path(key: str) -> str:
    slug = unicodedata.normalize("NFC", key.strip().lower().replace(" ", "-"))
    return os.path.join(ASSETS, letter_of(slug), slug + ".png")


def load_scenes() -> dict:
    """예전에 그릴 때 쓴 장면 설명. 뜻은 이걸로 잡혀 있으니 최대한 살린다"""
    import glob

    out = {}
    for path in glob.glob(SCENE_GLOB):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for k, v in data.items():
            if not isinstance(v, str):
                continue
            key = unicodedata.normalize("NFC", k.strip().lower().replace(" ", "-"))
            out.setdefault(key, v)
    return out


def strip_text_props(scene: str) -> str:
    """장면에서 글자를 부르는 소품만 바꾼다. 나머지 묘사는 그대로 둔다"""
    out = scene
    # 대문자로 또박또박 적어 둔 말은 모델이 그 글자를 그대로 그리려 한다
    out = re.sub(r"\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b", "", out)
    for pattern, repl in PROP_SWAP:
        out = re.sub(pattern, repl, out, flags=re.I)
    out = re.sub(r"\s+", " ", out)
    out = re.sub(r"\s*,\s*,+", ", ", out)
    return out.strip(" ,")


def load_words() -> dict:
    """그림 열쇠 → (낱말, 예문). 장면을 지을 재료다"""
    info = {}
    for lang in ("en", "ja"):
        p = os.path.join(ROOT, f"src/data/{lang}/words.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for spelling, entry in json.load(f).items():
                key = (entry.get("conceptId") or spelling)
                key = unicodedata.normalize("NFC", key).replace(" ", "-")
                info.setdefault(key, (spelling, entry.get("example") or ""))
    return info


def build_scene(key: str, spelling: str, example: str) -> str:
    """단어와 예문으로 글자 없는 장면 설명을 만든다.

    예문을 그대로 넘기면 "북극곰"처럼 중요한 낱말이 문장 뒤에 묻혀
    그냥 평범한 방 그림이 나온다. 그래서 뜻을 지탱하는 낱말만 뽑아
    맨 앞에 먼저 세우고, 문장은 뒤에서 상황을 보탠다.
    """
    subject = key.replace("-", " ")
    sentence = re.sub(r"[^\x00-\x7F]+", " ", example).strip()
    # 예문에 간판·문서 같은 말이 있으면 빼 버린다. 그게 글자를 부른다
    sentence = TEXT_WORDS.sub("object", sentence)
    sentence = re.sub(r"\s+", " ", sentence).strip(" ,.")

    if not sentence:
        return f"{NO_TEXT}, {subject}, a clear everyday situation showing {subject}"

    # 뜻을 지탱하는 낱말만 남긴다 (기능어와 단어 자신은 뺀다)
    own = set(re.findall(r"[a-z]+", subject.lower()))
    keys = []
    for w in re.findall(r"[A-Za-z]+", sentence):
        low = w.lower()
        if low in STOP or len(low) <= 2 or low in own or low in keys:
            continue
        keys.append(low)
    head = ", ".join(keys[:6])

    return f"{NO_TEXT}, {head}, {subject}, {sentence}" if head else f"{NO_TEXT}, {subject}, {sentence}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="대상만 보여 준다")
    ap.add_argument("--limit", type=int, default=0, help="앞에서 몇 장만 그린다")
    ap.add_argument("--start", type=int, default=0, help="몇 번째부터 그린다")
    ap.add_argument("--seed", type=int, default=777, help="시작 시드 (이전과 달라야 한다)")
    ap.add_argument("--out", type=str, default="", help="다른 폴더에 저장 (시험용)")
    args = ap.parse_args()

    with open(REGEN_LIST, encoding="utf-8") as f:
        targets = json.load(f)

    words = load_words()
    scenes = load_scenes()
    rows = targets[args.start:]
    if args.limit:
        rows = rows[: args.limit]

    with open(HAND_SCENES, encoding="utf-8") as f:
        hand = json.load(f)

    def scene_for(key: str) -> tuple[str, str]:
        """(장면, 출처). 손으로 쓴 것 → 예전 장면 → 예문 순으로 고른다"""
        if key in hand:
            return f"{NO_TEXT}, {hand[key]}", "수작업"
        orig = scenes.get(key)
        if orig:
            return f"{NO_TEXT}, {strip_text_props(orig)}", "원본"
        spelling, example = words.get(key, (key.replace("-", " "), ""))
        return build_scene(key, spelling, example), "예문"

    if args.list:
        from collections import Counter

        src = Counter()
        for i, t in enumerate(rows, 1):
            scene, where = scene_for(t["word"])
            src[where] += 1
            print(f"{i:3}. {t['word']:24} [{where}] {', '.join(t['reasons'])}")
            print(f"     {scene[:150]}")
        print(f"\n대상 {len(rows)}장 — {dict(src)}")
        return 0

    done = failed = 0
    for i, t in enumerate(rows, 1):
        key = t["word"]
        scene, where = scene_for(key)
        out = os.path.join(args.out, os.path.basename(image_path(key))) if args.out else image_path(key)

        print(f"\n[{i}/{len(rows)}] {key}  [{where}] ({', '.join(t['reasons'])})", flush=True)
        try:
            # 시드를 단어마다 다르게 줘야 예전과 같은 그림이 다시 나오지 않는다
            generate_linear_image(
                concept=scene,
                output_path=out,
                seed=args.seed + i * 13,
                width=512,
                height=512,
                steps=8,
            )
            done += 1
        except Exception as e:
            print(f"    실패: {e}", flush=True)
            failed += 1

    print(f"\n완료 {done}장 / 실패 {failed}장")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
