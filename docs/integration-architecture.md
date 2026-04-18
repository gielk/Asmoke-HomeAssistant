# Home Assistant Architectuur

## Korte conclusie

Voor Asmoke is de juiste route een Home Assistant custom integration met een eigen verbinding naar de vendor MQTT-broker. Een HACS frontend plugin of een losse add-on is daarvoor niet de primaire vorm.

## Juiste distributievorm

- Home Assistant vorm: custom integration
- HACS repo type: `integration`
- Niet geschikt als HACS `plugin`
- Alleen eventueel later een add-on als optionele onboarding-helper

## Aanbevolen domein

Aanbevolen integratiedomein: `asmoke_cloud`.

Reden:

- de huidige route is expliciet cloud-gebaseerd;
- het voorkomt verwarring als er later ooit een echte lokale Asmoke-API opduikt;
- het maakt de runtimeverantwoordelijkheid meteen duidelijk.

Als je zeker weet dat er nooit een aparte lokale variant komt, is `asmoke` ook verdedigbaar.

## Aanbevolen repository- en integratiestructuur

```text
custom_components/
  asmoke_cloud/
    __init__.py
    manifest.json
    const.py
    config_flow.py
    coordinator.py
    mqtt.py
    services.py
    services.yaml
    diagnostics.py
    sensor.py
    binary_sensor.py
    number.py
    select.py
    translations/
      en.json
    brand/
      icon.png
      logo.png
tests/
  components/
    asmoke_cloud/
      test_config_flow.py
      test_init.py
      test_sensor.py
      test_services.py
      test_diagnostics.py
```

## Config flow

De minimale config flow moet vragen om:

- `device_id`
- optioneel een gebruikersnaam of friendly name voor het device

De integration vult zelf in:

- broker host;
- broker port;
- standaard keepalive;
- standaard topicpatronen;
- app-auth uit lokale secrets of een lokale auth-notitie.

Aanbevolen gedrag:

- `unique_id` gelijk aan de `device_id`;
- mislukte auth moet naar reauth kunnen leiden;
- een connectietest moet plaatsvinden voordat de entry wordt aangemaakt;
- een optiescherm moet later reconnect- en debugopties kunnen beheren.

## Options flow

Gebruik bij voorkeur een `OptionsFlowWithReload` zodat gewijzigde opties automatisch leiden tot herladen van de integration.

Geschikte opties:

- debug logging aan of uit;
- aanvullende topic-subscriptions voor onderzoek;
- reconnect-interval of backoff-profiel;
- entity- of featuretoggles voor experimentele commandos.

## Runtime-ontwerp

De runtime moet een gedeeld state-object hebben dat:

- de MQTT-verbinding beheert;
- reconnects centraal afhandelt;
- berichtpayloads decodeert naar een intern statusmodel;
- entities signaleert wanneer nieuwe data beschikbaar is.

Omdat Asmoke push-gebaseerd is, ligt polling niet voor de hand. Een coordinator-achtig runtime-object is wel nuttig voor centrale foutafhandeling, statusopslag en entity-updates.

## Entities

Waarschijnlijk nuttige entities:

- sensor grill temperature 1
- sensor grill temperature 2
- sensor probe A temperature
- sensor probe B temperature
- sensor battery level
- sensor roast progress
- sensor target temperature
- sensor target time
- binary sensor ignition status
- binary sensor online or active status
- select mode
- number target temperature

Voor nieuwe integraties hoort `has_entity_name = True` de standaard te zijn.

## Services

Aanbevolen services in de eerste implementatiefase:

- `publish_raw_action` voor gecontroleerd reverse-engineeren;
- `set_smoke_target_temp` voor bevestigde temperatuurcommando's.

Expose alleen services waarvoor payloadvorm en devicegedrag echt bevestigd zijn.

## Diagnostics

Voeg diagnostics toe waarmee een gebruiker zonder packet capture kan zien:

- verbonden of verbroken brokerstatus;
- gesubscribe topics;
- laatst ontvangen payloadtypes;
- laatst bekende device-status;
- foutdetails met redacties voor secrets.

Redigeer in ieder geval:

- username;
- password;
- client-id;
- complete device-identifiers als je die niet publiek wilt tonen.

## Vertalingen

Voor custom integrations gebruik je geen `strings.json`. Gebruik `translations/en.json` en eventuele extra taalbestanden in dezelfde map.

Dat is belangrijk, omdat `strings.json` en placeholder-verwijzingen build-time features van Home Assistant core zijn en niet automatisch werken voor custom integrations.

## Brand assets

Voor custom integrations horen brand assets lokaal in de integration, onder `custom_components/asmoke_cloud/brand/`.

## Security-grens

Deze repo moet publieke documentatie en code bevatten, maar geen live secrets. Houd daarom een lokaal, gitignored bestand aan voor:

- broker host;
- username;
- password;
- device-id's die je niet publiek wilt maken;
- testtopics of captures die privacygevoelig zijn.

## Aanbevolen uitvoeringsvolgorde

1. Start met read-only telemetry.
2. Voeg daarna config flow en reauth goed af.
3. Voeg daarna write-services toe voor bevestigde commandos.
4. Voeg diagnostics, tests en translations toe.
5. Maak het daarna HACS-ready.
