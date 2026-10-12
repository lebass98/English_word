"""웹 공유 미리보기(OG) 이미지를 만든다.

카카오톡·슬랙·페이스북 등에 링크를 붙였을 때 뜨는 1200x630 카드.
앱 아이콘(assets/icon.png)을 왼쪽에, 앱 이름과 소개 문구를 오른쪽에 둔다.
결과: public/og-image.png  (웹에서 /og-image.png 로 열린다)

    python3 scripts/make_og_image.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "public" / "og-image.png"

W, H = 1200, 630
# 아이콘 바탕(오른쪽 가장자리)과 같은 색으로 깔아야 아이콘 경계가 보이지 않는다
BG_TOP = (233, 235, 240)
BG_BOTTOM = (227, 230, 236)
INK = (30, 41, 59)
MINT = (14, 181, 130)
SUB = (100, 116, 139)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def main() -> None:
    # 아이콘 바탕과 이어지는 은은한 세로 그라데이션
    img = Image.new("RGB", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM))
        draw.line([(0, y), (W, y)], fill=c)

    # 아이콘을 카드 높이에 꽉 차게 왼쪽에 둔다. 오른쪽 끝은 배경으로 서서히 녹인다
    icon = Image.open(ROOT / "assets" / "icon.png").convert("RGBA")
    icon = icon.resize((H, H), Image.LANCZOS)
    fade = 140
    mask = Image.new("L", icon.size, 255)
    md = ImageDraw.Draw(mask)
    for i in range(fade):
        md.line([(H - fade + i, 0), (H - fade + i, H)], fill=round(255 * (1 - i / fade)))
    img.paste(icon, (0, 0), mask)

    x = 610
    title = font("PretendardGOV-Black.otf", 120)
    draw.text((x, 150), "Word", font=title, fill=INK)
    word_w = draw.textlength("Word", font=title)
    draw.text((x + word_w, 150), "Pic", font=title, fill=MINT)

    draw.text(
        (x + 4, 320),
        "그림으로 외우는 영어 단어",
        font=font("PretendardGOV-Bold.otf", 48),
        fill=INK,
    )
    draw.text(
        (x + 4, 400),
        "중학 · 고등 · 토익 · 토플",
        font=font("PretendardGOV-Regular.otf", 34),
        fill=SUB,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"saved {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
