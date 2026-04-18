from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN
from .mqtt import AsmokeMqttRuntime

_LOGGER = logging.getLogger(__name__)


class AsmokeDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Asmoke runtime state for Home Assistant entities."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        self.entry = entry
        self.runtime = AsmokeMqttRuntime(hass, entry.entry_id, entry.data, entry.options)
        self.runtime.set_update_callback(self.async_set_updated_data)

    async def async_start(self) -> None:
        await self.runtime.async_start()
        await self.async_refresh()

    async def async_shutdown(self) -> None:
        await self.runtime.async_stop()

    async def _async_update_data(self) -> dict[str, Any]:
        return self.runtime.snapshot()
