# -*- coding: utf-8 -*-
"""그림에서 읽어 낸 글자를 영어 사전과 대조해 잘못된 그림을 추린다.

영어를 가르치는 앱이라 그림 속 철자가 틀리면 그대로 잘못 배운다.
OCR 이 뽑은 낱말을 사전에 넣어 보고, 사전에 없는 낱말이 섞인 그림을 표시한다.
사람 이름·상표처럼 사전에 없는 멀쩡한 낱말도 있으므로, 확정이 아니라
"눈으로 확인할 후보"를 좁히는 것이 목적이다.

  python3 scripts/check_image_text.py /tmp/ocr.json
"""

import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
OCR = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ocr.json")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/text_issues.json")

DICT = pathlib.Path("/usr/share/dict/words")

# 사전에 없지만 그림에 흔히 나오는 멀쩡한 낱말
EXTRA = {
    "ok", "tv", "wifi", "cafe", "menu", "sale", "open", "closed", "exit",
    "stop", "off", "on", "new", "km", "kg", "cm", "mm", "am", "pm", "usb",
    "id", "no", "yes", "dont", "cant", "wont", "isnt", "arent", "im", "ive",
    "its", "lets", "youre", "theyre", "wasnt", "didnt", "doesnt", "hasnt",
    "couldnt", "wouldnt", "shouldnt", "thats", "whats", "hes", "shes",
    "ill", "well", "were", "youve", "theyve", "weve", "id", "wed",
    "email", "online", "website", "app", "ceo", "diy", "faq", "vip",
    "gym", "zoo", "atm", "tax", "fee", "bus", "taxi", "hotel", "museum",
    "library", "bank", "park", "school", "store", "shop", "market",
    "today", "tomorrow", "yesterday", "monday", "tuesday", "wednesday",
    "thursday", "friday", "saturday", "sunday",
}


def load_dict() -> set[str]:
    words = {w.strip().lower() for w in DICT.read_text(errors="ignore").splitlines()}
    words |= EXTRA
    # 복수형·과거형은 사전에 없는 경우가 많아 간단한 어미를 붙여 넓힌다
    grown = set(words)
    for w in words:
        grown |= {w + "s", w + "es", w + "ed", w + "d", w + "ing", w + "ly"}
    return grown


HANGUL = re.compile(r"[가-힣]")
CJK = re.compile(r"[一-鿿぀-ヿ]")


def main() -> None:
    vocab = load_dict()
    ocr = json.loads(OCR.read_text(encoding="utf-8"))

    rows = []
    for key, lines in ocr.items():
        texts = [t for t, c in lines]
        joined = " ".join(texts)
        if not joined.strip():
            continue

        tokens = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z']{1,}", joined)]
        # 한 글자·숫자만 있는 그림은 판단 대상이 아니다
        if len(tokens) < 2:
            bad = []
        else:
            bad = [t for t in tokens if t.replace("'", "") not in vocab]

        flags = []
        if HANGUL.search(joined):
            flags.append("한글")
        if CJK.search(joined):
            flags.append("한자/가나")
        if tokens and len(bad) / len(tokens) >= 0.34 and len(bad) >= 2:
            flags.append("철자오류")
        elif bad and len(tokens) >= 4 and len(bad) >= 2:
            flags.append("의심")

        if flags:
            rows.append({
                "word": key,
                "flags": flags,
                "bad": bad[:12],
                "tokens": len(tokens),
                "text": joined[:220],
            })

    rows.sort(key=lambda r: (-len(r["flags"]), -len(r["bad"])))
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    tally = Counter(f for r in rows for f in r["flags"])
    print(f"글자가 있는 그림 {sum(1 for v in ocr.values() if v)}장 중 표시 {len(rows)}장")
    for k, v in tally.most_common():
        print(f"  {k}: {v}장")
    print(f"→ {OUT}")


if __name__ == "__main__":
    main()
