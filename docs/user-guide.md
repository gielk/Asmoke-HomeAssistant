# Gebruikershandleiding

## Doel

Met deze integration verbind je Home Assistant rechtstreeks met de Asmoke cloudbroker. Daardoor kun je Asmoke-telemetrie als Home Assistant entities gebruiken zonder de mobiele app als tussenlaag.

## Voorwaarden

Je hebt nodig:

- een werkende Home Assistant installatie;
- HACS of handmatige custom component installatie;
- de Asmoke `device_id`;
- de brokergegevens die bij jouw Asmoke-opstelling horen;
- internettoegang vanaf Home Assistant naar de Asmoke broker.

De BBQ hoeft niet aan te staan om de integration te installeren. Als de BBQ uit staat, zal de integration nog steeds laden, maar er komen dan geen live telemetrie-updates binnen.

## Installatie via HACS

1. Open HACS in Home Assistant.
2. Voeg deze repository toe als custom repository.
3. Kies type `integration`.
4. Installeer `Asmoke Cloud`.
5. Herstart Home Assistant.

## Handmatige installatie

1. Kopieer de map `custom_components/asmoke_cloud` naar je Home Assistant configuratiemap onder `custom_components/asmoke_cloud`.
2. Herstart Home Assistant.

## Eerste configuratie

1. Open Home Assistant.
2. Ga naar `Instellingen -> Apparaten en diensten`.
3. Klik op `Integratie toevoegen`.
4. Kies `Asmoke Cloud`.
5. Vul deze velden in:
   `device_id`
   optionele naam
   MQTT host
   MQTT port
   MQTT username
   MQTT password
   MQTT keepalive
6. Rond de config flow af.

## Optioneel: lokaal laten voorinvullen

Als je de brokergegevens niet steeds wilt invullen, kun je lokaal een bestand gebruiken dat niet naar Git hoort te gaan.

Gebruik als basis:

- `custom_components/asmoke_cloud/local_auth.json.example`

Ondersteunde locaties:

1. `custom_components/asmoke_cloud/local_auth.json`
2. `asmoke_cloud_local_auth.json` in de Home Assistant config-root

Ondersteunde environment variables:

- `ASMOKE_CLOUD_HOST`
- `ASMOKE_CLOUD_PORT`
- `ASMOKE_CLOUD_USERNAME`
- `ASMOKE_CLOUD_PASSWORD`
- `ASMOKE_CLOUD_KEEPALIVE`
- `ASMOKE_CLOUD_DEVICE_ID`
- `ASMOKE_CLOUD_NAME`

## Hoe je het gebruikt

Na installatie maakt de integration entities aan voor de gekozen smoker.

Praktische eerste checks:

1. Kijk of `broker connected` aan staat.
2. Kijk of `device online` aan of uit staat.
3. Zet de BBQ aan of open de Asmoke app zodat het device weer berichten publiceert.
4. Controleer of temperatuur- en statusentities waarden krijgen.

## Bediening in versie 1

Je kunt in deze eerste versie:

- temperatuur- en statusdata uitlezen;
- zien of de brokerverbinding actief is;
- zien of het device recent berichten heeft gestuurd;
- de smoke target temperature aanpassen;
- een raw action publiceren voor gecontroleerde experimenten.

## Services

Beschikbare services:

1. `asmoke_cloud.set_smoke_target_temp`
2. `asmoke_cloud.publish_raw_action`

### set_smoke_target_temp

Gebruik deze service of de number-entity om de bevestigde smoke target temperature payload te sturen.

### publish_raw_action

Gebruik deze alleen als je weet welke payload je wilt sturen. Deze service is bedoeld als gevorderde fallback en voor reverse-engineering van extra Asmoke-functies.

## Wat je ziet als de BBQ uit staat

Als de BBQ uit staat:

- blijft de integration geladen;
- blijft de brokerverbinding in principe kunnen bestaan;
- kan `device online` uit staan;
- kunnen temperatuur-entities unavailable zijn of oude waarden behouden tot nieuwe berichten binnenkomen.

Dit is normaal gedrag in deze architectuur, omdat de integration push-updates verwacht van het device.

## Problemen oplossen

### Config flow faalt direct

Controleer:

- broker host;
- broker port;
- username;
- password;
- of Home Assistant internettoegang heeft.

### Geen temperatuurdata zichtbaar

Controleer:

- of de juiste `device_id` is gebruikt;
- of de smoker aan staat;
- of de smoker recent berichten heeft gepubliceerd;
- of `broker connected` wel aan staat.

### Credentials zijn gewijzigd

Open de integration opnieuw in Home Assistant en werk de brokergegevens bij via de integratie-instellingen of reauth-flow.

## Wat nu al werkt en wat nog niet

Zie [docs/first-version.md](docs/first-version.md).
