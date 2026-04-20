# Versie 1

## Wat werkt nu

Deze eerste versie werkt voor:

1. installeren als custom integration;
2. toevoegen via Home Assistant config flow;
3. verbinding maken met de Asmoke cloud MQTT-broker;
4. subscribe op bevestigde topics voor status, temperatures en result;
5. entities aanmaken voor de belangrijkste telemetrie;
6. diagnostics met redactie van gevoelige data;
7. options flow voor debug logging, extra topics en offline timeout;
8. een bevestigde write-actie voor smoke target temperature;
9. een raw action service voor gevorderd gebruik;
10. blijven laden als de BBQ uit staat.

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

## Bekende datainterpretaties in versie 1

- `probeATemp = 499` wordt behandeld als probe niet aangesloten;
- `probeBTemp = 499` wordt behandeld als probe niet aangesloten.

## Wat nog beperkt is

Nog niet volledig uitgewerkt in versie 1:

1. automatische device discovery;
2. brede ondersteuning voor alle Asmoke-modi en commando's;
3. volledige mapping van alle statusvelden;
4. firmware-updates;
5. geavanceerde onboarding zonder `device_id`;
6. UI-polish en uitgebreide eindgebruikersdiagnostiek;
7. HACS default store opname.

## Belangrijke grenzen

1. Deze integration gebruikt cloud MQTT, geen lokale LAN-API.
2. De brokercredentials zijn gevoelig en horen niet in een publieke repo.
3. Als de BBQ uit staat, blijft de integration wel bestaan maar komen er geen nieuwe push-updates binnen.
4. `publish_raw_action` is krachtig maar ook risicovoller dan de bevestigde standaardactie.
