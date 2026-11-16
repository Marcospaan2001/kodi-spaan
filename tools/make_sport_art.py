"""Maak kleine lokale sporttegels zonder externe afbeeldingen of logo's."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1] / 'video-mod/resources/media/sports'
root.mkdir(parents=True, exist_ok=True)
for name in ('f1', 'voetbal', 'darts'):
    im = Image.new('RGB', (920, 220), '#151c29')
    d = ImageDraw.Draw(im)
    for x in range(920):
        d.line((x, 0, x, 220), fill=(20 + x // 45, 26 + x // 70, 38 + x // 65))
    d.line((0, 219, 920, 219), fill='#e53935', width=6)
    if name == 'f1':
        d.line((72, 185, 72, 60), fill='white', width=6)
        for x in range(5):
            for y in range(3):
                d.rectangle((77+x*22,60+y*22,99+x*22,82+y*22), fill='white' if (x+y)%2==0 else '#e53935')
    elif name == 'voetbal':
        d.ellipse((65,55,195,185), outline='white', width=5)
        d.regular_polygon((130,120,31),5,rotation=0,fill='#e53935')
        for a,b in [((130,89),(130,55)),((100,110),(68,94)),((111,145),(93,175)),((149,145),(168,175)),((160,110),(191,94))]:
            d.line((a,b),fill='white',width=4)
    else:
        for r in (67,45,23):
            d.ellipse((130-r,120-r,130+r,120+r),outline='white',width=4)
        d.ellipse((123,113,137,127),fill='#e53935')
        d.line((130,120,199,57),fill='#e53935',width=7)
        d.polygon(((199,57),(184,57),(199,73)),fill='#e53935')
    im.save(root / (name+'.png'), optimize=True)
