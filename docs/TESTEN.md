# Testen van Krispijn Video 1.1.0

## Op de Shield

- [ ] Werk repository 1.0.7, video 1.1.0 en skin Kodi 21 1.1.0 bij; herstart Kodi.
- [ ] Open Krispijn Video: de eigen interface verschijnt direct.
- [ ] Wissel snel tussen Trending, Actie en Sciencefiction. Een laat antwoord mag nooit de nieuwere keuze vervangen.
- [ ] Open dezelfde categorie opnieuw. Eerder geladen titels komen uit de cache.
- [ ] Zoek een bekende film en een serie, ook met spaties, accenten en een ampersand.
- [ ] Open de volgende pagina en keer terug; selectie en titel horen bij de juiste pagina.
- [ ] Controleer lege resultaten, offline netwerk, opnieuw proberen en teruggaan met de afstandsbediening.
- [ ] Real-Debrid koppelen geeft een expliciete uitslag; annuleren bewaart een bestaande koppeling.
- [ ] Een opgeslagen koppeling zonder recente controle wordt niet als geverifieerd gepresenteerd.
- [ ] Klik een film: de meegeleverde bronzoeker is actief. Een ontbrekende koppeling, geen bronnen en weggefilterde bronnen geven verschillende uitleg.
- [ ] Speel een beschikbare bron, stop halverwege en hervat via Verder kijken.
- [ ] Open een serie, seizoen en aflevering; controleer hervatten van de juiste aflevering.
- [ ] Familieportretten verschijnen bij welkom en er draait geen gezicht over de laadindicator.
- [ ] Geen POV-naam of logo in gewone menu's, meldingen of laadvensters.
- [ ] Ondertitels kunnen via de optionele OpenSubtitles.com-add-on worden gedownload.

## Prestaties meten

Gebruik hetzelfde netwerk en wis de caches niet. Meet drie keer en noteer de middelste tijd:

| Handeling | Vorige versie | 1.1.0 |
|---|---|---|
| Kodi koud starten tot bedienbaar | | |
| Krispijn Video openen tot bedienbaar menu | | |
| Eerste keer Trending laden | | |
| Tweede keer Trending openen | | |
| Van film terug naar overzicht | | |

De geteste Linux-omgeving bewijst geen snelheid op een Shield. Netwerk, afbeeldingscache en bronnen hebben invloed.
Er zijn geen per-titelverzoeken nodig om een cataloguslijst te tekenen. Het zoeken naar afspeelbronnen gebeurt pas bij kiezen van een titel.

## Bouwcontroles

Voer `python tools/build.py`, `python -m unittest discover -s tests` en `python tools/check_deps.py` uit.
Controleer na publicatie de versies in addons.xml, de MD5 en de zipdownloads.
Behoud de Kodi 22-zip zolang die variant niet wordt gewijzigd.
