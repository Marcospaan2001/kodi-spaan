"""Filmhub, lokale voortgang en gecombineerde zoekresultaten. GPL-3.0."""
from urllib.parse import urlencode

BASE = 'plugin://plugin.video.krispijn/'
LIMIT = 8


def mixed(movies, shows, limit=LIMIT):
    """Wissel films en series af; houd identiteiten en inhoudstypen gescheiden."""
    result, seen = [], set()
    for index in range(max(len(movies), len(shows))):
        for kind, rows in (('movie', movies), ('tvshow', shows)):
            if index >= len(rows):
                continue
            row = rows[index]
            key = (kind, row.get('id'))
            if not key[1] or key in seen or row.get('adult'):
                continue
            seen.add(key)
            result.append(dict(row, krispijn_type=kind))
            if len(result) >= limit:
                return result
    return result


def progress_rows(bookmarks, limit=LIMIT):
    """Nieuwste onafgemaakte film/aflevering; maximaal één aflevering per serie."""
    rows = []
    for row in bookmarks:
        try:
            if row[0] not in ('movie', 'episode') or not 0 < float(row[4]) < 100:
                continue
            if float(row[5]) <= 0:
                continue
            rows.append(row)
        except (IndexError, TypeError, ValueError):
            continue
    rows.sort(key=lambda row: str(row[6]), reverse=True)
    result, seen = [], set()
    for row in rows:
        key = row[0], str(row[1])
        if key not in seen:
            seen.add(key)
            result.append(row)
            if len(result) >= limit:
                break
    return result


def media_route(row):
    movie = row['krispijn_type'] == 'movie'
    return {'mode': 'play_media', 'mediatype': 'movie', 'tmdb_id': row['id']} if movie else {
        'mode': 'build_season_list', 'tmdb_id': row['id']}


def listing(rows, title, search=False, next_route=None):
    import sys
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
    handle = int(sys.argv[1])
    addon = xbmcaddon.Addon('plugin.video.krispijn')
    if search:
        item = xbmcgui.ListItem(label='Zoek een film of serie')
        item.setArt({'icon': addon.getAddonInfo('icon')})
        xbmcplugin.addDirectoryItem(handle, BASE + '?mode=krispijn.query', item, False)
    for row in rows:
        movie = row['krispijn_type'] == 'movie'
        name = row.get('title') if movie else row.get('name')
        date = row.get('release_date') if movie else row.get('first_air_date')
        year = (date or '')[:4]
        item = xbmcgui.ListItem(label=(name or 'Onbekende titel') + (' (' + year + ')' if year else ''))
        poster = row.get('poster_path')
        poster = 'https://image.tmdb.org/t/p/w342' + poster if poster and poster.startswith('/') else addon.getAddonInfo('icon')
        item.setArt({'poster': poster, 'thumb': poster, 'icon': poster})
        tag = item.getVideoInfoTag()
        tag.setTitle(name or '')
        tag.setMediaType('movie' if movie else 'tvshow')
        tag.setUniqueIDs({'tmdb': str(row['id'])})
        tag.setPlot(row.get('overview') or '')
        if year.isdigit():
            tag.setYear(int(year))
        tag.setRating(float(row.get('vote_average') or 0), int(row.get('vote_count') or 0), 'tmdb', True)
        if movie:
            item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle, BASE + '?' + urlencode(media_route(row)), item, not movie)
    if next_route:
        item = xbmcgui.ListItem(label='Volgende pagina')
        xbmcplugin.addDirectoryItem(handle, BASE + '?' + urlencode(next_route), item, True)
    xbmcplugin.setPluginCategory(handle, title)
    xbmcplugin.setContent(handle, 'videos')
    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)


def continued():
    import sys
    import xbmcplugin
    from concurrent.futures import ThreadPoolExecutor
    from caches.watched_cache import get_bookmarks
    # Lokale voortgang, onafhankelijk van trackeraccounts.
    records = progress_rows(list(get_bookmarks(0, 'movie').values()) + list(get_bookmarks(0, 'episode').values()))
    if records:
        from menus.movies import Movies
        from menus.episodes import Episodes
        def build(index, row):
            # Eén renderer per taak voorkomt gedeelde lijstmutaties.
            renderer = Movies({'action': 'in_progress_movies'}) if row[0] == 'movie' else Episodes({'id_type': 'in_progress_episode'})
            if row[0] == 'movie':
                renderer.build_movie_content(index, row[1])
            else:
                renderer.build_episode_content(index, {'media_ids': {'tmdb': row[1]}, 'season': row[2], 'episode': row[3]})
            return renderer.items[0] if renderer.items else None
        with ThreadPoolExecutor(max_workers=3) as pool:
            items = list(pool.map(lambda pair: build(*pair), enumerate(records)))
        xbmcplugin.addDirectoryItems(int(sys.argv[1]), [item for item in items if item])
    xbmcplugin.setContent(int(sys.argv[1]), 'videos')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)


