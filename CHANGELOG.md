# Changelog

This repository uses semantic versioning for functional HACS releases.

Changelog entries should stay user-facing, concise, and written in English.

## Unreleased

## v0.4.0-beta.2 - 2026-04-20

- Added a `Stop cook` press button entity.
- Added a `Start quick cook` button plus local Quick target temperature and target time number entities.
- Expanded the documentation with concrete service reference examples and Home Assistant automation YAML snippets.

## v0.4.0-beta.1 - 2026-04-20

- Added confirmed `start_cook` and `stop_cook` services for the newly verified Asmoke control routes.
- Added support for `smoke`, `quick`, and `roast` start actions with vendor payloads that match the captured app traffic.
- Added the confirmed `device/roast/<device_id>` topic to the default runtime subscriptions.

## v0.3.3 - 2026-04-20

- Added local Home Assistant brand assets for `asmoke_cloud`.
- Added `icon.png`, `icon@2x.png`, `logo.png`, and `logo@2x.png` so the integration card and UI branding no longer fall back to placeholders.

## v0.3.2 - 2026-04-20

- Refreshed the documentation to match the current HACS and onboarding flow.
- Fixed the Smoke target temperature command to publish the confirmed vendor key `targetTemp`.

## v0.3.1 - 2026-04-20

- Added real GitHub Releases for HACS instead of relying on git tags alone.
- Hid the default branch in HACS so users install named versions instead of commit hashes.

## v0.3.0 - 2026-04-20

- Added automatic `device_id` discovery through a temporary MQTT discovery step.
- Split the config flow into discover and manual onboarding paths.
- Added support for device metadata such as grill type and firmware version when present in payloads.

## v0.2.0 - 2026-04-20

- Treated probe temperature value `499` as disconnected instead of exposing it as a real temperature.

## v0.1.1 - 2026-04-20

- Fixed the Home Assistant config flow loading issue so the integration opens reliably in the UI.

## v0.1.0 - 2026-04-18

- First public working release of the Asmoke Home Assistant integration.
- Included the cloud MQTT runtime, config flow, entities, services, and base documentation.