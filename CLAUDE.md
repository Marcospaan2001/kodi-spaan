# Projectcontext

Eigen Kodi-setup van Marco: een eigen repository-addon (`repository.spaan`) op GitHub
Pages en een skin-mod op basis van Arctic Fuse 2 voor Kodi 21 en Arctic Fuse 3 voor Kodi 22 met TMDbHelper. Doel: Netflix-niveau
uiterlijk, met één bron-URL te installeren op elk apparaat.

## Over de gebruiker

- Microsoft 365/Intune-consultant. Kent PowerShell, Git en scripting.
- Kent geen Python en geen Kodi-internals: leg Kodi-specifieke keuzes kort uit en
  houd Python-scripts eenvoudig, met alleen de standaardbibliotheek waar dat kan.
- Voertaal is Nederlands. Gebruik in documenten geen gedachtestreepjes.

## Vastgelegde keuzes (fase 0)

- Doelapparaat: Nvidia Shield / Android TV, Kodi uit de Play Store.
- Kodi 21 (Omega) gebruikt Arctic Fuse 2 2.12.12, commit
  `e138a25fe11f24254c6456711d37ac9d1053f541`, met `xbmc.gui` 5.17.0.
  Upstream is gearchiveerd. Gebruik deze variant voor de Shield met Kodi 21.2.
- Kodi 22 (Piers) gebruikt Arctic Fuse 3, met `xbmc.gui` 5.18.0.
- Fuse 2 vereist `script.skinvariables` >= 2.1.28, `script.texturemaker` >= 0.2.9
  en `plugin.video.themoviedb.helper` >= 6.12.1, plus `resource.images.weathericons.white`,
  `resource.images.studios.coloured` en `resource.font.robotocjksc`.
- Afhankelijkheden van Fuse 3: `script.skinvariables` >= 2.2.18,
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
  vanaf 1.0.0 in `skin-mod/fuse3.json`. Kodi 21 gebruikt de naam
  "Familie Krispijn (Kodi 21)", id `skin.arctic.fuse.2.krispijn` en eigen versie
  1.0.0 in `skin-mod/fuse2.json`. Het thema staat in `skin-mod/mod.json`.
- Thema Bioscooprood: accent `ffe53935`, achtergrond `0b0e15`.
- Het gezin gebruikt Kodi alleen voor video-add-ons. Geen bibliotheek, muziek,
  live-tv of weer. Standaard-homescherm: één rij met video-add-ons.
- Geen "Wie kijkt er?"-scherm. Wel: af en toe (1 op 5) een gezichtje over de
  laad-spinner, plus gezichtje en laadtekst op het opstartscherm.
- Gezichtjes zijn tijdelijke tekeningen. Echte gezinsfoto's komen nooit in de repo:
  ze staan lokaal in `fotos/` (gitignored) en op het apparaat, gekozen via
  `Skin.SetPath(Krispijn.FacesPath)`.
- De eerste-start-wizard van upstream is uitgeschakeld; thema en homescherm worden
  direct gezet in `skinvariables-startup.json`. Bij Fuse 2 zet hetzelfde bestand
  `Wizard.FirstRun` en komt de video-addonrij uit het zijmenu.
- Ratings via MDBList, Trakt wordt nog aangemaakt.
- Er wordt geen eigen versie of aanpassing van The Crew of andere scraper-add-ons
  gebouwd of gehost, en er worden geen TMDbHelper-players voor zulke add-ons gemaakt.

## Opbouw van de mod

- `upstream/skin.arctic.fuse.2/` en `upstream/skin.arctic.fuse.3/` zijn onaangeroerde git subtrees. Nooit bewerken.
- Fuse 3 staat vast op de uitgebrachte commit `254f7fadd6` (3.4.22). De kop van
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

- Elke publieke wijziging vraagt een versieverhoging (skin: `skin-mod/fuse2.json` of `skin-mod/fuse3.json`,
  repository: `repository.spaan/addon.xml`), daarna `python tools/build.py`, daarna
  commit en push.
- `docs/` is build-uitvoer. Niet met de hand bewerken, behalve `docs/SETUP.md` en `docs/TESTEN.md`.
- De mapnaam van een addon moet gelijk zijn aan zijn addon-id.
- `.gitattributes` zet regeleinde-conversie uit. Laat dat zo: de md5 van
  `addons.xml` moet exact overeenkomen met wat GitHub Pages serveert.
- De skin-zips zijn circa 63 MiB (Fuse 2) en 57 MiB (Fuse 3). Elke versie blijft in de git-historie staan. Bundel
  wijzigingen dus in een release in plaats van elke kleine aanpassing te pushen.
- Vraag eerst om akkoord voor iets dat publiek zichtbaar wordt of niet terug te
  draaien is.

## Fases

0. Inventarisatie (klaar)
1. Repository en hosting (klaar, live op GitHub Pages)
2. Skin-mod Familie Krispijn 1.0.0 voor Kodi 21 en 22. Beide builds zijn gemaakt.
   Op de Shield is alleen de installatie van Spaan Repository bevestigd.
   Fuse 3 is onzichtbaar op Kodi 21.2. De installatie en werking van Fuse 2
   moeten nog op de Shield worden getest.
3. `docs/SETUP.md` (klaar)
4. `docs/TESTEN.md`: testchecklist, bekende beperkingen, Kodi-updates (klaar)

Openstaand: eigen gezinsfoto's (levert Marco zelf, lokaal), een knop voor
`Krispijn.DisableFaces` in de skin-instellingen, en de checklist in TESTEN.md is nog
niet volledig doorlopen.

## Kodi 21: optimalisatie 1.0.1

De update schakelt dynamische blur eenmalig uit en kiest de Simple-achtergrondstijl.
De achtergrondafbeelding, widgets en sleutels blijven behouden.
Daarna gekozen achtergrondinstellingen worden niet opnieuw overschreven.

Onder Skin-instellingen > Menus staan schakelaars voor de ratings-service en
gezichtjes. Herstart Kodi na het wijzigen van de service. De keuze blijft bewaard.
Ratings blijven standaard aan. Kodi 22 en de familieafbeeldingen zijn ongewijzigd.

Kleurtextuurgeneratie blijft intact vanwege themawisselingen en profielen.
De prestatiewinst moet nog op de Shield worden gemeten.

## Extra installatiepakketten, repository 1.0.2

Op verzoek worden het originele The Crew-repositorypakket 0.3.8 en
OpenSubtitles.com 1.0.90 uit de officiele Kodi 21-repository aangeboden.
Dit vervangt de eerdere afspraak om geen The Crew-pakket aan te bieden.
Externe code wordt niet aangepast. De bouw controleert SHA256, zip-integriteit,
addon-id en versie. De pakketten staan onder docs/downloads.

Installeer via Add-ons > Installeren vanuit zip-bestand > spaan.
Kies The Crew Repository of OpenSubtitles.com, eventueel via downloads.
Installeer The Crew daarna vanuit zijn eigen repository.
OpenSubtitles.com installeert rechtstreeks en ontvangt updates via Kodi.

Vul je eigen OpenSubtitles.com-account in bij de add-oninstellingen.
Kies bij Instellingen > Speler > Taal Nederlands als ondertiteltaal en
OpenSubtitles.com als standaard ondertitelservice voor films en series.

Beide skins blijven ongewijzigd. Dit verhelpt geen Kodi-opstartcrash.
Accountgegevens en familieportretten blijven buiten de openbare repository.
