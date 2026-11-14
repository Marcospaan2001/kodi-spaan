"""Bouwt de Kodi-repository naar docs/ (GitHub Pages).

Gebruik:  python tools/build.py

Wat het doet:
  1. Zoekt in de projectroot elke map met een addon.xml (dat is een Kodi-addon).
  2. Maakt per addon docs/zips/<id>/<id>-<versie>.zip en zet addon.xml, icon en
     fanart ernaast (Kodi haalt die los op om de addonlijst te tonen).
  3. Voegt alle addon.xml's samen tot docs/zips/addons.xml en schrijft de
     md5-checksum naar docs/zips/addons.xml.md5. Aan die md5 ziet Kodi of er
     updates zijn.
  4. Kopieert de repository-zip naar docs/ en schrijft docs/index.html met een
     link ernaar, zodat de bestandsbeheerder van Kodi hem kan vinden.

Alleen de standaardbibliotheek van Python is nodig.
"""
import hashlib
import html
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from make_skin import load_configs, make_skin

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ZIPS = DOCS / "zips"

REPO_ADDON_ID = "repository.spaan"
SKIP_DIRS = {"docs", "tools", "build", "upstream", "skin-mod", "fotos"}
EXCLUDE_NAMES = {".git", ".github", ".gitignore", ".gitattributes", "__pycache__",
                 "Thumbs.db", "desktop.ini", ".DS_Store"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".psd", ".xcf"}
# Bestanden die Kodi los naast de zip verwacht
LOOSE_FILES = ("addon.xml", "icon.png", "fanart.jpg", "fanart.png")
# Vaste tijdstempel: dezelfde bron geeft byte-voor-byte dezelfde zip, dus geen
# onnodige wijzigingen in git en geen nep-updates in Kodi.
FIXED_TIME = (2020, 1, 1, 0, 0, 0)


def find_addons(skin_dirs):
    addons = []
    # Addons in de projectroot plus gegenereerde addons (de skin-mod) in build/
    candidates = sorted(ROOT.iterdir()) + sorted(skin_dirs)
    for folder in candidates:
        if not folder.is_dir() or folder.name.startswith(".") or folder.name in SKIP_DIRS:
            continue
        addon_xml = folder / "addon.xml"
        if not addon_xml.is_file():
            continue
        root = ET.parse(addon_xml).getroot()
        addon_id, version = root.get("id"), root.get("version")
        if not addon_id or not version:
            sys.exit(f"FOUT: {addon_xml} mist een id of version.")
        if addon_id != folder.name:
            sys.exit(f"FOUT: map '{folder.name}' moet gelijk zijn aan addon-id '{addon_id}'.")
        addons.append((folder, addon_id, version))
    return addons


def included_files(folder):
    # Windows en Linux sorteren Path verschillend. Houd de oorspronkelijke
    # Windows-volgorde aan op elk platform, ook bij verschillen in hoofdletters.
    def zip_order(path):
        return tuple((part.casefold(), part) for part in path.relative_to(folder).parts)

    for path in sorted(folder.rglob("*"), key=zip_order):
        if not path.is_file():
            continue
        rel = path.relative_to(folder)
        if any(part in EXCLUDE_NAMES for part in rel.parts):
            continue
        if path.suffix.lower() in EXCLUDE_SUFFIXES:
            continue
        yield path, rel


def build_zip(folder, addon_id, version):
    out_dir = ZIPS / addon_id
    out_dir.mkdir(parents=True, exist_ok=True)
    # Oude versies opruimen: de repository biedt alleen de nieuwste aan.
    for old in out_dir.glob("*.zip"):
        old.unlink()
    zip_path = out_dir / f"{addon_id}-{version}.zip"
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path, rel in included_files(folder):
            info = zipfile.ZipInfo(f"{addon_id}/{rel.as_posix()}", FIXED_TIME)
            info.create_system = 0  # Gebruik ook op Linux dezelfde ZIP-header als op Windows.
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
            count += 1
    for name in LOOSE_FILES:
        src = folder / name
        if src.is_file():
            shutil.copyfile(src, out_dir / name)
    return zip_path, count


