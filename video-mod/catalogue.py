"""Eén verzoek per cataloguspagina, lokale cache en herkenbare fouten. GPL-3.0."""
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

class CatalogueError(Exception):
    pass

class Catalogue:
    def __init__(self, token, cache_dir, transport=None, clock=time.time):
        self.token, self.cache_dir = token, Path(cache_dir)
        self.cancelled=lambda:False
        self.transport, self.clock = transport or self._request, clock
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _request(self, path):
        try:
            request = Request('https://api.themoviedb.org/3/' + path, headers={'Authorization': 'Bearer ' + self.token, 'User-Agent': 'Krispijn/1.1'})
            with urlopen(request, timeout=8) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 401: raise CatalogueError('De cataloguskoppeling is verlopen. Controleer of er een update is.') from None
            if error.code == 429: raise CatalogueError('De catalogus is even druk. Probeer het straks opnieuw.') from None
            raise CatalogueError('De catalogus is tijdelijk niet bereikbaar.') from None
        except (URLError, OSError, ValueError):
            raise CatalogueError('Geen verbinding met de catalogus. Controleer je internetverbinding.') from None

    def fetch(self, section='trending', page=1, query='', media='movie', genres='', year=None, min_rating=None, tmdb_id=None, season=None):
        if section == 'digital':return self.digital(page)
        page = max(1, min(500, int(page)))
        params = {'language':'nl-NL', 'page':page, 'include_adult':'false'}
        kind = media
        if section == 'search':
            endpoint = 'search/multi'; params['query'] = query.strip()
        elif section == 'home':
            endpoint='discover/movie'; kind='movie'
            params.update(seasonal_selection()[1])
        elif section == 'trending':
            endpoint = 'trending/all/week'
        elif section == 'cinema':
            endpoint='movie/now_playing'; params['region']='NL'; kind='movie'
        elif section == 'seasons':
            endpoint=f'tv/{int(tmdb_id)}'; kind='season'
        elif section == 'episodes':
            endpoint=f'tv/{int(tmdb_id)}/season/{int(season)}'; kind='episode'
        else:
            kind = 'tv' if section in ('tv','newshows') else media
            endpoint = 'discover/' + ('tv' if kind in ('tv','tvshow') else 'movie')
            params['sort_by']='popularity.desc'
            if genres: params['with_genres']=genres
            if year: params['first_air_date_year' if kind == 'tv' else 'primary_release_year']=str(year)
            if min_rating: params.update({'vote_average.gte':str(min_rating),'vote_count.gte':'50'})
        path=endpoint+'?'+urlencode(params)
        file=self.cache_dir/(hashlib.sha256(path.encode()).hexdigest()+'.json')
        cached=None
        try:
            cached=json.loads(file.read_text(encoding='utf-8'))
            if self.clock()-cached['time'] < 900: return dict(cached['data'],stale=False)
        except (OSError,ValueError,KeyError): pass
        try:
            data=self.transport(path)
            if not isinstance(data,dict) or data.get('success') is False: raise CatalogueError('De catalogus gaf geen geldig antwoord.')
            raw=data.get('seasons' if kind=='season' else 'episodes' if kind=='episode' else 'results',[])
            results=[]
            for row in raw:
                typ=row.get('media_type',kind)
                if typ not in ('movie','tv','tvshow','season','episode') or row.get('adult'): continue
                item=dict(row,krispijn_type='tvshow' if typ=='tv' else typ)
                if typ in ('season','episode'): item.update(krispijn_show_id=tmdb_id, krispijn_season=season)
                results.append(item)
            output={'results':results,'page':page,'total_pages':min(500,data.get('total_pages',1)),'stale':False}
            temp=file.with_suffix('.tmp')
            temp.write_text(json.dumps({'time':self.clock(),'data':output}),encoding='utf-8');os.replace(temp,file)
            return output
        except (CatalogueError, OSError):
            if cached and self.clock()-cached.get('time',0)<7*86400: return dict(cached['data'],stale=True)
            raise

    def cached_raw(self, path, ttl=86400):
        file=self.cache_dir/('raw-'+hashlib.sha256(path.encode()).hexdigest()+'.json')
        try:
            saved=json.loads(file.read_text(encoding='utf-8'))
            if self.clock()-saved['time']<ttl:return saved['data']
        except (ValueError,KeyError,OSError):pass
        data=self.transport(path)
        if not isinstance(data,dict) or data.get('success') is False:
            raise CatalogueError('De catalogus gaf geen geldig antwoord.')
        temp=file.with_suffix('.tmp')
        temp.write_text(json.dumps({'time':self.clock(),'data':data}),encoding='utf-8')
        os.replace(temp,file)
        return data

    def digital(self, page=1):
        page=max(1,min(500,int(page)));today=date.today();since=today-timedelta(days=120)
        params={'language':'nl-NL','region':'US','with_release_type':'4',
                'release_date.gte':since.isoformat(),'release_date.lte':today.isoformat(),
                'primary_release_date.gte':(today-timedelta(days=365)).isoformat(),
                'include_adult':'false','sort_by':'release_date.desc','page':page}
        # US digitale releases dekken ook internationale films die later in NL verschijnen.
        data=self.cached_raw('discover/movie?'+urlencode(params),21600)
        def verified(row):
            if self.cancelled():return None
            release=self.cached_raw(f"movie/{int(row['id'])}/release_dates")
            cinemas=[];digital=[]
            for country in release.get('results',[]):
                for entry in country.get('release_dates',[]):
                    try: day=date.fromisoformat(entry['release_date'][:10])
                    except (KeyError,ValueError,TypeError):continue
                    if entry.get('type') in (2,3) and day<=today:cinemas.append(day)
                    if country.get('iso_3166_1')=='US' and entry.get('type')==4 and since<=day<=today:digital.append(day)
            if not cinemas or not digital or min(cinemas)>min(digital):return None
            return dict(row,krispijn_type='movie',krispijn_digital=min(digital).isoformat())
        # Alleen de geopende pagina controleren, maximaal vier gelijktijdige aanvragen.
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows=[r for r in pool.map(verified,data.get('results',[])) if r is not None]
        rows.sort(key=lambda r:r['krispijn_digital'],reverse=True)
        return {'results':rows,'page':page,'total_pages':min(500,data.get('total_pages',1)),'stale':False}

    def trailer(self, row):
        kind='movie' if row['krispijn_type']=='movie' else 'tv'
        identifier=row.get('krispijn_show_id') or row['id']
        # Zonder taalfilter: één aanvraag met alle taalvarianten.
        data=self.cached_raw(f'{kind}/{int(identifier)}/videos')
        videos=[v for v in data.get('results',[]) if v.get('site')=='YouTube'
                and v.get('type')=='Trailer' and v.get('key')]
        videos.sort(key=lambda v:(bool(v.get('official')),v.get('iso_639_1') in ('nl','en'),v.get('published_at','')),reverse=True)
        return videos[0] if videos else None


