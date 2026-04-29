from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS

AsmokeConfigEntry = ConfigEntry
_LOGGER = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).parent / "frontend"
FRONTEND_STATIC_PATH = f"/{DOMAIN}/frontend"
FRONTEND_CARD_URL = f"{FRONTEND_STATIC_PATH}/asmoke-smoker-card.js"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    from .services import async_register_services

    hass.data.setdefault(DOMAIN, {})
    await _async_register_frontend(hass)
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


async def _async_register_frontend(hass: HomeAssistant) -> None:
    if (http := getattr(hass, "http", None)) is not None:
        await http.async_register_static_paths(
            [
                StaticPathConfig(
                    FRONTEND_STATIC_PATH,
                    str(FRONTEND_DIR),
                    cache_headers=False,
                )
            ]
        )

    if _add_frontend_module(hass):
        return

    @callback
    def _register_frontend_module_when_started(event: Event) -> None:
        _add_frontend_module(hass)

    hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_STARTED, _register_frontend_module_when_started
    )


@callback
def _add_frontend_module(hass: HomeAssistant) -> bool:
    try:
        from homeassistant.components import frontend

        frontend.add_extra_js_url(hass, FRONTEND_CARD_URL)
    except KeyError:
        _LOGGER.debug("Home Assistant frontend is not ready for extra JS registration")
        return False
    return True
