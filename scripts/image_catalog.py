#!/usr/bin/env python3
"""단어 그림 카탈로그(src/data/images/catalog.json)를 만든다.

그림은 철자 하나에 한 장이다. 학년·코스(levels/*.json)는 철자 목록만 갖고,
같은 철자는 어느 과정에서든 같은 그림을 쓴다. 뜻이 갈리는 동음이의어도
대표 뜻 하나로 통일한다 (가장 낮은 과정에서 처음 나오는 뜻).

카탈로그 한 항목:
    "bear": {
      "file": "assets/words/b/bear.png",  # 없으면 null
      "blob": "3f2a…",                    # 그림 내용 지문 (git blob). 그림이 바뀌었는지 가린다
      "courses": ["m1", "m2", "h1", "tf"],
      "sense": "곰, 낳다, 참다",          # 대표 뜻 (sense_from 칸의 한국어 뜻)
      "sense_from": "m1-123",
      "scene": "영문 장면 묘사",           # 생성에 쓰는 장면 (대표 뜻 기준)
      "scene_source": "scripts/....py",   # "manual" 이면 다시 만들어도 덮어쓰지 않는다
      "style": "v3",                      # v3 / v2 / legacy / null
      "status": "ok",                     # ok / review / missing  (status_manual 이 있으면 그 값)
      "note": "..."                       # 선택
    }

그림체 버전은 그림 파일이 마지막으로 커밋된 시각으로 가른다. 다만 그림을 폴더만
옮겼을 때는 커밋 시각이 이동 시각이 되므로, 내용 지문(blob)이 이전과 같으면
이전에 매긴 버전을 그대로 쓴다. 아직 커밋하지 않은 그림은 지금 기준(v3)으로 본다.

사용법:
    python3 scripts/image_catalog.py          # 만들고 요약 출력
    python3 scripts/image_catalog.py --check  # 파일은 쓰지 않고 요약만
"""
import argparse
import ast
import glob
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "src/data/images/catalog.json")
ASSETS = os.path.join(ROOT, "assets/words")

# 학습 과정 이름 → 단어 id 앞머리, 그리고 대표 뜻을 정할 때의 우선순위 (낮을수록 먼저)
COURSES = [
    ("middle-1", "m1"), ("middle-2", "m2"), ("middle-3", "m3"),
    ("high-1", "h1"), ("high-2", "h2"), ("high-3", "h3"), ("toefl", "tf"),
]
RANK = {code: i for i, (_, code) in enumerate(COURSES)}

# 그림체 기준이 바뀐 커밋. 그림 파일이 마지막으로 커밋된 시각으로 버전을 가른다
STYLE_COMMITS = [
    ("v3", "60a6a8b", "좁은 몸통·선 두 줄 튜브 팔다리 + 머리와 몸통 분리 (현재 기준)"),
    ("v2", "efc187d", "좁은 몸통·선 두 줄 튜브 팔다리 (머리·몸 분리 전)"),
]
LEGACY = ("legacy", "개정 전 그림 (막대 인간·SD 캐릭터·색 들어간 그림 등이 섞임)")
CURRENT_STYLE = "v3"

# 눈으로 확인해 문제가 있던 그림. status_manual 이 없는 항목에만 넣는다
KNOWN_ISSUES = {
    "control": "모니터 화면이 검게 채워지고 청록·주황색이 들어감",
    "French": "바게트에 주황·갈색, 칠판이 검게 채워짐",
    "unification": "간판 글자가 뜻 없는 영문",
    "stack": "색이 칠해지고 선이 굵음 (선형그래픽 아님)",
}


def git(*args):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else ""


def file_name(spelling):
    return spelling.replace(" ", "-")


def load_courses():
    """철자 → [(과정 코드, 단어 id)] (과정 순서대로)"""
    usage = {}
    for level, code in COURSES:
        path = os.path.join(ROOT, f"src/data/en/levels/{level}.json")
        if not os.path.exists(path):
            continue
        for i, word in enumerate(json.load(open(path)), 1):
            usage.setdefault(word, []).append((code, f"{code}-{i}"))
    return usage


def course_of(word_id, source_path):
    """장면 한 건이 어느 과정 것인지. id 가 있으면 id 로, 없으면 파일 이름으로"""
    for text in (word_id or "", os.path.basename(source_path)):
        m = re.search(r"\b(m[123]|h[123]|tf)(?:[-_]|$)", text) or re.search(r"(m[123]|h[123]|tf)_", text)
        if m:
            return m.group(1)
    return None


