# Changelog

This repository uses semantic versioning for functional HACS releases.

Changelog entries should stay user-facing, concise, and written in English.

## Unreleased

## v0.4.4-beta.2 - 2026-04-29

- Added explicit Home Assistant entity icon translations for the custom buttons, time controls, and status sensors, and locked in the local HACS/Home Assistant brand assets with metadata tests.
- Made the config-flow local auth status wording clearer so missing local defaults are described explicitly instead of showing a raw yes/no style indicator.

## v0.4.4-beta.1 - 2026-04-29

- Reworked the initial config flow so onboarding starts with a clearer prerequisites step that explains broker credentials are not in the public repository and gives better guidance for auto discovery.

## v0.4.3 - 2026-04-21

- Translated the public documentation set to English so the project can be shared externally without Dutch-only guides and examples.
- Polished the README, user guide, feature overview, dashboard guide, automation examples, architecture notes, and research summary so they read like public project documentation instead of internal notes.

## v0.4.2 - 2026-04-20

- Fixed the initial config-flow menu so the `Discover Asmoke device` and `Enter device ID manually` options render with readable labels.

## v0.4.1 - 2026-04-20

- Replaced the raw `Wi-Fi status` sensor with a normalized `Wi-Fi connected` binary sensor because current captures only confirm a boolean-like vendor connection flag.

## v0.4.0 - 2026-04-20

- Added confirmed cook controls for smoke, quick, roast, and stop, including a pit climate entity, start and stop buttons, and a dedicated Quick target time number.
- Kept the climate entity and runtime state aligned with the confirmed smoker `status`, so `idle` is treated as off even when the vendor `mode` remains sticky.
- Added a `Cook active` binary sensor and made Quick target time updates work live during an active Quick cook.
- Expanded the documentation with a ready-to-copy Lovelace dashboard YAML view and updated automation examples for the current climate, `cook_active`, and live Quick target time behavior.

## v0.4.0-beta.7 - 2026-04-20

- Made the Quick target time number update the smoker live during an active Quick cook instead of only changing the next-start preset.
- Aligned the Quick target time number with the reported device target time while Quick mode is running, so the editable control matches the live cooker state.

## v0.4.0-beta.6 - 2026-04-20

- Added a `Cook active` binary sensor that follows the confirmed smoker `status` field and cleanly reports whether a cook is running or idle.
- Reused the same derived cook-status logic in the climate entity so the thermostat state and the new binary sensor stay in sync.

## v0.4.0-beta.5 - 2026-04-20

- Kept the climate entity `off` after Stop once the smoker reports `status: idle`, even if vendor telemetry keeps the previous cook mode value.
- Added the normalized device `status` to runtime handling and climate state attributes so off-versus-running behavior is derived from the confirmed smoker state.

## v0.4.0-beta.4 - 2026-04-20

- Fixed the initial `paho.mqtt.client` import to happen off the Home Assistant event loop, avoiding blocking-operation warnings during startup.
- Made climate `off` explicitly publish the confirmed Stop action through both HVAC mode changes and `climate.turn_off`.
- Set the climate target temperature step to 10 degrees to match the vendor app behavior.

## v0.4.0-beta.3 - 2026-04-20

- Added a climate entity with one shared target temperature and selectable `smoke` or `quick` preset modes.
- Removed the separate Smoke and Quick target temperature number entities to reduce control duplication.
- Kept Quick target time as the remaining mode-specific input and wired the Quick button to the shared climate target temperature.

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