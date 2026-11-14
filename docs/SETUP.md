# Setup: Familie Krispijn op een nieuw apparaat

Controleer je Kodi-versie bij **Instellingen > Systeeminfo**.

| Kodi-versie | Kies deze skin | Basis |
|---|---|---|
| Kodi 21 (Omega), ook Kodi 21.2 op de Shield | **Familie Krispijn (Kodi 21)** | Arctic Fuse 2 |
| Kodi 22 (Piers) | **Familie Krispijn** | Arctic Fuse 3 |

Op de Shield is de repository-installatie bevestigd. De skin-installatie en
weergave moeten nog op het apparaat worden getest.

De namen van menu's kunnen per versie van TMDbHelper iets afwijken. Waar dat speelt
staat de Engelse naam erbij.

## 1. Repository en skin installeren

1. **Onbekende bronnen aanzetten:** Instellingen > Systeem > Add-ons > Onbekende
   bronnen.
2. **Bron toevoegen:** Instellingen > Bestandsbeheer > Bron toevoegen > kies `<Geen>`
   en typ `https://marcospaan2001.github.io/kodi-spaan/`. Noem de bron `spaan`.
3. **Repository installeren:** Add-ons > Installeren vanuit zip-bestand > `spaan` >
   `repository.spaan-x.y.z.zip`.
4. **Skin installeren:** Add-ons > Installeren vanuit repository > Spaan Repository >
   Uiterlijk > Skin > kies de skin uit de tabel > Installeren. Kodi haalt
   TMDbHelper, Skin Variables en de overige afhankelijkheden zelf op. De
   download is circa 63 MiB voor Kodi 21 en 57 MiB voor Kodi 22.
5. Kies **Ja** op de vraag of je de skin wilt behouden.

Bij de eerste start bouwt de skin zijn menu's op. Je ziet dan het opstartscherm met
het logo, een gezichtje en een laadtekst. Dat duurt de eerste keer het langst.

## 2. Wat je standaard krijgt

- Thema Bioscooprood: donkere achtergrond, rode selectie, wit op rood.
- Homescherm met één rij: al je geïnstalleerde **video-add-ons**.
- Menu met Video add-ons, Add-ons en Fotomap gezichtjes. Live-tv staat uit.
- Opstartscherm met "FAMILIE KRISPIJN", een wisselend gezichtje en een willekeurige
  laadtekst.
- Tijdens het laden duikt af en toe (ongeveer 1 op de 5 keer) een wiebelend
  gezichtje op over het laad-rondje.
- TMDbHelper kijkt op de achtergrond mee naar de film of serie waar je op staat en
  zoekt daar de gegevens en ratings bij. Dat werkt in lijsten van elke video-add-on,
  zolang titel en jaar herkend worden.

De keuzewizard van beide skins wordt bij de eerste start overgeslagen, omdat die
het thema en het homescherm zou overschrijven. Hij blijft bereikbaar via de
skin-instellingen.

## 3. Ratings: IMDb, Rotten Tomatoes en Metacritic

Ratings komen via TMDbHelper van MDBList. Je hebt daarvoor een eigen gratis sleutel
nodig. Deel die sleutel niet en zet hem nooit in de repository.

1. Maak een account op `mdblist.com` en kopieer je API-sleutel bij je
   accountinstellingen (API Access).
2. In Kodi: Add-ons > Mijn add-ons > Video-add-ons > TheMovieDb Helper >
   Configureren.
3. Ga naar **Services** > **MDbList** > **Open settings**. Kodi installeert zo nodig
   eerst de MDbList-module. Vul daarna je sleutel in.
4. Herstart Kodi.

Wil je liever of daarnaast OMDb gebruiken: vraag een gratis sleutel aan op
`omdbapi.com` en vul die in bij **Services** > **API keys** > **OMDb key**. De gratis
OMDb-sleutel is beperkt tot 1000 opvragingen per dag.

**Controleren:** open een video-add-on, ga op een bekende film staan en wacht een
paar seconden. De scores verschijnen bij de filminformatie. Zie je niets:

- Controleer of de skin-instelling voor de TMDbHelper-service aan staat
  (Skin-instellingen, zoek op "TMDbHelper"). De mod zet die standaard aan.
- Ratings in kleur aan of uit zet je in de skin-instellingen onder Ratings.
- Niet elke add-on geeft een herkenbare titel met jaartal door. Bij rare titels
  vindt TMDbHelper geen match en blijft het leeg.

## 4. Trakt koppelen

Trakt houdt bij wat je gekeken hebt en waar je gebleven was, over apparaten heen.

