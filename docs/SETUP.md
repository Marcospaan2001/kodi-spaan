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


## Videohub 1.2.0

Filmavond toont drie afzonderlijke horizontale rijen: Verder kijken, de
seizoenskeuze en Nieuw digitaal. De lokale kijkvoortgang verschijnt eerst;
online rijen worden daarna onafhankelijk gevuld. Bij een verbindingsprobleem
blijven de andere rijen bruikbaar. De knop Alle nieuwe films opent een raster
met meerdere rijen posters en paginering. Zoeken staat vast rechtsboven.
De losse Actie- en Sciencefictiontabs zijn vervangen door het bestaande menu
Genres en filters. Afspelen stoppen blijft beschikbaar in het zijmenu.

Nieuw digitaal gebruikt TMDb: digitale releases in de VS van de afgelopen
120 dagen, met een eerste release in het afgelopen jaar en een geregistreerde
bioscooprelease op of voor de digitale releasedatum. De VS dient als bron voor
internationale digitale releases; dit is geen garantie van Nederlandse
beschikbaarheid of afspeelbronnen. Alleen de geopende cataloguspagina wordt
gecontroleerd, met maximaal vier gelijktijdige releasecontroles. De pagina
wordt zes uur gecachet en releasedetails één dag. De eerste ongevulde cache
kan trager zijn. Een pagina kan minder titels bevatten na de bioscoopcontrole;
Volgende doorzoekt de volgende bronpagina. Sortering binnen de pagina gebeurt
op de bevestigde digitale datum.

Kies een poster en daarna Trailer bekijken. Hiervoor is de officiële YouTube-
add-on nodig. Krispijn biedt installatie aan als deze ontbreekt. Eventuele
YouTube-configuratie, API-sleutels of toegangseisen hangen af van die add-on.
Trailers worden uitsluitend op verzoek opgehaald en niet automatisch gestart.
Een kleine speler opent boven de hub, met Volledig scherm, Pauze / afspelen en
Trailer sluiten. Sluiten stopt de trailer. Terug vanuit volledig scherm brengt
je terug naar de kleine speler. Bij een andere spelende video vraagt Krispijn
eerst of deze mag worden gestopt. Ontbreekt een trailer, dan volgt een melding.
De onderliggende interface en categorie blijven behouden.

Deze versie is gebouwd en statisch gecontroleerd. Afstandsbediening, YouTube-
afspelen en snelheid moeten nog op de Shield worden beoordeeld.


## Rustigere indeling in 1.2.1

Filmavond heeft weer twee rijen: Verder kijken en Seizoensfilms. Nieuw digitaal
is verwijderd, inclusief de bijbehorende catalogus- en releaseaanvragen. De
beschrijving heeft weer een ruim tekstvak; Hele beschrijving opent de volledige
tekst in een leesvenster. De overige categorieën tonen grotere posters en minder
films tegelijk. Zoeken blijft rechtsboven. De kleine trailerspeler heeft alleen
Pauze / afspelen en Trailer sluiten; de fullscreenknop is verwijderd.

De tweerijenindeling en het beschrijvingsvak zijn daadwerkelijk bekeken in het
Kodi 21.2-lab. Streaming en de Shield-prestaties zijn niet opnieuw getest.


## Filmavond en Sport in 1.2.2

Filmavond toont uitsluitend seizoensfilms. Verder kijken staat alleen nog in
het zijmenu. Hierdoor hoeft Filmavond ook geen kijkhistorie op te halen.

Sport biedt Formule 1, Voetbal en Darts. Kies binnen een sport The Loop openen.
Als The Loop ontbreekt, biedt Krispijn installatie aan. Vernieuw eerst Spaan
Repository 1.0.14 zodat Kodi de nieuwe externe catalogus kent. Rond Kodi's
installatiedialoog af en open Sport opnieuw. Als alternatief staat de originele
repository.loop-3.0.4.zip onder de bestaande spaan-bestandsbron.

De categorieën gebruiken geverifieerde routes uit The Loop 8.4: Auto Zone voor
Formule 1, het voetbalmenu voor voetbal en de livezoekroute voor darts. De
inhoud en beschikbaarheid worden door The Loop bepaald. Bij openen verlaat je
de Krispijn-hub en gebruik je de oorspronkelijke The Loop-interface. Updates
van The Loop komen uit zijn eigen catalogus. Er is geen nieuwe achtergrondtaak
in Krispijn, maar The Loop heeft zelf wel een service en meerdere afhankelijkheden.
De liveweergave en installatieketen zijn niet op de Shield getest.

Per sport kun je ook eigen http- of https-streamadressen toevoegen, afspelen
en verwijderen. Die adressen worden alleen in je lokale Kodi-profiel bewaard,
niet in GitHub. Tijdelijke toegangstokens in een streamadres kunnen verlopen.

Bron: https://loopaddon.uk/theloop/ . De repositoryzip is ongewijzigd en met
een vastgezette SHA256 gecontroleerd. Spaan verwijst naar dezelfde twee
externe catalogi als de Loop-repository, zodat afhankelijkheden vindbaar zijn.


