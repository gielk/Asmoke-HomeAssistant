# Version 1 Overview

## Current capabilities

The current integration supports:

1. installation as a custom integration;
2. adding the integration through the Home Assistant config flow;
3. semi-automatic discovery of the `device_id` through temporary MQTT listening;
4. connecting to the Asmoke cloud MQTT broker;
5. subscribing to confirmed status, temperatures, and result topics;
6. creating entities for the main telemetry data;
7. diagnostics with sensitive data redacted;
8. an options flow for debug logging, extra topics, and offline timeout;
9. confirmed start actions for smoke, quick, and roast cooks;
10. a confirmed stop action for a running cook;
11. a raw action service for advanced use;
12. loading even when the grill is off;
13. a climate entity with a shared target temperature and `smoke`/`quick` mode selection;
14. a `Stop cook` button entity and a `Start quick cook` button entity;
15. a `Cook active` binary sensor to answer whether a cook is really running;
16. Quick target time through a number entity that works as an idle preset and can update live during an active Quick cook.

## Entity coverage

Available entity types:

- sensors for grill temperature 1 and 2;
- sensors for probe A and probe B temperature;
- a battery level sensor;
- a roast progress sensor;
- a target time sensor;
- a mode sensor;
- a last result message sensor;
- a broker connected binary sensor;
- a device online binary sensor;
- a cook active binary sensor;
- a Wi-Fi connected binary sensor;
- an ignition active binary sensor;
- a pit thermostat climate entity;
- a Quick target time number entity;
- a Stop cook button entity;
- a Start quick cook button entity.

## Confirmed write paths

Confirmed and implemented:

- smoke and quick through a shared climate target temperature;
- smoke and quick mode selection through climate preset modes;
- Quick target time through a dedicated number entity;
- live Quick target time updates through that same number entity during an active Quick cook;
- smoke target temperature through `asmoke_cloud.set_smoke_target_temp`;
- cook start through `asmoke_cloud.start_cook` with confirmed `smoke`, `quick`, and `roast` modes;
- cook stop through `asmoke_cloud.stop_cook`;
- smoke start through the climate entity in the `smoke` preset;
- quick start through the climate entity in the `quick` preset;
- stop cook through a press button entity;
- quick start through a press button entity that uses the current Quick number values.

## Known data interpretations

- `probeATemp = 499` is treated as probe disconnected;
- `probeBTemp = 499` is treated as probe disconnected;
- `status: idle` is the authoritative off state even if `mode` still contains an older value such as `QUICK`;
- `wifiStatus` is currently treated as a connected/disconnected flag and not as usable Wi-Fi signal strength;
- `binary_sensor.cook_active` is therefore the recommended automation and dashboard signal for on/off.

## Current limitations

Not yet fully implemented in version 1:

1. fully hands-off onboarding without broker credentials;
2. broad support for all Asmoke modes and commands beyond `smoke`, `quick`, `roast`, and `stop`;
3. full mapping of all status fields;
4. confirmed firmware version detection;
5. firmware updates;
6. UI polish and broader end-user diagnostics;
7. inclusion in the HACS default store.

## Important boundaries

1. This integration uses cloud MQTT, not a local LAN API.
2. Broker credentials are sensitive and do not belong in a public repository.
3. If the grill is off, the integration remains loaded but no new push updates arrive.
4. `publish_raw_action` is powerful, but also riskier than the confirmed standard actions.
