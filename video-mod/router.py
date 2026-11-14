"""Nederlands start- en instellingsmenu voor Krispijn Video, GPL-3.0."""
import os
import sys
from urllib.parse import parse_qsl, urlencode

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

ADDON_ID = 'plugin.video.krispijn'
BASE = 'plugin://' + ADDON_ID + '/'
addon = xbmcaddon.Addon(ADDON_ID)
params = dict(parse_qsl(sys.argv[2].lstrip('?'))) if len(sys.argv) > 2 else {}
mode = params.get('mode', 'krispijn.home')


def directory(rows):
    handle = int(sys.argv[1])
    for title, route, folder in rows:
        item = xbmcgui.ListItem(label=title)
        item.setArt({'icon': addon.getAddonInfo('icon'), 'fanart': addon.getAddonInfo('fanart')})
        xbmcplugin.addDirectoryItem(handle, BASE + '?' + urlencode(route), item, folder)
    xbmcplugin.setContent(handle, 'files')
    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)


def portraits():
    import uuid
    source = xbmcgui.Dialog().browse(0, 'Kies de map met familieportretten', 'files')
    if not source:
        return
    _, files = xbmcvfs.listdir(source)
    files = [f for f in files if os.path.splitext(f)[1].lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif')]
    if not files or len(files) > 50:
        xbmcgui.Dialog().ok('Familieportretten', 'Kies een map met 1 tot 50 afbeeldingen.')
        return
    target = 'special://profile/addon_data/' + ADDON_ID + '/family/' + uuid.uuid4().hex + '/'
    xbmcvfs.mkdirs(target)
    copied = []
    try:
        for index, name in enumerate(sorted(files)):
            src = source.rstrip('/\\') + '/' + name
            if xbmcvfs.Stat(src).st_size() > 8 * 1024 * 1024:
                raise ValueError('Afbeelding groter dan 8 MB')
            dst = target + f'{index:02d}' + os.path.splitext(name)[1].lower()
            if not xbmcvfs.copy(src, dst):
                raise OSError('Kopieren mislukt')
            copied.append(dst)
    except Exception:
        for file in copied:
            xbmcvfs.delete(file)
        xbmcvfs.rmdir(target)
        xbmcgui.Dialog().ok('Familieportretten', 'Kopieren mislukt. De vorige fotomap blijft actief. Gebruik afbeeldingen van maximaal 8 MB.')
        return
    addon.setSetting('krispijn.family.path', target)
    if xbmc.getSkinDir().startswith('skin.arctic.fuse.'):
        xbmc.executebuiltin('Skin.SetString(Krispijn.FacesPath,' + target + ')')
    xbmc.executebuiltin('Skin.Reset(Krispijn.DisableFaces)')
    xbmcgui.Dialog().ok('Familieportretten', f'{len(copied)} portretten staan nu lokaal op dit apparaat. De bronmap is niet meer nodig.')


if mode in ('krispijn.home', 'navigator.main'):
    rows = []
    if not addon.getSetting('rd.token'):
        rows.append(('Begin hier: Real-Debrid koppelen', {'mode': 'krispijn.rd'}, False))
    rows.extend([
        ('Films', {'mode': 'krispijn.movies'}, True),
        ('Series', {'mode': 'krispijn.tv'}, True),
        ('Zoeken', {'mode': 'krispijn.search'}, True),
        ('Verder kijken', {'mode': 'krispijn.resume'}, True),
        ('Instellen', {'mode': 'krispijn.settings'}, True),
    ])
    directory(rows)
elif mode in ('krispijn.movies', 'krispijn.tv'):
    movie = mode == 'krispijn.movies'
    media = 'movie' if movie else 'tvshow'
    prefix = 'tmdb_movies_' if movie else 'tmdb_tv_'
    # Deze namen zijn vastgezet op de gecontroleerde POV-routes.
    actions = ('tmdb_movies_popular', 'tmdb_movies_trending', 'tmdb_movies_latest_releases') if movie else (
        'tmdb_tv_popular', 'tmdb_tv_trending', 'tmdb_tv_premieres')
    directory([(label, {'mode': 'build_' + media + '_list', 'action': action}, True)
               for label, action in zip(('Populair', 'Nu populair', 'Nieuw'), actions)])
elif mode == 'krispijn.search':
    directory([
        ('Films zoeken', {'mode': 'search_history', 'action': 'movie'}, True),
        ('Series zoeken', {'mode': 'search_history', 'action': 'tvshow'}, True),
    ])
elif mode == 'krispijn.resume':
    directory([
        ('Films hervatten', {'mode': 'build_movie_list', 'action': 'in_progress_movies'}, True),
        ('Series hervatten', {'mode': 'build_tvshow_list', 'action': 'in_progress_tvshows'}, True),
    ])
elif mode == 'krispijn.settings':
    directory([
        ('Real-Debrid koppelen of ontkoppelen', {'mode': 'krispijn.rd'}, False),
        ('OpenSubtitles instellen (optioneel)', {'mode': 'krispijn.subtitles'}, False),
        ('Familieportretten kiezen', {'mode': 'krispijn.portraits'}, False),
        ('Uitgebreide instellingen', {'mode': 'open_settings'}, False),
    ])
elif mode == 'krispijn.rd':
    from modules.myservices import RealDebrid
    RealDebrid().set()
elif mode == 'krispijn.portraits':
    portraits()
elif mode == 'krispijn.subtitles':
    subtitle_id = 'service.subtitles.opensubtitles-com'
    if not xbmc.getCondVisibility('System.HasAddon(' + subtitle_id + ')'):
        xbmc.executebuiltin('InstallAddon(' + subtitle_id + ')')
    else:
        xbmcaddon.Addon(subtitle_id).openSettings()
else:
    from modules.entry import Router
    Router()()
