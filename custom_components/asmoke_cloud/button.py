from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AsmokeDataUpdateCoordinator
from .entity import AsmokeCoordinatorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AsmokeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            AsmokeQuickCookButton(coordinator),
            AsmokeStopCookButton(coordinator),
        ]
    )


class AsmokeActionButton(AsmokeCoordinatorEntity, ButtonEntity):
    @property
    def available(self) -> bool:
        data = self.coordinator.data or {}
        return bool(data.get("broker_connected"))


class AsmokeQuickCookButton(AsmokeActionButton):
    _attr_translation_key = "start_quick_cook"

    def __init__(self, coordinator: AsmokeDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "start_quick_cook")

    async def async_press(self) -> None:
        settings = self.coordinator.cook_settings
        await self.coordinator.runtime.async_publish_cook_start(
            "quick",
            settings.target_temp,
            settings.target_time,
        )


class AsmokeStopCookButton(AsmokeActionButton):
    _attr_translation_key = "stop_cook"

    def __init__(self, coordinator: AsmokeDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "stop_cook")

    async def async_press(self) -> None:
        await self.coordinator.runtime.async_publish_stop()