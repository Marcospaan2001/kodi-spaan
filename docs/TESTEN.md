# Testchecklist en bekende beperkingen

Loop deze lijst door na een nieuwe versie van de skin, na een upstream-update en na
een update van Kodi. Noteer bij een afwijking de versie van de skin, van Kodi en wat
je precies zag.

## 1. Installatie vanaf nul

Doe dit op een schoon apparaat, of wis eerst de app-gegevens van Kodi
(Android-instellingen > Apps > Kodi > Opslag > Gegevens wissen).

- [ ] Kodi-versie is 22 of hoger (Instellingen > Systeeminfo).
- [ ] Bron `https://marcospaan2001.github.io/kodi-spaan/` is toe te voegen en toont
      `repository.spaan-x.y.z.zip`.
- [ ] Repository installeert zonder foutmelding.
- [ ] Skin Familie Krispijn staat onder Spaan Repository > Uiterlijk > Skin.
- [ ] Installatie haalt alle afhankelijkheden zelf op, zonder "afhankelijkheid niet
      voldaan".
- [ ] Eerste start: opstartscherm met logo, gezichtje en laadtekst, daarna het
      homescherm. Geen keuze-wizard.
- [ ] Thema is rood op donker, met witte tekst op de selectie.
- [ ] Homescherm toont de rij Video add-ons. Zonder geïnstalleerde video-add-ons is
      die rij leeg; installeer er dan eerst een.
- [ ] Menu bevat Video add-ons, Add-ons en Fotomap gezichtjes. Geen live-tv.

## 2. Update via de repository

- [ ] Verhoog `version` in `skin-mod/mod.json`, bouw, draai `check_deps.py`, push.
- [ ] Na een paar minuten: Spaan Repository > Controleren op updates toont de nieuwe
      versie.
- [ ] Na de update start de skin zonder foutmelding en bouwt hij zijn menu's opnieuw
      op.
- [ ] Eigen homescherm-rijen, kleurkeuze en fotomap zijn behouden.
- [ ] Het versienummer in de skin-instellingen is het nieuwe nummer.

## 3. Prestaties

Meet met een stopwatch en vergelijk met de vorige versie.

- [ ] Koude start van Kodi tot bruikbaar homescherm. Richtwaarde Shield: onder
      15 seconden na de eerste keer.
- [ ] Scrollen door de rij op het homescherm hapert niet.
- [ ] Openen van een video-add-on en bladeren door een lijst van 50 of meer titels
      hapert niet.
- [ ] Het gezichtje over de laad-spinner verschijnt en verdwijnt vloeiend, zonder
      dat het laden merkbaar langer duurt.
- [ ] Na een uur gebruik is Kodi niet trager geworden.

