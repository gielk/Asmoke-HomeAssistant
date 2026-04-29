# User Guide

## Overview

This integration connects Home Assistant directly to the Asmoke cloud broker, so you can expose Asmoke telemetry and controls in Home Assistant without depending on the mobile app during normal runtime.

## Requirements

You need:

- Home Assistant `2025.1.0` or newer;
- HACS or a manual custom component installation;
- the broker credentials for your Asmoke device, or those values prefilled locally;
- internet access from Home Assistant to the Asmoke broker.

The grill does not need to be powered on to install the integration. If the grill is off, the integration will still load, but no live telemetry updates will come in.

Important: the MQTT username and password are intentionally not stored in the public repository. If they are not already available in a private local auth file, contact the maintainer directly for setup help.

## Installation via HACS

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository.
3. Choose type `integration`.
4. Install `Asmoke Cloud`.
5. Restart Home Assistant.

## Manual installation

1. Copy `custom_components/asmoke_cloud` into your Home Assistant configuration directory under `custom_components/asmoke_cloud`.
2. Restart Home Assistant.

## Dashboard and YAML examples

The repository includes the following documentation for the current entity set:

- [custom-card.md](custom-card.md) for the included Asmoke dashboard cards;
- [dashboard-example.md](dashboard-example.md) for a complete Lovelace view with dashboard YAML;
- [dashboard-example.yaml](dashboard-example.yaml) as a directly copyable YAML file;
- [automation-examples.md](automation-examples.md) for updated automations and helper-driven examples.

## Initial configuration

1. Open Home Assistant.
2. Go to `Settings -> Devices & Services`.
3. Click `Add Integration`.
4. Choose `Asmoke Cloud`.
5. Read the prerequisites screen in the config flow.
6. Choose one of these routes:
  `Auto-discover device ID`
  `Enter device ID manually`
7. For auto discovery:
  optionally enter a name;
  verify host, port, username, password, and keepalive;
  turn on the smoker;
  open the Asmoke app on a phone connected to the same local network as the smoker;
  wait for Home Assistant to collect candidate Asmoke devices for about 45 seconds;
  select the discovered device that belongs to your smoker.
8. For manual entry:
  enter `device_id`;
  optionally enter a name;
  verify host, port, username, password, and keepalive.
9. Complete the config flow.

## Where do these values come from?

You do not get these values from Home Assistant itself. In practice, the required connection details need to come from a private local auth file, prior setup information you already have, or direct setup help from the maintainer.

In practice you need the following values:

- `device_id`
- `host`
- `port`
- `username`
- `password`
- `keepalive`

If you already captured or stored those values, the easiest route is to prefill them locally through a `local_auth.json` file so you do not have to type them manually in the config flow.

If you do not have them yet, do not expect to find them in the public repository. The intended path is to request setup help from the maintainer instead of trying to discover public credentials in the repo.

The integration can try to discover `device_id` automatically by temporarily listening for Asmoke device messages, but that only works if Home Assistant can already log in with valid broker credentials. Discovery shows candidates for confirmation before creating the config entry.

This repository intentionally does not ship vendor-shared MQTT credentials as public defaults. If you already have those values privately, you can prefill them locally and let discovery learn only the `device_id`.

## Optional local prefilling

If you do not want to enter the broker credentials every time, you can use a local file that stays out of Git.

Use this as a base:

- `custom_components/asmoke_cloud/local_auth.json.example`

`device_id` is optional in this file if you want to use discovery.

Supported locations:

1. `custom_components/asmoke_cloud/local_auth.json`
2. `asmoke_cloud_local_auth.json` in the Home Assistant config root

Supported environment variables:

- `ASMOKE_CLOUD_HOST`
- `ASMOKE_CLOUD_PORT`
- `ASMOKE_CLOUD_USERNAME`
- `ASMOKE_CLOUD_PASSWORD`
- `ASMOKE_CLOUD_KEEPALIVE`
- `ASMOKE_CLOUD_DEVICE_ID`
- `ASMOKE_CLOUD_NAME`

## What gets created

After installation, the integration creates entities for the selected smoker.

Main entities you will typically use:

- `climate.asmoke_backyard_pit_thermostat` for smoke and quick with a shared target temperature;
- `number.asmoke_backyard_quick_target_time` for Quick target time;
- `binary_sensor.asmoke_backyard_cook_active` as the recommended on/off state for the running cook;
- `binary_sensor.asmoke_backyard_wi_fi_connected` as a simple Wi-Fi connected flag, not as signal strength;
- `sensor.asmoke_backyard_target_time` for the target time reported by the smoker;
- `button.asmoke_backyard_start_quick_cook` to start a Quick cook directly;
- `button.asmoke_backyard_stop_cook` to send Stop directly.

The easiest dashboard start is the included custom card set:

```yaml
- type: custom:asmoke-smoker-card

- type: custom:asmoke-smoker-history-card
  hours_to_show: 6

- type: custom:asmoke-smoker-session-card
  hours_to_show: 24
```