def collect_scenes():
    """scripts/ 에 흩어진 장면 묘사를 모두 모은다 → [(word, scene, id, course, source, commit_time)]"""
    records = []
    skip = {"scripts/image_catalog.py", "scripts/generate_images.py",
            "scripts/sync_word_images.py", "scripts/migrate_images_by_letter.py"}

    def source_time(rel):
        t = git("log", "-1", "--format=%ct", "--", rel).strip()
        return int(t) if t else 0

    def add_items(items, rel, t):
        for it in items:
            if isinstance(it, dict) and it.get("word") and it.get("scene"):
                records.append((it["word"], it["scene"], it.get("id"), course_of(it.get("id"), rel), rel, t))

    for path in sorted(glob.glob(os.path.join(ROOT, "scripts/*.py"))):
        rel = os.path.relpath(path, ROOT)
        if rel in skip:
            continue
        try:
            tree = ast.parse(open(path).read())
        except SyntaxError:
            continue
        t = None
        for node in tree.body:
            if not (isinstance(node, ast.Assign) and isinstance(node.value, (ast.Dict, ast.List))):
                continue
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                continue
            t = source_time(rel) if t is None else t
            if isinstance(value, list):
                add_items(value, rel, t)
            elif isinstance(value, dict):
                for key, v in value.items():
                    if isinstance(v, list):
                        add_items(v, rel, t)
                    elif isinstance(key, str) and isinstance(v, str) and len(v.split()) > 4:
                        records.append((key, v, None, course_of(None, rel), rel, t))

    for path in sorted(glob.glob(os.path.join(ROOT, "scripts/*.json"))):
        rel = os.path.relpath(path, ROOT)
        try:
            value = json.load(open(path))
        except ValueError:
            continue
        t = source_time(rel)
        if isinstance(value, list):
            add_items(value, rel, t)
        elif isinstance(value, dict):
            for key, v in value.items():
                if isinstance(v, str) and len(v.split()) > 4:
                    records.append((key, v, None, course_of(None, rel), rel, t))
    return records


def find_image_files():
    """파일 이름(확장자 뺀 철자) → 저장소 기준 경로. 글자 폴더가 있으면 그쪽을 쓴다"""
    files = {}
    for dirpath, _, names in os.walk(ASSETS):
        for name in names:
            if name.endswith(".png") and not name.startswith("._"):
                rel = os.path.relpath(os.path.join(dirpath, name), ROOT)
                stem = name[:-4]
                in_letter_folder = os.path.dirname(rel) != "assets/words"
                if stem not in files or in_letter_folder:
                    files[stem] = rel
    return files


def image_blobs(paths):
    """그림 경로 → 내용 지문. 커밋된 그림은 git 색인에서 한 번에, 나머지만 따로 계산"""
    blobs = {}
    for line in git("ls-files", "-s", "--", "assets/words").splitlines():
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) >= 2:
            blobs[path] = parts[1]
    for path in paths:
        if path not in blobs:
            h = git("hash-object", path).strip()
            if h:
                blobs[path] = h
    return blobs


def image_commit_times():
    """그림 파일 → 마지막으로 커밋된 시각 (git log 한 번으로)"""
    times, current = {}, None
    for line in git("log", "--format=__%ct", "--name-only", "--", "assets/words").splitlines():
        if line.startswith("__"):
            current = int(line[2:])
        elif line.strip() and current is not None:
            times.setdefault(line.strip(), current)
    return times


def style_boundaries():
    bounds = []
    for name, sha, desc in STYLE_COMMITS:
        t = git("show", "-s", "--format=%ct", sha).strip()
        if t:
            bounds.append((name, int(t), desc))
    return bounds


