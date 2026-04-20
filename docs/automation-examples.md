# Automation-voorbeelden

Deze voorbeelden zijn bijgewerkt voor de huidige entityset met:

- `binary_sensor...cook_active` als aanbevolen aan/uit-signaal;
- `climate...pit_thermostat` voor smoke en quick;
- `number...quick_target_time` die tijdens een actieve Quick-cook live mee kan sturen;
- `sensor...target_time` als gerapporteerde device target time.

Pas altijd eerst deze placeholders aan:

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
- `notify.mobile_app_jouw_telefoon`
- `input_boolean.asmoke_stop_requested`
- `input_boolean.asmoke_extend_quick_15`

## 1. Notificatie als de smoker offline raakt

```yaml
alias: Asmoke smoker offline
description: Meld als de smoker 10 minuten geen cloud-updates meer heeft gestuurd.
trigger:
  - platform: state
    entity_id: binary_sensor.asmoke_backyard_device_online
    to: "off"
    for: "00:10:00"
action:
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke offline
      message: De smoker heeft al 10 minuten geen statusupdates meer gestuurd.
mode: single
```

## 2. Notificatie als een cook start of stopt

Gebruik hiervoor bewust `cook_active` en niet `sensor.mode`, omdat de vendor-mode na Stop nog sticky kan blijven.

```yaml
alias: Asmoke cook status veranderd
description: Stuur een melding zodra een cook echt start of stopt.
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
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke cook status
      message: >-
        {% if trigger.to_state.state == 'on' %}
          Er draait nu een cook. Modus: {{ states('sensor.asmoke_backyard_mode') }}.
        {% else %}
          De cook is gestopt of klaar. Laatste modus: {{ states('sensor.asmoke_backyard_mode') }}.
        {% endif %}
mode: queued
```

## 3. Notificatie als probe A een kerntemperatuur haalt

```yaml
alias: Asmoke probe A target bereikt
description: Meld alleen tijdens een actieve cook als probe A boven de doelwaarde komt.
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
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke target gehaald
      message: >-
        Probe A is {{ states('sensor.asmoke_backyard_probe_a_temperature') }} C en dus boven 65 C gekomen.
mode: single
```

Opmerking: omdat de integratie `499` al omzet naar geen geldige probe-waarde, geeft dit voorbeeld geen valse melding op een niet-aangesloten probe.

## 4. Smoke cook starten via climate preset

```yaml
alias: Asmoke smoke starten via climate
description: Start een smoke-cook op een vast tijdstip via de climate-entity.
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
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke smoke gestart
      message: Smoke cook is gestart op 110 C.
mode: single
```

## 5. Quick cook starten via climate plus button

```yaml
alias: Asmoke quick 12 minuten
description: Stel temperatuur en Quick target time in en start daarna Quick.
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
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke quick gestart
      message: Quick cook is gestart op 160 C voor 12 minuten.
mode: single
```

## 6. Actieve Quick-cook live verlengen met 15 minuten

Dit voorbeeld gebruikt een helper zoals `input_boolean.asmoke_extend_quick_15`. Zodra je die helper aanzet, verhoogt Home Assistant live de Quick target time. Dankzij de huidige integratie publiceert `number.quick_target_time` dit direct naar de smoker zolang Quick actief is.

```yaml
alias: Asmoke verleng quick met 15 minuten
description: Verhoog live de target time van een actieve Quick-cook.
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
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke quick verlengd
      message: Quick target time is nu {{ new_quick_time }} minuten.
  - service: input_boolean.turn_off
    target:
      entity_id: input_boolean.asmoke_extend_quick_15
mode: single
```

## 7. Stop-button gebruiken en daarna direct een notificatie sturen

```yaml
alias: Asmoke stop cook en meld het
description: Gebruik een helper als dashboard-trigger voor Stop cook.
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
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke stop verstuurd
      message: Het bevestigde Stop-commando is naar de smoker gestuurd.
  - service: input_boolean.turn_off
    target:
      entity_id: input_boolean.asmoke_stop_requested
mode: single
```

## 8. Notificatie op nieuwe result-message

De sensor `last_result_message` is bruikbaar voor vendorbevestigingen zoals succesvol gestarte modes of andere resultaatmeldingen.

```yaml
alias: Asmoke result message
description: Stuur alleen een melding voor een echte nieuwe result-message.
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
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke melding
      message: "{{ trigger.to_state.state }}"
mode: queued
```

## 9. Melding als de grill op de ingestelde smoke-temperatuur zit

```yaml
alias: Asmoke grill op doeltemperatuur
description: Meld als grill temperature 1 de ingestelde climate target temperature bereikt.
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
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke op temperatuur
      message: >-
        Grill temperature 1 is {{ states('sensor.asmoke_backyard_grill_temperature_1') }} C en heeft de ingestelde target bereikt.
mode: single
```

## Praktische tip

Begin met een eenvoudige notification-automation en controleer eerst in Ontwikkelaarstools of je entity IDs precies overeenkomen met jouw installatie. Vooral de climate-, button-, number- en binary sensor-namen hangen af van de naam die Home Assistant aan je device heeft gegeven.