If you have multiple Asmoke smokers, select the smoker by `device_id` or
`climate`. See [custom-card.md](custom-card.md) for loading instructions and
optional entity overrides.

The cards are designed for the first dashboard setup. You can still build your
own dashboard with the individual Home Assistant entities if you want a more
custom layout.

Recommended first checks:

1. Check whether `broker connected` is on.
2. Check whether `device online` is on or off.
3. Check whether `cook active` is off while no cook is running.
4. Turn on the grill or open the Asmoke app so the device starts publishing messages again.
5. Check whether temperature, target time, and status entities receive values.

## Status interpretation

For dashboards and automations, this is the most important distinction:

- use `binary_sensor...cook_active` when the question is whether a cook is running;
- use `binary_sensor...wi_fi_connected` only as a connected/disconnected indication for the Wi-Fi module;
- use `sensor...mode` only as informational vendor status;
- use `binary_sensor...ignition_active` only as a low-level signal, not as the main on/off state.

The reason is that after a stop, Asmoke can keep reporting an old `mode` such as `QUICK`, while the real status is already `idle`. The integration therefore derives `cook_active` from the confirmed runtime status.

## Current control surface

In the current version you can:

- read temperature and status data;
- see whether the broker connection is active;
- see whether the device has published messages recently;
- see whether a cook is really active through `Cook active`;
- start a cook in confirmed `smoke`, `quick`, or `roast` mode;
- control `smoke` and `quick` through a climate entity with a shared target temperature;
- stop a running cook;
- use a `Stop cook` button directly from the device page or a dashboard;
- use a `Start quick cook` button with the current Quick values;
- set Quick target time separately for Quick mode, both as an idle preset and live during an active Quick cook;
- publish a raw action for controlled experiments.

In practical terms:

- there is only one shared target temperature for `smoke` and `quick`;
- you choose the desired cook mode through the climate preset `smoke` or `quick`;
- `cook_active` is the recommended automation state for on or off;
- `Stop cook` is available directly as a press button;
- `Start quick cook` is available directly as a press button;
- only Quick `target_time` remains as a separate number entity;
- during an active Quick cook, the Quick number follows the smoker target time live and can update it directly;
- for confirmed actions you do not always need to send raw JSON;
- for unconfirmed functionality you can still use `publish_raw_action`.

## Disconnected probes

On Asmoke, the value `499` for `probeATemp` or `probeBTemp` appears to be a sentinel value for a disconnected probe.

In this integration, `499` is therefore treated as not being a valid temperature.

In practice this means:

- a probe with value `499` is not shown as a real temperature;
- the corresponding probe entity becomes unavailable or empty instead of showing `499` degrees.

## Services

The examples below assume an automation or script in YAML.

If you only have one smoker in Home Assistant, you usually do not need to provide `entry_id` or `device_id`.
If you have multiple Asmoke smokers connected, add one of those fields so the action goes to the correct device.

Available services:

1. `asmoke_cloud.set_smoke_target_temp`
2. `asmoke_cloud.start_cook`
3. `asmoke_cloud.stop_cook`
4. `asmoke_cloud.publish_raw_action`

### set_smoke_target_temp

Use this service, or the climate entity, to change the smoke target temperature. In Home Assistant you pass the field `target_temp`; the integration maps that internally to the confirmed vendor command.

Required:

- `target_temp`

Example YAML:

```yaml
action:
  - service: asmoke_cloud.set_smoke_target_temp
    data:
      target_temp: 110
```

### Climate entity

The integration now creates a climate entity for pit control.

It includes:

- one shared target temperature for `smoke` and `quick`;
- mode selection through the climate preset modes `smoke` and `quick`;
- target temperature steps of 10 degrees, matching the app behavior;
- `off` and `heat` as climate HVAC modes.

Practical usage:

- choose preset `smoke` to start a normal smoke cook;
- choose preset `quick` to start a Quick cook;
- set the temperature through the climate target temperature;
- then set the climate to `heat` to start the selected mode;
- set the climate to `off` or use `climate.turn_off` to send a stop command;
- the climate also stays truly `off` once the smoker reports `status: idle`, even if the vendor `mode` still keeps an older value.

Example YAML for Smoke through climate:

```yaml
action:
  - service: climate.set_preset_mode
    target:
      entity_id: climate.asmoke_backyard_pit_thermostat
    data:
      preset_mode: smoke
  - service: climate.set_temperature
    target:
      entity_id: climate.asmoke_backyard_pit_thermostat
    data:
      temperature: 110
  - service: climate.set_hvac_mode
    target:
      entity_id: climate.asmoke_backyard_pit_thermostat
    data:
      hvac_mode: heat
```

### Quick button entities

For Quick mode, the following entities are available:

- a number entity for `Quick target time`;
- a sensor for the `Target time` reported by the smoker;
- a `Start quick cook` press button.

First set the climate target temperature and the Quick target time, then press the Quick button. That button publishes the confirmed Quick payload with those current values.

