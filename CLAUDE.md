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
  `resource.font.robotocjksc`. Controleer deze lijst opnieuw bij elke upstream-merge.
- Afhankelijkheden hosten we niet zelf: `repository.spaan` verwijst door naar de
  repository van jurialmunkey.
- De bijgeleverde `repository.thecrew` was alleen een sjabloon voor de opbouw. Er
  worden geen bronnen van derden uit overgenomen.
- Licentie van de skin is CC BY-NC-SA 4.0: naamsvermelding behouden, niet-commercieel,
  mod onder dezelfde licentie.

## Werkafspraken

- Elke publieke wijziging aan een addon vraagt een versieverhoging in zijn
  `addon.xml`, daarna `python tools/build.py`, daarna commit en push.
- `docs/` is build-uitvoer. Niet met de hand bewerken, behalve `docs/SETUP.md`.
- De mapnaam van een addon moet gelijk zijn aan zijn addon-id.
- De skin-mod heeft een eigen id (`skin.arctic.fuse.3.spaan`), zodat hij naast het
  origineel kan bestaan en upstream-updates hem niet overschrijven.
- `.gitattributes` zet regeleinde-conversie uit. Laat dat zo: de md5 van
  `addons.xml` moet exact overeenkomen met wat GitHub Pages serveert.
- Vraag eerst om akkoord voor iets dat publiek zichtbaar wordt of niet terug te
  draaien is.

## Fases

0. Inventarisatie (klaar)
1. Repository en hosting
2. Skin-mod: upstream binnenhalen, eigen id, kleurthema, logo, opstartscherm
3. `docs/SETUP.md`: TMDbHelper, ratings via OMDb of MDBList, Trakt, homescherm-rijen,
   back-up van skin-instellingen
4. Testchecklist en bekende beperkingen
