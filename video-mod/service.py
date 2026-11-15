"""Alleen lokale initialisatie en instellingenmonitor; geen accountsynchronisatie."""
from modules.entry import (SettingsMonitor, initializeDatabases, checkSettingsFile,
                           viewsSetWindowProperties)

if __name__ == '__main__':
    from modules.krispijn_playback_setup import migrate
    migrate()
    from modules.krispijn_languages import defaults
    defaults()
    monitor = SettingsMonitor()
    initializeDatabases()
    checkSettingsFile()
    viewsSetWindowProperties()
    monitor.waitForAbort()
