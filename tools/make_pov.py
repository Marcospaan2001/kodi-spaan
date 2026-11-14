"""Bouw Krispijn Video uit een vastgezette, gecontroleerde POV-bron (GPL-3.0)."""
import ast
import hashlib
import io
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_ID = 'plugin.video.pov'
ADDON_ID = 'plugin.video.krispijn'
VERSION = '1.0.1'
URL = 'https://raw.githubusercontent.com/kodifitzwell/repo/2c8390c6e65213853a862a00044597946b946132/plugin.video.pov/plugin.video.pov-6.11.03.zip'
SHA256 = '9ac93ad045910774503cbfeeb45b63bbd9b23837c9e76749885076c9b11edfba'


def download(url, maximum=32 * 1024 * 1024):
    request = urllib.request.Request(url, headers={'User-Agent': 'KrispijnVideoBuild/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError('Download groter dan toegestaan')
    return data


def make_pov():
    archive_path = ROOT / 'video-mod/upstream-pov-6.11.03.zip'
    data = archive_path.read_bytes() if archive_path.exists() else download(URL)
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('POV-bron wijkt af van de vastgezette SHA256; bouw gestopt.')
    if not archive_path.exists():
        archive_path.write_bytes(data)
    folder = ROOT / 'build' / ADDON_ID
    if folder.exists():
        shutil.rmtree(folder)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip() is not None:
            raise ValueError('Beschadigd POV-bronpakket')
        for item in archive.infolist():
            if item.is_dir():
                continue
            parts = item.filename.split('/')
            if parts[0] != UPSTREAM_ID or any(p in ('', '..') for p in parts) or '\\' in item.filename:
                raise ValueError('Ongeldig pad in POV-bronpakket')
            target = folder.joinpath(*parts[1:])
            content = archive.read(item)
            if target.suffix in {'.py', '.xml', '.json', '.po', '.txt'}:
                content = (
                    content.decode('utf-8-sig')
                    .replace(UPSTREAM_ID, ADDON_ID)
                    .replace(UPSTREAM_ID[::-1], ADDON_ID[::-1])
                    .replace('getVideoInfoTag(offscreen=True)', 'getVideoInfoTag()')
                    .replace('pov_fanart.png', 'fanart.jpg')
                    .replace('pov_poster.png', 'icon.png')
                    .replace('pov.png', 'icon.png')
                    .encode('utf-8')
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    path = folder / 'addon.xml'
    tree = ET.parse(path)
    addon = tree.getroot()
    if addon.get('version') != '6.11.03':
        raise ValueError('Onverwachte POV-versie')
    addon.set('version', VERSION)
    addon.set('name', 'Krispijn Video')
    addon.set('provider-name', 'Spaan, gebaseerd op kodifitzwell POV')
    for node in addon.findall("extension[@point='xbmc.addon.metadata']/summary"):
        node.text = 'Films en series voor Familie Krispijn'
    assets = addon.find("extension[@point='xbmc.addon.metadata']/assets")
    for key, name in (('icon', 'icon.png'), ('fanart', 'fanart.jpg')):
        node = assets.find(key)
        shutil.copyfile(
            ROOT / 'video-mod/icon.png' if key == 'icon'
            else ROOT / 'skin-mod/overlay' / name,
            folder / name)
        node.text = name
    path.write_bytes(ET.tostring(addon, encoding='utf-8', xml_declaration=True))
    settings_path = folder / 'resources/settings.xml'
    settings = ET.parse(settings_path)
    defaults = {
        'meta_language': 'nl', 'meta_language_display': 'Nederlands',
        'subtitles.language': 'Dutch', 'image_resolutions': '1',
        'provider.external': 'false', 'auto_start_pov': 'false',
        'skip_intro.enable': 'false', 'autoplay_next_show_window': 'false', 'load_action': '0',
        'trakt.sync_refresh_widgets': 'false', 'thumb_fanart': 'false',
    }
    found = set()
    for node in settings.iter('setting'):
        key = node.get('id')
        if key in defaults:
            node.set('default', defaults[key])
            found.add(key)
    if found != set(defaults):
        raise ValueError('Gewijzigde POV-instellingen: ' + str(set(defaults) - found))
    category = ET.SubElement(settings.getroot(), 'category', {'label': 'Familieportretten'})
    ET.SubElement(category, 'setting', {'id': 'krispijn.family.path', 'type': 'text',
                                      'default': '', 'visible': 'false'})
    settings_path.write_bytes(ET.tostring(settings.getroot(), encoding='utf-8', xml_declaration=True))
    shutil.copyfile(ROOT / 'video-mod/router.py', folder / 'resources/lib/router.py')
    shutil.copyfile(ROOT / 'video-mod/service.py', folder / 'resources/lib/service.py')
    # Label de bestaande TMDb-score correct, zonder extra ratingprovider.
    for indexer in ('movies.py', 'tvshows.py'):
        path = folder / 'resources/lib/menus' / indexer
        text = path.read_text(encoding='utf-8')
        marker = "infotag.setRating(meta_get('rating'))"
        if text.count(marker) != 1:
            raise ValueError('TMDb-scorepad is upstream veranderd: ' + indexer)
        text = text.replace(marker,
            "infotag.setRating(float(meta_get('rating') or 0), int(meta_get('votes') or 0), 'tmdb', True)")
        path.write_bytes(text.encode('utf-8'))
    # De koppeling toont een code en officiële URL; geen externe QR-afbeelding.
    path = folder / 'resources/lib/modules/myservices.py'
    text = path.read_text(encoding='utf-8')
    marker = "qr_str % '&data=%s' % quote(result['direct_verification_url'])"
    if text.count(marker) != 1:
        raise ValueError('Real-Debrid-autorisatie is upstream veranderd')
    path.write_bytes(text.replace(marker, "''").encode('utf-8'))
    license_path = ROOT / 'video-mod/COPYING'
    if not license_path.exists():
        license = download('https://www.gnu.org/licenses/gpl-3.0.txt', 1024 * 1024)
        if b'GNU GENERAL PUBLIC LICENSE' not in license:
            raise ValueError('GPL-licentie ontbreekt')
        license_path.write_bytes(license)
    shutil.copyfile(license_path, folder / 'COPYING')
    (folder / 'FORK.md').write_text(
        '# Krispijn Video 1.0.1\n\nGebaseerd op POV 6.11.03 van kodifitzwell, GPL-3.0.\n'
        'Broncode: https://github.com/Marcospaan2001/kodi-spaan\n'
        'Bouw: tools/make_pov.py, aanpassingen: video-mod/.\n'
        'Eigen addon-id, Nederlands startmenu, beperkte lokale opstartservice,\n'
        'Nederlandse metadata en middelgrote afbeeldingen.\n'
        f'Upstream: {URL}\nSHA256: {SHA256}\n', encoding='utf-8')
    for file in folder.rglob('*.py'):
        ast.parse(file.read_text(encoding='utf-8-sig'), filename=str(file))
    for file in folder.rglob('*.xml'):
        ET.parse(file)
    print('  Krispijn Video 1.0.1 op basis van POV 6.11.03, bron-SHA256 akkoord')
    return folder


if __name__ == '__main__':
    make_pov()
