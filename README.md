# kodi-spaan

Persoonlijke Kodi-setup: een eigen repository (`repository.spaan`) en een skin-mod op
basis van Arctic Fuse 3, te installeren op elk apparaat via één bron-URL.

## Installeren in Kodi

Bron-URL: `https://marcospaan2001.github.io/kodi-spaan/`

1. Instellingen > Systeem > Add-ons > zet **Onbekende bronnen** aan.
2. Instellingen > Bestandsbeheer > **Bron toevoegen** > vul de bron-URL in en noem
   hem `spaan`.
3. Add-ons > **Installeren vanuit zip-bestand** > `spaan` >
   `repository.spaan-x.y.z.zip`.
4. Add-ons > **Installeren vanuit repository** > Spaan Repository.

## Mappen

| Map | Inhoud |
|---|---|
| `repository.spaan/` | De repository-addon: vertelt Kodi waar de addons staan |
| `skin.arctic.fuse.3.spaan/` | De skin-mod (volgt in fase 2) |
| `tools/build.py` | Bouwt zips, `addons.xml` en `addons.xml.md5` naar `docs/` |
| `tools/make_art.py` | Genereert icon en fanart van de repository |
| `docs/` | Uitvoer van de build, gepubliceerd via GitHub Pages |

Bewerk nooit iets met de hand in `docs/zips/`; dat wordt bij elke build overschreven.

## Een wijziging publiceren

1. Pas de addon aan.
2. Verhoog `version` in de `addon.xml` van die addon. Zonder hogere versie ziet
   Kodi geen update.
3. Bouw en publiceer:

```
python tools/build.py
git add -A
git commit -m "Beschrijving van de wijziging"
git push
```

GitHub Pages heeft daarna een paar minuten nodig. Kodi controleert zelf periodiek op
updates; forceren kan via Add-ons > Spaan Repository > Controleren op updates.

## Hoe een Kodi-repository werkt

- `addons.xml` is de catalogus: alle `addon.xml`-bestanden achter elkaar.
- `addons.xml.md5` is de checksum daarvan. Kodi downloadt de catalogus alleen opnieuw
  als de checksum verandert.
- Per addon staat er een map `zips/<id>/` met `<id>-<versie>.zip` en losse
  `icon.png` en `fanart.jpg` voor de weergave in de lijst.
- De repository-addon verwijst naast deze repo ook naar de repository van
  jurialmunkey. Daar komen TMDbHelper, script.skinvariables en script.texturemaker
  vandaan, zodat Kodi de afhankelijkheden van de skin zelf kan ophalen.

## Licentie en herkomst

De skin-mod is gebaseerd op
[Arctic Fuse 3](https://github.com/jurialmunkey/skin.arctic.fuse.3) van jurialmunkey,
gelicentieerd onder CC BY-NC-SA 4.0. De mod valt daarom onder dezelfde licentie:
naamsvermelding, niet-commercieel, gelijk delen. De scripts in `tools/` en
`repository.spaan/` zijn eigen werk.
