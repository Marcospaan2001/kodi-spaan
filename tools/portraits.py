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

    # De startup heeft een eigen achtergrondinclude, los van Background.Image.
    background = skin_dir / '1080i/Includes_Background.xml'
    bt = ET.parse(background)
    node = bt.getroot().find("include[@name='Background_StartUp']/definition")
    if node is None:
        raise ValueError('Startupachtergrond ontbreekt')
    node.clear()
    node.append(ET.fromstring('<control type="image"><width>1920</width><height>1080</height><texture colordiffuse="ff101217">common/white.png</texture></control>'))
    background.write_bytes(ET.tostring(bt.getroot(),encoding='utf-8',xml_declaration=True))
    shutil.copyfile(ROOT / 'video-mod/icon.png', skin_dir / 'extras/krispijn/brand.png')
    objects = skin_dir / '1080i/Includes_Objects.xml'
    ot = ET.parse(objects)
    logo = ot.getroot().find("include[@name='Object_StartUp_Logo']")
    if logo is None:
        raise ValueError('Startuplogo ontbreekt')
    logo.clear()
    logo.set('name','Object_StartUp_Logo')
    logo.append(ET.fromstring('<control type="image"><left>710</left><top>375</top><width>500</width><height>230</height><aspectratio>keep</aspectratio><texture>special://skin/extras/krispijn/brand.png</texture></control>'))
    objects.write_bytes(ET.tostring(ot.getroot(),encoding='utf-8',xml_declaration=True))
