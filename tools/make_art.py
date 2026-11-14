"""Genereert alle eigen plaatjes: iconen, fanart, logo en getekende gezichtjes.

Gebruik:  python tools/make_art.py
Vereist Pillow (pip install pillow). Alleen nodig als je plaatjes wilt vernieuwen;
de uitvoer staat gewoon in git. Kleuren staan hieronder.

Uitvoer:
  repository.spaan/icon.png, fanart.jpg
  skin-mod/overlay/icon.png, fanart.jpg
  skin-mod/overlay/extras/icons/kodi.png          logo (wit, de skin kleurt het in)
  skin-mod/overlay/extras/krispijn/faces/*.png    getekende gezichtjes (tijdelijk,
                                                  te vervangen door eigen foto's)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "repository.spaan"
OVERLAY = ROOT / "skin-mod" / "overlay"

BG_TOP = (16, 20, 31)
BG_BOTTOM = (6, 8, 13)
ACCENT = (229, 57, 53)
TEXT = (245, 245, 245)
INK = (30, 30, 36)
FONT = "C:/Windows/Fonts/segoeuib.ttf"
SS = 4  # tekenen op 4x en verkleinen geeft gladde randen


def font(size):
    return ImageFont.truetype(FONT, size)


def gradient(width, height):
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / (height - 1)
        draw.line([(0, y), (width, y)],
                  fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))
    return img, draw


def tile_icon(letter, path, size=512):
    img, draw = gradient(size, size)
    m = size * 96 // 512
    draw.rounded_rectangle([m, m, size - m, size - m], radius=size // 8, fill=ACCENT)
    draw.text((size / 2, size * 250 / 512), letter, font=font(size * 250 // 512), fill=TEXT, anchor="mm")
    img.save(path, optimize=True)


def fanart(title, path, subtitle=None):
    img, draw = gradient(1920, 1080)
    draw.rectangle([160, 500, 172, 620], fill=ACCENT)
    draw.text((210, 545 if subtitle else 560), title, font=font(120), fill=TEXT, anchor="lm")
    if subtitle:
        draw.text((214, 640), subtitle, font=font(40), fill=(170, 170, 178), anchor="lm")
    img.save(path, quality=88)


def logo_glyph(path, size=128):
    """Wit logo op transparant: de skin kleurt het met de accentkleur."""
    big = size * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad, stroke = big * 6 // 128, big * 10 // 128
    draw.rounded_rectangle([pad, pad, big - pad, big - pad], radius=big // 4,
                           outline=(255, 255, 255, 255), width=stroke)
    draw.text((big / 2, big * 0.49), "K", font=font(big * 78 // 128), fill=(255, 255, 255, 255), anchor="mm")
    img.resize((size, size), Image.LANCZOS).save(path, optimize=True)


def background(path):
    """Zachte achtergrond in themakleur, in de stijl van de blur-achtergronden van de skin."""
    small = Image.new("RGB", (192, 108), (11, 14, 21))
    draw = ImageDraw.Draw(small)
    draw.ellipse([-70, 40, 80, 170], fill=(150, 28, 30))      # rode gloed linksonder
    draw.ellipse([60, -30, 150, 50], fill=(26, 32, 58))       # koel blauw midden boven
    draw.ellipse([150, 60, 230, 140], fill=(52, 22, 30))      # warme tint rechtsonder
    small = small.filter(ImageFilter.GaussianBlur(26))
    small.resize((1920, 1080), Image.BICUBIC).filter(ImageFilter.GaussianBlur(12)).save(path, quality=90)


# --- gezichtjes ------------------------------------------------------------

class Face:
    """Tekent op een vlak van 512x512 (intern 4x zo groot)."""

    def __init__(self, colour):
        self.img = Image.new("RGBA", (512 * SS, 512 * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.ellipse(256, 256, 236, 236, fill=INK)
        self.ellipse(256, 256, 222, 222, fill=colour)

    def s(self, *values):
        return [v * SS for v in values]

    def ellipse(self, cx, cy, rx, ry, **kw):
        if "width" in kw:
            kw["width"] *= SS
        self.d.ellipse(self.s(cx - rx, cy - ry, cx + rx, cy + ry), **kw)

    def arc(self, cx, cy, rx, ry, start, end, width=14, fill=INK):
        self.d.arc(self.s(cx - rx, cy - ry, cx + rx, cy + ry), start, end, fill=fill, width=width * SS)

    def line(self, points, width=14, fill=INK):
        self.d.line([c * SS for p in points for c in p], fill=fill, width=width * SS, joint="curve")

    def rounded(self, x0, y0, x1, y1, r, **kw):
        if "width" in kw:
            kw["width"] *= SS
        self.d.rounded_rectangle(self.s(x0, y0, x1, y1), radius=r * SS, **kw)

    def eye(self, cx, cy, r=46, look=(0, 0), pupil=20):
        self.ellipse(cx, cy, r, r, fill=(255, 255, 255), outline=INK, width=8)
        self.ellipse(cx + look[0], cy + look[1], pupil, pupil, fill=INK)

    def tongue(self, cx, top, w=70, h=86):
        self.rounded(cx - w / 2, top, cx + w / 2, top + h, w / 2, fill=(240, 98, 120), outline=INK, width=8)
        self.line([(cx, top + 10), (cx, top + h - 30)], width=6)

    def save(self, path):
        self.img.resize((512, 512), Image.LANCZOS).save(path, optimize=True)


def faces(out):
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()

    f = Face((255, 202, 40))                      # 1: knipoog met tong
    f.eye(176, 210, look=(8, 6))
    f.arc(336, 222, 48, 34, 200, 340)
    f.arc(256, 300, 120, 78, 20, 160)
    f.tongue(286, 352)
    f.save(out / "gezicht-1.png")

    f = Face((129, 212, 250))                     # 2: scheel met kronkelmond
    f.eye(176, 216, r=56, look=(26, 10), pupil=18)
    f.eye(336, 216, r=56, look=(-26, 10), pupil=18)
    f.line([(150, 364), (188, 334), (226, 364), (264, 334), (302, 364), (340, 334), (372, 360)])
    f.save(out / "gezicht-2.png")

    f = Face((174, 213, 129))                     # 3: grote grijns met tanden
    f.arc(176, 150, 50, 30, 190, 350, width=12)
    f.arc(336, 136, 50, 30, 190, 350, width=12)
    f.eye(176, 220, r=40, pupil=18)
    f.eye(336, 220, r=40, pupil=18)
    f.rounded(132, 300, 380, 400, 44, fill=(255, 255, 255), outline=INK, width=10)
    for x in (182, 232, 282, 332):
        f.line([(x, 304), (x, 396)], width=6)
    f.line([(138, 350), (374, 350)], width=6)
    f.save(out / "gezicht-3.png")

    f = Face((255, 171, 145))                     # 4: verbaasd
    f.eye(170, 204, r=62, pupil=26)
    f.eye(342, 204, r=62, pupil=26)
    f.ellipse(256, 372, 44, 58, fill=INK)
    f.ellipse(256, 392, 26, 26, fill=(240, 98, 120))
    f.save(out / "gezicht-4.png")

    f = Face((206, 147, 216))                     # 5: bolle wangen, dichtgeknepen ogen
    f.line([(130, 196), (186, 222), (130, 248)])
    f.line([(382, 196), (326, 222), (382, 248)])
    f.ellipse(120, 318, 46, 38, fill=(240, 98, 146))
    f.ellipse(392, 318, 46, 38, fill=(240, 98, 146))
    f.ellipse(256, 350, 26, 26, fill=INK)
    f.save(out / "gezicht-5.png")

    f = Face((255, 138, 101))                     # 6: bril, scheve mond, tong opzij
    f.rounded(104, 164, 236, 276, 30, fill=(255, 255, 255), outline=INK, width=12)
    f.rounded(276, 164, 408, 276, 30, fill=(255, 255, 255), outline=INK, width=12)
    f.line([(236, 214), (276, 214)], width=12)
    f.ellipse(190, 236, 18, 18, fill=INK)
    f.ellipse(320, 200, 18, 18, fill=INK)
    f.line([(160, 372), (240, 352), (350, 380)])
    f.tongue(326, 366, w=58, h=70)
    f.save(out / "gezicht-6.png")


if __name__ == "__main__":
    tile_icon("S", REPO / "icon.png")
    fanart("SPAAN", REPO / "fanart.jpg")
    OVERLAY.mkdir(parents=True, exist_ok=True)
    tile_icon("K", OVERLAY / "icon.png")
    fanart("FAMILIE KRISPIJN", OVERLAY / "fanart.jpg", subtitle="gebaseerd op Arctic Fuse 3 van jurialmunkey")
    (OVERLAY / "extras" / "icons").mkdir(parents=True, exist_ok=True)
    logo_glyph(OVERLAY / "extras" / "icons" / "kodi.png")
    faces(OVERLAY / "extras" / "krispijn" / "faces")
    background(OVERLAY / "extras" / "krispijn" / "background.jpg")
    print("Plaatjes geschreven.")
