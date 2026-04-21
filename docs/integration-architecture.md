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
    local_auth.py
    local_auth.json.example
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

The config flow currently offers two routes:

1. `discover`
2. `manual`

For `discover`, Home Assistant temporarily logs in to the broker and listens on `device/status/+` to find a `device_id`. For `manual`, the user enters the `device_id` directly.

In the current version both routes ask for broker host, port, username, password, and keepalive, unless those values are already prefilled through local auth or environment variables.

## Reauth and options

The integration has a reauth flow for broker credentials and an `OptionsFlowWithReload` for:

- `offline_timeout`;
- `extra_topics`;
- `debug_logging`.

The options flow does not manage broker credentials.

## Runtime design

The runtime lives in `AsmokeMqttRuntime` and uses its own `paho-mqtt` client. That runtime:

- validates broker connectivity;
- manages reconnect behavior;
- processes status, temperature, result, and roast topics;
- keeps shared state for entities and diagnostics;
- can keep loading even when the grill is off.

For discovery, a temporary MQTT client is used only to find a usable `device_id` and any metadata such as grill type or firmware version.

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

The public repository does not contain live broker secrets. For local prefilling, the integration supports:

- `custom_components/asmoke_cloud/local_auth.json`;
- `asmoke_cloud_local_auth.json` in the Home Assistant config root;
- environment variables such as `ASMOKE_CLOUD_USERNAME` and `ASMOKE_CLOUD_PASSWORD`.

## Main limitation of the current architecture

Onboarding is currently semi-automatic: `device_id` discovery works, but broker credentials still need to be known or prefilled locally. No usable local LAN integration has been found that fully replaces this model.
