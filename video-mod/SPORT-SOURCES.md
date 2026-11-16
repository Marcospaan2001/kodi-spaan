# Krispijn Sport: herkomst en onderhoud

De zelfstandige sportmodule gebruikt aangepaste parsers uit JetExtractors 3.3.31,
Copyright (c) 2020 t4ils, MIT. De volledige licentie staat in SPORT-LICENSE.txt.
Onderzocht bronpakket: https://loopaddon.uk/zips19/script.module.jetextractors/script.module.jetextractors-3.3.31.zip

Overgenomen protocollen: FawaNews-evenementkaarten en streamadressen;
StreamsCenter-evenementkaarten en stream-API. Beide zijn eigen adapters in
sport_sources.py. De huidige FawaNews-array van CDN-adressen wordt eveneens gelezen.
Deze module is geen volledige kopie van The Loop of JetExtractors.

Er is geen afhankelijkheid van The Loop, zijn catalogus, JetExtractors, ResolveURL
of een externe sport-add-on. Geen telemetrie, remote Python-updater, gedownloade
uitvoerbare code of permanente sportservice. De runtime gebruikt uitsluitend de
Python-standaardbibliotheek en Kodi. HTTP-antwoorden hebben een tijd- en groottelimiet.
Webscripts worden nooit uitgevoerd. Certificaatcontrole blijft ingeschakeld.

Alleen Formule 1, voetbal en darts worden geselecteerd. De bronlijsten worden op
verzoek opgehaald met twee werkers en twee minuten lokaal gecachet. Een stream
wordt pas bij selectie opgezocht. Annuleren start geen speler achteraf.
De bron vermeldt niet altijd een betrouwbare datum of actuele livestatus: de
interface noemt de resultaten daarom uitzendingen, niet gegarandeerd live.

Niet overgenomen: de gesloten Streamed-dienst, andere sporten, IPTV-gidsdiensten,
Loop-feeds, externe proxyservices en alle overige JetExtractors-providers.
Niet iedere iframe- of versleutelde playerindeling wordt ondersteund. Een website
kan bereikbaar zijn terwijl zijn uitzending offline is. Geen garantie op
beschikbaarheid, resolutie of continu afspelen; onderhoud gebeurt in deze repo.

Eigen streamadressen en eventuele toegangstokens blijven uitsluitend in Kodi userdata.
Bestaande installaties van The Loop worden niet automatisch verwijderd; andere
add-ons kunnen die gebruiken. Krispijn roept ze niet meer aan.

SHA256 van het onderzochte JetExtractors-bronpakket:
`2d72ddd5f98102cd40e220a7de26fdf6995135e787c4368faedd6872ef771737`.
