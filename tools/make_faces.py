"""Maakt van gewone foto's ronde gezichtjes voor de skin.

Gebruik:
  1. Zet foto's (jpg/png) in de map  fotos/  in de projectroot. Die map staat in
     .gitignore en komt dus NIET op GitHub.
  2. python tools/make_faces.py
  3. Kopieer de map  fotos/klaar/  naar het apparaat (USB of netwerk) en kies hem
     in Kodi via het homescherm-menu > Fotomap gezichtjes.

Elke foto wordt vierkant uitgesneden rond het midden, rond gemaakt met een donker
randje en opgeslagen als png van 512x512. Zorg dus dat het gezicht ongeveer in het
midden van de foto staat. Vereist Pillow (pip install pillow).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "fotos"
OUT = SRC / "klaar"
SIZE, BORDER, SS = 512, 14, 4


def make_round(path):
    photo = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    photo = ImageOps.fit(photo, (SIZE, SIZE), Image.LANCZOS, centering=(0.5, 0.4))
    big = SIZE * SS
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse([BORDER * SS, BORDER * SS, big - BORDER * SS, big - BORDER * SS], fill=255)
    ring = Image.new("L", (big, big), 0)
    ImageDraw.Draw(ring).ellipse([0, 0, big - 1, big - 1], fill=255)
    out = Image.new("RGBA", (SIZE, SIZE), (30, 30, 36, 0))
    out.putalpha(ring.resize((SIZE, SIZE), Image.LANCZOS))
    out.paste(photo, (0, 0), mask.resize((SIZE, SIZE), Image.LANCZOS))
    return out


def main():
    photos = sorted(p for p in SRC.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
    if not photos:
        sys.exit(f"Geen foto's gevonden in {SRC}. Maak de map aan en zet er foto's in.")
    OUT.mkdir(parents=True, exist_ok=True)
    for path in photos:
        make_round(path).save(OUT / f"{path.stem}.png", optimize=True)
        print(f"  {path.name} -> klaar/{path.stem}.png")
    print(f"Klaar: {len(photos)} gezichtjes in {OUT}")


if __name__ == "__main__":
    main()
