"""Controleert of Kodi alle afhankelijkheden van de skin-mod kan vinden.

Gebruik:  python tools/check_deps.py     (na python tools/build.py, heeft internet nodig)

De skin eist minimale versies van andere add-ons. Die moeten te vinden zijn in de
repository van jurialmunkey of in de officiele Kodi-repository, anders weigert Kodi
de skin te installeren. Dit gaat vooral mis als upstream in zijn broncode al een
nieuwere versie eist dan er uitgebracht is. Draai deze controle daarom na elke
upstream-update en voor elke publicatie.
"""
import gzip
import sys
import urllib.request
import xml.etree.ElementTree as ET

from make_skin import BUILD, load_configs

JM = "https://raw.githubusercontent.com/jurialmunkey/repository.jurialmunkey/master/{}/zips/addons.xml"
KODI_MIRROR = "https://mirrors.kodi.tv/addons/{}/addons.xml.gz"
JM_DIRS = {"omega": ("omega", "repo"), "piers": ("piers", "omega", "repo")}


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


def check_variant(cfg, catalogs):
    kodi = cfg["kodi"]
    addon_xml = BUILD / cfg["id"] / "addon.xml"
    if not addon_xml.is_file():
        sys.exit(f"{addon_xml} ontbreekt. Draai eerst python tools/build.py.")
    print(f"\n{cfg['name']} ({kodi})")
    imports = [(item.attrib["addon"], item.get("version", "0.0.0"))
               for item in ET.parse(addon_xml).getroot().findall("requires/import")
               if not item.attrib["addon"].startswith(("xbmc.", "kodi."))
               and item.get("optional") != "true"]

    sources = [(f"jurialmunkey {name}", JM.format(name)) for name in JM_DIRS[kodi]]
    sources.append((f"Kodi officieel ({kodi})", KODI_MIRROR.format(kodi)))
    available = []
    for name, url in sources:
        if url not in catalogs:
            try:
                catalogs[url] = fetch(url)
            except (OSError, ET.ParseError) as err:
                catalogs[url] = None
                print(f"  LET OP: {name} niet bereikbaar of ongeldig ({err})")
        if catalogs[url] is not None:
            available.append((name, catalogs[url]))

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
    return problems


def main():
    catalogs = {}
    configs = load_configs() + [{"id": "plugin.video.krispijn", "name": "Krispijn Video", "kodi": "omega"}]
    problems = sum(check_variant(cfg, catalogs) for cfg in configs)
    if problems:
        sys.exit(f"{problems} vereiste afhankelijkheid(en) niet gevonden.")
    print("\nAlle vereiste afhankelijkheden van beide skins en Krispijn Video zijn gevonden.")


if __name__ == "__main__":
    main()
