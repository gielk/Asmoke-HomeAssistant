# Asmoke Home Assistant

<p align="center">
	<img src="https://cdn.shopify.com/s/files/1/0288/2060/2954/files/logo_final_43448c3c-dfd2-4921-8526-ca91ac15a6f0.png?height=628&pad_color=ffffff&v=1646132983&width=1200" alt="Asmoke logo" width="320">
</p>

Home Assistant custom integration for Asmoke smokers over the Asmoke cloud MQTT broker.

Minimum supported Home Assistant version: `2025.1.0`.

## Overview

This repository provides a Home Assistant custom integration that connects directly to the Asmoke cloud MQTT broker.

It can:

- add the smoker through a Home Assistant config flow;
- discover the `device_id` automatically through a temporary MQTT discovery step;
- read temperature, status, and result messages from the broker;
- expose Home Assistant entities for telemetry, controls, and runtime state;
- publish confirmed commands for smoke, quick, roast, and stop cook control;
- keep loading even when the grill is powered off.

The current integration also includes a pit climate entity, Quick target time control, direct start and stop buttons, and derived runtime sensors such as `Cook active`.

## Dashboard cards

The integration includes Home Assistant dashboard cards for daily smoker use:

- live pit control with target temperature, Quick time, start, and stop controls;
- BBQ-style temperature history for grill and probe sensors;
- cook session history based on the `Cook active` entity.

![Asmoke dashboard cards preview](docs/images/asmoke-dashboard-cards-preview.png)

For a single Asmoke smoker, the cards can usually be added without entity YAML:

```yaml
type: custom:asmoke-smoker-card
```

For multiple smokers, select the smoker by Home Assistant device or climate entity. See [docs/custom-card.md](docs/custom-card.md).

## Quick start

1. Add this repository to HACS as a custom repository of type `integration`.
2. Install `Asmoke Cloud` through HACS.
3. Restart Home Assistant.
4. Go to `Settings -> Devices & Services -> Add Integration`.
5. Choose `Asmoke Cloud`.
6. Enter the MQTT broker settings. Host, port, and keepalive are prefilled with the known cloud defaults.
7. Choose `Auto-discover device ID` or `Enter device ID manually`.
8. For auto discovery, make sure the smoker is powered on and the Asmoke app is open on a phone connected to the same local network as the smoker so the device publishes fresh messages.
9. Select the discovered device that belongs to your smoker. If discovery does not find it, choose manual entry and copy the device ID from the Asmoke app under `Me -> Device`.
10. Complete the config flow.

Note: the required MQTT username and password are intentionally not included in the public repository. Enter them during onboarding. If you do not already have those values, contact the maintainer directly for setup help.

## Documentation

- Full setup and usage guide: [docs/user-guide.md](docs/user-guide.md)
- Included Asmoke dashboard cards: [docs/custom-card.md](docs/custom-card.md)
- Copyable Lovelace dashboard example: [docs/dashboard-example.md](docs/dashboard-example.md)
- Automation, script, and notification examples: [docs/automation-examples.md](docs/automation-examples.md)
- Current feature scope: [docs/first-version.md](docs/first-version.md)

## Releases

This repository uses semantic version releases for HACS. The latest stable release is `v0.4.6`.

Beta prereleases remain available for testing when prereleases are enabled in HACS.

The `main` branch may already contain features that have not been released yet. Check the top section of `CHANGELOG.md` for current unreleased work.

Release history is available in [CHANGELOG.md](CHANGELOG.md).

## Repository guide

- Integration code: [custom_components/asmoke_cloud](custom_components/asmoke_cloud)
- Tests: [tests/components/asmoke_cloud](tests/components/asmoke_cloud)
- Research summary: [docs/research-summary.md](docs/research-summary.md)
- Architecture notes: [docs/integration-architecture.md](docs/integration-architecture.md)

## Tests

Run the component test suite locally with:

```bash
python -m pytest tests/components/asmoke_cloud -q
```