1. Maak een gratis account op `trakt.tv`.
2. In TheMovieDb Helper > Configureren > **Sync** > **Providers**: kies Trakt en
   volg de aanwijzing. Je krijgt een code die je op `trakt.tv/activate` invult.
3. Zet **Sync watched and resume** aan als je bekeken-vinkjes en hervatpunten in de
   lijsten wilt zien.

Trakt registreert alleen wat er daadwerkelijk aan Trakt gemeld wordt. TMDbHelper
doet dat voor wat je via TMDbHelper start. Speel je rechtstreeks vanuit een
video-add-on af, dan hangt het van die add-on af of hij zelf een Trakt-koppeling
heeft. Een alternatief is de officiële Trakt-add-on uit de Kodi-repository, die alles
meldt wat Kodi afspeelt en herkent.

## 5. Homescherm-rijen aanpassen

De standaard is bewust kaal: één rij video-add-ons. Rijen toevoegen:

1. Ga op het homescherm naar het menu en open de skin-instellingen, of houd de
   menuknop ingedrukt op een rij voor het contextmenu.
2. Kies het bewerken van de **Home widgets**. Bij Fuse 2 hoort de rij bij de knop **Video add-ons** in het zijmenu.
3. Voeg een rij toe en kies een bron. Voorbeelden via TheMovieDb Helper:
   - Trending films en series deze week
   - Populair en Best beoordeeld
   - Trakt > Verder kijken (na het koppelen van Trakt)
   - Eigen lijsten van Trakt of MDBList, bijvoorbeeld een IMDb-toplijst
4. Kies per rij een weergave (posters, liggende kaarten, groot).

Let op: titels uit TMDbHelper-rijen spelen alleen af als TMDbHelper weet waarmee.
Dat stel je in bij TheMovieDb Helper > Configureren > **Players**. Zonder player zijn
zulke rijen alleen om te bladeren.

## 6. Eigen gezichtjes of gezinsfoto's

De skin bevat zes getekende gezichtjes. Die vervang je door eigen foto's zonder dat
er iets op internet komt:

1. Op de pc: zet foto's in de map `fotos/` van het project en draai
   `python tools/make_faces.py`. In `fotos/klaar/` staan daarna ronde uitsnedes.
   De map `fotos/` wordt door git genegeerd.
2. Kopieer `fotos/klaar/` naar een USB-stick of een netwerkmap en maak hem
   bereikbaar voor de Shield.
3. In Kodi: homescherm-menu > **Fotomap gezichtjes** > blader naar de map.

Vanaf dat moment gebruikt de skin jouw map voor het opstartscherm en de
laad-animatie. Terug naar de getekende gezichtjes: kies de optie opnieuw en maak het
pad leeg.

## 7. Instellingen exporteren en back-up

Alles wat je in de skin instelt staat in de gebruikersmap van Kodi:

| Wat | Map onder `userdata/addon_data/` |
|---|---|
| Skin-instellingen, kleuren, fotomap | `skin.arctic.fuse.2.krispijn/` voor Kodi 21 of `skin.arctic.fuse.3.krispijn/` voor Kodi 22 |
| Homescherm-rijen en menu's | `script.skinvariables/` |
| TMDbHelper, sleutels en Trakt-koppeling | `plugin.video.themoviedb.helper/` en de `script.module.tmdbhelper.sync.*`-mappen |

De eenvoudigste back-up is de add-on **Backup** uit de officiële Kodi-repository
(Programma-add-ons). Kies daarin minimaal "Add-on data" en schrijf weg naar een
USB-stick of netwerkmap. Terugzetten op een nieuw apparaat: eerst stap 1 van deze
handleiding, dan Backup > Herstellen.

De back-up bevat je API-sleutels en Trakt-token. Bewaar hem dus niet op een openbare
plek.

## 8. Overstappen naar Kodi 22

1. Maak een back-up volgens stap 7.
2. Werk Kodi bij zodra de stabiele Kodi 22 voor je Shield in de Play Store staat.
3. Open Spaan Repository en installeer **Familie Krispijn** volgens stap 1.
4. Selecteer de nieuwe skin. De twee skins hebben verschillende add-on-id's.
   Kies je fotomap opnieuw en stel eigen skin-instellingen en widgets opnieuw in.
5. Controleer je video-add-ons, ratings en Trakt-koppeling op het apparaat.

## 9. Updates

- **Skin en repository:** Kodi controleert zelf periodiek. Forceren kan via Add-ons >
  Mijn add-ons > Add-on-repository > Spaan Repository > Controleren op updates.
- **Na een skin-update** bouwt de skin zijn menu's opnieuw op. Eigen rijen en
  instellingen blijven staan.