Hapert het op zwakke hardware (Fire TV Stick, oudere tv's), probeer dan in deze
volgorde:

1. Skin-instellingen: zet blur en vervaging van achtergronden uit.
2. Skin-instellingen: zet de TMDbHelper-service uit. Je verliest dan de ratings bij
   het bladeren, maar dit scheelt het meest.
3. Zet de gezichtjes uit met de skin-instelling `Krispijn.DisableFaces`
   (zie beperkingen).
4. Minder rijen op het homescherm.

## 4. Ratings

- [ ] MDBList-sleutel is ingevuld (SETUP.md, stap 3) en Kodi is daarna herstart.
- [ ] Bij een bekende film in een add-on-lijst verschijnen binnen enkele seconden
      IMDb, Rotten Tomatoes en Metacritic.
- [ ] Het infoscherm van die film toont dezelfde scores.
- [ ] Bij een serie werken de scores ook.
- [ ] Een titel zonder herkenbaar jaartal geeft geen verkeerde film, hooguit niets.

## 5. Eigen onderdelen van de mod

- [ ] Opstartscherm: het gezichtje wisselt en de laadtekst is niet elke keer
      dezelfde.
- [ ] Laad-spinner: bij ongeveer 1 op de 5 laadmomenten duikt een gezichtje op.
- [ ] Fotomap gezichtjes: na het kiezen van een eigen map verschijnen die foto's op
      het opstartscherm en bij het laden.
- [ ] Het logo is overal het K-logo, nergens meer het Kodi-logo van de skin.

## Bekende beperkingen

- **Alleen Kodi 22 of hoger.** Arctic Fuse 3 werkt niet op Kodi 21.
- **Geen Nederlandse vertaling van de skin.** Arctic Fuse 3 heeft geen Nederlands
  taalbestand, dus de skin-instellingen zijn Engels. De rest van Kodi volgt je
  taalinstelling.
- **"Af en toe" is op tijd gebaseerd.** Een skin kan niet dobbelen. Het gezichtje
  verschijnt als de klok op een seconde staat die op 0 of 5 eindigt. Bij lang laden
  duikt het dus elke vijf seconden even op.
- **Gezichtjes uitzetten heeft nog geen knop.** De instelling
  `Krispijn.DisableFaces` bestaat, maar staat niet in het instellingenmenu. Een knop
  toevoegen kan in een volgende versie.
- **Eigen foto's moeten rond zijn uitgesneden.** Gebruik `tools/make_faces.py`.
  Gewone rechthoekige foto's worden als rechthoek getoond.
- **De fotomap staat per apparaat.** Op elk apparaat kopieer je de map en kies je
  hem opnieuw.
- **Ratings hangen af van de add-on.** TMDbHelper herkent een titel aan naam en
  jaar of een IMDb-id. Geeft een add-on dat niet door, dan blijven de scores leeg.
- **TMDbHelper-rijen spelen niet vanzelf af.** Rijen zoals Trending zijn zonder
  ingestelde player alleen om te bladeren.
- **De keuze-wizard van Arctic Fuse 3 is overgeslagen.** Kies je daar later toch een
  preset of kleurenschema, dan overschrijft die het homescherm en het rode thema.
- **Grote download.** De skin is ongeveer 58 MB en GitHub waarschuwt bij bestanden
  boven 50 MB. De harde grens is 100 MB. Groeit de skin daar richting, dan moet de
  zip naar GitHub Releases verhuizen.
- **De repository groeit.** Elke gepubliceerde skin-versie blijft in de
  git-historie. GitHub adviseert repositories onder 1 GB te houden, dus bundel
  wijzigingen.
- **Afhankelijk van jurialmunkey.** TMDbHelper, Skin Variables en Texture Maker
  komen uit zijn repository. Verdwijnt of verhuist die, dan installeert de skin niet
  meer op nieuwe apparaten tot `repository.spaan/addon.xml` is aangepast.

## Controleren bij een Kodi-update

Kleine updates (22.0 naar 22.1) geven zelden problemen. Bij een nieuwe hoofdversie
(Kodi 23):

1. **Wacht met updaten** tot Arctic Fuse 3 de nieuwe versie ondersteunt. Kijk in
   `addon.xml` van upstream naar de regel `xbmc.gui`: die versie moet passen bij de
   nieuwe Kodi. Een skin met een te oude `xbmc.gui` wordt door Kodi uitgeschakeld en
   je valt terug op de standaardskin.
2. Zet automatische updates van Kodi in de Play Store uit, zodat de tv niet
   ongemerkt naar een versie gaat waar de skin nog niet op werkt.
3. Werk upstream bij volgens de README, draai `build.py` en `check_deps.py`.
4. Controleer in `repository.spaan/addon.xml` of jurialmunkey een nieuwe map voor de
   nieuwe Kodi-versie heeft (nu `omega` en `piers`). Voeg die zo nodig toe en
   verhoog de versie van de repository.
5. Loop daarna deze checklist door, te beginnen bij installatie vanaf nul.
6. Maak vooraf een back-up (SETUP.md, stap 7).

## Als de skin niet meer start

- Kodi valt bij een kapotte skin meestal zelf terug op de standaardskin Estuary.
- Gebeurt dat niet: wis de app-gegevens van Kodi, of verwijder op het apparaat de
  map `addons/skin.arctic.fuse.3.krispijn`.
- Het logboek staat in `kodi.log` in de Kodi-gebruikersmap. Zoek op `ERROR` en op
  `skin.arctic.fuse.3.krispijn`.
