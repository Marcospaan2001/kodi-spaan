"""Maakt de skin-mod uit de onaangeroerde Arctic Fuse 2 en 3 in upstream/.

Gebruik:  python tools/make_skin.py     (build.py roept dit ook zelf aan)

Stappen:
  1. Kopieert de juiste Arctic Fuse-versie naar build/<eigen id>/.
  2. Vervangt het addon-id overal, zodat de mod naast het origineel kan bestaan.
  3. Legt de bestanden uit skin-mod/overlay/ eroverheen (logo, gezichtjes,
     eigen includes, standaard-homescherm).
  4. Voert een klein aantal gerichte tekstwijzigingen uit (naam, kleuren, logo,
     laad-animatie). Elke wijziging controleert of de te vervangen tekst precies
     zo vaak voorkomt als verwacht. Klopt dat na een upstream-update niet meer,
     dan stopt het script met een duidelijke melding in plaats van stil iets
     verkeerds te bouwen.

Naam en versie staan in fuse2.json en fuse3.json. mod.json bevat het gedeelde thema.
Alleen de standaardbibliotheek van Python is nodig.
"""
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parent.parent
MOD_DIR = ROOT / "skin-mod"
BUILD = ROOT / "build"

TEXT_SUFFIXES = {".xml", ".json", ".po", ".xmltemplate", ".txt", ".md", ".xsp"}
SKIP_UPSTREAM = shutil.ignore_patterns(".git", ".github", ".gitignore", ".gitattributes")

VARIANTS = ("fuse2", "fuse3")


def load_configs():
    shared = json.loads((MOD_DIR / "mod.json").read_text(encoding="utf-8"))
    return [
        shared | json.loads((MOD_DIR / f"{variant}.json").read_text(encoding="utf-8"))
        for variant in VARIANTS
    ]


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


