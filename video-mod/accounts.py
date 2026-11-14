"""Real-Debrid met expliciete controle, annulering en bevestiging. GPL-3.0."""
import json
import time
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

class AccountError(Exception): pass

def request(path, data=None, token='', pending=False):
    headers={'User-Agent':'Krispijn/1.1'}
    if token: headers['Authorization']='Bearer '+token
    if data is not None: headers['Content-Type']='application/x-www-form-urlencoded'
    try:
        with urlopen(Request('https://api.real-debrid.com/'+path, data=urlencode(data).encode() if data is not None else None,headers=headers),timeout=8) as response:
            return json.load(response)
    except HTTPError as e:
        if pending and e.code in (400,403): return None
        raise AccountError('Real-Debrid kon niet worden gecontroleerd. Controleer je verbinding en koppeling.') from None
    except (OSError,ValueError): raise AccountError('Real-Debrid is nu niet bereikbaar. Je bestaande koppeling blijft bewaard.') from None

def offline_status(addon=None):
    if addon is None:
        import xbmcaddon
        addon=xbmcaddon.Addon('plugin.video.krispijn')
    if not addon.getSetting('rd.token'): return 'Real-Debrid niet gekoppeld'
    try: recent=time.time()-float(addon.getSetting('krispijn.rd.checked'))<3600
    except ValueError: recent=False
    if recent: return 'Real-Debrid: '+addon.getSetting('krispijn.rd.state')
    return 'Real-Debrid opgeslagen; controle via Instellen'

def verify(addon, token=None):
    token=token or addon.getSetting('rd.token')
    if not token: raise AccountError('Er is nog geen Real-Debrid-koppeling.')
    user=request('rest/1.0/user',token=token)
    if not user.get('username'): raise AccountError('Real-Debrid gaf geen geldig account terug.')
    state='actief abonnement' if user.get('type')=='premium' and int(user.get('premium',0))>0 else 'gekoppeld, geen actief abonnement'
    addon.setSetting('krispijn.rd.state',state)
    addon.setSetting('krispijn.rd.checked',str(time.time()))
    return user,state

def connect(addon):
    import xbmc,xbmcgui
    client='X245A4XAIBGVM'
    response=request('oauth/v2/device/code?'+urlencode({'client_id':client,'new_credentials':'yes'}))
    if not all(k in response for k in ('device_code','user_code','expires_in')): raise AccountError('De koppelcode kon niet worden gemaakt.')
    progress=xbmcgui.DialogProgress();progress.create('Real-Debrid koppelen','Ga naar https://real-debrid.com/device[CR]Code: [B]'+response['user_code']+'[/B]')
    deadline=time.monotonic()+min(int(response['expires_in']),900)
    interval=max(3,int(response.get('interval',5)));next_poll=0;monitor=xbmc.Monitor()
    credentials=None
    try:
        while time.monotonic()<deadline:
            if progress.iscanceled() or monitor.abortRequested(): return
            if time.monotonic()>=next_poll:
                credentials=request('oauth/v2/device/credentials?'+urlencode({'client_id':client,'code':response['device_code']}),pending=True)
                if credentials and credentials.get('client_secret'): break
                next_poll=time.monotonic()+interval
            if monitor.waitForAbort(0.2): return
        if not credentials or not credentials.get('client_secret'): raise AccountError('De koppelcode is verlopen. Probeer opnieuw.')
        data=request('oauth/v2/token',{'client_id':credentials['client_id'],'client_secret':credentials['client_secret'],'code':response['device_code'],'grant_type':'http://oauth.net/grant_type/device/1.0'})
        token=data.get('access_token')
        if not token: raise AccountError('Real-Debrid gaf geen geldig token terug.')
        user,state=verify(addon,token)
        for key,value in {'client_id':credentials['client_id'],'secret':credentials['client_secret'],'token':token,'refresh':data.get('refresh_token',''),'account_id':user['username'],'enabled':'true','torrent.enabled':'true'}.items(): addon.setSetting('rd.'+key,str(value))
    finally: progress.close()
    from modules import kodi_utils
    kodi_utils.clear_property('pov_settings')
    xbmcgui.Dialog().ok('Real-Debrid gekoppeld',user['username']+'[CR]'+state)

def manage():
    import xbmcaddon,xbmcgui
    addon=xbmcaddon.Addon('plugin.video.krispijn');dialog=xbmcgui.Dialog()
    choice=dialog.select('Real-Debrid',['Koppeling controleren','Koppelen of opnieuw koppelen','Ontkoppelen']) if addon.getSetting('rd.token') else 1
    try:
        if choice==0:
            user,state=verify(addon);dialog.ok('Real-Debrid gecontroleerd',user['username']+'[CR]'+state)
        elif choice==1: connect(addon)
        elif choice==2 and dialog.yesno('Real-Debrid','Wil je deze koppeling verwijderen?'):
            for key in ('token','refresh','secret','client_id','account_id'): addon.setSetting('rd.'+key,'')
            addon.setSetting('krispijn.rd.checked','')
            from modules import kodi_utils
            kodi_utils.clear_property('pov_settings')
            dialog.ok('Real-Debrid','De koppeling is verwijderd.')
    except (AccountError,KeyError,TypeError,ValueError) as error:
        dialog.ok('Real-Debrid',str(error) if isinstance(error,AccountError) else 'Koppelen is niet voltooid. Je bestaande koppeling blijft bewaard.')
