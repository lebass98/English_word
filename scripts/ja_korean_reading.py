# -*- coding: utf-8 -*-
"""일본어 가나 발음을 한국어 표기로 바꿔 tr/ko.json 에 넣는다.

표기는 국립국어원 외래어 표기법(일본어)을 따른다.
  - か행/た행은 어두에서 평음(가·다), 어중·어말에서 격음(카·타)
  - つ 는 자리와 무관하게 '쓰'
  - ん 은 'ㄴ' 받침, 촉음 っ 은 'ㅅ' 받침
  - 장음(ー)은 적지 않는다
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORDS = ROOT / "src/data/ja/words.json"
TR_KO = ROOT / "src/data/ja/tr/ko.json"

# 어중·어말에서 쓰는 기본 표기
MID = {
    "あ": "아", "い": "이", "う": "우", "え": "에", "お": "오",
    "か": "카", "き": "키", "く": "쿠", "け": "케", "こ": "코",
    "が": "가", "ぎ": "기", "ぐ": "구", "げ": "게", "ご": "고",
    "さ": "사", "し": "시", "す": "스", "せ": "세", "そ": "소",
    "ざ": "자", "じ": "지", "ず": "즈", "ぜ": "제", "ぞ": "조",
    "た": "타", "ち": "치", "つ": "쓰", "て": "테", "と": "토",
    "だ": "다", "ぢ": "지", "づ": "즈", "で": "데", "ど": "도",
    "な": "나", "に": "니", "ぬ": "누", "ね": "네", "の": "노",
    "は": "하", "ひ": "히", "ふ": "후", "へ": "헤", "ほ": "호",
    "ば": "바", "び": "비", "ぶ": "부", "べ": "베", "ぼ": "보",
    "ぱ": "파", "ぴ": "피", "ぷ": "푸", "ぺ": "페", "ぽ": "포",
    "ま": "마", "み": "미", "む": "무", "め": "메", "も": "모",
    "や": "야", "ゆ": "유", "よ": "요",
    "ら": "라", "り": "리", "る": "루", "れ": "레", "ろ": "로",
    "わ": "와", "を": "오",
}

# 어두에서만 다르게 적는 글자 (か행·た행 평음화)
INIT = {
    "か": "가", "き": "기", "く": "구", "け": "게", "こ": "고",
    "た": "다", "ち": "지", "て": "데", "と": "도",
}

# 요음(拗音). 두 글자가 한 음절이 된다
MID_YOUON = {
    "きゃ": "캬", "きゅ": "큐", "きょ": "쿄",
    "ぎゃ": "갸", "ぎゅ": "규", "ぎょ": "교",
    "しゃ": "샤", "しゅ": "슈", "しょ": "쇼",
    "じゃ": "자", "じゅ": "주", "じょ": "조",
    "ちゃ": "차", "ちゅ": "추", "ちょ": "초",
    "にゃ": "냐", "にゅ": "뉴", "にょ": "뇨",
    "ひゃ": "햐", "ひゅ": "휴", "ひょ": "효",
    "びゃ": "뱌", "びゅ": "뷰", "びょ": "뵤",
    "ぴゃ": "퍄", "ぴゅ": "퓨", "ぴょ": "표",
    "みゃ": "먀", "みゅ": "뮤", "みょ": "묘",
    "りゃ": "랴", "りゅ": "류", "りょ": "료",
}

INIT_YOUON = {
    "きゃ": "갸", "きゅ": "규", "きょ": "교",
    "ちゃ": "자", "ちゅ": "주", "ちょ": "조",
}

# 가나의 모음. お·う 단 뒤에 오는 う 는 장음이라 적지 않는다.
# 한글 표기의 중성에서 모음을 되짚는다 (ㅏ=0, ㅗ=8, ㅜ=13, ㅡ=18, ㅣ=20 …)
_JUNG_VOWEL = {
    0: "a", 1: "e", 2: "a", 3: "e", 4: "e", 5: "e", 6: "e", 7: "e",
    8: "o", 12: "o", 13: "u", 17: "u", 18: "u", 20: "i",
}


def _vowel_of(hangul: str) -> str:
    jung = ((ord(hangul[-1]) - 0xAC00) % 588) // 28
    return _JUNG_VOWEL.get(jung, "i")


VOWEL = {k: _vowel_of(v) for k, v in MID.items()}
VOWEL.update({k: _vowel_of(v) for k, v in MID_YOUON.items()})

# 가타카나는 히라가나로 바꿔 같은 표에 태운다
def to_hiragana(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        # 가타카나 블록(ァ~ヶ)을 히라가나로 내린다
        if 0x30A1 <= code <= 0x30F6:
            out.append(chr(code - 0x60))
        else:
            out.append(ch)
    return "".join(out)


JONG_N = 4   # ㄴ
JONG_S = 19  # ㅅ


def add_jong(syllable: str, jong: int) -> str:
    """앞 음절에 받침을 얹는다. 이미 받침이 있으면 그대로 둔다"""
    code = ord(syllable) - 0xAC00
    if not (0 <= code < 11172) or code % 28 != 0:
        return syllable
    return chr(0xAC00 + code + jong)


def to_korean(kana: str) -> str:
    src = to_hiragana(kana)
    out: list[str] = []
    prev_kana = ""
    i = 0
    # 어두 판정용. 아직 글자를 하나도 못 뽑았으면 어두다
    while i < len(src):
        ch = src[i]
        head = not out

        # 장음은 적지 않는다
        if ch == "ー":
            i += 1
            continue

        # お·う 단 뒤의 う 는 장음이다. こう→코, しゅう→슈
        if ch == "う" and VOWEL.get(prev_kana) in ("o", "u"):
            i += 1
            continue

        # 촉음은 앞 음절의 ㅅ 받침이 된다
        if ch == "っ":
            if out:
                out[-1] = add_jong(out[-1], JONG_S)
            i += 1
            continue

        # 발음(撥音)은 앞 음절의 ㄴ 받침이 된다
        if ch == "ん":
            if out:
                out[-1] = add_jong(out[-1], JONG_N)
            else:
                out.append("응")
            i += 1
            continue

        # 요음을 먼저 본다 (두 글자)
        pair = src[i : i + 2]
        if len(pair) == 2 and pair in MID_YOUON:
            table = INIT_YOUON if head else MID_YOUON
            out.append(table.get(pair, MID_YOUON[pair]))
            prev_kana = pair
            i += 2
            continue

        table = INIT if head else MID
        mapped = table.get(ch) or MID.get(ch)
        if mapped:
            out.append(mapped)
            prev_kana = ch
        i += 1

    return "".join(out)


def main() -> None:
    words = json.loads(WORDS.read_text(encoding="utf-8"))
    tr = json.loads(TR_KO.read_text(encoding="utf-8"))
    details = tr.setdefault("details", {})

    filled = 0
    for spelling, entry in words.items():
        kana = entry.get("phonetic")
        if not kana:
            continue
        reading = to_korean(kana)
        if not reading:
            continue
        details.setdefault(spelling, {})["readingKo"] = reading
        filled += 1

    TR_KO.write_text(
        json.dumps(tr, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
    )
    print(f"한국어 발음 {filled}개 기록")


if __name__ == "__main__":
    main()
