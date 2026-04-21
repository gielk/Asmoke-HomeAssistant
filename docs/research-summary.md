# Asmoke Research Summary

## Goal

The goal of the research was to:

1. determine how Asmoke communicates on the network;
2. decide whether there is a usable route for Home Assistant;
3. confirm whether direct broker access is possible;
4. map the topic structure and payload formats.

## Public part of the confirmed findings

### 1. No usable local API was found

No stable local HTTP or MQTT interface was found on the smoker that would make sense as a Home Assistant LAN integration. The relevant communication goes through the cloud.

### 2. The relevant transport layer is cloud MQTT

The app and smoker use raw MQTT through a cloud broker on port `1883`.

### 3. The smoker publishes telemetry on its own

The important messages do not only return through the phone. The smoker itself publishes status and temperature updates to the broker.

### 4. The app publishes commands on a separate action topic

There is a clear separation between:

- telemetry from the device;
- commands from the app;
- result or status confirmations from the device.

### 5. Direct broker login is feasible

A direct MQTT login using credentials derived from the app was confirmed locally. The exact credentials are intentionally not included in this public repository.

## Confirmed topic patterns

- `device/status/<device_id>`
- `device/temperatures/<device_id>`
- `device/result/<device_id>`
- `asmoke/action/<device_id>`

## Confirmed payload shapes

### Temperature payload

Example:

```json
{"grillTemp1":135,"grillTemp2":159,"probeATemp":499,"probeBTemp":499}
```

Confirmed fields:

- `grillTemp1`
- `grillTemp2`
- `probeATemp`
- `probeBTemp`

### Observed raw command payload

Example:

```json
{"type":"action","command":"Smoke","data":{"targetTemp":110}}
```

This is the vendor format observed directly on the broker. The Home Assistant service `set_smoke_target_temp` uses the field `target_temp` in Home Assistant, but maps it internally back to this vendor payload format.

### Result payload

Example:

```json
{"type":"result","status":1,"message":"Smoke mode updated: temperature."}
```

### Status payload

At minimum, the following fields were visible in captures:

- `status`
- `batteryLevel`
- `mode`
- `wifiStatus`
- `ignitionStatus`
- `roastProgress`
- `targetTemp`
- `targetTime`
- `temperatures`

## What this means for Home Assistant

The shortest useful route is a dedicated MQTT client inside a Home Assistant custom integration. That allows Home Assistant to:

- read live telemetry;
- receive status updates;
- publish confirmed commands;
- receive result messages.

## Limits and open points

- Not every command payload has been validated yet.
- Device onboarding is now implemented as manual input or temporary MQTT discovery of `device_id`.
- Broker credentials still need to be known or prefilled locally.
- Secrets and exact device identifiers stay out of this repository.
- A local MITM or sniffing helper is optional, but not a good primary runtime architecture.
