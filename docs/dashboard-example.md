# Dashboard Example

This document matches the current Asmoke entity set and uses:

- the climate entity for smoke and quick;
- `number.quick_target_time` as the Quick input;
- `binary_sensor.cook_active` as the clean cook status;
- the current `Start quick cook` and `Stop cook` button entities.

## Usage

1. Copy the YAML from [docs/dashboard-example.yaml](docs/dashboard-example.yaml).
2. Replace every instance of the `asmoke_backyard` slug with the entity prefix of your device.
3. Paste the content into a YAML dashboard or include the view under `views:` in your existing Lovelace configuration.

## What this dashboard shows

- central pit control through the climate card;
- a dedicated Quick target time control;
- quick start and stop buttons;
- a status block for broker, device, and cook activity;
- gauges for grill and probe temperatures;
- a compact live telemetry card;
- a history graph for the main temperatures.

## Important note

For dashboards and automations, prefer `binary_sensor...cook_active` when the question is whether the smoker is actually on or off. The separate `sensor...mode` is still useful as vendor information, but it can continue showing an old mode for a short time after Stop.