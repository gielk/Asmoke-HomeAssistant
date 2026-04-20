# Gebruikershandleiding

## Doel

Met deze integration verbind je Home Assistant rechtstreeks met de Asmoke cloudbroker. Daardoor kun je Asmoke-telemetrie als Home Assistant entities gebruiken zonder de mobiele app als tussenlaag.

## Voorwaarden

Je hebt nodig:

- Home Assistant `2025.1.0` of nieuwer;
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
- een cook starten in bevestigde `smoke`-, `quick`- of `roast`-modus;
- `smoke` en `quick` bedienen via een climate-entity met een gedeelde doeltemperatuur;
- een lopende cook stoppen;
- een `Stop cook` button direct vanaf het device-scherm gebruiken;
- een `Start quick cook` button gebruiken met vooraf ingestelde Quick-waarden;
- de Quick target time apart instellen voor Quick-modus;
- een raw action publiceren voor gecontroleerde experimenten.

Praktisch betekent dat:

- er nog maar één gedeelde target temperature is voor `smoke` en `quick`;
- je de gewenste cook-modus kiest via de climate preset `smoke` of `quick`;
- `Stop cook` direct als press button beschikbaar is;
- `Start quick cook` direct als press button beschikbaar is;
- alleen Quick `target_time` nog als aparte number-entity ingesteld wordt;
- je voor bevestigde acties niet altijd ruwe JSON hoeft te sturen;
- je voor onbevestigde functies nog steeds `publish_raw_action` kunt gebruiken.

## Probe niet aangesloten

Bij Asmoke lijkt de waarde `499` voor `probeATemp` of `probeBTemp` in de praktijk een sentinelwaarde te zijn voor een niet-aangesloten probe.

In deze integration wordt `499` daarom behandeld als geen geldige temperatuurwaarde.

Praktisch betekent dat:

- een probe met waarde `499` wordt niet als echte temperatuur getoond;
- de betreffende probe-entity wordt dan unavailable of leeg in plaats van `499` graden.

## Services

De voorbeelden hieronder gaan uit van een automation of script in YAML.

Als je maar een smoker in Home Assistant hebt, hoef je meestal geen `entry_id` of `device_id` mee te geven.
Heb je meerdere Asmoke-smokers gekoppeld, voeg dan een van die twee velden toe zodat de action naar het juiste device gaat.

Beschikbare services:

1. `asmoke_cloud.set_smoke_target_temp`
2. `asmoke_cloud.start_cook`
3. `asmoke_cloud.stop_cook`
4. `asmoke_cloud.publish_raw_action`

### set_smoke_target_temp

Gebruik deze service of de climate-entity om de smoke target temperature te wijzigen. In Home Assistant geef je hiervoor het veld `target_temp` mee; de integratie vertaalt dat intern naar het bevestigde vendorcommando.

Benodigd:

- `target_temp`

Voorbeeld YAML:

```yaml
action:
  - service: asmoke_cloud.set_smoke_target_temp
    data:
      target_temp: 110
```

### Climate entity

De integratie maakt nu een climate-entity aan voor de pit-bediening.

Daarin zitten:

- één gedeelde target temperature voor `smoke` en `quick`;
- een moduskiezer via climate preset modes `smoke` en `quick`;
- target temperature-stappen van 10 graden, gelijk aan de appbediening;
- `off` en `heat` als climate HVAC-modes.

Praktisch gebruik:

- kies preset `smoke` als je een gewone smoke-cook wilt starten;
- kies preset `quick` als je een quick-cook wilt starten;
- stel de temperatuur in via de climate target temperature;
- zet daarna de climate op `heat` om de gekozen modus te starten;
- zet de climate op `off` of gebruik `climate.turn_off` om een stop-commando te sturen.

Voorbeeld YAML voor Smoke via climate:

```yaml
action:
  - service: climate.set_preset_mode
    target:
      entity_id: climate.asmoke_pit_thermostat
    data:
      preset_mode: smoke
  - service: climate.set_temperature
    target:
      entity_id: climate.asmoke_pit_thermostat
    data:
      temperature: 110
  - service: climate.set_hvac_mode
    target:
      entity_id: climate.asmoke_pit_thermostat
    data:
      hvac_mode: heat
```

### Quick button entities

Voor Quick zijn nu ook entities beschikbaar:

- een number-entity voor `Quick target time`;
- een press button `Start quick cook`.

Je stelt eerst de climate target temperature en de Quick target time in en drukt daarna op de Quick-button. Die button publiceert vervolgens de bevestigde Quick-payload met die huidige waarden.

Voorbeeld YAML om de Quick-button te gebruiken:

