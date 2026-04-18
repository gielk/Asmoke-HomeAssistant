# Asmoke Onderzoeksverslag

## Doel

Doel van het onderzoek was:

1. vaststellen hoe Asmoke op het netwerk communiceert;
2. bepalen of er een bruikbare route is voor Home Assistant;
3. bevestigen of directe broker-toegang mogelijk is;
4. de topicstructuur en payloadvormen in kaart brengen.

## Publiek deel van de bevestigde bevindingen

### 1. Geen bruikbare lokale API gevonden

Er is geen stabiele lokale HTTP- of MQTT-interface op de smoker gevonden die logisch als Home Assistant LAN-integratie gebruikt kan worden. De relevante communicatie loopt via de cloud.

### 2. Relevante transportlaag is cloud MQTT

De app en smoker gebruiken raw MQTT via een cloudbroker op poort `1883`.

### 3. De smoker publiceert zelf telemetrie

De belangrijke berichten komen niet alleen via de telefoon terug. De smoker publiceert zelf status- en temperatuurupdates naar de broker.

### 4. De app publiceert commando's op een aparte action-topic

Er is een duidelijke scheiding tussen:

- telemetrie van het device;
- commando's van de app;
- result- of statusbevestigingen van het device.

### 5. Directe broker-login is haalbaar

Een directe MQTT-login met de uit de app herleide auth is lokaal bevestigd. De exacte credentials staan bewust niet in deze publieke repo.

## Bevestigde topicpatronen

- `device/status/<device_id>`
- `device/temperatures/<device_id>`
- `device/result/<device_id>`
- `asmoke/action/<device_id>`

## Bevestigde payloadvormen

### Temperatuurpayload

Voorbeeld:

```json
{"grillTemp1":135,"grillTemp2":159,"probeATemp":499,"probeBTemp":499}
```

Bevestigde velden:

- `grillTemp1`
- `grillTemp2`
- `probeATemp`
- `probeBTemp`

### Command payload

Voorbeeld:

```json
{"type":"action","command":"Smoke","data":{"targetTemp":110}}
```

### Result payload

Voorbeeld:

```json
{"type":"result","status":1,"message":"Smoke mode updated: temperature."}
```

### Statuspayload

In captures waren in ieder geval deze velden zichtbaar:

- `status`
- `batteryLevel`
- `mode`
- `wifiStatus`
- `ignitionStatus`
- `roastProgress`
- `targetTemp`
- `targetTime`
- `temperatures`

## Wat dit betekent voor Home Assistant

De kortste bruikbare route is een eigen MQTT-client in een Home Assistant custom integration. Daarmee kan Home Assistant:

- live telemetrie lezen;
- statusupdates ontvangen;
- bevestigde commando's publiceren;
- result-berichten terugkrijgen.

## Grenzen en open punten

- Niet elk commandopayload is al gevalideerd.
- Device-onboarding moet nog ontworpen worden.
- Secrets en exacte device-identifiers blijven buiten deze repo.
- Een lokale MITM- of sniffing-helper is optioneel, maar geen goede primaire runtime-architectuur.
