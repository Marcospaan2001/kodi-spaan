"""Controleert of Kodi alle afhankelijkheden van de skin-mod kan vinden.

Gebruik:  python tools/check_deps.py     (na python tools/build.py, heeft internet nodig)

De skin eist minimale versies van andere add-ons. Die moeten te vinden zijn in de
repository van jurialmunkey of in de officiele Kodi-repository, anders weigert Kodi
de skin te installeren. Dit gaat vooral mis als upstream in zijn broncode al een
nieuwere versie eist dan er uitgebracht is. Draai deze controle daarom na elke
upstream-update en voor elke publicatie.
"""
import gzip
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JM = "https://raw.githubusercontent.com/jurialmunkey/repository.jurialmunkey/master/{}/zips/addons.xml"
SOURCES = [
    ("jurialmunkey piers", JM.format("piers")),
    ("jurialmunkey omega", JM.format("omega")),
    ("jurialmunkey repo", JM.format("repo")),
    ("Kodi officieel (piers)", "https://mirrors.kodi.tv/addons/piers/addons.xml.gz"),
]
BUILT_IN = ("xbmc.", "kodi.")


def version_key(version):
    parts = []
    for piece in version.replace("~", ".").replace("+", ".").split("."):
        parts.append((0, int(piece)) if piece.isdigit() else (1, piece))
    return parts


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "kodi-repo-check"})
    data = urllib.request.urlopen(request, timeout=60).read()
    if url.endswith(".gz"):
        data = gzip.decompress(data)
    return {a.get("id"): a.get("version") for a in ET.fromstring(data).iter("addon")}


def main():
    cfg = json.loads((ROOT / "skin-mod" / "mod.json").read_text(encoding="utf-8"))
    addon_xml = ROOT / "build" / cfg["id"] / "addon.xml"
    if not addon_xml.is_file():
        sys.exit("Draai eerst python tools/build.py.")
    imports = [(i.get("addon"), i.get("version"))
               for i in ET.parse(addon_xml).getroot().iter("import")
               if not i.get("addon").startswith(BUILT_IN)]

    available = []
    for name, url in SOURCES:
        try:
            available.append((name, fetch(url)))
        except Exception as err:  # netwerkfout of ontbrekende repo: melden, niet stoppen
            print(f"  LET OP: {name} niet bereikbaar ({err})")

    problems = 0
    for addon_id, wanted in imports:
        hits = [(name, found[addon_id]) for name, found in available if addon_id in found]
        good = [(n, v) for n, v in hits if version_key(v) >= version_key(wanted)]
        if good:
            name, version = max(good, key=lambda h: version_key(h[1]))
            print(f"  ok    {addon_id} >= {wanted}: {version} in {name}")
        else:
            problems += 1
            seen = ", ".join(f"{v} in {n}" for n, v in hits) or "nergens gevonden"
            print(f"  FOUT  {addon_id} >= {wanted}: niet beschikbaar ({seen})")
    if problems:
        sys.exit(f"{problems} afhankelijkheid(en) niet beschikbaar: Kodi zal de skin niet installeren.")
    print("Alle afhankelijkheden zijn beschikbaar.")


if __name__ == "__main__":
    main()
