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
    # Dit staat alleen in het startmenu van onze video-add-on, nooit bij films.
    entry = '''
    <include name="Krispijn_AddonPortrait">
        <control type="group" id="99873">
            <visible>!Skin.HasSetting(Krispijn.DisableFaces) + [String.IsEqual(Container.FolderPath,plugin://plugin.video.krispijn/) | String.IsEqual(Container.FolderPath,plugin://plugin.video.krispijn/?mode=krispijn.home) | String.IsEqual(Container.FolderPath,plugin://plugin.video.krispijn/?mode=navigator.main)]</visible>
            <left>1660</left><top>150</top><width>150</width><height>150</height>
            <control type="multiimage">
                <width>150</width><height>150</height>
                <imagepath>$VAR[Krispijn_FacesPath]</imagepath>
                <aspectratio>keep</aspectratio>
                <timeperimage>5000</timeperimage><fadetime>200</fadetime>
                <randomize>true</randomize><loop>yes</loop>
            </control>
        </control>
    </include>
'''
    text = text.replace('</includes>', entry + '</includes>')
    path.write_bytes(text.encode('utf-8'))
    path = skin_dir / '1080i/MyVideoNav.xml'
    text = path.read_text(encoding='utf-8')
    if text.count('</controls>') != 1:
        raise ValueError('Onverwachte video-navigatie')
    path.write_bytes(text.replace('</controls>', '<include>Krispijn_AddonPortrait</include>\n    </controls>').encode('utf-8'))
