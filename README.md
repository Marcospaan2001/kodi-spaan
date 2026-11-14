# kodi-spaan

Persoonlijke Kodi-setup: een eigen repository (`repository.spaan`) en een skin-mod op
basis van Arctic Fuse 3 (Familie Krispijn), te installeren op elk apparaat via één bron-URL.

## Installeren in Kodi

Bron-URL: `https://marcospaan2001.github.io/kodi-spaan/`

1. Instellingen > Systeem > Add-ons > zet **Onbekende bronnen** aan.
2. Instellingen > Bestandsbeheer > **Bron toevoegen** > vul de bron-URL in en noem
   hem `spaan`.
3. Add-ons > **Installeren vanuit zip-bestand** > `spaan` >
   `repository.spaan-x.y.z.zip`.
4. Add-ons > **Installeren vanuit repository** > Spaan Repository.

## Mappen

| Map | Inhoud |
|---|---|
| `repository.spaan/` | De repository-addon: vertelt Kodi waar de addons staan |
| `upstream/skin.arctic.fuse.3/` | Onaangeroerde kopie van Arctic Fuse 3 (git subtree). Hier nooit in bewerken |
| `skin-mod/mod.json` | Naam, versie, kleuren en laadteksten van de mod |
| `skin-mod/overlay/` | Eigen bestanden die over de skin heen gelegd worden: logo, gezichtjes, achtergrond, eigen includes, standaard-homescherm |
| `tools/make_skin.py` | Maakt de mod: upstream + ander id + overlay + gerichte wijzigingen, naar `build/` |
| `tools/build.py` | Bouwt alles: skin-mod, zips, `addons.xml` en `addons.xml.md5` naar `docs/` |
| `tools/make_art.py` | Genereert iconen, fanart, logo, achtergrond en getekende gezichtjes |
| `tools/check_deps.py` | Controleert of Kodi alle afhankelijkheden van de skin kan vinden |
| `tools/make_faces.py` | Maakt ronde gezichtjes van eigen foto's in `fotos/` (blijft lokaal) |
| `docs/` | Uitvoer van de build plus `SETUP.md`, gepubliceerd via GitHub Pages |

`build/` en `fotos/` staan in `.gitignore`. Bewerk nooit iets met de hand in
`docs/zips/` of `build/`; dat wordt bij elke build overschreven.

De handleiding voor het inrichten van een apparaat staat in
[docs/SETUP.md](docs/SETUP.md). De testchecklist, bekende beperkingen en wat je bij
een Kodi-update moet controleren staan in [docs/TESTEN.md](docs/TESTEN.md).

## De skin aanpassen

- **Naam, kleuren, laadteksten:** `skin-mod/mod.json`.
- **Plaatjes:** kleuren aanpassen in `tools/make_art.py` en opnieuw draaien, of een
  bestand in `skin-mod/overlay/` vervangen.
- **Een bestaand skin-bestand wijzigen:** voeg een stap toe in `patch_skin()` in
  `tools/make_skin.py`. Niet het bestand in `upstream/` bewerken en niet het hele
  bestand naar de overlay kopiëren, want dan mis je latere upstream-wijzigingen.
- **Iets nieuws toevoegen:** zet het in `skin-mod/overlay/1080i/Includes_Krispijn.xml`.

## Arctic Fuse 3 bijwerken (upstream)

De skin staat als git subtree in `upstream/`, vastgezet op de laatst **uitgebrachte**
versie. Neem niet blind de nieuwste code van de branch `piers`: de maker verhoogt daar
soms al de vereiste versie van een afhankelijkheid voordat die is uitgebracht, en dan
weigert Kodi de skin te installeren.

Bijwerken:

```
git fetch upstream piers
git log --oneline -15 FETCH_HEAD -- addon.xml
```

Kies de commit van de laatste "version bump" die ook in de repository van
jurialmunkey is uitgebracht en haal die binnen:

```
git subtree merge --prefix=upstream/skin.arctic.fuse.3 <commit> --squash
python tools/build.py
python tools/check_deps.py
```

Omdat er nooit in `upstream/` bewerkt wordt, geeft de merge geen conflicten. Daarna:

- **`build.py`** controleert elke wijziging van de mod. Heeft upstream een regel
  veranderd die de mod aanpast, dan stopt `make_skin.py` met de melding welk bestand
  en welke tekst niet meer gevonden wordt. Pas dan die ene stap aan.
- **`check_deps.py`** controleert of alle vereiste add-ons in de vereiste versie te
  vinden zijn. Meldt het een fout, kies dan een oudere upstream-commit.
- Verhoog `version` in `skin-mod/mod.json` en test in Kodi voor je pusht.

De remote is eenmalig toegevoegd met:

```
git remote add upstream https://github.com/jurialmunkey/skin.arctic.fuse.3.git
```

## Een wijziging publiceren

1. Pas de addon aan.
2. Verhoog de versie: voor de skin in `skin-mod/mod.json`, voor de repository in
   `repository.spaan/addon.xml`. Zonder hogere versie ziet Kodi geen update.
3. Bouw en publiceer:

```
python tools/build.py
git add -A
git commit -m "Beschrijving van de wijziging"
git push
```

GitHub Pages heeft daarna een paar minuten nodig. Kodi controleert zelf periodiek op
updates; forceren kan via Add-ons > Spaan Repository > Controleren op updates.

## Hoe een Kodi-repository werkt

- `addons.xml` is de catalogus: alle `addon.xml`-bestanden achter elkaar.
- `addons.xml.md5` is de checksum daarvan. Kodi downloadt de catalogus alleen opnieuw
  als de checksum verandert.
- Per addon staat er een map `zips/<id>/` met `<id>-<versie>.zip` en losse
  `icon.png` en `fanart.jpg` voor de weergave in de lijst.
- De repository-addon verwijst naast deze repo ook naar de repository van
  jurialmunkey. Daar komen TMDbHelper, script.skinvariables en script.texturemaker
  vandaan, zodat Kodi de afhankelijkheden van de skin zelf kan ophalen.

## Licentie en herkomst

De skin-mod is gebaseerd op
[Arctic Fuse 3](https://github.com/jurialmunkey/skin.arctic.fuse.3) van jurialmunkey,
gelicentieerd onder CC BY-NC-SA 4.0. De mod valt daarom onder dezelfde licentie:
naamsvermelding, niet-commercieel, gelijk delen. De scripts in `tools/` en
`repository.spaan/` zijn eigen werk.
