# Projectcontext

Eigen Kodi-setup van Marco: een eigen repository-addon (`repository.spaan`) op GitHub
Pages en een skin-mod op basis van Arctic Fuse 3 met TMDbHelper. Doel: Netflix-niveau
uiterlijk, met één bron-URL te installeren op elk apparaat.

## Over de gebruiker

- Microsoft 365/Intune-consultant. Kent PowerShell, Git en scripting.
- Kent geen Python en geen Kodi-internals: leg Kodi-specifieke keuzes kort uit en
  houd Python-scripts eenvoudig, met alleen de standaardbibliotheek waar dat kan.
- Voertaal is Nederlands. Gebruik in documenten geen gedachtestreepjes.

## Vastgelegde keuzes (fase 0)

- Doelapparaat: Nvidia Shield / Android TV, Kodi uit de Play Store.
- Skin-basis: Arctic Fuse 3 (branch `piers`, vereist Kodi 22, `xbmc.gui` 5.18.0).
  Arctic Fuse 2 is door de maker stopgezet en gearchiveerd op 9 januari 2026.
- Afhankelijkheden van de skin: `script.skinvariables` >= 2.2.18,
  `script.texturemaker` >= 0.2.9, `plugin.video.themoviedb.helper` >= 6.21.5,
  plus `resource.images.arctic.splash`, `resource.images.arctic.weather`,
  `resource.images.weathericons.white`, `resource.images.studios.coloured` en
  `resource.font.robotocjksc`. De uitgebrachte 3.4.22 eist `script.skinvariables`
  >= 2.2.15. Controleer deze lijst opnieuw bij elke upstream-merge.
- Afhankelijkheden hosten we niet zelf: `repository.spaan` verwijst door naar de
  repository van jurialmunkey.
- De bijgeleverde `repository.thecrew` was alleen een sjabloon voor de opbouw. Er
  worden geen bronnen van derden uit overgenomen.
- Licentie van de skin is CC BY-NC-SA 4.0: naamsvermelding behouden, niet-commercieel,
  mod onder dezelfde licentie.

## Keuzes voor de skin (fase 2)

- Naam "Familie Krispijn", id `skin.arctic.fuse.3.krispijn`, eigen versienummering
  vanaf 1.0.0 in `skin-mod/mod.json`.
- Thema Bioscooprood: accent `ffe53935`, achtergrond `0b0e15`.
- Het gezin gebruikt Kodi alleen voor video-add-ons. Geen bibliotheek, muziek,
  live-tv of weer. Standaard-homescherm: één rij met video-add-ons.
- Geen "Wie kijkt er?"-scherm. Wel: af en toe (1 op 5) een gezichtje over de
  laad-spinner, plus gezichtje en laadtekst op het opstartscherm.
- Gezichtjes zijn tijdelijke tekeningen. Echte gezinsfoto's komen nooit in de repo:
  ze staan lokaal in `fotos/` (gitignored) en op het apparaat, gekozen via
  `Skin.SetPath(Krispijn.FacesPath)`.
- De eerste-start-wizard van upstream is uitgeschakeld; thema en homescherm worden
  direct gezet in `skinvariables-startup.json`.
- Ratings via MDBList, Trakt wordt nog aangemaakt.
- Er wordt geen eigen versie of aanpassing van The Crew of andere scraper-add-ons
  gebouwd of gehost, en er worden geen TMDbHelper-players voor zulke add-ons gemaakt.

## Opbouw van de mod

- `upstream/skin.arctic.fuse.3/` is een onaangeroerde git subtree. Nooit bewerken.
- Upstream staat vast op de uitgebrachte commit `254f7fadd6` (3.4.22). De kop van
  branch `piers` eiste op 14-11-2026 `script.skinvariables` 2.2.18 terwijl alleen
  2.2.16 was uitgebracht. Draai daarom na elke upstream-update
  `python tools/check_deps.py`.
- `tools/make_skin.py` bouwt de mod naar `build/` (gitignored): kopie van upstream,
  id vervangen, `skin-mod/overlay/` eroverheen, daarna gerichte tekstvervangingen
  die elk hun aantal treffers controleren.
- Wijzigingen aan bestaande skin-bestanden horen als stap in `patch_skin()`, niet als
  volledig bestand in de overlay.
- Er is op de ontwikkel-pc geen Kodi geïnstalleerd. Skin-wijzigingen zijn dus
  alleen op geldige XML gecontroleerd en moeten op de Shield getest worden.

## Werkafspraken

- Elke publieke wijziging vraagt een versieverhoging (skin: `skin-mod/mod.json`,
  repository: `repository.spaan/addon.xml`), daarna `python tools/build.py`, daarna
  commit en push.
- `docs/` is build-uitvoer. Niet met de hand bewerken, behalve `docs/SETUP.md`.
- De mapnaam van een addon moet gelijk zijn aan zijn addon-id.
- `.gitattributes` zet regeleinde-conversie uit. Laat dat zo: de md5 van
  `addons.xml` moet exact overeenkomen met wat GitHub Pages serveert.
- De skin-zip is ongeveer 58 MB en elke versie blijft in de git-historie staan. Bundel
  wijzigingen dus in een release in plaats van elke kleine aanpassing te pushen.
- Vraag eerst om akkoord voor iets dat publiek zichtbaar wordt of niet terug te
  draaien is.

## Fases

0. Inventarisatie (klaar)
1. Repository en hosting
2. Skin-mod: upstream binnenhalen, eigen id, kleurthema, logo, opstartscherm (gebouwd, nog niet in Kodi getest)
3. `docs/SETUP.md` (geschreven): TMDbHelper, ratings via OMDb of MDBList, Trakt, homescherm-rijen,
   back-up van skin-instellingen
4. Testchecklist en bekende beperkingen
