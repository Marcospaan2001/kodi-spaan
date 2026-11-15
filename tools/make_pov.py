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
VERSION = '1.1.3'
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
    # Een zoekterm mag geen eigen URL-parameters introduceren.
    search_path = folder / 'resources/lib/indexers/tmdb_api.py'
    search_text = search_path.read_text(encoding='utf-8')
    for kind in ('movie', 'tv'):
        old = "url = '/3/search/" + kind + "?language=en-US&query=%s&page=%s' % (query, page_no)"
        if search_text.count(old) != 1:
            raise ValueError('Onverwachte TMDb-zoekroute')
        search_text = search_text.replace(old, old.replace('(query, page_no)', '(quote(query, safe=""), page_no)'))
    search_path.write_bytes(('from urllib.parse import quote\n' + search_text).encode('utf-8'))
    utils = folder / 'resources/lib/modules/kodi_utils.py'
    text = utils.read_text(encoding='utf-8')
    old = "xbmcgui.Dialog().notification('POV', line1, icon, time, sound)"
    if text.count(old) != 1:
        raise ValueError('Onverwachte notificatietitel')
    utils.write_bytes(text.replace(old, "xbmcgui.Dialog().notification(get_addoninfo('name'), line1, icon, time, sound)").encode('utf-8'))
    path = folder / 'addon.xml'
    tree = ET.parse(path)
    addon = tree.getroot()
    if addon.get('version') != '6.11.03':
        raise ValueError('Onverwachte POV-versie')
    addon.set('version', VERSION)
    ET.SubElement(addon, 'extension', {'point':'xbmc.python.script','library':'resources/lib/experience_entry.py'})
    addon.set('name', 'Krispijn Video')
    addon.set('provider-name', 'Spaan, gebaseerd op kodifitzwell POV')
    for node in addon.findall("extension[@point='xbmc.addon.metadata']/summary"):
        node.text = 'Films en series voor Familie Krispijn'
    assets = addon.find("extension[@point='xbmc.addon.metadata']/assets")
    for key, name in (('icon', 'icon-krispijn-v2.png'), ('fanart', 'fanart.jpg')):
        node = assets.find(key)
        shutil.copyfile(
            ROOT / 'video-mod/icon.png' if key == 'icon'
            else ROOT / 'skin-mod/overlay/extras/krispijn/background.jpg',
            folder / name)
        if key == 'icon':shutil.copyfile(folder / name, folder / 'icon.png')
        node.text = name
    path.write_bytes(ET.tostring(addon, encoding='utf-8', xml_declaration=True))
    settings_path = folder / 'resources/settings.xml'
    settings = ET.parse(settings_path)
    defaults = {
        'meta_language': 'nl', 'meta_language_display': 'Nederlands',
        'subtitles.language': 'Dutch', 'image_resolutions': '1',
        'provider.external': 'true', 'auto_start_pov': 'false',
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
    for key in ('krispijn.sources.v1', 'krispijn.rd.state', 'krispijn.rd.checked', 'krispijn.languages.v1'):
        ET.SubElement(category, 'setting', {'id':key,'type':'text','default':'','visible':'false'})
    settings_path.write_bytes(ET.tostring(settings.getroot(), encoding='utf-8', xml_declaration=True))
    shutil.copyfile(ROOT / 'video-mod/hub.py', folder / 'resources/lib/modules/krispijn_hub.py')
    for name in ('catalogue', 'experience', 'accounts', 'playback_setup', 'languages'):
        shutil.copyfile(ROOT / f'video-mod/{name}.py', folder / f'resources/lib/modules/krispijn_{name}.py')
    shutil.copytree(ROOT / 'video-mod/resources', folder / 'resources', dirs_exist_ok=True)
    shutil.copytree(ROOT / 'skin-mod/portraits', folder / 'extras/portraits', dirs_exist_ok=True)
    shutil.copyfile(ROOT / 'video-mod/experience_entry.py', folder / 'resources/lib/experience_entry.py')

    shutil.copyfile(ROOT / 'video-mod/router.py', folder / 'resources/lib/router.py')
    shutil.copyfile(ROOT / 'video-mod/service.py', folder / 'resources/lib/service.py')
    source_path = folder / 'resources/lib/modules/sources.py'
    source_text = source_path.read_text(encoding='utf-8')
    old = '\t\tnotification(32573)'
    if source_text.count(old) != 1:
        raise ValueError('Onverwacht geen-bronnenpad')
    source_text = source_text.replace(old, '\t\tfrom modules.krispijn_playback_setup import no_sources\n\t\tno_sources(len(getattr(self, \'orig_results\', [])))')
    source_path.write_bytes(source_text.encode('utf-8'))
    player_path = folder / 'resources/lib/modules/player.py'
    player_text = player_path.read_text(encoding='utf-8')
    marker = '\tdef onAVStarted(self):\n\t\tself.playback_event = True'
    if player_text.count(marker) != 1:
        raise ValueError('Onverwacht afspeelstartpunt')
    player_text = player_text.replace(marker, marker + '\n\t\tfrom modules.krispijn_languages import apply_streams\n\t\tapply_streams()')
    old_subs = "\t\t\t\tposter = self.meta.get('poster') or poster_empty\n\t\t\t\tfrom indexers.subtitles import SubtitleScraper\n\t\t\t\tThread(target=SubtitleScraper(self, poster)).start()"
    if player_text.count(old_subs) != 1:raise ValueError('Onverwacht ondertitelzoekpad')
    player_text = player_text.replace(old_subs, '\t\t\t\tfrom modules.krispijn_languages import search_missing\n\t\t\t\tsearch_missing()')
    player_path.write_bytes(player_text.encode('utf-8'))
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
        '# Krispijn Video 1.1.3\n\nGebaseerd op POV 6.11.03 van kodifitzwell, GPL-3.0.\n'
        'Broncode: https://github.com/Marcospaan2001/kodi-spaan\n'
        'Bouw: tools/make_pov.py, aanpassingen: video-mod/.\n'
        'Eigen addon-id, Nederlands startmenu, beperkte lokale opstartservice,\n'
        'Nederlandse metadata en middelgrote afbeeldingen.\n'
        f'Upstream: {URL}\nSHA256: {SHA256}\n', encoding='utf-8')
    from branding import apply_branding
    apply_branding(folder)
    for file in folder.rglob('*.py'):
        ast.parse(file.read_text(encoding='utf-8-sig'), filename=str(file))
    for file in folder.rglob('*.xml'):
        ET.parse(file)
    print('  Krispijn Video 1.1.3 op basis van POV 6.11.03, bron-SHA256 akkoord')
    return folder


if __name__ == '__main__':
    make_pov()
