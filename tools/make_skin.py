"""Maakt de skin-mod uit de onaangeroerde Arctic Fuse 3 in upstream/.

Gebruik:  python tools/make_skin.py     (build.py roept dit ook zelf aan)

Stappen:
  1. Kopieert upstream/skin.arctic.fuse.3 naar build/<eigen id>/.
  2. Vervangt het addon-id overal, zodat de mod naast het origineel kan bestaan.
  3. Legt de bestanden uit skin-mod/overlay/ eroverheen (logo, gezichtjes,
     eigen includes, standaard-homescherm).
  4. Voert een klein aantal gerichte tekstwijzigingen uit (naam, kleuren, logo,
     laad-animatie). Elke wijziging controleert of de te vervangen tekst precies
     zo vaak voorkomt als verwacht. Klopt dat na een upstream-update niet meer,
     dan stopt het script met een duidelijke melding in plaats van stil iets
     verkeerds te bouwen.

Instellingen (naam, versie, kleuren, laadteksten) staan in skin-mod/mod.json.
Alleen de standaardbibliotheek van Python is nodig.
"""
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD_DIR = ROOT / "skin-mod"
BUILD = ROOT / "build"

TEXT_SUFFIXES = {".xml", ".json", ".po", ".xmltemplate", ".txt", ".md", ".xsp"}
SKIP_UPSTREAM = shutil.ignore_patterns(".git", ".github", ".gitignore", ".gitattributes")


class Patcher:
    """Tekstvervanging in een bestand, met controle op het aantal treffers."""

    def __init__(self, skin_dir):
        self.skin_dir = skin_dir
        self.count = 0

    def replace(self, rel_path, old, new, expected=1):
        path = self.skin_dir / rel_path
        text = path.read_bytes().decode("utf-8")
        found = text.count(old)
        if found != expected:
            sys.exit(
                f"FOUT in {rel_path}: verwachtte {expected}x de tekst\n    {old[:120]!r}\n"
                f"maar vond hem {found}x. Upstream is hier waarschijnlijk gewijzigd; "
                f"pas de bijbehorende stap in tools/make_skin.py aan."
            )
        path.write_bytes(text.replace(old, new).encode("utf-8"))
        self.count += 1


def copy_upstream(cfg, skin_dir):
    if skin_dir.exists():
        shutil.rmtree(skin_dir)
    shutil.copytree(ROOT / cfg["upstream_dir"], skin_dir, ignore=SKIP_UPSTREAM)


def replace_addon_id(cfg, skin_dir):
    old, new = cfg["upstream_id"].encode(), cfg["id"].encode()
    changed = 0
    for path in skin_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            data = path.read_bytes()
            if old in data:
                path.write_bytes(data.replace(old, new))
                changed += 1
    return changed


def apply_overlay(skin_dir):
    overlay = MOD_DIR / "overlay"
    files = [p for p in overlay.rglob("*") if p.is_file()]
    for src in files:
        dst = skin_dir / src.relative_to(overlay)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return len(files)


def loading_line_variable(lines):
    """Kiest een laadtekst op basis van het laatste cijfer van de seconden."""
    if len(lines) != 10:
        sys.exit("FOUT: mod.json moet precies 10 loading_lines bevatten (een per eindcijfer).")
    rows = []
    for digit, line in enumerate(lines[:-1]):
        safe = line.replace("&", "&amp;").replace("<", "&lt;")
        rows.append(f'        <value condition="String.EndsWith(System.Time(ss),{digit})">{safe}...</value>')
    last = lines[-1].replace("&", "&amp;").replace("<", "&lt;")
    rows.append(f"        <value>{last}...</value>")
    return "\n".join(rows)