If a Quick cook is already running, `number.quick_target_time` no longer acts only as a local preset:

- the number follows the current device `target_time`;
- a change through `number.set_value` publishes a live Quick update directly to the smoker;
- the separate `sensor.target_time` keeps showing the raw device telemetry.

Example YAML to use the Quick button:

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

Example YAML to extend an active Quick cook live:

```yaml
action:
  - service: number.set_value
    target:
      entity_id: number.asmoke_backyard_quick_target_time
    data:
      value: 90
```

### Stop button entity

In addition to the service, there is now also a `Stop cook` press button. It publishes the same confirmed Stop action, but is more convenient for direct use from the device page or a dashboard.

If you prefer to work entirely through climate, you can also use `climate.set_hvac_mode` with `off`.

Example YAML to use the Stop button:

```yaml
action:
  - service: button.press
    target:
      entity_id: button.asmoke_backyard_stop_cook
```

### start_cook

Use this service to start a confirmed cook mode.

Confirmed values for `mode`:

- `smoke`: requires `target_temp`;
- `quick`: requires `target_temp` and `target_time`;
- `roast`: requires `target_temp`, `target_time`, `probe_temp`, `ingredient_category`, and `k_value`.

The integration maps this to the confirmed vendor payloads:

- `smoke` -> `{"type":"action","command":"Smoke","data":{"targetTemp":...}}`
- `quick` -> `{"type":"action","command":"Quick","data":{"targetTemp":...,"targetTime":...}}`
- `roast` -> `{"type":"action","command":"Roast","data":{"targetTemp":...,"targetTime":...,"probeTemp":...,"kValue":"...","ingredientCategory":"..."}}`

The current Roast support intentionally stays strict: the integration only exposes the exact confirmed fields from the capture and does not fill in unconfirmed defaults.

Example YAML for `smoke`:

```yaml
action:
  - service: asmoke_cloud.start_cook
    data:
      mode: smoke
      target_temp: 110
```

Example YAML for `quick`:

```yaml
action:
  - service: asmoke_cloud.start_cook
    data:
      mode: quick
      target_temp: 160
      target_time: 12
```

Example YAML for `roast`:

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

Use this service to stop a running cook. The integration publishes the confirmed vendor action `{"type":"action","command":"Stop"}`.

Required:

- no extra fields if you only have one smoker;
- otherwise `entry_id` or `device_id`.

Example YAML:

```yaml
action:
  - service: asmoke_cloud.stop_cook
```

### publish_raw_action

Only use this if you know which payload you want to send. This service expects raw vendor JSON, for example `{"targetTemp":110}` for the confirmed Smoke command. It is intended as an advanced fallback and for reverse engineering additional Asmoke functions.

In YAML you can pass `payload` as an object. In the Home Assistant service UI, a JSON string is often the most practical.

Required:

- `command`
- optional `payload`

Example YAML:

```yaml
action:
  - service: asmoke_cloud.publish_raw_action
    data:
      command: Smoke
      payload:
        targetTemp: 110
```

Example as a JSON string:

```yaml
action:
  - service: asmoke_cloud.publish_raw_action
    data:
      command: Smoke
      payload: '{"targetTemp":110}'
```

## Direct control entities

Besides services, the integration also creates direct control entities:

- `climate.<name>_pit_thermostat`
- `number.<name>_quick_target_time`
- `button.<name>_start_quick_cook`
- `button.<name>_stop_cook`

The exact entity IDs depend on the device name in Home Assistant. Always verify them in Developer Tools or on the device page.

## Automation examples

For complete examples with notifications and YAML, see [automation-examples.md](automation-examples.md).

## When the grill is off

When the grill is off:

- the integration remains loaded;
- the broker connection may still remain established;
- `device online` can be off;
- temperature entities can become unavailable or keep older values until new messages arrive.

This is normal behavior in this architecture, because the integration expects push updates from the device.

## Troubleshooting

### The config flow fails immediately

Check:

- broker host;
- broker port;
- username;
- password;
- whether Home Assistant has internet access.

### No temperature data is visible

Check:

- whether the correct `device_id` is in use;
- whether the smoker is on;
- whether the smoker has published messages recently;
- whether `broker connected` is on.

### Discovery finds no device

Check:

- whether the broker credentials are correct;
- whether the grill is on or has just been woken through the app;
- whether Home Assistant has internet access;
- whether a fresh status message was actually sent by the smoker during discovery.

### Credentials changed

In this version, the options flow only manages `offline_timeout`, `extra_topics`, and `debug_logging`. If broker credentials changed, add the integration again with the new values. Only use the reauth flow if Home Assistant explicitly offers it.

## What already works and what does not yet

See [first-version.md](first-version.md).

## Firmware version

In the captures confirmed so far, no clearly identifiable firmware field has been seen yet. If Asmoke later starts including a recognizable firmware field in the status payload, the integration will pick it up automatically for device info.
