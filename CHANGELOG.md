# Changelog

Deze repository gebruikt semantic versioning voor functionele HACS-releases.

## v0.3.3 - 2026-04-20

- voegt lokale Home Assistant brand-assets toe voor `asmoke_cloud`;
- levert `icon.png`, `icon@2x.png`, `logo.png` en `logo@2x.png` zodat de integratiekaart en UI-branding gevuld zijn.

## v0.3.2 - 2026-04-20

- valideert en actualiseert de documentatie voor de huidige HACS- en onboardingflow;
- zet het Smoke temperature-commando weer op het bevestigde vendorveld `targetTemp`.

## v0.3.1 - 2026-04-20

- voegt echte GitHub Releases toe voor HACS-versies in plaats van alleen git-tags;
- verbergt de default branch in HACS zodat gebruikers niet meer op commit-hashes uitkomen.

## v0.3.0 - 2026-04-20

- toevoegt automatische `device_id` discovery via een tijdelijke MQTT discovery-stap;
- splitst de config flow op in discover en manual onboarding;
- vult device metadata zoals grill type en een eventuele firmwareversie aan wanneer die in payloads aanwezig zijn.

## v0.2.0 - 2026-04-20

- behandelt probe temperatuurwaarde `499` als niet aangesloten in plaats van als echte temperatuur.

## v0.1.1 - 2026-04-20

- lost de Home Assistant config flow laadfout op zodat de integratie betrouwbaar opent in de UI.

## v0.1.0 - 2026-04-18

- eerste publieke werkende versie van de Asmoke Home Assistant integratie;
- cloud MQTT runtime, config flow, entities, services en basisdocumentatie.