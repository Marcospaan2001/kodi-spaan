"""Genereert icon.png (512x512) en fanart.jpg (1920x1080) voor repository.spaan.

Tijdelijk beeldmerk tot het thema in fase 2 vastligt. Pas de kleuren hieronder aan
en draai opnieuw:  python tools/make_art.py
Vereist Pillow (pip install pillow). Alleen nodig als je de plaatjes wilt vernieuwen.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "repository.spaan"

BG_TOP = (16, 20, 31)      # donkerblauw
BG_BOTTOM = (6, 8, 13)     # bijna zwart
ACCENT = (229, 57, 53)     # rood
TEXT = (245, 245, 245)
FONT = "C:/Windows/Fonts/segoeuib.ttf"


def gradient(width, height):
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / (height - 1)
        draw.line(
            [(0, y), (width, y)],
            fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)),
        )
    return img, draw


def make_icon():
    img, draw = gradient(512, 512)
    draw.rounded_rectangle([96, 96, 416, 416], radius=64, fill=ACCENT)
    draw.text((256, 250), "S", font=ImageFont.truetype(FONT, 250), fill=TEXT, anchor="mm")
    img.save(OUT / "icon.png", optimize=True)


def make_fanart():
    img, draw = gradient(1920, 1080)
    draw.rectangle([160, 500, 172, 620], fill=ACCENT)
    draw.text((210, 560), "SPAAN", font=ImageFont.truetype(FONT, 120), fill=TEXT, anchor="lm")
    img.save(OUT / "fanart.jpg", quality=88)


if __name__ == "__main__":
    make_icon()
    make_fanart()
    print(f"icon.png en fanart.jpg geschreven naar {OUT}")
