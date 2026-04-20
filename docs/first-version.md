# Versie 1

## Wat werkt nu

Deze eerste versie werkt voor:

1. installeren als custom integration;
2. toevoegen via Home Assistant config flow;
3. semi-automatische discovery van het `device_id` via tijdelijke MQTT-listening;
4. verbinding maken met de Asmoke cloud MQTT-broker;
5. subscribe op bevestigde topics voor status, temperatures en result;
6. entities aanmaken voor de belangrijkste telemetrie;
7. diagnostics met redactie van gevoelige data;
8. options flow voor debug logging, extra topics en offline timeout;
9. bevestigde start-acties voor smoke, quick en roast cook;
10. een bevestigde stop-actie voor een lopende cook;
11. een raw action service voor gevorderd gebruik;
12. blijven laden als de BBQ uit staat.

## Entities in versie 1

Beschikbare entitytypes:

- sensoren voor grill temperature 1 en 2;
- sensoren voor probe A en probe B temperature;
- sensor voor battery level;
- sensor voor roast progress;
- sensor voor target time;
- sensor voor mode;
- sensor voor Wi-Fi status;
- sensor voor last result message;
- binary sensor voor broker connected;
- binary sensor voor device online;
- binary sensor voor ignition active;
- number entity voor smoke target temperature.

## Bevestigde schrijfroute in versie 1

Bevestigd en ingebouwd:

- smoke target temperature via de number-entity;
- smoke target temperature via `asmoke_cloud.set_smoke_target_temp`.
- cook start via `asmoke_cloud.start_cook` met bevestigde `smoke`, `quick` en `roast` modi;
- cook stop via `asmoke_cloud.stop_cook`.

## Bekende datainterpretaties in versie 1

- `probeATemp = 499` wordt behandeld als probe niet aangesloten;
- `probeBTemp = 499` wordt behandeld als probe niet aangesloten.

## Wat nog beperkt is

Nog niet volledig uitgewerkt in versie 1:

1. volledig hands-off onboarding zonder brokercredentials;
2. brede ondersteuning voor alle Asmoke-modi en commando's buiten `smoke`, `quick`, `roast` en `stop`;
3. volledige mapping van alle statusvelden;
4. bevestigde firmwareversie-uitlezing;
5. firmware-updates;
6. UI-polish en uitgebreide eindgebruikersdiagnostiek;
7. HACS default store opname.

## Belangrijke grenzen

1. Deze integration gebruikt cloud MQTT, geen lokale LAN-API.
2. De brokercredentials zijn gevoelig en horen niet in een publieke repo.
3. Als de BBQ uit staat, blijft de integration wel bestaan maar komen er geen nieuwe push-updates binnen.
4. `publish_raw_action` is krachtig maar ook risicovoller dan de bevestigde standaardacties.
