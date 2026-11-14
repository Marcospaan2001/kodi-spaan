"""Alleen lokale initialisatie en instellingenmonitor; geen accountsynchronisatie."""
from modules.entry import (SettingsMonitor, initializeDatabases, checkSettingsFile,
                           viewsSetWindowProperties)

if __name__ == '__main__':
    monitor = SettingsMonitor()
    initializeDatabases()
    checkSettingsFile()
    viewsSetWindowProperties()
    monitor.waitForAbort()
