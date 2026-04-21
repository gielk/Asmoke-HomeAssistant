# Automation Examples

These examples are updated for the current entity set, with:

- `binary_sensor...cook_active` as the recommended on/off signal;
- `climate...pit_thermostat` for smoke and quick;
- `number...quick_target_time`, which can publish live updates during an active Quick cook;
- `sensor...target_time` as the reported device target time.

Always replace these placeholders first:

- `binary_sensor.asmoke_backyard_broker_connected`
- `binary_sensor.asmoke_backyard_device_online`
- `binary_sensor.asmoke_backyard_cook_active`
- `climate.asmoke_backyard_pit_thermostat`
- `button.asmoke_backyard_stop_cook`
- `button.asmoke_backyard_start_quick_cook`
- `number.asmoke_backyard_quick_target_time`
- `sensor.asmoke_backyard_target_time`
- `sensor.asmoke_backyard_mode`
- `sensor.asmoke_backyard_probe_a_temperature`
- `sensor.asmoke_backyard_grill_temperature_1`
- `sensor.asmoke_backyard_last_result_message`
- `notify.mobile_app_your_phone`
- `input_boolean.asmoke_stop_requested`
- `input_boolean.asmoke_extend_quick_15`

## 1. Notification when the smoker goes offline

```yaml
alias: Asmoke smoker offline
description: Notify when the smoker has not sent cloud updates for 10 minutes.
trigger:
  - platform: state
    entity_id: binary_sensor.asmoke_backyard_device_online
    to: "off"
    for: "00:10:00"
action:
  - service: notify.mobile_app_your_phone
    data:
      title: Asmoke offline
      message: The smoker has not sent any status updates for 10 minutes.
mode: single
```

## 2. Notification when a cook starts or stops

Use `cook_active` intentionally here instead of `sensor.mode`, because the vendor mode can remain sticky after Stop.

```yaml
alias: Asmoke cook status changed
description: Send a notification when a cook really starts or stops.
trigger:
  - platform: state
    entity_id: binary_sensor.asmoke_backyard_cook_active
condition:
  - condition: template
    value_template: >-
      {{ trigger.to_state is not none
         and trigger.to_state.state in ['on', 'off']
         and trigger.from_state is not none
         and trigger.from_state.state != trigger.to_state.state }}
action:
  - service: notify.mobile_app_your_phone
    data:
      title: Asmoke cook status
      message: >-
        {% if trigger.to_state.state == 'on' %}
          A cook is now running. Mode: {{ states('sensor.asmoke_backyard_mode') }}.
        {% else %}
          The cook stopped or finished. Last mode: {{ states('sensor.asmoke_backyard_mode') }}.
        {% endif %}
mode: queued
```

## 3. Notification when probe A reaches the target internal temperature

```yaml
alias: Asmoke probe A target reached
description: Notify only during an active cook when probe A rises above the target value.
trigger:
  - platform: numeric_state
    entity_id: sensor.asmoke_backyard_probe_a_temperature
    above: 65
    for: "00:01:00"
condition:
  - condition: state
    entity_id: binary_sensor.asmoke_backyard_cook_active
    state: "on"
action:
  - service: notify.mobile_app_your_phone
    data:
      title: Asmoke target reached
      message: >-
        Probe A is {{ states('sensor.asmoke_backyard_probe_a_temperature') }} C and has now gone above 65 C.
mode: single
```

Note: because the integration already converts `499` into no valid probe value, this example does not generate a false alert for a disconnected probe.

## 4. Start a smoke cook through the climate preset

```yaml
alias: Asmoke start smoke through climate
description: Start a smoke cook at a fixed time through the climate entity.
trigger:
  - platform: time
    at: "17:30:00"
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
  - service: notify.mobile_app_your_phone
    data:
      title: Asmoke smoke started
      message: Smoke cook started at 110 C.
mode: single
```

## 5. Start a Quick cook through climate plus button

```yaml
alias: Asmoke quick 12 minutes
description: Set temperature and Quick target time, then start Quick.
trigger:
  - platform: time
    at: "18:00:00"
action:
  - service: climate.set_preset_mode
    target:
      entity_id: climate.asmoke_backyard_pit_thermostat
    data:
      preset_mode: quick
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
  - service: notify.mobile_app_your_phone
    data:
      title: Asmoke quick started
      message: Quick cook started at 160 C for 12 minutes.
mode: single
```

