# Asmoke Home Assistant

<p align="center">
	<img src="https://cdn.shopify.com/s/files/1/0288/2060/2954/files/logo_final_43448c3c-dfd2-4921-8526-ca91ac15a6f0.png?height=628&pad_color=ffffff&v=1646132983&width=1200" alt="Asmoke logo" width="320">
</p>

Home Assistant custom integration voor Asmoke smokers via de Asmoke cloud MQTT-broker.

## Wat dit is

Deze repository bevat een werkende eerste versie van een custom Home Assistant integration.

De integration:

- maakt een config flow aan in Home Assistant;
- verbindt rechtstreeks met de Asmoke MQTT-broker;
- leest temperatuur-, status- en result-berichten;
- maakt entities aan in Home Assistant;
- ondersteunt een eerste bevestigde write-actie voor smoke target temperature;
- blijft laden als de BBQ uit staat.

## Snelle start

1. Voeg deze repository toe aan HACS als custom repository van type `integration`.
2. Installeer `Asmoke Cloud` via HACS.
3. Herstart Home Assistant.
4. Ga naar `Instellingen -> Apparaten en diensten -> Integratie toevoegen`.
5. Kies `Asmoke Cloud`.
6. Vul je `device_id`, broker host, poort, username, password en keepalive in.
7. Rond de config flow af.

## Installatie en gebruik

De volledige handleiding staat in [docs/user-guide.md](docs/user-guide.md).

## Wat werkt in versie 1

Het actuele overzicht staat in [docs/first-version.md](docs/first-version.md).

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


