# Familie Krispijn installeren

## Eenmalig op de Shield

1. Controleer Kodi 21.2 onder Instellingen > Systeeminfo.
2. Voeg in Bestandsbeheer de bron `https://marcospaan2001.github.io/kodi-spaan/` toe met de naam `spaan`.
3. Kies Add-ons > Installeren vanuit zip-bestand > spaan > `repository.spaan-1.0.8.zip`.
4. Installeer vanuit Spaan Repository de video-add-on **Krispijn Video 1.1.1**.
5. Installeer voor de rest van Kodi **Familie Krispijn (Kodi 21) 1.1.1** onder Uiterlijk > Skin.
6. Open Krispijn Video. De eigen interface opent direct, ook wanneer je een andere Kodi-skin gebruikt.
7. Open Instellen > Real-Debrid en koppel je account. De add-on controleert het account en toont de uitslag. Een opgeslagen koppeling en een gecontroleerd actief abonnement zijn verschillende statussen.

Er is geen IMDb-, Trakt-, MDBList- of TMDb-account nodig. Scores zijn van TMDb.
Een titel in een catalogus is geen garantie dat er een afspeelbare bron beschikbaar is.

## Bijwerken vanaf een vorige versie

Laat Spaan Repository controleren op updates. Werk Krispijn Video en de Kodi 21-skin bij en herstart Kodi.
De update herstelt eenmalig de eerder per ongeluk uitgeschakelde meegeleverde bronzoeker.
Accountgegevens en kijkvoortgang blijven bewaard. Wis geen Kodi-gegevens of caches als installatiestap.

## Bediening

Het startscherm biedt onder andere Trending, Nu in de bioscoop, Films, Series, Actie, Sciencefiction en Zoeken.
Alleen de gekozen lijst wordt geladen. Gebruik links/rechts voor de titels en het menu voor een andere categorie.
Zoeken gebruikt het Kodi-toetsenbord en toont film- en serieresultaten na het bevestigen.
Verder kijken gebruikt de lokale voortgang op dit apparaat. Een nieuwe installatie heeft daar nog geen titels.

## Ondertitels

OpenSubtitles.com is optioneel. Installeer het pakket vanuit de spaan-bron of de officiële Kodi-repository.
Vul je eigen OpenSubtitles.com-account in bij de add-oninstellingen.
Kies onder Instellingen > Speler > Taal Nederlands en OpenSubtitles.com als standaard ondertitelservice.

## Familie en uiterlijk

De zeven aangeleverde gestileerde portretten zijn met toestemming meegeleverd.
Ze staan bij het welkom; de laadindicator gebruikt een rustige vorm zonder wiebelend portret.
Filmposters horen bij de betreffende film of serie. De interface gebruikt een vaste donkere achtergrond.

## Back-up en Kodi 22

Maak een back-up van Kodi userdata voordat je naar een andere hoofdversie van Kodi overstapt.
De back-up bevat accounttokens: bewaar hem privé.
De Kodi 22-skin blijft als aparte variant beschikbaar. Die skin heeft nog niet dezelfde aanpassingen als de Kodi 21-skin.
De zelfstandige Krispijn Video-interface vereist geen specifieke skin.

## Herkomst

De video-add-on is gebaseerd op POV 6.11.03 van kodifitzwell onder GPL-3.0.
De skins zijn gebaseerd op Arctic Fuse van jurialmunkey onder CC BY-NC-SA 4.0.
De bronvermelding en licenties staan in de broncode en credits, buiten de gewone navigatie.

## Eigen welkom in 1.1.1

De startdiavoorstelling van de Kodi 21-skin is vervangen door een vaste donkere
achtergrond met het Familie Krispijn-logo. In de video-add-on toont Filmavond
een grote galerij van alle zeven portretten zolang de navigatie actief is.
Ga naar de filmrij voor de titel, score en beschrijving. Geen extra netwerkverzoeken
of verplichte wachttijd. Het allereerste Kodi-logo van de Android-app valt buiten
de skin en wordt door deze update niet vervangen.