## 6. Extend an active Quick cook live by 15 minutes

This example uses a helper such as `input_boolean.asmoke_extend_quick_15`. As soon as you turn that helper on, Home Assistant increases the Quick target time live. With the current integration, `number.quick_target_time` publishes that update directly to the smoker while Quick is active.

```yaml
alias: Asmoke extend quick by 15 minutes
description: Increase the target time live for an active Quick cook.
trigger:
  - platform: state
    entity_id: input_boolean.asmoke_extend_quick_15
    to: "on"
condition:
  - condition: state
    entity_id: binary_sensor.asmoke_backyard_cook_active
    state: "on"
  - condition: state
    entity_id: sensor.asmoke_backyard_mode
    state: QUICK
action:
  - variables:
      current_quick_time: "{{ states('number.asmoke_backyard_quick_target_time') | int(0) }}"
      new_quick_time: "{{ [current_quick_time + 15, 1440] | min }}"
  - service: number.set_value
    target:
      entity_id: number.asmoke_backyard_quick_target_time
    data:
      value: "{{ new_quick_time }}"
  - service: notify.mobile_app_your_phone
    data:
      title: Asmoke quick extended
      message: Quick target time is now {{ new_quick_time }} minutes.
  - service: input_boolean.turn_off
    target:
      entity_id: input_boolean.asmoke_extend_quick_15
mode: single
```

## 7. Use the Stop button and send a notification immediately afterwards

```yaml
alias: Asmoke stop cook and notify
description: Use a helper as a dashboard trigger for Stop cook.
trigger:
  - platform: state
    entity_id: input_boolean.asmoke_stop_requested
    to: "on"
condition:
  - condition: state
    entity_id: binary_sensor.asmoke_backyard_cook_active
    state: "on"
action:
  - service: button.press
    target:
      entity_id: button.asmoke_backyard_stop_cook
  - service: notify.mobile_app_your_phone
    data:
      title: Asmoke stop sent
      message: The confirmed Stop command was sent to the smoker.
  - service: input_boolean.turn_off
    target:
      entity_id: input_boolean.asmoke_stop_requested
mode: single
```

## 8. Notification on a new result message

The `last_result_message` sensor is useful for vendor confirmations such as successfully started modes or other result messages.

```yaml
alias: Asmoke result message
description: Send a notification only for a real new result message.
trigger:
  - platform: state
    entity_id: sensor.asmoke_backyard_last_result_message
condition:
  - condition: template
    value_template: >-
      {{ trigger.to_state is not none
         and trigger.to_state.state not in ['unknown', 'unavailable', 'None', '']
         and trigger.from_state is not none
         and trigger.from_state.state != trigger.to_state.state }}
action:
  - service: notify.mobile_app_your_phone
    data:
      title: Asmoke message
      message: "{{ trigger.to_state.state }}"
mode: queued
```

## 9. Notification when the grill reaches the configured smoke temperature

```yaml
alias: Asmoke grill at target temperature
description: Notify when grill temperature 1 reaches the configured climate target temperature.
trigger:
  - platform: numeric_state
    entity_id: sensor.asmoke_backyard_grill_temperature_1
    above: 0
    for: "00:02:00"
condition:
  - condition: state
    entity_id: binary_sensor.asmoke_backyard_cook_active
    state: "on"
  - condition: template
    value_template: >-
      {% set grill = states('sensor.asmoke_backyard_grill_temperature_1') | int(0) %}
      {% set target = state_attr('climate.asmoke_backyard_pit_thermostat', 'temperature') | int(0) %}
      {{ target > 0 and grill >= target }}
action:
  - service: notify.mobile_app_your_phone
    data:
      title: Asmoke at temperature
      message: >-
        Grill temperature 1 is {{ states('sensor.asmoke_backyard_grill_temperature_1') }} C and has reached the configured target.
mode: single
```

## Practical tip

Start with a simple notification automation and first check in Developer Tools that your entity IDs exactly match your installation. The climate, button, number, and binary sensor names especially depend on the name Home Assistant assigned to your device.