def run(params):
    import xbmc
    import xbmcgui
    from modules.cache import check_databases
    check_databases()
    mode = params.get('mode')
    if mode == 'krispijn.hub':
        if xbmc.getSkinDir() == 'skin.arctic.fuse.2.krispijn':
            xbmc.executebuiltin('ActivateWindow(1188)')
        else:
            xbmcgui.Dialog().ok('Filmhub', 'Open de filmhub met Familie Krispijn (Kodi 21). Films, series en zoeken blijven ook via het hoofdmenu bereikbaar.')
        return
    if mode == 'krispijn.hubhome':
        if xbmc.getSkinDir() == 'skin.arctic.fuse.2.krispijn':
            xbmc.executebuiltin('Skin.ToggleSetting(Krispijn.HubAsHome)')
            xbmcgui.Dialog().ok('Filmhub', 'De keuze voor het startscherm is gewijzigd. Open de filmhub of herstart Kodi.')
        return
    if mode == 'krispijn.continue':
        continued()
        return
    from indexers import tmdb_api
    from concurrent.futures import ThreadPoolExecutor
    page = max(1, min(500, int(params.get('page', '1'))))
    if mode == 'krispijn.cinema':
        from caches.main_cache import cache_object
        data = cache_object(tmdb_api.get_tmdb, 'krispijn_cinema_nl_' + str(page), '/3/movie/now_playing?language=nl-NL&region=NL&page=' + str(page), expiration=4) or {}
        more = {'mode': mode, 'page': page + 1} if page < data.get('total_pages', 0) else None
        listing([dict(r, krispijn_type='movie') for r in data.get('results', [])], 'Nu in de bioscoop', next_route=more)
    elif mode == 'krispijn.newmovies':
        data = tmdb_api.tmdb_movies_latest_releases(1) or {}
        listing([dict(r, krispijn_type='movie') for r in data.get('results', [])[:LIMIT]], 'Nieuwe films')
    elif mode == 'krispijn.newshows':
        data = tmdb_api.tmdb_tv_premieres(1) or {}
        listing([dict(r, krispijn_type='tvshow') for r in data.get('results', [])[:LIMIT]], 'Nieuwe series')
    elif mode == 'krispijn.query':
        query = xbmcgui.Dialog().input('Zoek films en series').strip()
        if len(query) >= 2:
            xbmc.executebuiltin('Container.Update(' + BASE + '?' + urlencode({'mode': 'krispijn.results', 'query': query}) + ')')
        elif query:
            xbmcgui.Dialog().ok('Zoeken', 'Gebruik minstens twee letters.')
    else:
        query = params.get('query', '').strip()
        with ThreadPoolExecutor(max_workers=2) as pool:
            if query:
                movie_job = pool.submit(tmdb_api.tmdb_movies_search, query, page)
                show_job = pool.submit(tmdb_api.tmdb_tv_search, query, page)
                title = 'Zoekresultaten: ' + query
            else:
                movie_job = pool.submit(tmdb_api.tmdb_movies_trending, page)
                show_job = pool.submit(tmdb_api.tmdb_tv_trending, page)
                title = 'Trending' if mode == 'krispijn.trending' else 'Zoeken en bekende titels'
            movies, shows = movie_job.result() or {}, show_job.result() or {}
        browsing = bool(query) or mode == 'krispijn.trending'
        more = {'mode': mode, 'query': query, 'page': page + 1} if browsing and page < max(movies.get('total_pages', 0), shows.get('total_pages', 0)) else None
        listing(mixed(movies.get('results', []), shows.get('results', []), 40 if browsing else LIMIT), title, search=mode != 'krispijn.trending', next_route=more)