def build(existing):
    usage = load_courses()
    ko = json.load(open(os.path.join(ROOT, "src/data/en/tr/ko.json")))["meanings"]
    scenes = collect_scenes()
    files = find_image_files()
    blobs = image_blobs(files.values())
    img_times = image_commit_times()
    bounds = style_boundaries()

    # 철자마다 대표 장면: 가장 낮은 과정 → 같은 과정이면 가장 최근에 고친 파일
    best = {}
    for word, scene, wid, course, src, t in scenes:
        key = (RANK.get(course, len(RANK)), -t)
        if word not in best or key < best[word][0]:
            best[word] = (key, scene, wid, course, src)

    spellings = list(usage.keys()) + [
        stem.replace("-", " ") if stem.replace("-", " ") in usage else stem
        for stem in files
        if stem not in usage and stem.replace("-", " ") not in usage
    ]
    catalog = {}
    for word in dict.fromkeys(spellings):
        prev = existing.get(word, {})
        uses = usage.get(word, [])
        path = files.get(file_name(word))
        entry = {
            "file": path,
            "blob": blobs.get(path) if path else None,
            "courses": [code for code, _ in uses],
            "sense": ko.get(uses[0][1]) if uses else None,
            "sense_from": uses[0][1] if uses else None,
        }
        if prev.get("scene_source") == "manual":
            entry["scene"], entry["scene_source"] = prev.get("scene"), "manual"
        elif word in best:
            _, scene, wid, course, src = best[word]
            entry["scene"], entry["scene_source"] = scene, src
            if uses and course and RANK.get(course) != RANK.get(uses[0][0]):
                entry["note"] = f"장면이 대표 뜻 과정({uses[0][0]})이 아니라 {course} 것"
        else:
            entry["scene"], entry["scene_source"] = None, None

        style = None
        if path:
            if prev.get("blob") and prev.get("blob") == entry["blob"] and prev.get("style"):
                style = prev["style"]  # 폴더만 옮긴 그림: 이전 판정 유지
            else:
                t = img_times.get(path)
                if t is None:
                    style = CURRENT_STYLE  # 아직 커밋 안 된 새 그림
                else:
                    style = LEGACY[0]
                    for name, bound, _ in bounds:
                        if t >= bound:
                            style = name
                            break
        entry["style"] = style

        if prev.get("status_manual"):
            entry["status"] = entry["status_manual"] = prev["status_manual"]
            if prev.get("note"):
                entry["note"] = prev["note"]
        elif not path:
            entry["status"] = "missing"
        elif word in KNOWN_ISSUES and not (prev.get("blob") and prev.get("blob") != entry["blob"]):
            entry["status"], entry["note"] = "review", KNOWN_ISSUES[word]
        else:
            entry["status"] = "ok" if style == CURRENT_STYLE else "review"
        catalog[word] = entry

    meta = {
        "about": "철자 하나에 그림 한 장. 과정별 데이터는 levels/*.json 철자 목록만 갖는다. scripts/image_catalog.py 가 만든다",
        "styles": {name: desc for name, _, desc in bounds} | {LEGACY[0]: LEGACY[1]},
    }
    return {"meta": meta, "images": dict(sorted(catalog.items(), key=lambda kv: kv[0].lower()))}


def summary(data):
    images = data["images"]
    count = lambda pred: sum(1 for e in images.values() if pred(e))
    used = count(lambda e: e["courses"])
    print(f"항목 {len(images)} (과정에서 쓰는 철자 {used})")
    print(f"  그림 있음 {count(lambda e: e['file'])} / 없음 {count(lambda e: e['status'] == 'missing')}")
    print(f"  상태: ok {count(lambda e: e['status'] == 'ok')}, review {count(lambda e: e['status'] == 'review')}, missing {count(lambda e: e['status'] == 'missing')}")
    for style in ("v3", "v2", "legacy"):
        print(f"  그림체 {style}: {count(lambda e, s=style: e['style'] == s)}")
    print(f"  장면 묘사 있음 {count(lambda e: e['scene'])} / 그림 없는데 장면도 없음 {count(lambda e: e['status'] == 'missing' and not e['scene'])}")
    print(f"  장면이 대표 뜻 과정과 다른 항목 {count(lambda e: (e.get('note') or '').startswith('장면이 대표 뜻'))}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="파일은 쓰지 않고 요약만 출력")
    args = parser.parse_args()

    existing = {}
    if os.path.exists(CATALOG):
        existing = json.load(open(CATALOG)).get("images", {})
    data = build(existing)
    summary(data)
    if not args.check:
        os.makedirs(os.path.dirname(CATALOG), exist_ok=True)
        # 임시 파일에 다 쓴 다음 한 번에 바꿔 끼운다.
        # 그림 생성기가 매 장마다 이 파일을 읽는데, 바로 덮어쓰면 쓰다 만 파일을
        # 읽어 JSON 오류로 죽는다. 실제로 한 번 그렇게 멈춘 적이 있다.
        tmp = CATALOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
            f.write("\n")
        os.replace(tmp, CATALOG)
        print("wrote", os.path.relpath(CATALOG, ROOT))


if __name__ == "__main__":
    main()
