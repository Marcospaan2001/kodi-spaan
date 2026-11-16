"""Zelfstandige sportbronnen. Parsers aangepast uit JetExtractors 3.3.31 (MIT).

Zie SPORT-LICENSE.txt. Geen Loop-catalogus, externe code-updater of telemetrie.
"""
import html
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import quote, urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36'
PROVIDERS = ('FawaNews', 'StreamsCenter')
SPORTS = ('Formule 1', 'Voetbal', 'Darts')


class SportError(Exception):
    pass


def request(url, referer='', post=None):
    if urlsplit(url).scheme not in ('http', 'https'):
        raise SportError('Ongeldig bronadres')
    headers = {'User-Agent': UA, 'Accept-Encoding': 'identity'}
    if referer:
        headers['Referer'] = referer
    data = urlencode(post).encode() if post else None
    try:
        with urlopen(Request(url, data=data, headers=headers), timeout=8) as response:
            raw = response.read(2 * 1024 * 1024 + 1)
            if len(raw) > 2 * 1024 * 1024:
                raise SportError('Bronantwoord te groot')
            return raw.decode('utf-8', 'replace')
    except (OSError, ValueError) as exc:
        raise SportError('De sportbron is niet bereikbaar') from exc


def clean(value):
    return html.unescape(re.sub('<[^>]+>', '', value)).strip()


def sport_for(title):
    value = title.lower()
    if re.search(r'\b(darts|pdc|wdf)\b', value):
        return 'Darts'
    if re.search(r'\b(f1|formula\s*1|formule\s*1|formula one)\b', value):
        return 'Formule 1'
    # American football and other sports must not enter the football category.
    if re.search(r'\b(nfl|ncaa|basketball|nba|hockey|nhl|rugby|cricket|tennis|boxing)\b', value):
        return None
    if re.search(r'soccer|football|voetbal|league|liga|serie a|uefa|fifa|cup of nations|world cup|eredivisie|bundesliga|championship|fa cup|ligue', value):
        return 'Voetbal'
    return None


def parse_fawa(page):
    rows = []
    for block in re.split(r'<div\s+class=["\']user-item\s', page)[1:]:
        title = re.search(r'class=["\']user-item__name["\'][^>]*>(.*?)</div>', block, re.S)
        link = re.search(r'href=["\']([^"\']+)', block)
        league = re.search(r'class=["\']user-item__playing["\'][^>]*>(.*?)</div>', block, re.S)
        if not title or not link:
            continue
        title, league = clean(title[1]), clean(league[1]) if league else ''
        sport = sport_for(title + ' ' + league)
        if not sport:
            continue
        address = urljoin('http://www.fawanews.sc/', quote(html.unescape(link[1]), safe='/:?=&%'))
        if urlsplit(address).hostname not in ('www.fawanews.sc', 'fawanews.sc'):
            continue
        rows.append(dict(title=title, detail=league, sport=sport, url=address, provider='FawaNews'))
    return rows


def parse_center(page):
    rows = []
    for block in re.findall(r'<article class="game-card-row">.*?</article>', page, re.S):
        title = re.search(r'<h3[^>]*aria-label="([^"]+)"', block)
        link = re.search(r'href="(/watch/[^"]+)"', block)
        league = re.search(r'<p class="game-card-league">([^<]*)</p>', block)
        if not title or not link:
            continue
        title, league = clean(title[1]), clean(league[1]) if league else ''
        sport = sport_for(title + ' ' + league)
        if not sport:
            continue
        stamp = re.search(r'<time[^>]*dateTime="([^"]+)"', block)
        detail = league
        if stamp:
            try:
                start = datetime.fromisoformat(stamp[1].replace('Z', '+00:00')).astimezone()
                detail += ' | ' + start.strftime('%d-%m %H:%M')
            except ValueError:
                pass
        rows.append(dict(title=title, detail=detail, sport=sport, url=urljoin('https://streamcenter.st', link[1]), provider='StreamsCenter'))
    return rows


def events(sport, cache, refresh=False):
    """Twee begrensde aanvragen parallel, alleen na openen Sport; cache 2 minuten."""
    path = cache / 'sports-events.json'
    if not refresh:
        try:
            saved = json.loads(path.read_text(encoding='utf-8'))
            if 0 <= time.time() - saved['time'] < 120:
                return [r for r in saved['rows'] if r['sport'] == sport], saved['errors']
        except (OSError, ValueError, KeyError, TypeError):
            pass
    def load(provider):
        try:
            if provider == 'FawaNews':
                return parse_fawa(request('http://www.fawanews.sc/')), None
            return parse_center(request('https://streamcenter.st/game-cards/embed')), None
        except SportError:
            return [], provider
    rows, errors = [], []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result, error in pool.map(load, PROVIDERS):
            rows.extend(result)
            if error:
                errors.append(error)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(dict(time=time.time(), rows=rows, errors=errors)), encoding='utf-8')
    tmp.replace(path)
    return [r for r in rows if r['sport'] == sport], errors


def direct_links(page, base):
    """Lees URL-literals; voer nooit JavaScript van een sportwebsite uit."""
    page = html.unescape(page).replace('\\/', '/').replace('\\u0026', '&')
    links = re.findall(r'''["'](https?://[^"'<>\s]+\.m3u8[^"'<>\s]*)["']''', page)
    # Oud en nieuw FawaNews-formaat: losse strings of een array van CDN-adressen.
    parts = re.findall(r'''var\s+d\d+\s*=\s*["']([^"']*)["']''', page)
    if len(parts) >= 3:
        links.append(''.join(parts))
    array = re.search(r'var\s+S1\s*=\s*\[(.*?)\]', page, re.S)
    tail = [re.search(r'''var\s+S%s\s*=\s*["']([^"']*)["']''' % n, page) for n in (2, 3)]
    if array and all(tail):
        links.extend(s + tail[0][1] + tail[1][1] for s in re.findall(r'''["']([^"']+)["']''', array[1]))
    return list(dict.fromkeys(urljoin(base, u) for u in links if '.m3u8' in u))


def resolve(row):
    address = row['url']
    if row.get('provider') == 'StreamsCenter':
        match = urlsplit(address).path.rsplit('/', 1)[-1]
        raw = request('https://streamcenter.st/api/stream/iframe/' + quote(match, safe=''))
        try:
            entries = json.loads(raw)
            address = next(e['embedUrl'] for e in entries if isinstance(e, dict) and e.get('embedUrl'))
        except (ValueError, TypeError, KeyError, StopIteration):
            raise SportError('Deze uitzending heeft nog geen beschikbare stream')
    visited = set()
    referer = row['url']
    # Geen onbeperkte iframeketens of externe resolver-add-ons.
    for _ in range(3):
        if address in visited:
            break
        visited.add(address)
        page = request(address, referer)
        links = direct_links(page, address)
        if links:
            origin = '{0.scheme}://{0.netloc}'.format(urlsplit(address))
            return [dict(url=u, headers={'User-Agent': UA, 'Referer': address, 'Origin': origin}) for u in links]
        frame = re.search(r'''<iframe\b[^>]*\bsrc=["']([^"']+)["']''', page, re.I)
        if not frame:
            break
        referer, address = address, urljoin(address, html.unescape(frame[1]))
    raise SportError('Deze bron biedt nu geen ondersteunde stream. Kies een andere uitzending of bron.')
