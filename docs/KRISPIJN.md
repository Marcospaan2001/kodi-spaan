# Krispijn Video en Familie Krispijn op Kodi 21

Deze release bevat Krispijn Video 1.0.0 op basis van POV 6.11.03 en de Kodi 21-skin
Familie Krispijn 1.0.2. Repository Spaan wordt 1.0.4. De Kodi 22-skin blijft 1.0.0.

## Eerste inrichting

1. Voeg alleen https://marcospaan2001.github.io/kodi-spaan/ als bron toe.
2. Installeer Spaan Repository en daarna Krispijn Video uit die repository.
3. Open Krispijn Video en kies Real-Debrid koppelen. Bevestig de code op de
   getoonde officiële Real-Debrid-pagina. De aanmelding gebeurt op jouw apparaat.
4. OpenSubtitles is optioneel, via Instellen > OpenSubtitles instellen.
   Na installatie kies je dezelfde optie om het eigen OpenSubtitles.com-account
   in te vullen. Het account en de dienst kunnen eigen downloadlimieten hebben.
5. Installeer of update Familie Krispijn (Kodi 21). De skin verzorgt de vormgeving.

Geen verplichte Trakt-, IMDb-, TMDb- of MDBList-registratie. Scores komen uit de
bestaande TMDb-metadatastroom. Ze worden als TMDb aangeduid, niet als IMDb.
Een Real-Debrid-koppeling is één autorisatie voor deze eigen add-on; een bestaande
koppeling in een andere add-on wordt niet heimelijk overgenomen.

## Familieportretten

Bewaar de zes familieportretten en de hond samen in een map op USB of een
bereikbare map. Open Krispijn Video > Instellen > Familieportretten kiezen.
De afbeeldingen worden één keer naar de gebruikersmap van Kodi gekopieerd.
Daarna is USB of de oorspronkelijke netwerkmap niet meer nodig.

De keuze blijft bewaard wanneer je de portretten vanuit een andere skin importeert.
De Familie Krispijn-skin gebruikt vervolgens deze lokale map voor het opstarten
én laden. De Kodi 21-skin valt niet meer terug op de meegeleverde smileys.
Zonder geïmporteerde afbeeldingen is de portretplek leeg; het laden blijft werken.

De aangeleverde portretten zijn stilstaande afbeeldingen. De skin wisselt ze en
past een lichte beweging toe. Dat verandert nog geen gezichtsuitdrukking.
Gebruik bij voorkeur kleine afbeeldingen. Een import accepteert maximaal
50 afbeeldingen van elk maximaal 8 MB. Een mislukte import behoudt de vorige map.
Portretten en accountgegevens worden nooit in de publieke build opgenomen.

## Snelheid

De eenmalige migratie naar skin 1.0.2 kiest een vaste achtergrond, schakelt blur
uit en schakelt de aanvullende TMDbHelper-achtergrondservice uit. De scores uit
Krispijn Video zijn hiervan onafhankelijk. Het standaard rode thema gebruikt de
meegeleverde texturen, zodat opnieuw genereren daarvan bij starten wordt overgeslagen.
Bij verloopkleuren of een apart skinprofiel blijft de oorspronkelijke generatie werken.

Gezichtjes wisselen op het opstartscherm iedere vijf seconden. De beweging hangt
af van de zichtbaarheid van het eigen schermonderdeel. Er komt geen aparte
achtergrondservice voor de portretten.

De POV-basis start niet automatisch zijn eigen venster, synchroniseert geen externe
trackeraccounts en controleert bij het opstarten geen abonnementen. De lokale
database- en instellingeninitialisatie blijft behouden, net als de bestaande
code voor afspelen en hervatten. Externe scrapers staan standaard uit; de interne
POV-providers blijven beschikbaar. Afbeeldingskwaliteit staat op Medium.

De uitgebreide POV-instellingen blijven bereikbaar als ontsnappingsmogelijkheid.
Bestaande gebruikersgegevens en Kodi-caches worden niet gewist. Verlopen gegevens
worden volgens de cachelogica genegeerd. Zware onderhouds- en prefetchacties draaien
niet automatisch bij deze eerste versie; handmatig cacheonderhoud blijft beschikbaar.

## Onderhoud

De POV-download staat vast op commit 2c8390c6e65213853a862a00044597946b946132,
versie 6.11.03 en SHA256. Het oorspronkelijke bronpakket wordt ook lokaal
bewaard onder video-mod, zodat een volgende build niet van de beschikbaarheid
van upstream afhankelijk is. Een afwijkende bron stopt de build. tools/make_pov.py
bouwt de eigen variant. video-mod bevat het eigen menu en de beperkte service.
De oorspronkelijke GPL-3.0-vermeldingen blijven behouden. COPYING en FORK.md worden
meegeleverd. GitHub bevat de scripts en aanpassingen waarmee de fork reproduceerbaar is.

De skinwijzigingen staan in tools/skin_fast.py en worden alleen op de Kodi 21-build
toegepast. Geen wijzigingen in de Arctic Fuse-subtrees. De oude Crew-fork wordt
niet opgenomen. Het oude Crew-repositorypakket verdwijnt uit de bronpagina.

## Validatie vóór brede uitrol

De build en statische controles vervangen geen praktijktest. Op de Shield:

- Controleer dat de skin na een herstart voorbij Initialising skin komt.
- Koppel Real-Debrid, sluit Kodi af en controleer dat de koppeling bewaard blijft.
- Open Films en Series, zoek een titel en test afspelen en hervatten.
- Controleer de TMDb-score en de Nederlandse metadata.
- Importeer de zeven portretten en controleer het opstart- en laadscherm.
- Test zonder USB of netwerkmap nadat de import klaar is.
- Controleer bestaande widgets, fotomapkeuzes en eigen thema's na de update.
- Meet drie koude starts en dezelfde browsehandelingen; vergelijk de middelste tijd.

Er is geen gemeten prestatiewinst op de Shield vastgesteld. De eerder gemelde crash
en opstartblokkade zijn zonder kodi.log niet definitief verklaard of opgelost.

## Correctie Krispijn Video 1.0.1

Herstelt ook omgekeerd opgeslagen POV-ids. Filmlinks, paginering en het
autorisatievenster verwijzen daardoor naar de eigen add-on.
Verwijdert het voor Kodi 21 ongeldige offscreen-argument bij getVideoInfoTag.
Voegt Nederlandse genres, gecombineerde genres en verdere filters toe.
Gebruikt eigen logo en achtergrond; bron- en licentievermeldingen blijven behouden.
De skins wijzigen niet. Real-Debrid-autorisatie en afspelen nog op de Shield testen.
