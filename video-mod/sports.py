"""Krispijn Sport: eigen sportmenu, bronzoekers en speler zonder andere sport-add-on."""
import json
import threading
from pathlib import Path
from urllib.parse import urlencode, urlsplit


def wait_job(title, function):
    import xbmc, xbmcgui
    progress = xbmcgui.DialogProgress()
    progress.create('Krispijn Sport', title)
    finished = threading.Event()
    result = {}
    def run():
        try:
            result['value'] = function()
        except Exception as error:
            result['error'] = error
        finally:
            finished.set()
    threading.Thread(target=run, daemon=True).start()
    monitor = xbmc.Monitor()
    try:
        while not finished.wait(0.1):
            if progress.iscanceled() or monitor.abortRequested():
                return None
        if 'error' in result:
            from modules.krispijn_sport_sources import SportError
            error = result['error']
            message = str(error) if isinstance(error, SportError) else 'Ophalen mislukt. Probeer het later opnieuw.'
            xbmcgui.Dialog().ok('Krispijn Sport', message)
            return None
        return result.get('value')
    finally:
        progress.close()


def play(name, stream):
    import xbmc, xbmcgui
    address = stream['url']
    if stream.get('headers'):
        address += '|' + urlencode(stream['headers'])
    item = xbmcgui.ListItem(label=name, path=address)
    item.getVideoInfoTag().setTitle(name)
    item.setProperty('IsPlayable', 'true')
    if '.m3u8' in stream['url']:
        item.setMimeType('application/vnd.apple.mpegurl')
        item.setContentLookup(False)
    xbmc.Player().play(address, item)


def open_sports(close_hub=None):
    import xbmcaddon, xbmcgui, xbmcvfs
    from modules.krispijn_sport_sources import SPORTS, events, resolve
    dialog = xbmcgui.Dialog()
    addon = xbmcaddon.Addon('plugin.video.krispijn')
    profile = Path(xbmcvfs.translatePath(addon.getAddonInfo('profile')))
    file = profile / 'sports-streams.json'
    try:
        data = json.loads(file.read_text(encoding='utf-8'))
    except (ValueError, OSError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    while True:
        choice = dialog.select('Krispijn Sport', list(SPORTS))
        if choice < 0:
            return
        sport = SPORTS[choice]
        while True:
            streams = data.get(sport, [])
            if not isinstance(streams, list):
                streams = []
            streams = [r for r in streams if isinstance(r, dict) and isinstance(r.get('name'), str) and isinstance(r.get('url'), str)]
            selected = dialog.select(sport, ['Uitzendingen bekijken', 'Uitzendingen vernieuwen', 'Eigen livestream toevoegen', 'Eigen livestream verwijderen'] + [r['name'] for r in streams])
            if selected < 0:
                break
            if selected in (0, 1):
                result = wait_job('Uitzendingen ophalen…', lambda: events(sport, profile, refresh=selected == 1))
                if result is None:
                    continue
                rows, errors = result
                if errors:
                    dialog.notification('Sportbron niet bereikbaar', ', '.join(errors))
                if not rows:
                    dialog.ok(sport, 'Geen uitzendingen gevonden. Er hoeft op dit moment geen evenement te zijn. Probeer later opnieuw of voeg een eigen livestream toe.')
                    continue
                while True:
                    index = dialog.select(sport + ' | Uitzendingen', [r['title'] + ' | ' + r['detail'] + ' | ' + r['provider'] for r in rows])
                    if index < 0:
                        break
                    row = rows[index]
                    sources = wait_job('Stream ophalen…', lambda: resolve(row))
                    if not sources:
                        continue
                    source = 0 if len(sources) == 1 else dialog.select('Kies een stream', ['Stream ' + str(i + 1) for i in range(len(sources))])
                    if source >= 0:
                        play(row['title'], sources[source])
                        return
            elif selected == 2:
                name = dialog.input('Naam van de livestream').strip()
                if not name:
                    continue
                url = dialog.input('Stream-URL (https:// of http://)').strip()
                try:
                    parsed = urlsplit(url)
                    valid = parsed.scheme in ('http', 'https') and parsed.hostname and '\n' not in url and '\r' not in url
                except ValueError:
                    valid = False
                if not valid:
                    dialog.ok('Stream toevoegen', 'Vul een geldig http- of https-streamadres in.')
                    continue
                streams.append({'name': name, 'url': url})
                save(file, data, sport, streams)
                dialog.notification('Sport', 'Livestream toegevoegd')
            elif selected == 3:
                index = dialog.select('Welke livestream verwijderen?', [r['name'] for r in streams])
                if index >= 0:
                    streams.pop(index)
                    save(file, data, sport, streams)
            else:
                stream = streams[selected - 4]
                play(stream['name'], stream)
                return

def save(file,data,sport,streams):
    data[sport]=streams;file.parent.mkdir(parents=True,exist_ok=True)
    temporary=file.with_suffix('.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    temporary.replace(file)
