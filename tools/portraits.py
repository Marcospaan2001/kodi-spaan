"""Meegeleverde familieportretten voor Kodi 21, zonder achtergrondservice."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def apply_portraits(skin_dir):
    # Een rustige achtergrond zonder de oude ondertitel in de afbeelding.
    shutil.copyfile(ROOT / 'skin-mod/overlay/extras/krispijn/background.jpg', skin_dir / 'fanart.jpg')
    source = ROOT / 'skin-mod/portraits'
    photos = sorted(source.glob('portret-*.jpg'))
    if len(photos) != 7:
        raise ValueError('Er moeten precies zeven familieportretten aanwezig zijn')
    target = skin_dir / 'extras/krispijn/faces'
    shutil.rmtree(target)
    target.mkdir()
    for photo in photos:
        shutil.copyfile(photo, target / photo.name)
    path = skin_dir / '1080i/Includes_Krispijn.xml'
    text = path.read_text(encoding='utf-8')
    old = '<value>special://profile/addon_data/skin.arctic.fuse.2.krispijn/faces/</value>'
    if text.count(old) != 1:
        raise ValueError('Verwachte standaardfotomap ontbreekt')
    text = text.replace(old, '<value>special://skin/extras/krispijn/faces/</value>')
    start = text.index('<expression name="Exp_Krispijn_FaceMoment">')
    end = text.index('</expression>', start)
    text = text[:start] + '<expression name="Exp_Krispijn_FaceMoment">!Skin.HasSetting(Krispijn.DisableFaces)' + text[end:]
    # Rustige familiegalerij tijdens het starten; geen gezichten op de spinner.
    import xml.etree.ElementTree as ET
    tree = ET.fromstring(text)
    busy = tree.find("include[@name='Krispijn_BusyFace']")
    busy.clear()
    busy.set('name', 'Krispijn_BusyFace')
    splash = tree.find("include[@name='Krispijn_Splash_Extras']")
    splash.clear()
    splash.set('name', 'Krispijn_Splash_Extras')
    group = ET.SubElement(splash, 'control', {'type': 'group'})
    ET.SubElement(group, 'visible').text = '!Skin.HasSetting(Krispijn.DisableFaces)'
    ET.SubElement(group, 'left').text = '574'
    ET.SubElement(group, 'top').text = '265'
    for index in range(7):
        card = ET.SubElement(group, 'control', {'type': 'image'})
        for tag, value in [('left',str(index*112)),('width','100'),('height','100'),('aspectratio','keep'),('texture', f'special://skin/extras/krispijn/faces/portret-{index+1}.jpg')]:
            ET.SubElement(card, tag).text = value
    label = ET.SubElement(splash, 'control', {'type':'label'})
    for tag, value in [('left','400'),('top','650'),('width','1120'),('height','48'),('font','font_main'),('align','center'),('textcolor','ffb9bdc8'),('label','Een avond voor ons samen')]:
        ET.SubElement(label,tag).text=value
    path.write_bytes(ET.tostring(tree, encoding='utf-8', xml_declaration=True))