def window_xml():
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<window type="window" id="1188">
 <defaultcontrol always="true">501</defaultcontrol>
 <onload>SetProperty(KrispijnHubRefresh,$INFO[System.Time(hh:mm:ss)])</onload>
 <controls>
  <control type="image"><width>1920</width><height>1080</height><texture>special://skin/extras/krispijn/background.jpg</texture></control>
  <control type="image"><left>50</left><top>20</top><width>150</width><height>120</height><aspectratio>keep</aspectratio><texture>special://home/addons/plugin.video.krispijn/icon.png</texture></control>
  <control type="label"><left>230</left><top>40</top><width>900</width><height>60</height><font>font_main</font><label>Filmavond bij Familie Krispijn</label><textcolor>ffffffff</textcolor></control>
  <control type="button" id="110"><left>1300</left><top>40</top><width>180</width><height>60</height><font>font_main</font><label>Zoeken</label><onleft>112</onleft><onright>111</onright><ondown>501</ondown><onclick>ActivateWindow(Videos,plugin://plugin.video.krispijn/?mode=krispijn.search,return)</onclick></control>
  <control type="button" id="111"><left>1490</left><top>40</top><width>160</width><height>60</height><font>font_main</font><label>Genres</label><onleft>110</onleft><onright>112</onright><ondown>501</ondown><onclick>ActivateWindow(Videos,plugin://plugin.video.krispijn/?mode=krispijn.movies,return)</onclick></control>
  <control type="button" id="112"><left>1660</left><top>40</top><width>210</width><height>60</height><font>font_main</font><label>Instellen</label><onleft>111</onleft><onright>110</onright><ondown>501</ondown><onclick>ActivateWindow(Videos,plugin://plugin.video.krispijn/?mode=krispijn.settings,return)</onclick></control>
  <control type="grouplist" id="400"><left>50</left><top>150</top><width>1820</width><height>900</height><orientation>vertical</orientation><itemgap>20</itemgap>
'''
    for i, (title, route) in enumerate((('Verder kijken', 'continue'), ('Nieuwe films', 'newmovies'), ('Nieuwe series', 'newshows'))):
        cid = 500 + i
        xml += f'''<control type="group"><width>1820</width><height>350</height>
 <control type="label"><width>1800</width><height>40</height><font>font_main</font><textcolor>ffffffff</textcolor><label>{title}</label></control>
 <control type="fixedlist" id="{cid}"><top>45</top><width>1820</width><height>300</height><orientation>horizontal</orientation><focusposition>1</focusposition><onup>{cid-1 if i else 110}</onup><ondown>{cid+1 if i < 2 else 110}</ondown>
 <itemlayout width="210" height="295"><control type="image"><width>190</width><height>240</height><aspectratio>scale</aspectratio><texture background="true">$INFO[ListItem.Art(poster)]</texture></control><control type="label"><top>245</top><width>190</width><height>45</height><font>font_main</font><label>$INFO[ListItem.Label]</label><textcolor>ffcccccc</textcolor></control></itemlayout>
 <focusedlayout width="210" height="295"><control type="image"><width>198</width><height>248</height><texture colordiffuse="ffe53935">common/white.png</texture></control><control type="image"><left>4</left><top>4</top><width>190</width><height>240</height><aspectratio>scale</aspectratio><texture background="true">$INFO[ListItem.Art(poster)]</texture></control><control type="label"><top>250</top><width>200</width><height>40</height><font>font_main</font><label>$INFO[ListItem.Label]</label><textcolor>ffffffff</textcolor></control></focusedlayout>
 <content target="videos" limit="8">plugin://plugin.video.krispijn/?mode=krispijn.{route}&amp;refresh=$INFO[Window.Property(KrispijnHubRefresh)]</content>
 </control>
'''.replace('i &lt; 2', 'i < 2')
        if i == 0:
            xml += '<control type="label"><top>100</top><width>1750</width><height>60</height><font>font_main</font><label>Hier verschijnen films en afleveringen die je nog niet hebt afgekeken.</label><visible>Integer.IsEqual(Container(500).NumItems,0)</visible></control>'
        xml += '</control>'
    extra = '<control type="image"><top>210</top><width>190</width><height>30</height><texture colordiffuse="dd0b0e15">common/white.png</texture></control><control type="label"><top>210</top><width>190</width><height>30</height><font>font_main</font><label>$INFO[ListItem.Rating,TMDb ,]  $INFO[ListItem.Property(watchedprogress),, % bekeken]</label><textcolor>ffffffff</textcolor></control>'
    xml = xml.replace('</itemlayout>', extra + '</itemlayout>').replace('</focusedlayout>', extra + '</focusedlayout>')
    return xml + '</control></controls></window>\n'
