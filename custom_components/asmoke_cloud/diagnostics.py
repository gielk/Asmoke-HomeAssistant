from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SENSITIVE_KEYS
from .coordinator import AsmokeDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict:
    coordinator: AsmokeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "entry": async_redact_data(dict(entry.data), SENSITIVE_KEYS),
        "options": dict(entry.options),
        "runtime": async_redact_data(
            coordinator.runtime.diagnostics_snapshot(),
            {CONF_PASSWORD, CONF_USERNAME, "client_id"},
        ),
    }