def apply_overlay(cfg, skin_dir):
    overlay = MOD_DIR / "overlay"
    files = [p for p in overlay.rglob("*") if p.is_file()]
    copied = 0
    for src in files:
        relative = src.relative_to(overlay)
        # Fuse 2 bewaart de widgets in het menu-item zelf.
        if cfg["kodi"] == "omega" and relative.parts[0] == "shortcuts":
            continue
        dst = skin_dir / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copied += 1
    return copied


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

    # Gebruik de upstream-metadata ook voor de naamsvermelding in de mod.
    upstream_name = cfg["upstream_name"]
    upstream_version = ET.parse(skin_dir / "addon.xml").getroot().attrib["version"]
    name = escape(cfg["name"])
    p.replace("addon.xml",
              f'name="{upstream_name}" provider-name="jurialmunkey" version="{upstream_version}"',
              f'name={quoteattr(cfg["name"])} provider-name="jurialmunkey (mod: Krispijn)" '
              f'version={quoteattr(cfg["version"])}')
    p.replace("addon.xml", '<summary lang="en">A minimal row based skin</summary>',
              f'<summary lang="en">{name}: a family mod of {upstream_name}</summary>\n'
              f'        <summary lang="nl">{name}: gezinsmod van {upstream_name}</summary>')
    p.replace("addon.xml",
              f'<description lang="en">{upstream_name} is a minimal row based skin with customisable widgets</description>',
              f'<description lang="en">{name} is a personal mod of {upstream_name} {upstream_version} by jurialmunkey '
              f'(CC BY-NC-SA 4.0): own colours, logo, startup screen and family faces.</description>\n'
              f'        <description lang="nl">{name} is een persoonlijke mod van {upstream_name} {upstream_version} van '
              f'jurialmunkey (CC BY-NC-SA 4.0): eigen kleuren, logo, opstartscherm en gezinsgezichtjes.</description>')

    omega = cfg["kodi"] == "omega"

    # --- kleuren: achtergrond ----------------------------------------------
    for group in ("main_bg", "dialog_bg", "panel_bg"):
        for alpha, level in (("ff", "100"), ("e7", "90"), ("b3", "70"), ("80", "50"), ("4d", "30"), ("1f", "12")):
            if group == "panel_bg" and (level == "100" or (omega and level in ("90", "30"))):
                continue  # bestaat niet in upstream
            p.replace("colors/defaults.xml",
                      f'<color name="{group}_{level}">{alpha}000000</color>',
                      f'<color name="{group}_{level}">{alpha}{bg}</color>')

    startup = "shortcuts/skinvariables-startup.json"
    background = '"Skin.SetString(Background.Image,special://skin/extras/krispijn/background.jpg)",'
    accent_action = f'"Skin.SetString(focuscolor.name,{accent})",'
    white_text = '"Skin.SetBool(RevertSelectedText)",'
    if omega:
        # Fuse 2 opent zijn wizard vanuit Home.xml. Stel de voorkeuren in vóór InitDone.
        marker = '"Skin.SetBool(DefaultConfig.InitDone)"'
        p.replace(startup, marker, "\n                        ".join((
            accent_action, white_text, background,
            '"Skin.SetBool(Hub.Home.DisableSpotlight)",',
            '"Skin.SetBool(Wizard.FirstRun)",',
            marker,
        )))
    else:
        p.replace(startup, '"Skin.SetBool(SetupWizard.Pending)",',
                  f'{accent_action}\n                        {white_text}')
        p.replace(startup,
                  '"Skin.SetString(Background.Image,special://skin/extras/backgrounds/blur/purple_blur.jpg)",',
                  background)

    # --- eigen includes aanmelden ------------------------------------------
    p.replace("1080i/Includes.xml", '    <include file="Includes_Font.xml" />',
              '    <include file="Includes_Font.xml" />\n    <include file="Includes_Krispijn.xml" />')
    p.replace("1080i/Includes_Krispijn.xml", "        <!--LOADING_LINES-->",
              loading_line_variable(cfg["loading_lines"]))

    # --- opstartscherm: eigen naam, gezichtje en laadtekst ------------------
    p.replace("1080i/Includes_Objects.xml", "<label>KODI</label>", f'<label>{escape(cfg["logo_text"])}</label>')
    spinner = (
        '                <include content="Furniture_Busy" condition="$PARAM[busyspinner]">\n'
        '                    <param name="hasspinner">true</param>\n'
        '                    <param name="spinspinner">true</param>\n'
        '                    <param name="spinnervisible">[!Window.IsActive(DialogVolumeBar.xml) | Player.Muted]</param>'
    )
    p.replace("1080i/Includes_Hubs.xml", spinner,
              '                <include>Krispijn_Splash_Extras</include>\n' + spinner)

    # --- laad-animatie: af en toe een gezichtje in plaats van het rondje ----
    p.replace("1080i/Includes_Furniture.xml",
              '                        <include content="Furniture_Busy_Spinner" condition="$PARAM[hasspinner]">\n'
              '                            <param name="spinspinner">$PARAM[spinspinner]</param>\n'
              '                        </include>',
              '                        <include content="Furniture_Busy_Spinner" condition="$PARAM[hasspinner]">\n'
              '                            <param name="spinspinner">$PARAM[spinspinner]</param>\n'
              '                        </include>\n'
              '                        <include condition="$PARAM[hasspinner]">Krispijn_BusyFace</include>')

    if omega:
        patch_fuse2_menu(p)
    else:
        hubs_path = skin_dir / "shortcuts/skinvariables-shortcut-hubs.json"
        hubs = json.loads(hubs_path.read_text(encoding="utf-8"))
        livetv = [h for h in hubs if h.get("window") == "1107"]
        if len(livetv) != 1:
            sys.exit("FOUT: hub 1107 (live-tv) niet gevonden in skinvariables-shortcut-hubs.json.")
        livetv[0]["disabled"] = "True"
        hubs_path.write_text(json.dumps(hubs, indent=4, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    return p.count, upstream_version


def patch_fuse2_menu(p):
    # Fuse 2 genereert Home-widgets uit het zijmenu. De rij hoort bij de
    # eerste knop; de andere knoppen zijn alleen snelkoppelingen.
    shortcuts = MOD_DIR / "overlay" / "shortcuts"
    relative = "shortcuts/skinvariables-shortcut-sidemenu.json"
    original = (p.skin_dir / relative).read_bytes().decode("utf-8")
    first_guid = "guid-19ada9cd"
    if sum(item.get("guid") == first_guid for item in json.loads(original)) != 1:
        sys.exit(f"FOUT: verwacht één standaarditem {first_guid} in {relative}.")
    items = json.loads((shortcuts / "skinvariables-shortcut-homesubmenu.json").read_text(encoding="utf-8"))
    widget, = json.loads((shortcuts / "skinvariables-shortcut-homewidgets.json").read_text(encoding="utf-8"))
    for item, guid in zip(items, (first_guid, "guid-c990dfe4", "guid-8fc53d50"), strict=True):
        item["guid"] = guid
    items[0]["widgets"] = [{**widget, "widget_style": "Square", "guid": "guid-f5d496d2"}]
    p.replace(relative, original, json.dumps(items, indent=4, ensure_ascii=False) + "\n")


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


def make_skin(cfg):
    skin_dir = BUILD / cfg["id"]
    copy_upstream(cfg, skin_dir)
    id_files = replace_addon_id(cfg, skin_dir)
    overlay_files = apply_overlay(cfg, skin_dir)
    patches, upstream_version = patch_skin(cfg, skin_dir)
    check_xml(skin_dir)
    print(f"  skin-mod {cfg['id']} {cfg['version']} op basis van {cfg['upstream_name']} {upstream_version}: "
          f"id vervangen in {id_files} bestanden, {overlay_files} overlay-bestanden, {patches} wijzigingen")
    return skin_dir


if __name__ == "__main__":
    for cfg in load_configs():
        make_skin(cfg)
