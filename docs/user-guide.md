# Gebruikershandleiding

## Doel

Met deze integration verbind je Home Assistant rechtstreeks met de Asmoke cloudbroker. Daardoor kun je Asmoke-telemetrie als Home Assistant entities gebruiken zonder de mobiele app als tussenlaag.

## Voorwaarden

Je hebt nodig:

- een werkende Home Assistant installatie;
- HACS of handmatige custom component installatie;
- de brokergegevens die bij jouw Asmoke-opstelling horen of lokaal zijn vooringevuld;
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
5. Kies een van deze routes:
   `Discover Asmoke device`
   `Enter device ID manually`
6. Bij discovery:
   vul optioneel een naam in;
   controleer host, port, username, password en keepalive;
   zet de BBQ aan of open de Asmoke app;
   wacht tot Home Assistant een statusbericht ziet en het `device_id` automatisch leert.
7. Bij handmatige invoer:
   vul `device_id` in;
   vul optioneel een naam in;
   controleer host, port, username, password en keepalive.
8. Rond de config flow af.

## Waar haal je deze gegevens vandaan?

Je haalt deze gegevens niet uit Home Assistant zelf. Voor deze Asmoke integration komen ze uit de Asmoke app-verkeersanalyse of uit een lokaal bestand waarin je ze eerder hebt opgeslagen.

Voor jouw huidige Asmoke-opstelling zijn deze waarden al eerder bevestigd:

- `device_id`: jouw Asmoke device-id
- `host`: de Asmoke MQTT broker host
- `port`: de Asmoke MQTT broker poort
- `username`: de Asmoke app MQTT username
- `password`: de Asmoke app MQTT password
- `keepalive`: de gebruikte MQTT keepalive

Als je deze waarden al eerder hebt vastgelegd, is de makkelijkste route om ze lokaal te laten voorinvullen via een `local_auth.json` bestand. Dan hoef je ze in de config flow niet handmatig over te typen.

Als je ze nog niet hebt, dan zijn er praktisch twee routes:

1. gebruik de eerder lokaal vastgelegde waarden uit je reverse-engineeringnotities;
2. of herhaal een packet capture / MITM-analyse om de app-verbinding opnieuw te bevestigen.

De integration kan nu wel automatisch het `device_id` proberen te ontdekken door tijdelijk naar `device/status/+` te luisteren. Dat werkt alleen als Home Assistant al met geldige brokercredentials kan inloggen.

De repository levert bewust geen vendor-shared MQTT credentials als publieke standaard mee. Als je die gegevens privé al kent, kun je ze lokaal voorinvullen en hoeft discovery meestal alleen nog het `device_id` te leren.

## Optioneel: lokaal laten voorinvullen

Als je de brokergegevens niet steeds wilt invullen, kun je lokaal een bestand gebruiken dat niet naar Git hoort te gaan.

Gebruik als basis:

- `custom_components/asmoke_cloud/local_auth.json.example`

Het `device_id` is optioneel in dit bestand als je discovery wilt gebruiken.

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

## Probe niet aangesloten

Bij Asmoke lijkt de waarde `499` voor `probeATemp` of `probeBTemp` in de praktijk een sentinelwaarde te zijn voor een niet-aangesloten probe.

In deze integration wordt `499` daarom behandeld als geen geldige temperatuurwaarde.

Praktisch betekent dat:

- een probe met waarde `499` wordt niet als echte temperatuur getoond;
- de betreffende probe-entity wordt dan unavailable of leeg in plaats van `499` graden.

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

### Discovery vindt geen device

Controleer:

- of de brokercredentials kloppen;
- of de BBQ aan staat of net via de app is gewekt;
- of Home Assistant internettoegang heeft;
- of er tijdens discovery echt een nieuw statusbericht van de smoker is verstuurd.

### Credentials zijn gewijzigd

Open de integration opnieuw in Home Assistant en werk de brokergegevens bij via de integratie-instellingen of reauth-flow.

## Wat nu al werkt en wat nog niet

Zie [docs/first-version.md](docs/first-version.md).

## Firmwareversie

In de tot nu toe bevestigde captures is nog geen duidelijk firmwareveld gezien. Als Asmoke later wel een herkenbaar firmwareveld in de statuspayload meestuurt, pakt de integratie dat automatisch op voor device info.
