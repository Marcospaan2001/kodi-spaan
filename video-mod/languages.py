"""Engelse audio en Nederlandse ondertitels, zonder netwerkverzoeken."""
import json


def rpc(method, params=None):
    import xbmc
    data=json.loads(xbmc.executeJSONRPC(json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or {}})))
    if 'error' in data: raise ValueError('Kodi-taalinstelling niet beschikbaar')
    return data.get('result')


def defaults():
    import xbmcaddon,xbmc
    addon=xbmcaddon.Addon('plugin.video.krispijn')
    if addon.getSetting('krispijn.languages.v1')=='true': return
    try:
        for key,value in [('locale.audiolanguage','English'),('locale.subtitlelanguage','Dutch'),('videoplayer.preferdefaultflag',False)]:
            if rpc('Settings.SetSettingValue',{'setting':key,'value':value}) is not True:
                raise ValueError('Kodi heeft de taalinstelling geweigerd')
        addon.setSetting('subtitles.language','Dutch')
        addon.setSetting('krispijn.languages.v1','true')
    except (ValueError,TypeError):
        xbmc.log('Krispijn: taalvoorkeuren nog niet toegepast',xbmc.LOGWARNING)


def choose(streams, languages):
    candidates=[s for s in streams if str(s.get('language','')).lower().replace('_','-').split('-')[0] in languages]
    # Geef gewone sporen voorrang boven commentaar of uitsluitend forced-regels.
    candidates.sort(key=lambda s: any(word in s.get('name','').lower() for word in ('commentary','commentaar','description','forced')))
    return candidates[0]['index'] if candidates else None


def apply_streams():
    import xbmc,xbmcgui
    try:
        players=rpc('Player.GetActivePlayers')
        player=next((p['playerid'] for p in players if p.get('type')=='video'),None)
        if player is None:return
        info=rpc('Player.GetProperties',{'playerid':player,'properties':['audiostreams','subtitles']})
        audio=choose(info.get('audiostreams',[]),{'en','eng','english'})
        subs=choose(info.get('subtitles',[]),{'nl','nld','dut','dutch','nederlands'})
        if audio is not None:rpc('Player.SetAudioStream',{'playerid':player,'stream':audio})
        if subs is not None:rpc('Player.SetSubtitle',{'playerid':player,'subtitle':subs,'enable':True})
        elif info.get('subtitles'):
            rpc('Player.SetSubtitle',{'playerid':player,'subtitle':'off'})
        missing=[]
        if audio is None and info.get('audiostreams'):missing.append('Geen Engels audiospoor in deze bron')
        if missing:xbmcgui.Dialog().notification('Familie Krispijn','. '.join(missing),time=6000)
    except (ValueError,TypeError,KeyError):
        xbmc.log('Krispijn: taalsporen konden niet worden geselecteerd',xbmc.LOGWARNING)


def search_missing(playback=None, metadata=None):
    """Eenmalig na de afspeelstart; gebruiker kiest zelf de passende vertaling."""
    import xbmc, xbmcaddon, xbmcgui
    try:
        player=next((p['playerid'] for p in rpc('Player.GetActivePlayers') if p.get('type')=='video'),None)
        if player is None:return
        info=rpc('Player.GetProperties',{'playerid':player,'properties':['subtitles']})
        if choose(info.get('subtitles',[]),{'nl','nld','dut','dutch','nederlands'}) is not None:return
        sid='service.subtitles.opensubtitles-com'
        if not xbmc.getCondVisibility('System.HasAddon('+sid+')'):
            xbmcgui.Dialog().notification('Familie Krispijn','Geen Nederlandse ondertitels. Stel OpenSubtitles in via Instellen.',time=6000)
            return
        provider=xbmcaddon.Addon(sid)
        if not provider.getSetting('OSuser') or not provider.getSetting('OSpass'):
            xbmcgui.Dialog().notification('Familie Krispijn','Log eenmalig in bij OpenSubtitles via Instellen.',time=6000)
            return
        for key,value in [('subtitles.languages',['Dutch']),('subtitles.movie',sid),('subtitles.tv',sid),('subtitles.downloadfirst',False)]:
            if rpc('Settings.SetSettingValue',{'setting':key,'value':value}) is not True:return
        if playback is not None and metadata:
            prepare_subtitle_metadata(playback, metadata)
        xbmc.executebuiltin('ActivateWindow(subtitlesearch)')
    except (ValueError,TypeError,KeyError,RuntimeError):
        xbmc.log('Krispijn: automatisch ondertitels zoeken niet beschikbaar',xbmc.LOGWARNING)


def prepare_subtitle_metadata(playback, metadata):
    """Herstel catalogustitels nadat de stream zijn eigen releasenaam heeft geladen."""
    title=str(metadata.get('title') or metadata.get('original_title') or '').strip()
    original=str(metadata.get('original_title') or title).strip()
    if not title:return
    item=playback.make_listitem()
    item.setPath(playback.getPlayingFile())
    item.setLabel(title)
    tag=item.getVideoInfoTag()
    if metadata.get('mediatype') == 'episode':
        tag.setMediaType('episode')
        tag.setTvShowTitle(original)
        tag.setTitle(str(metadata.get('ep_name') or title))
        tag.setOriginalTitle(str(metadata.get('ep_name') or title))
        for key, setter in [('season',tag.setSeason),('episode',tag.setEpisode)]:
            try:setter(int(metadata[key]))
            except (KeyError,ValueError,TypeError):pass
    else:
        tag.setMediaType('movie')
        tag.setTitle(title)
        tag.setOriginalTitle(original)
    try:tag.setYear(int(metadata.get('year')))
    except (ValueError,TypeError):pass
    playback.updateInfoTag(item)
