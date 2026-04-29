from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS

AsmokeConfigEntry = ConfigEntry


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    from .services import async_register_services

    hass.data.setdefault(DOMAIN, {})
    await async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: AsmokeConfigEntry) -> bool:
    from .coordinator import AsmokeDataUpdateCoordinator
    from .services import async_register_services

    hass.data.setdefault(DOMAIN, {})

    coordinator = AsmokeDataUpdateCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_start()
    await async_register_services(hass)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AsmokeConfigEntry) -> bool:
    from .coordinator import AsmokeDataUpdateCoordinator

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if not unloaded:
        return False

    coordinator: AsmokeDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.async_shutdown()
    return True


async def _async_update_listener(hass: HomeAssistant, entry: AsmokeConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def async_get_coordinator(
    hass: HomeAssistant, entry_id: str
) -> Any:
    entry_data: dict[str, Any] = hass.data.get(DOMAIN, {})
    return entry_data.get(entry_id)