## Taalvoorkeuren vanaf Krispijn Video 1.1.2

De update zet Kodi eenmalig op Engelse audio en Nederlandse ondertitels.
De standaardmarkering van een bron krijgt geen voorrang meer boven de audiotaal.
Deze Kodi-voorkeuren gelden ook buiten Krispijn Video. Tijdens het starten van een
Krispijn-stream worden aanwezige Engelse en Nederlandse sporen geselecteerd.
Een handmatige wijziging tijdens het kijken wordt niet periodiek teruggedraaid.
Ontbreekt Engels, kies dan een andere bron. Ontbreekt Nederlands, dan blijven
vreemde ondertitels uit en kun je via Ondertitels downloaden OpenSubtitles gebruiken.
Ondertitels die in het videobeeld zelf zijn ingebrand kunnen niet worden uitgezet.


## Filmavond en ondertitels in 1.1.2

Filmavond toont eerst lokale kijkvoortgang en daarna maximaal twaalf seizoensfilms.
In november en december zijn dat kerstfilms; de selectie wisselt automatisch met
het seizoen. Trending houdt zijn eigen weekoverzicht. Titels uit Verder kijken
worden niet dubbel in de seizoenskeuze gezet. Zonder kijkhistorie zie je alleen
de seizoenskeuze. Het ophalen van die selectie blokkeert de lokale voortgang niet.
Er is maximaal één catalogusaanvraag nodig, met de bestaande cache van vijftien minuten.
De seizoenskeuze is redactioneel op thema, geen persoonlijke aanbeveling op basis
van een online account. Beschikbaarheid van afspeelbronnen is niet gegarandeerd.

Ontbreekt een Nederlands ondertitelspoor, dan opent de add-on automatisch het
ondertitelzoekvenster van Kodi met OpenSubtitles.com en Nederlands als zoektaal.
Installeer OpenSubtitles via Instellen en vul daar eenmalig je account in.
Kies zelf het resultaat dat bij de release past; het eerste resultaat wordt niet
blind gedownload. Dit voorkomt onnodige fouten in de synchronisatie.
De standaardservice voor films en series en de zoektaal gelden voor heel Kodi.

Het add-onicoon heeft een nieuwe bestandsnaam om een oud gecachet POV-icoon te
omzeilen. De oude interne afbeeldingsnamen bevatten ook het Familie Krispijn-logo.


## Afspelen stoppen in 1.1.3

In het linkermenu van de videohub staat direct onder Filmavond de knop
Afspelen stoppen. Daarmee stop je de video die op de achtergrond speelt, ook
wanneer die gepauzeerd is. Het menu blijft open op de huidige categorie.
Teruggaan naar het menu alleen stopt de video niet. Als er geen video speelt,
geeft de knop een korte melding. De bestaande opslag van kijkvoortgang blijft
via de normale afspeelstop werken.


## Ondertiteltitels en kijkvoortgang in 1.1.4

Vlak voordat OpenSubtitles opent, krijgt Kodi opnieuw de oorspronkelijke
catalogustitel en het filmjaar. Daarmee hoeft OpenSubtitles niet op de lange
releasenaam terug te vallen. Een beschikbare film-ID kan de service gebruiken
voor een preciezere match. Bij series blijven serienaam, seizoen en aflevering
behouden. Serie-IDs worden niet meer ten onrechte als aflevering-IDs meegegeven.
De bestandsnaam blijft beschikbaar voor de synchronisatiekeuze van ondertitels.
Een schone titel garandeert niet dat Nederlandse ondertitels beschikbaar zijn.

Posters in Verder kijken en Filmavond tonen een rode voortgangsbalk en het
bekeken percentage uit de lokale kijkhistorie. Bij de geselecteerde titel staat
een knop Verder kijken, Film afspelen of Bekijk seizoenen. Vorige en Volgende
zijn alleen actief wanneer die pagina bestaat. De vaste achtergrond en bestaande
afbeeldingscache blijven behouden; er komen geen extra catalogusverzoeken bij.
De stopknop uit 1.1.3 is eveneens opgenomen in deze update.
