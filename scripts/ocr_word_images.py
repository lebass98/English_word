# -*- coding: utf-8 -*-
"""단어 그림 안에 적힌 글자를 모두 읽어 낸다 (macOS Vision).

이 앱은 영어를 가르치는 앱이라 그림 속 영어 철자가 틀리면 그대로 잘못 배운다.
사람이 5천 장을 일일이 읽을 수 없으니 글자만 기계로 뽑아 두고,
사전에 없는 낱말이 섞인 그림만 따로 추려 눈으로 확인한다.

  python3 scripts/ocr_word_images.py <결과.json> [폴더]
"""

import json
import pathlib
import sys

import Quartz
import Vision

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ocr.json")
TARGET = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "assets/words"


def read_text(path: pathlib.Path) -> list[tuple[str, float]]:
    url = Quartz.CFURLCreateWithFileSystemPath(
        None, str(path), Quartz.kCFURLPOSIXPathStyle, False
    )
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    if src is None:
        return []
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    if img is None:
        return []

    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    req.setUsesLanguageCorrection_(False)  # 틀린 철자를 고쳐 버리면 안 된다
    req.setRecognitionLanguages_(["ko-KR", "en-US"])

    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    ok, _ = handler.performRequests_error_([req], None)
    if not ok:
        return []

    out = []
    for obs in req.results() or []:
        cand = obs.topCandidates_(1)
        if cand:
            out.append((str(cand[0].string()), float(cand[0].confidence())))
    return out


def main() -> None:
    files = sorted(TARGET.rglob("*.png"))
    result = {}
    for i, f in enumerate(files, 1):
        try:
            result[f.stem] = read_text(f)
        except Exception as e:
            result[f.stem] = [("__오류__: " + str(e), 0.0)]
        if i % 250 == 0:
            print(f"  {i}/{len(files)}", flush=True)

    OUT.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    with_text = sum(1 for v in result.values() if v)
    print(f"\n{len(files)}장 중 글자가 있는 그림 {with_text}장 → {OUT}")


if __name__ == "__main__":
    main()
