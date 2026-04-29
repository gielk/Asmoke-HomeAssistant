# Asmoke Dashboard Cards

The integration includes custom Lovelace cards for a compact Asmoke dashboard.
They are designed to feel close to current Home Assistant tile dashboards:
rounded tiles, clear status chips, BBQ-inspired history visuals, light and dark
theme support, and no extra frontend dependency.

## Cards

### Asmoke Smoker Card

```yaml
type: custom:asmoke-smoker-card
climate: climate.asmoke_backyard_pit_thermostat
```

Shows live pit control, Quick target time, start/stop buttons, grill and probe
temperature tiles, broker/device/Wi-Fi status, battery, and last result.

### Asmoke Temperature History

```yaml
type: custom:asmoke-smoker-history-card
climate: climate.asmoke_backyard_pit_thermostat
hours_to_show: 6
```

Shows a BBQ-style temperature chart for Grill 1, Grill 2, Probe A, and Probe B.
It also shows pit average, peak temperature, probe peak, current target, and a
manual refresh chip.

### Asmoke Cook Sessions

```yaml
type: custom:asmoke-smoker-session-card
climate: climate.asmoke_backyard_pit_thermostat
hours_to_show: 24
```

Shows historical cook runtime from `binary_sensor...cook_active`, including a
timeline, total runtime, cook count, longest cook, current/idle state, and the
latest sessions.

## Loading the cards

After installing or updating the integration, restart Home Assistant. The
integration serves the card at:

```text
/asmoke_cloud/frontend/asmoke-smoker-card.js
```

The integration also tries to register this JavaScript module with the Home
Assistant frontend automatically. If Home Assistant was already open in your
browser or mobile app, refresh the page or fully close and reopen the app.

If the cards do not appear in the card picker, add the module manually as a dashboard
resource:

1. Open `Settings -> Dashboards`.
2. Open the three-dot menu and choose `Resources`.
3. Add this resource:

```yaml
url: /asmoke_cloud/frontend/asmoke-smoker-card.js
type: module
```

## Minimal dashboard YAML

```yaml
- type: custom:asmoke-smoker-card
  climate: climate.asmoke_backyard_pit_thermostat

- type: custom:asmoke-smoker-history-card
  climate: climate.asmoke_backyard_pit_thermostat
  hours_to_show: 6

- type: custom:asmoke-smoker-session-card
  climate: climate.asmoke_backyard_pit_thermostat
  hours_to_show: 24
```

In most installs this is enough. The card derives the related Asmoke entities
from the climate entity prefix. For example:

```text
climate.asmoke_backyard_pit_thermostat -> asmoke_backyard
```

## Optional overrides

Use overrides on any of the three cards if Home Assistant renamed one of your
entities or if you want a different title.

```yaml
type: custom:asmoke-smoker-card
name: Backyard smoker
climate: climate.asmoke_backyard_pit_thermostat
quick_time: number.asmoke_backyard_quick_target_time
start_quick: button.asmoke_backyard_start_quick_cook
stop: button.asmoke_backyard_stop_cook
cook_active: binary_sensor.asmoke_backyard_cook_active
device_online: binary_sensor.asmoke_backyard_device_online
broker_connected: binary_sensor.asmoke_backyard_broker_connected
```

Advanced entity overrides are also supported:

```yaml
grill_temp_1: sensor.asmoke_backyard_grill_temperature_1
grill_temp_2: sensor.asmoke_backyard_grill_temperature_2
probe_a_temp: sensor.asmoke_backyard_probe_a_temperature
probe_b_temp: sensor.asmoke_backyard_probe_b_temperature
battery: sensor.asmoke_backyard_battery_level
target_time: sensor.asmoke_backyard_target_time
mode: sensor.asmoke_backyard_mode
wifi_connected: binary_sensor.asmoke_backyard_wi_fi_connected
last_result: sensor.asmoke_backyard_last_result_message
```

History-specific options:

```yaml
hours_to_show: 12
refresh_interval: 300
min_temp: 0
max_temp: 300
```

`refresh_interval` is in seconds. The history cards use Home Assistant recorder
history, so their data depends on the recorder retention and includes only data
that Home Assistant has already stored.

## Card picker

Once the module is loaded, Home Assistant can show these cards in the custom
card picker:

- `Asmoke Smoker Card`
- `Asmoke Temperature History`
- `Asmoke Cook Sessions`

The built-in editors expose the most important fields. For advanced overrides,
use YAML mode.