## YouTube-herstelprofiel in 1.2.3

Bij de eerste trailer stelt Krispijn YouTube eenmalig in op maximaal 720p,
H.264-video en AAC-audio. Alleen-audio en kwaliteitsvragen staan uit; AV1, VP9,
HDR en hoge framerates worden niet geselecteerd in het streamfilter. De bestaande
keuze voor InputStream Adaptive blijft behouden. Het profiel is gecontroleerd
tegen het instellingsschema van officiële YouTube 7.4.4 voor Kodi 21. Bij een
afwijkend schema wordt niets gewijzigd en verschijnt een updateadvies.

Dit geldt voor de hele YouTube-add-on, ook buiten Krispijn. Film-, sport- en
Kodi-hardwareversnellingsinstellingen worden niet veranderd. Eerdere waarden
worden lokaal bewaard. Via Instellen > YouTube en trailers kun je het profiel
opnieuw toepassen, de vorige waarden terugzetten of YouTube-instellingen openen.
Na terugzetten wordt het profiel niet vanzelf opnieuw toegepast. Accounts,
API-sleutels en tokens worden niet aangepast of in de back-up opgenomen.

Ontbreekt YouTube, dan biedt de trailerfunctie installatie vanuit Kodi aan.
Bestaande installaties volgen Kodi's update-instelling. Vanuit het trailermenu
kunnen repositories opnieuw worden gecontroleerd, maar dit forceert geen update.

Dit is een herstelmaatregel voor mogelijke codec- en kwaliteitsproblemen, geen
bewezen oplossing voor elke vastloper. Zwart beeld, netwerkproblemen, YouTube-
veranderingen of Android-rendering kunnen een andere oorzaak hebben. De fout
na tien seconden is zonder Shield-log niet gereproduceerd.

## Zelfstandig Sport vanaf 1.2.4

Werk Spaan Repository bij naar 1.0.16 en Krispijn Video naar 1.2.4.
Open Sport en kies Formule 1, Voetbal of Darts, daarna Uitzendingen bekijken.
De bronzoekers zitten nu in Krispijn zelf. Er is geen Loop-repository of
Loop-add-on nodig en je verlaat de hub niet voor een andere sportinterface.
De oude Loop-download en beide daarvoor toegevoegde catalogi zijn verwijderd.

Kies een uitzending en indien nodig een stream. Er worden geen andere sport-add-ons
geïnstalleerd. Uitzendingen vernieuwen ververst de korte cache. Ophalen kun je
annuleren. Eigen livestreams toevoegen en verwijderen blijft beschikbaar.
FawaNews en StreamsCenter worden rechtstreeks bevraagd; zij bepalen het aanbod.
Lege categorieën zijn mogelijk buiten evenementen. Niet ieder extern playerformaat
wordt ondersteund. Een gevonden uitzending is geen garantie op een werkende stream.

The Loop wordt niet automatisch van bestaande apparaten verwijderd. Als je die
nergens anders gebruikt, kun je hem zelf verwijderen via Mijn add-ons. Deze update
verandert geen Real-Debrid-koppeling, ondertitelaccount of opgeslagen eigen streams.

## Sportbroncontrole in 1.2.5

Krispijn controleert een gevonden HLS-afspeellijst voordat Kodi start. Bij een
onbeschikbaar CDN-adres probeert het automatisch het volgende adres. Ook de
videovariant achter een masterplaylist wordt gecontroleerd. Een lege playlist,
HTML-foutpagina of HTTP-fout gaat niet meer rechtstreeks naar de speler.

Zijn de adressen onbeschikbaar, dan blijft het sportmenu open met uitleg dat de
uitzending nog niet beschikbaar of tijdelijk offline is. Probeer rond de starttijd
opnieuw. De controle is annuleerbaar en verandert geen account- of spelerinstellingen.
Een geslaagde controle garandeert geen blijvende beschikbaarheid van de videofragmenten.
Eigen handmatig toegevoegde livestreams behouden hun bestaande afspeelgedrag.

Sport staat nu in de eigen videohub: drie vaste tegels voor Formule 1, Voetbal
en Darts, met daaronder evenementkaarten. Selecteer een kaart om de stream te
controleren en af te spelen. Vernieuwen haalt de bronlijst opnieuw op; Eigen
streams opent het beheer van je lokale adressen. Zonder geselecteerde sport
worden geen sportbronnen opgevraagd. Trailers en filmpaginering verdwijnen in Sport.

Starttijden worden getoond wanneer de bron ze levert. StreamsCenter-tijden
worden omgerekend naar de apparaattijdzone. Bij FawaNews is de tijdzone niet
bevestigd; die tijden blijven brontijden. Er wordt geen onbevestigd Live-label
getoond. Als een HLS-masterplaylist resoluties vermeldt, verschijnt bij starten
welke maximale resolutie de bron aanbiedt. Dit is geen meting van de daadwerkelijk
afgespeelde kwaliteit. Een bron zonder hogere resolutie wordt niet opgeschaald.
