# HACS En Publicatieplan

## Korte conclusie

Als deze repo publiek verdeeld moet worden via Home Assistant, is de juiste route een HACS `integration` repository. Niet een `plugin`, niet een app en niet primair een add-on.

## Wat HACS verwacht

Voor een HACS integration-repo is dit de relevante basis:

- een publieke GitHub-repository;
- precies een integratie per repo;
- de integration onder `custom_components/<domain>/`;
- een duidelijke README;
- een repositorybeschrijving en logische GitHub-topics;
- releases zodra de integratie installeerbaar is;
- later een `hacs.json` in de repo-root.

## Wat nu nog niet moet

Deze repo heeft nu nog geen werkende integration-code. Voeg daarom nog geen misleidende HACS-bestanden toe alleen om de repo er "klaar" uit te laten zien.

Concreet:

- pas `hacs.json` toevoegen zodra de integration echt installeerbaar is;
- pas releases maken zodra er bruikbare installabele code staat;
- pas HACS store-submissie doen nadat custom repository-installatie stabiel werkt.

## Minimale technische eisen voor de eerste codefase

- `manifest.json` met `config_flow: true`
- `config_flow.py`
- ten minste een basis `__init__.py`
- ten minste een platform zoals `sensor.py`
- `translations/en.json`
- tests voor setup en config flow

## Quality scale doel

Voor een nieuwe integratie is Bronze het minimale kwaliteitsniveau om serieus te mikken. Praktisch betekent dat:

- UI-configuratie via config flow;
- basis documentatie;
- geautomatiseerde tests voor setup;
- nette foutafhandeling.

Silver is het eerstvolgende realistische doel:

- stabiele reconnects;
- goede fout- en authafhandeling;
- reauth-flow;
- betere troubleshooting-documentatie.

## Teststrategie

Aanbevolen testset:

- config flow success en auth failure;
- reauth-flow;
- entity setup vanuit bekende payloads;
- service calls naar MQTT publish;
- diagnostics-redactie;
- reconnect- of unavailable-gedrag.

Voor custom integrations is `pytest-homeassistant-custom-component` de praktische testbasis.

## CI en validatie

Zodra de eerste code er staat:

- run `ruff` of vergelijkbare linting;
- run `pytest`;
- valideer de integrationstructuur met `hassfest`;
- voeg een GitHub Action toe voor linting en tests.

## Releasepad

Aanbevolen volgorde:

1. Werk lokaal en valideer met tests.
2. Maak de repo bruikbaar als handmatige custom repository in HACS.
3. Maak een eerste tagged release.
4. Voeg HACS-validatie toe.
5. Overweeg daarna pas opname in de HACS default store.
