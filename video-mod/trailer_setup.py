"""Herstelbaar YouTube-profiel voor de kleine trailerspeler op Kodi 21."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

VALUES={
    'kodion.audio_only':False,
    'kodion.video.quality.ask':False,
    'kodion.video.quality':3,
    'kodion.mpd.quality.selection':3,
    'kodion.mpd.stream.features':['avc1','mp4a','vtt','filter'],
}


def context():
    import xbmcaddon,xbmcvfs
    yt=xbmcaddon.Addon('plugin.video.youtube')
    own=xbmcaddon.Addon('plugin.video.krispijn')
    file=Path(xbmcvfs.translatePath(own.getAddonInfo('profile')))/'youtube-profile.json'
    return yt,file


def apply(force=False):
    import xbmc,xbmcgui
    yt,file=context()
    try:state=json.loads(file.read_text(encoding='utf-8'))
    except (OSError,ValueError):state={}
    if not force and (state.get('applied') or state.get('restored')):return
    schema=ET.parse(Path(yt.getAddonInfo('path'))/'resources/settings.xml')
    ids={s.get('id') for s in schema.findall('.//setting')}
    if not set(VALUES).issubset(ids):
        xbmcgui.Dialog().notification('Trailers','Werk YouTube bij via de officiële Kodi-repository.',time=6000)
        return
    settings=yt.getSettings()
    def get(key,value):
        if isinstance(value,list):return settings.getStringList(key)
        if isinstance(value,bool):return settings.getBool(key)
        return settings.getInt(key)
    if 'previous' not in state:state['previous']={k:get(k,v) for k,v in VALUES.items()}
    # Bewaar herstelgegevens voordat de eerste instelling wordt gewijzigd.
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(state),encoding='utf-8')
    write(settings,VALUES)
    state.update(applied=True,restored=False,version=yt.getAddonInfo('version'))
    file.write_text(json.dumps(state),encoding='utf-8')
    xbmcgui.Dialog().notification('Trailers','YouTube: 720p, H.264 en AAC ingesteld.',time=4000)


def write(settings,values):
    for key,value in values.items():
        if isinstance(value,list):ok=settings.setStringList(key,value)
        elif isinstance(value,bool):ok=settings.setBool(key,value)
        else:ok=settings.setInt(key,value)
        if ok is False:raise ValueError('YouTube-instelling geweigerd')


def manage():
    import xbmc,xbmcaddon,xbmcgui
    dialog=xbmcgui.Dialog()
    if not xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
        xbmc.executebuiltin('InstallAddon(plugin.video.youtube)');return
    choice=dialog.select('YouTube en trailers',['Herstelprofiel: 720p / H.264','Vorige instellingen terugzetten','YouTube-instellingen openen','Controleren op repository-updates'])
    if choice==0:apply(force=True)
    elif choice==1:
        yt,file=context()
        try:state=json.loads(file.read_text(encoding='utf-8'))
        except (ValueError,OSError):state={}
        if not state.get('previous'):
            dialog.ok('YouTube','Er zijn geen eerdere instellingen bewaard.');return
        write(yt.getSettings(),state['previous'])
        state.update(applied=False,restored=True);file.write_text(json.dumps(state),encoding='utf-8')
        dialog.notification('YouTube','Vorige instellingen teruggezet')
    elif choice==2:xbmcaddon.Addon('plugin.video.youtube').openSettings()
    elif choice==3:
        xbmc.executebuiltin('UpdateAddonRepos')
        dialog.ok('YouTube','Kodi vernieuwt de repositories. Beschikbare updates volgen je Kodi-updatevoorkeur.')
