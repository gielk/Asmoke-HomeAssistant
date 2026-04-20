# Automation-voorbeelden

Deze voorbeelden laten zien hoe je de Asmoke-integratie praktisch in Home Assistant kunt gebruiken.

Pas altijd eerst deze placeholders aan:

- `binary_sensor.asmoke_backyard_device_online`
- `sensor.asmoke_backyard_probe_a_temperature`
- `sensor.asmoke_backyard_last_result_message`
- `climate.asmoke_backyard_pit_thermostat`
- `button.asmoke_backyard_stop_cook`
- `button.asmoke_backyard_start_quick_cook`
- `number.asmoke_backyard_quick_target_time`
- `notify.mobile_app_jouw_telefoon`

## 1. Notificatie als de smoker offline raakt

Handig als je wilt weten wanneer de smoker langere tijd geen cloud-updates meer stuurt.

```yaml
alias: Asmoke smoker offline
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

## 2. Notificatie als probe A een kerntemperatuur haalt

Dit is een praktisch voorbeeld voor Roast of andere cooks waarbij je vooral op de probe let.

```yaml
alias: Asmoke probe A target bereikt
trigger:
  - platform: numeric_state
    entity_id: sensor.asmoke_backyard_probe_a_temperature
    above: 65
action:
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke target gehaald
      message: Probe A is boven 65 C gekomen.
mode: single
```

Opmerking: omdat de integratie `499` al omzet naar geen geldige probe-waarde, geeft dit voorbeeld geen valse melding op een niet-aangesloten probe.

## 3. Notificatie op nieuwe result-message

De sensor `last_result_message` is bruikbaar voor vendorbevestigingen zoals een succesvol gestarte mode of andere resultaatmeldingen.

```yaml
alias: Asmoke result message
trigger:
  - platform: state
    entity_id: sensor.asmoke_backyard_last_result_message
condition:
  - condition: template
    value_template: >-
      {{ trigger.to_state is not none
         and trigger.to_state.state not in ['unknown', 'unavailable', 'None', ''] }}
action:
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke melding
      message: "{{ trigger.to_state.state }}"
mode: queued
```

## 4. Quick cook starten via button plus vooraf ingestelde waarden

Dit laat zien hoe je de climate target temperature, de Quick target time en de Quick-button samen gebruikt.

```yaml
alias: Asmoke quick 12 minuten
trigger:
  - platform: time
    at: "18:00:00"
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
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke quick gestart
      message: Quick cook is gestart op 160 C voor 12 minuten.
mode: single
```

## 5. Smoke cook starten via climate preset

Dit is de meest natuurlijke thermostaatachtige route voor Smoke: preset kiezen, temperatuur instellen en de climate op `heat` zetten.

```yaml
alias: Asmoke smoke starten via climate
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

## 6. Stop-button gebruiken en daarna direct een notificatie sturen

Dit is handig voor een dashboard-automation of een script dat je ook elders kunt aanroepen.

```yaml
alias: Asmoke stop cook en meld het
trigger:
  - platform: state
    entity_id: input_boolean.asmoke_stop_requested
    to: "on"
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

## 7. Melding als grilltemperatuur boven de smoke-setpoint komt

Voor Smoke is dit een eenvoudige manier om een heads-up te krijgen zodra de grill op temperatuur is.

```yaml
alias: Asmoke grill op smoke temperatuur
trigger:
  - platform: numeric_state
    entity_id: sensor.asmoke_backyard_grill_temperature_1
    above: 110
condition:
  - condition: state
    entity_id: sensor.asmoke_backyard_mode
    state: SMOKE
action:
  - service: notify.mobile_app_jouw_telefoon
    data:
      title: Asmoke op temperatuur
      message: Grill temperature 1 is boven 110 C gekomen in Smoke-modus.
mode: single
```

## Praktische tip

Begin met een eenvoudige notification-automation en controleer eerst in Ontwikkelaarstools of je entity IDs precies overeenkomen met jouw installatie. Vooral de climate-, button- en number-entitynamen hangen af van de naam die Home Assistant aan je device heeft gegeven.