# Dashboard Example

This document matches the current Asmoke entity set and uses:

- the included custom Asmoke Smoker Card as the primary dashboard card;
- included BBQ-style history cards for temperature curves and cook sessions;
- the climate entity for smoke and quick;
- `number.quick_target_time` as the Quick input;
- `binary_sensor.cook_active` as the clean cook status;
- the current `Start quick cook` and `Stop cook` button entities.

## Usage

1. Restart Home Assistant after installing or updating the integration so the custom card module can load.
2. Copy the YAML from [dashboard-example.yaml](dashboard-example.yaml).
3. Replace every instance of the `asmoke_backyard` slug with the entity prefix of your device.
4. Paste the content into a YAML dashboard or include the view under `views:` in your existing Lovelace configuration.

If the custom card is not available in the picker yet, see [custom-card.md](custom-card.md).

For a single Asmoke smoker, the custom cards can also be added without entity
YAML. The longer example keeps explicit entities so it remains easy to adapt and
inspect.

## What this dashboard shows

- central pit control through the climate card;
- a compact tile-style Asmoke Smoker Card;
- compact historical temperature and session cards;
- a dedicated Quick target time control;
- quick start and stop buttons;
- a status block for broker, device, and cook activity;
- gauges for grill and probe temperatures;
- a compact live telemetry card;
- optional detailed entity cards for deeper checks.

## Important note

For dashboards and automations, prefer `binary_sensor...cook_active` when the question is whether the smoker is actually on or off. The separate `sensor...mode` is still useful as vendor information, but it can continue showing an old mode for a short time after Stop.
