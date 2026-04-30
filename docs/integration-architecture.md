# Home Assistant Architecture

## Short conclusion

Asmoke runs in this repository as a Home Assistant custom integration with its own connection to the vendor MQTT broker. A separate add-on is not required for normal runtime use.

## Current distribution model

- Home Assistant form: custom integration;
- HACS type: `integration`;
- domain: `asmoke_cloud`.

## Current repository structure

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
    button.py
    climate.py
    services.py
    services.yaml
    diagnostics.py
    brand/
      icon.png
      icon@2x.png
      logo.png
      logo@2x.png
    translations/
      en.json
tests/
  components/
    asmoke_cloud/
      conftest.py
      test_binary_sensor.py
      test_button.py
      test_climate.py
      test_config_flow.py
      test_diagnostics.py
      test_init.py
      test_number.py
      test_sensor.py
      test_services.py
```

## Config flow

The config flow starts by asking for the MQTT broker settings and validating that Home Assistant can log in to the Asmoke broker. After that, the user enters the smoker `device_id`.

The broker host, port, username, password, keepalive, and optional display name are collected first. The `device_id` is copied from the Asmoke app under `Me -> Device` and stored on the Home Assistant config entry.

## Reauth and options

The integration has a reauth flow for broker authentication failures and an options flow for:

- broker host;
- broker port;
- MQTT username;
- MQTT password;
- MQTT keepalive;
- `device_id`;
- `offline_timeout`;
- `debug_logging`.

When broker connection fields change, the options flow validates the MQTT
connection before saving. Saved data and options are updated together so the
config-entry update listener reloads the integration once with the new runtime
settings.

## Runtime design

The runtime lives in `AsmokeMqttRuntime` and uses its own `paho-mqtt` client. That runtime:

- validates broker connectivity;
- manages reconnect behavior;
- processes status, temperature, result, and roast topics;
- keeps shared state for entities and diagnostics;
- can keep loading even when the grill is off.

## Entities and services

The current entity platforms are:

- sensors;
- binary sensors;
- number;
- button;
- climate.

The integration exposes grill and probe temperatures, battery/roast/target data, broker status, device online state, cook activity, Wi-Fi connected state, direct button controls, climate control, and Quick target time control.

Available services:

- `publish_raw_action`;
- `set_smoke_target_temp`;
- `start_cook`;
- `stop_cook`.

## Diagnostics

Diagnostics include runtime and payload information, but redact sensitive values such as username, password, and client ID.

## Security boundary

The public repository does not contain live broker secrets. The integration no longer reads local credential files or environment variables for onboarding; users enter broker credentials through the Home Assistant config flow, and diagnostics redact sensitive values such as username, password, and client ID.

## Main limitation of the current architecture

Onboarding requires broker credentials and the device ID from the Asmoke app. No usable local LAN integration has been found that fully replaces this model.