def write_addons_xml(addons):
    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "<addons>"]
    for folder, _, _ in addons:
        text = (folder / "addon.xml").read_text(encoding="utf-8-sig")
        lines = [ln.rstrip() for ln in text.splitlines()
                 if ln.strip() and not ln.lstrip().startswith("<?xml")]
        parts.extend(lines)
    parts.append("</addons>")
    data = ("\n".join(parts) + "\n").encode("utf-8")
    ET.fromstring(data)  # controle: moet geldige XML zijn
    (ZIPS / "addons.xml").write_bytes(data)
    md5 = hashlib.md5(data).hexdigest()
    (ZIPS / "addons.xml.md5").write_bytes(md5.encode("ascii"))
    return md5


def write_index(repo_zip_name):
    name = html.escape(repo_zip_name)
    page = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spaan Repository</title>
<style>
body {{ font-family: system-ui, sans-serif; background: #0b0e15; color: #f5f5f5;
       max-width: 40rem; margin: 3rem auto; padding: 0 1rem; line-height: 1.5; }}
a {{ color: #ff6b66; }}
code {{ background: #1b2130; padding: .1rem .35rem; border-radius: .25rem; }}
</style>
</head>
<body>
<h1>Spaan Repository</h1>
<p>Voeg deze pagina in Kodi toe als bron en installeer daarna vanuit zip:</p>
<p><a href="{name}">{name}</a></p>
<p>Uitleg: <a href="https://github.com/Marcospaan2001/kodi-spaan/blob/main/docs/SETUP.md">SETUP.md</a></p>
</body>
</html>
"""
    (DOCS / "index.html").write_text(page, encoding="utf-8", newline="\n")


def main():
    skin_dirs = [make_skin(cfg) for cfg in load_configs()]
    addons = find_addons(skin_dirs)
    if not addons:
        sys.exit("FOUT: geen addons gevonden (mappen met een addon.xml).")
    ZIPS.mkdir(parents=True, exist_ok=True)
    (DOCS / ".nojekyll").touch()  # GitHub Pages: bestanden ongewijzigd serveren

    # Addons die uit de bron verdwenen zijn ook uit docs/zips halen
    current_ids = {addon_id for _, addon_id, _ in addons}
    for stale in ZIPS.iterdir():
        if stale.is_dir() and stale.name not in current_ids:
            shutil.rmtree(stale)

    repo_zip_name = None
    for folder, addon_id, version in addons:
        if "GITHUB-GEBRUIKER" in (folder / "addon.xml").read_text(encoding="utf-8-sig"):
            print(f"LET OP: {addon_id}/addon.xml bevat nog de tijdelijke naam GITHUB-GEBRUIKER.")
        zip_path, count = build_zip(folder, addon_id, version)
        size_kb = zip_path.stat().st_size / 1024
        print(f"  {addon_id} {version}: {count} bestanden, {size_kb:,.0f} kB")
        if addon_id == REPO_ADDON_ID:
            for old in DOCS.glob(f"{REPO_ADDON_ID}-*.zip"):
                old.unlink()
            repo_zip_name = zip_path.name
            shutil.copyfile(zip_path, DOCS / repo_zip_name)

    md5 = write_addons_xml(addons)
    print(f"  addons.xml: {len(addons)} addon(s), md5 {md5}")
    if repo_zip_name:
        write_index(repo_zip_name)
        print(f"  index.html verwijst naar {repo_zip_name}")
    else:
        print(f"LET OP: {REPO_ADDON_ID} niet gevonden, index.html niet bijgewerkt.")
    print("Klaar. Commit en push docs/ om te publiceren.")


if __name__ == "__main__":
    main()
