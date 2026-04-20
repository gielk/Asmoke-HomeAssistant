# Asmoke Home Assistant

<p align="center">
	<img src="https://cdn.shopify.com/s/files/1/0288/2060/2954/files/logo_final_43448c3c-dfd2-4921-8526-ca91ac15a6f0.png?height=628&pad_color=ffffff&v=1646132983&width=1200" alt="Asmoke logo" width="320">
</p>

Home Assistant custom integration voor Asmoke smokers via de Asmoke cloud MQTT-broker.

Minimaal ondersteunde Home Assistant versie: `2025.1.0`.

## Wat dit is

Deze repository bevat een werkende eerste versie van een custom Home Assistant integration.

De integration:

- maakt een config flow aan in Home Assistant;
- verbindt rechtstreeks met de Asmoke MQTT-broker;
- kan het `device_id` automatisch ontdekken via een tijdelijke MQTT discovery-stap;
- leest temperatuur-, status- en result-berichten;
- maakt entities aan in Home Assistant;
- ondersteunt bevestigde write-acties voor smoke, quick, roast en stop-cook bediening;
- maakt een climate-entity aan met een gedeelde target temperature en `smoke`/`quick` modekeuze, plus een Quick target time number-entity die tijdens een actieve Quick-cook live mee kan sturen;
- houdt daarnaast een `Stop cook` button-entity en een `Start quick cook` button-entity beschikbaar;
- exposeert een `Cook active` binary sensor als nette aan/uit-status voor dashboards en automations;
- blijft laden als de BBQ uit staat.

## Snelle start

1. Voeg deze repository toe aan HACS als custom repository van type `integration`.
2. Installeer `Asmoke Cloud` via HACS.
3. Herstart Home Assistant.
4. Ga naar `Instellingen -> Apparaten en diensten -> Integratie toevoegen`.
5. Kies `Asmoke Cloud`.
6. Kies `Discover Asmoke device` of `Enter device ID manually`.
7. Bij discovery: zet de BBQ aan of open de Asmoke app zodat Home Assistant tijdelijk een statusbericht kan opvangen.
8. Rond de config flow af.

Opmerking: host, poort en keepalive worden al met de bekende clouddefaults ingevuld. Deze repository commit geen vendor-shared MQTT credentials; als je die lokaal beschikbaar maakt via `local_auth.json` of environment variables, hoeven gebruikers in de praktijk meestal alleen nog een naam te kiezen en discovery te starten.

## Installatie en gebruik

De volledige handleiding staat in [docs/user-guide.md](docs/user-guide.md).

Voor een kopieerbaar Lovelace-dashboard in YAML zie [docs/dashboard-example.md](docs/dashboard-example.md).

Voor automation-, script- en notificatievoorbeelden met YAML zie [docs/automation-examples.md](docs/automation-examples.md).

## Wat werkt in versie 1

Het actuele overzicht staat in [docs/first-version.md](docs/first-version.md).

## Releases

Deze repository gebruikt semver-releases voor HACS. De laatste stabiele release is `v0.4.2`.

De main-branch kan al nieuwe, nog niet gereleasete integratiefuncties bevatten. Kijk daarvoor naar de bovenste sectie in `CHANGELOG.md`.

Het overzicht van functionele releases staat in [CHANGELOG.md](CHANGELOG.md).

## Belangrijkste bestanden

- Integratiecode: [custom_components/asmoke_cloud](custom_components/asmoke_cloud)
- Tests: [tests/components/asmoke_cloud](tests/components/asmoke_cloud)
- Onderzoekscontext: [docs/research-summary.md](docs/research-summary.md)
- Architectuurkeuzes: [docs/integration-architecture.md](docs/integration-architecture.md)

## Lokale auth-defaults

Voor lokaal gebruik kun je brokergegevens laten voorinvullen via een lokaal bestand of environment variables. Gebruik hiervoor [custom_components/asmoke_cloud/local_auth.json.example](custom_components/asmoke_cloud/local_auth.json.example).

Ondersteunde routes:

1. `custom_components/asmoke_cloud/local_auth.json`
2. `asmoke_cloud_local_auth.json` in de Home Assistant config-root
3. environment variables zoals `ASMOKE_CLOUD_USERNAME` en `ASMOKE_CLOUD_PASSWORD`

Deze lokale bestanden horen niet in Git.

## Tests

De componenttests draaien lokaal met:

```bash
python -m pytest tests/components/asmoke_cloud -q
```


