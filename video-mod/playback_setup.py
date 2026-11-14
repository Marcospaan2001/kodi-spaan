"""Herstel de meegeleverde bronzoeker één keer, ook op bestaande installaties."""

def migrate(addon=None):
    if addon is None:
        import xbmcaddon
        addon=xbmcaddon.Addon('plugin.video.krispijn')
    if addon.getSetting('krispijn.sources.v1')=='true': return False
    addon.setSetting('provider.external','true')
    addon.setSetting('krispijn.sources.v1','true')
    try:
        from modules import kodi_utils
        kodi_utils.clear_property('pov_settings')
    except ImportError: pass
    return True


def ready():
    import xbmcaddon,xbmcgui
    addon=xbmcaddon.Addon('plugin.video.krispijn')
    migrate(addon)
    if not any(addon.getSetting(key+'.token') for key in ('rd','ad','pm','tb','oc')) and not addon.getSetting('easynews.username'):
        xbmcgui.Dialog().ok('Familie Krispijn','Koppel eerst Real-Debrid via Instellen. Je kunt zonder koppeling wel films en series bekijken in de catalogus.')
        return False
    return True


def no_sources(raw_count=0):
    import xbmcgui
    text=('Er zijn bronnen gevonden, maar je filters hebben ze uitgesloten. Controleer de bronfilters bij de uitgebreide instellingen.' if raw_count else 'Er is voor deze titel nu geen afspeelbare bron gevonden. Controleer Real-Debrid bij Instellen of probeer een andere titel. Een vermelding in de bioscoopcatalogus betekent niet dat een bron beschikbaar is.')
    xbmcgui.Dialog().ok('Familie Krispijn',text)
