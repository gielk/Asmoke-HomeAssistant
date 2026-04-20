# Home Assistant Architectuur

## Korte conclusie

Asmoke draait in deze repo als Home Assistant custom integration met een eigen verbinding naar de vendor MQTT-broker. Een add-on is niet nodig voor de normale runtime.

## Huidige distributievorm

- Home Assistant vorm: custom integration;
- HACS type: `integration`;
- domein: `asmoke_cloud`.

## Actuele repositorystructuur

```text
custom_components/
  asmoke_cloud/
    __init__.py
    manifest.json
    const.py
    config_flow.py
    coordinator.py
    mqtt.py
    entity.py
    sensor.py
    binary_sensor.py
    number.py
    services.py
    services.yaml
    diagnostics.py
    local_auth.py
    local_auth.json.example
    translations/
      en.json
tests/
  components/
    asmoke_cloud/
      conftest.py
      test_config_flow.py
      test_diagnostics.py
      test_init.py
      test_sensor.py
      test_services.py
```

## Config flow

De config flow biedt nu twee routes:

1. `discover`
2. `manual`

Bij `discover` logt Home Assistant tijdelijk in op de broker en luistert kort op `device/status/+` om een `device_id` te vinden. Bij `manual` vult de gebruiker het `device_id` zelf in.

Beide routes vragen in de huidige versie broker host, port, username, password en keepalive, tenzij die al lokaal zijn vooringevuld via local auth of environment variables.

## Reauth en options

De integratie heeft een reauth-flow voor brokercredentials en een `OptionsFlowWithReload` voor:

- `offline_timeout`;
- `extra_topics`;
- `debug_logging`.

De options flow beheert dus geen brokercredentials.

## Runtime-ontwerp

De runtime zit in `AsmokeMqttRuntime` en gebruikt een eigen `paho-mqtt` client. Die runtime:

- valideert brokerconnectiviteit;
- beheert reconnectgedrag;
- verwerkt status-, temperatuur- en result-topics;
- houdt gedeelde state bij voor entities en diagnostics;
- blijft kunnen laden ook als de BBQ uit staat.

Voor discovery wordt tijdelijk een losse MQTT-client gebruikt die alleen zoekt naar een bruikbaar `device_id` en eventuele metadata zoals grill type of firmwareversie.

## Entities en services

De actuele platforms zijn:

- sensors;
- binary sensors;
- number.

Daarmee exposeert de integratie onder meer grill- en probetemperaturen, battery/roast/targetinformatie, brokerstatus, device-online status en een number entity voor smoke target temperature.

Beschikbare services:

- `publish_raw_action`;
- `set_smoke_target_temp`.

## Diagnostics

Diagnostics bevatten runtime- en payloadinformatie, maar redigeren gevoelige velden zoals username, password en client-id.

## Security-grens

Publieke repo-inhoud bevat geen live brokersecrets. Voor lokaal voorinvullen gebruikt de integratie:

- `custom_components/asmoke_cloud/local_auth.json`;
- `asmoke_cloud_local_auth.json` in de Home Assistant config-root;
- environment variables zoals `ASMOKE_CLOUD_USERNAME` en `ASMOKE_CLOUD_PASSWORD`.

## Belangrijkste beperking van de huidige architectuur

Onboarding is nu semi-automatisch: `device_id` discovery werkt, maar brokercredentials moeten nog steeds bekend zijn of lokaal worden vooringevuld. Er is geen bruikbare lokale LAN-integratie gevonden die dit volledig vervangt.
