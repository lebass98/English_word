#!/usr/bin/env python3
"""
중1 Unit 2 및 Unit 3 단어를 src/constants/wordImages.ts 에 등록하는 스크립트
- 중복 키 검사 및 방지:
  이미 존재하는 단어명 키(sophomore, furniture, worth, crack, decrease 등)는 단어명 키 중복 생성을 배제하고 ID 키(m1-*)로만 연결
- TypeScript TS1117 중복 키 에러 원천 방지
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
WORD_IMAGES_TS = os.path.join(PROJECT_ROOT, "src", "constants", "wordImages.ts")

# 유닛 2 단어 (m1-21 ~ m1-40)
UNIT2 = [
    ("m1-21", "sophomore", "sophomore.png"),
    ("m1-22", "quarter", "quarter.png"),
    ("m1-23", "store", "store.png"),
    ("m1-24", "furniture", "furniture.png"),
    ("m1-25", "possible", "possible.png"),
    ("m1-26", "sink", "sink.png"),
    ("m1-27", "powder", "powder.png"),
    ("m1-28", "chest", "chest.png"),
    ("m1-29", "join", "join.png"),
    ("m1-30", "least", "least.png"),
    ("m1-31", "favorite", "favorite.png"),
    ("m1-32", "suppose", "suppose.png"),
    ("m1-33", "bring", "bring.png"),
    ("m1-34", "branch", "branch.png"),
    ("m1-35", "worth", "worth.png"),
    ("m1-36", "angle", "angle.png"),
    ("m1-37", "simple", "simple.png"),
    ("m1-38", "nurse", "nurse.png"),
    ("m1-39", "crack", "crack.png"),
    ("m1-40", "brown", "brown.png"),
]

# 유닛 3 단어 (m1-41 ~ m1-60)
UNIT3 = [
    ("m1-41", "decrease", "decrease.png"),
    ("m1-42", "prison", "prison.png"),
    ("m1-43", "potato", "potato.png"),
    ("m1-44", "hide", "hide.png"),
    ("m1-45", "suddenly", "suddenly.png"),
    ("m1-46", "deck", "deck.png"),
    ("m1-47", "price", "price.png"),
    ("m1-48", "expensive", "expensive.png"),
    ("m1-49", "cheap", "cheap.png"),
    ("m1-50", "robber", "robber.png"),
    ("m1-51", "equal", "equal.png"),
    ("m1-52", "unlike", "unlike.png"),
    ("m1-53", "frog", "frog.png"),
    ("m1-54", "private", "private.png"),
    ("m1-55", "upside down", "upside-down.png"),
    ("m1-56", "giant", "giant.png"),
    ("m1-57", "huge", "huge.png"),
    ("m1-58", "deal", "deal.png"),
    ("m1-59", "living room", "living-room.png"),
    ("m1-60", "nearly", "nearly.png"),
]

def register():
    with open(WORD_IMAGES_TS, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 등록된 키들 집합 수집
    existing_keys = set()
    for m in re.finditer(r'^\s*["\']?([^"\':\s]+(?:\s+[^"\':\s]+)*)["\']?\s*:', content, re.MULTILINE):
        existing_keys.add(m.group(1))

    new_entries = []

    # Unit 2 단어명 항목
    u2_word_lines = []
    for wid, wname, fname in UNIT2:
        if wname not in existing_keys:
            quoted_key = f'"{wname}"' if " " in wname else wname
            u2_word_lines.append(f'  {quoted_key}: require("../../assets/words/{fname}"),')
            existing_keys.add(wname)

    # Unit 2 ID 항목
    u2_id_lines = []
    for wid, wname, fname in UNIT2:
        if wid not in existing_keys:
            u2_id_lines.append(f'  "{wid}": require("../../assets/words/{fname}"),')
            existing_keys.add(wid)

    # Unit 3 단어명 항목
    u3_word_lines = []
    for wid, wname, fname in UNIT3:
        if wname not in existing_keys:
            quoted_key = f'"{wname}"' if " " in wname else wname
            u3_word_lines.append(f'  {quoted_key}: require("../../assets/words/{fname}"),')
            existing_keys.add(wname)

    # Unit 3 ID 항목
    u3_id_lines = []
    for wid, wname, fname in UNIT3:
        if wid not in existing_keys:
            u3_id_lines.append(f'  "{wid}": require("../../assets/words/{fname}"),')
            existing_keys.add(wid)

    addition_block = []
    if u2_word_lines or u2_id_lines:
        addition_block.append("\n  // 중학교 1학년 2Unit (20개 단어)")
        if u2_word_lines:
            addition_block.extend(u2_word_lines)
        if u2_id_lines:
            addition_block.append("  // 단어 ID 매핑 (m1-21 ~ m1-40)")
            addition_block.extend(u2_id_lines)

    if u3_word_lines or u3_id_lines:
        addition_block.append("\n  // 중학교 1학년 3Unit (20개 단어)")
        if u3_word_lines:
            addition_block.extend(u3_word_lines)
        if u3_id_lines:
            addition_block.append("  // 단어 ID 매핑 (m1-41 ~ m1-60)")
            addition_block.extend(u3_id_lines)

    if not addition_block:
        print("추가할 신규 항목이 없습니다. 이미 모두 등록되어 있습니다.")
        return

    # WORD_IMAGES 객체의 닫는 괄호 `};` 바로 앞에 삽입
    new_text = "\n".join(addition_block) + "\n"
    # 마지막 `};` 찾기
    last_brace_idx = content.rfind("};")
    if last_brace_idx == -1:
        raise RuntimeError("wordImages.ts 에서 '};' 를 찾지 못했습니다.")

    updated_content = content[:last_brace_idx] + new_text + content[last_brace_idx:]
    with open(WORD_IMAGES_TS, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"wordImages.ts 에 중1 유닛 2 & 유닛 3 매핑 등록 완료!")

if __name__ == "__main__":
    register()
