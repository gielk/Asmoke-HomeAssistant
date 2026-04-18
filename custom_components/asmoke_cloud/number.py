from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULT_TARGET_TEMPERATURE,
    DOMAIN,
    MAX_TARGET_TEMPERATURE,
    MIN_TARGET_TEMPERATURE,
)
from .coordinator import AsmokeDataUpdateCoordinator
from .entity import AsmokeCoordinatorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AsmokeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AsmokeTargetTemperatureNumber(coordinator)])


class AsmokeTargetTemperatureNumber(AsmokeCoordinatorEntity, NumberEntity):
    _attr_translation_key = "smoke_target_temperature"
    _attr_native_min_value = MIN_TARGET_TEMPERATURE
    _attr_native_max_value = MAX_TARGET_TEMPERATURE
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = NumberDeviceClass.TEMPERATURE

    def __init__(self, coordinator: AsmokeDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "smoke_target_temperature")

    @property
    def native_value(self) -> int:
        return int(
            self.coordinator.data.get("target_temp")
            or DEFAULT_TARGET_TEMPERATURE
        )

    @property
    def available(self) -> bool:
        return bool(self.coordinator.data.get("broker_connected"))

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.runtime.async_publish_smoke_target_temp(int(value))