def patch_skin(cfg, skin_dir):
    p = Patcher(skin_dir)
    accent, bg = cfg["accent"], cfg["background"]

    # --- addon.xml: naam, versie, herkomst ---------------------------------
    p.replace("addon.xml", 'name="Arctic Fuse 3" provider-name="jurialmunkey" version="',
              f'name="{cfg["name"]}" provider-name="jurialmunkey (mod: Krispijn)" version="KRISPIJN_VERSION" upstream-version="')
    # het attribuut upstream-version is geen geldig Kodi-attribuut: haal de oude versie eruit
    addon_xml = skin_dir / "addon.xml"
    text = addon_xml.read_text(encoding="utf-8")
    start = text.index('upstream-version="')
    end = text.index('"', start + len('upstream-version="')) + 1
    upstream_version = text[start + len('upstream-version="'):end - 1]
    text = text[:start].rstrip() + text[end:]
    text = text.replace("KRISPIJN_VERSION", cfg["version"])
    addon_xml.write_text(text, encoding="utf-8", newline="\n")
    p.replace("addon.xml", '<summary lang="en">A minimal row based skin</summary>',
              f'<summary lang="en">{cfg["name"]}: a family mod of Arctic Fuse 3</summary>\n'
              f'        <summary lang="nl">{cfg["name"]}: gezinsmod van Arctic Fuse 3</summary>')
    p.replace("addon.xml",
              '<description lang="en">Arctic Fuse 3 is a minimal row based skin with customisable widgets</description>',
              f'<description lang="en">{cfg["name"]} is a personal mod of Arctic Fuse 3 {upstream_version} by jurialmunkey '
              f'(CC BY-NC-SA 4.0): own colours, logo, startup screen and family faces.</description>\n'
              f'        <description lang="nl">{cfg["name"]} is een persoonlijke mod van Arctic Fuse 3 {upstream_version} van '
              f'jurialmunkey (CC BY-NC-SA 4.0): eigen kleuren, logo, opstartscherm en gezinsgezichtjes.</description>')

    # --- kleuren: achtergrond ----------------------------------------------
    for group in ("main_bg", "dialog_bg", "panel_bg"):
        for alpha, level in (("ff", "100"), ("e7", "90"), ("b3", "70"), ("80", "50"), ("4d", "30"), ("1f", "12")):
            if group == "panel_bg" and level == "100":
                continue  # bestaat niet in upstream
            p.replace("colors/defaults.xml",
                      f'<color name="{group}_{level}">{alpha}000000</color>',
                      f'<color name="{group}_{level}">{alpha}{bg}</color>')

    # --- eerste start: eigen thema in plaats van de keuze-wizard ------------
    # Upstream opent bij de eerste start een wizard die kleuren en een
    # homescherm-preset laat kiezen en daarmee onze standaard zou overschrijven.
    # Wij zetten het thema direct. De wizard blijft bereikbaar via de
    # skin-instellingen. Een gekleurde selectie hoort bij RevertSelectedText
    # (witte tekst op de selectie), net als bij de kleurpresets van upstream.
    p.replace("shortcuts/skinvariables-startup.json",
              '"Skin.SetBool(SetupWizard.Pending)",',
              f'"Skin.SetString(focuscolor.name,{accent})",\n'
              '                        "Skin.SetBool(RevertSelectedText)",')
    p.replace("shortcuts/skinvariables-startup.json",
              '"Skin.SetString(Background.Image,special://skin/extras/backgrounds/blur/purple_blur.jpg)",',
              '"Skin.SetString(Background.Image,special://skin/extras/krispijn/background.jpg)",')

    # --- eigen includes aanmelden ------------------------------------------
    p.replace("1080i/Includes.xml", '    <include file="Includes_Font.xml" />',
              '    <include file="Includes_Font.xml" />\n    <include file="Includes_Krispijn.xml" />')
    p.replace("1080i/Includes_Krispijn.xml", "        <!--LOADING_LINES-->",
              loading_line_variable(cfg["loading_lines"]))

    # --- opstartscherm: eigen naam, gezichtje en laadtekst ------------------
    p.replace("1080i/Includes_Objects.xml", "<label>KODI</label>", f'<label>{cfg["logo_text"]}</label>')
    p.replace("1080i/Includes_Hubs.xml",
              '                <include content="Furniture_Busy" condition="$PARAM[busyspinner]">\n'
              '                    <param name="hasspinner">true</param>\n'
              '                    <param name="spinspinner">true</param>\n'
              '                    <param name="spinnervisible">[!Window.IsActive(DialogVolumeBar.xml) | Player.Muted]</param>',
              '                <include>Krispijn_Splash_Extras</include>\n'
              '                <include content="Furniture_Busy" condition="$PARAM[busyspinner]">\n'
              '                    <param name="hasspinner">true</param>\n'
              '                    <param name="spinspinner">true</param>\n'
              '                    <param name="spinnervisible">[!Window.IsActive(DialogVolumeBar.xml) | Player.Muted]</param>')

    # --- laad-animatie: af en toe een gezichtje in plaats van het rondje ----
    p.replace("1080i/Includes_Furniture.xml",
              '                        <include content="Furniture_Busy_Spinner" condition="$PARAM[hasspinner]">\n'
              '                            <param name="spinspinner">$PARAM[spinspinner]</param>\n'
              '                        </include>',
              '                        <include content="Furniture_Busy_Spinner" condition="$PARAM[hasspinner]">\n'
              '                            <param name="spinspinner">$PARAM[spinspinner]</param>\n'
              '                        </include>\n'
              '                        <include condition="$PARAM[hasspinner]">Krispijn_BusyFace</include>')

    # --- standaard-hubs: live-tv uit, wij kijken alleen video-add-ons -------
    hubs_path = skin_dir / "shortcuts/skinvariables-shortcut-hubs.json"
    hubs = json.loads(hubs_path.read_text(encoding="utf-8"))
    livetv = [h for h in hubs if h.get("window") == "1107"]
    if len(livetv) != 1:
        sys.exit("FOUT: hub 1107 (live-tv) niet gevonden in skinvariables-shortcut-hubs.json.")
    livetv[0]["disabled"] = "True"
    hubs_path.write_text(json.dumps(hubs, indent=4, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    return p.count, upstream_version


def check_xml(skin_dir):
    """Elke XML moet goed gevormd zijn; een kapotte skin-XML laat Kodi vastlopen."""
    bad = []
    for path in sorted(skin_dir.rglob("*.xml")):
        try:
            ET.parse(path)
        except ET.ParseError as err:
            bad.append(f"{path.relative_to(skin_dir)}: {err}")
    if bad:
        sys.exit("FOUT: ongeldige XML na het aanpassen:\n  " + "\n  ".join(bad))


def make_skin():
    cfg = json.loads((MOD_DIR / "mod.json").read_text(encoding="utf-8"))
    skin_dir = BUILD / cfg["id"]
    copy_upstream(cfg, skin_dir)
    id_files = replace_addon_id(cfg, skin_dir)
    overlay_files = apply_overlay(skin_dir)
    patches, upstream_version = patch_skin(cfg, skin_dir)
    check_xml(skin_dir)
    print(f"  skin-mod {cfg['id']} {cfg['version']} op basis van Arctic Fuse 3 {upstream_version}: "
          f"id vervangen in {id_files} bestanden, {overlay_files} overlay-bestanden, {patches} wijzigingen")
    return skin_dir


if __name__ == "__main__":
    make_skin()