def from_kodi():
    import xbmcaddon, xbmcvfs
    import xml.etree.ElementTree as ET
    addon=xbmcaddon.Addon('plugin.video.krispijn')
    token=addon.getSetting('tmdb_read_token')
    if not token:
        root=ET.parse(os.path.join(addon.getAddonInfo('path'),'resources/settings.xml'))
        token=root.find(".//setting[@id='tmdb_read_token']").get('default','')
    return Catalogue(token,os.path.join(xbmcvfs.translatePath(addon.getAddonInfo('profile')),'catalogue'))


def seasonal_selection(today=None):
    """Seizoensselectie voor Nederland, zonder account of extra metadata-aanvragen."""
    today = today or date.today()
    base = {'sort_by':'popularity.desc', 'vote_count.gte':'50',
            'vote_average.gte':'6', 'primary_release_date.lte':today.isoformat()}
    if today.month in (11, 12):
        title = 'Samen richting kerst'
        base['with_keywords'] = '207317'  # TMDb: christmas
    elif today.month in (1, 2):
        title = 'Warme winteravonden'; base['with_genres'] = '35|10751'
    elif today.month in (3, 4, 5):
        title = 'Voorjaarsavonturen'; base['with_genres'] = '12|16'
    elif today.month in (6, 7, 8):
        title = 'Zomerse filmavond'; base['with_genres'] = '12|35'
    elif today.month == 10:
        title = 'Spannende herfstavonden'; base['with_genres'] = '9648|53'
    else:
        title = 'Samen op de bank'; base['with_genres'] = '18|35'
    return title, base
