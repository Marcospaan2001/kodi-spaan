"""Sportmenu op aanvraag; originele The Loop-routes en eigen streamadressen."""
import json
from pathlib import Path
from urllib.parse import quote, urlsplit

LOOP='plugin.video.the-loop'
ROUTES={
    'Formule 1': 'get_list/'+quote('https://loopaddon.uk/files/k19/AutoZone.json',safe=''),
    'Voetbal': 'get_list/'+quote('https://loopaddon.uk/files/k19/xmls/ScoreZone/soccertoday4.json',safe=''),
    'Darts': 'ls3arch3/search/darts',
}


def open_sports(close_hub):
    import xbmc,xbmcaddon,xbmcgui,xbmcvfs
    dialog=xbmcgui.Dialog()
    choice=dialog.select('Sport',list(ROUTES))
    if choice<0:return
    sport=list(ROUTES)[choice]
    addon=xbmcaddon.Addon('plugin.video.krispijn')
    file=Path(xbmcvfs.translatePath(addon.getAddonInfo('profile')))/'sports-streams.json'
    try:data=json.loads(file.read_text(encoding='utf-8'))
    except (ValueError,OSError):data={}
    if not isinstance(data,dict):data={}
    streams=data.get(sport,[])
    if not isinstance(streams,list):streams=[]
    streams=[r for r in streams if isinstance(r,dict) and isinstance(r.get('name'),str) and isinstance(r.get('url'),str)]
    selected=dialog.select(sport,['The Loop openen','Eigen livestream toevoegen','Eigen livestream verwijderen']+[r['name'] for r in streams])
    if selected<0:return
    if selected==0:
        if not xbmc.getCondVisibility('System.HasAddon('+LOOP+')'):
            if dialog.yesno('The Loop installeren','The Loop en zijn afhankelijkheden installeren? Dit is een aparte add-on met eigen services en instellingen.'):
                xbmc.executebuiltin('InstallAddon('+LOOP+')')
                dialog.ok('Sport','Voltooi de installatie van The Loop. Open daarna Sport opnieuw. Vind je de add-on niet, vernieuw dan Spaan Repository.')
            return
        close_hub()
        xbmc.executebuiltin('ActivateWindow(Videos,plugin://'+LOOP+'/'+ROUTES[sport]+',return)')
    elif selected==1:
        name=dialog.input('Naam van de livestream').strip()
        if not name:return
        url=dialog.input('Stream-URL (https:// of http://)').strip()
        try:parsed=urlsplit(url)
        except ValueError:
            dialog.ok('Stream toevoegen','Dit streamadres is ongeldig.');return
        if parsed.scheme not in ('http','https') or not parsed.hostname or '\n' in url or '\r' in url:
            dialog.ok('Stream toevoegen','Vul een geldig http- of https-streamadres in.');return
        streams.append({'name':name,'url':url})
        save(file,data,sport,streams)
        dialog.notification('Sport','Livestream toegevoegd')
    elif selected==2:
        index=dialog.select('Welke livestream verwijderen?',[r['name'] for r in streams])
        if index>=0:
            streams.pop(index);save(file,data,sport,streams)
    else:
        stream=streams[selected-3]
        item=xbmcgui.ListItem(label=stream['name']);item.setPath(stream['url'])
        xbmc.Player().play(stream['url'],item)


def save(file,data,sport,streams):
    data[sport]=streams;file.parent.mkdir(parents=True,exist_ok=True)
    temporary=file.with_suffix('.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    temporary.replace(file)