```yaml
action:
  - service: climate.set_temperature
    target:
      entity_id: climate.asmoke_backyard_pit_thermostat
    data:
      temperature: 160
  - service: number.set_value
    target:
      entity_id: number.asmoke_backyard_quick_target_time
    data:
      value: 12
  - service: button.press
    target:
      entity_id: button.asmoke_backyard_start_quick_cook
```

### Stop button entity

Naast de service is er nu ook een press button `Stop cook`. Die publiceert dezelfde bevestigde Stop-actie, maar is handiger voor direct gebruik vanaf het device-scherm of een dashboard.

Als je liever volledig via climate werkt, kun je ook `climate.set_hvac_mode` met `off` gebruiken.

Voorbeeld YAML om de Stop-button te gebruiken:

```yaml
action:
  - service: button.press
    target:
      entity_id: button.asmoke_backyard_stop_cook
```

### start_cook

Gebruik deze service om een bevestigde cook-modus te starten.

Bevestigde waarden voor `mode`:

- `smoke`: vereist `target_temp`;
- `quick`: vereist `target_temp` en `target_time`;
- `roast`: vereist `target_temp`, `target_time`, `probe_temp`, `ingredient_category` en `k_value`.

De integratie vertaalt dit naar de bevestigde vendorpayloads:

- `smoke` -> `{"type":"action","command":"Smoke","data":{"targetTemp":...}}`
- `quick` -> `{"type":"action","command":"Quick","data":{"targetTemp":...,"targetTime":...}}`
- `roast` -> `{"type":"action","command":"Roast","data":{"targetTemp":...,"targetTime":...,"probeTemp":...,"kValue":"...","ingredientCategory":"..."}}`

De huidige Roast-ondersteuning blijft bewust strikt: de integratie exposeert alleen de exact bevestigde velden uit de capture en vult geen onbevestigde defaults in.

Voorbeeld YAML voor `smoke`:

```yaml
action:
  - service: asmoke_cloud.start_cook
    data:
      mode: smoke
      target_temp: 110
```

Voorbeeld YAML voor `quick`:

```yaml
action:
  - service: asmoke_cloud.start_cook
    data:
      mode: quick
      target_temp: 160
      target_time: 12
```

Voorbeeld YAML voor `roast`:

```yaml
action:
  - service: asmoke_cloud.start_cook
    data:
      mode: roast
      target_temp: 200
      target_time: 50
      probe_temp: 65
      ingredient_category: Beef
      k_value: "0.014"
```

### stop_cook

Gebruik deze service om een lopende cook te stoppen. De integratie publiceert hiervoor de bevestigde vendoractie `{"type":"action","command":"Stop"}`.

Benodigd:

- geen extra velden als je maar één smoker hebt;
- anders `entry_id` of `device_id`.

Voorbeeld YAML:

```yaml
action:
  - service: asmoke_cloud.stop_cook
```

### publish_raw_action

Gebruik deze alleen als je weet welke payload je wilt sturen. Deze service verwacht ruwe vendor-JSON, bijvoorbeeld `{"targetTemp":110}` voor het bevestigde Smoke-commando. Deze service is bedoeld als gevorderde fallback en voor reverse-engineering van extra Asmoke-functies.

In YAML kun je `payload` als object meegeven. In de Home Assistant service-UI is een JSON-string vaak het meest praktisch.

Benodigd:

- `command`
- optioneel `payload`

Voorbeeld YAML:

```yaml
action:
  - service: asmoke_cloud.publish_raw_action
    data:
      command: Smoke
      payload:
        targetTemp: 110
```

Voorbeeld als JSON-string:

```yaml
action:
  - service: asmoke_cloud.publish_raw_action
    data:
      command: Smoke
      payload: '{"targetTemp":110}'
```

## Entities voor bediening

Naast services maakt de integratie ook directe bedienings-entities aan:

- `climate.<naam>_pit_thermostat`
- `number.<naam>_quick_target_time`
- `button.<naam>_start_quick_cook`
- `button.<naam>_stop_cook`

De exacte entity IDs hangen af van je device name in Home Assistant. Controleer ze altijd even in Ontwikkelaarstools of op het device-scherm.

## Automation-voorbeelden

Voor complete voorbeelden met notificaties en YAML zie [automation-examples.md](automation-examples.md).

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

De options flow in deze versie beheert alleen `offline_timeout`, `extra_topics` en `debug_logging`. Als brokercredentials zijn gewijzigd, voeg de integratie opnieuw toe met de nieuwe waarden. Gebruik de reauth-flow alleen als Home Assistant die expliciet aanbiedt.

## Wat nu al werkt en wat nog niet

Zie [first-version.md](first-version.md).

## Firmwareversie

In de tot nu toe bevestigde captures is nog geen duidelijk firmwareveld gezien. Als Asmoke later wel een herkenbaar firmwareveld in de statuspayload meestuurt, pakt de integratie dat automatisch op voor device info.
