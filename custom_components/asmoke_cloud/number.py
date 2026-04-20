from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, RestoreNumber
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULT_QUICK_TARGET_TIME,
    DEFAULT_TARGET_TEMPERATURE,
    DOMAIN,
    MAX_TARGET_TIME,
    MAX_TARGET_TEMPERATURE,
    MIN_TARGET_TIME,
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
    async_add_entities(
        [
            AsmokeTargetTemperatureNumber(coordinator),
            AsmokeQuickTargetTemperatureNumber(coordinator),
            AsmokeQuickTargetTimeNumber(coordinator),
        ]
    )


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


class AsmokeQuickSettingNumber(AsmokeCoordinatorEntity, RestoreNumber):
    """Base class for local quick-start settings that are restored across restarts."""

    _attr_native_step = 1

    def __init__(
        self,
        coordinator: AsmokeDataUpdateCoordinator,
        unique_suffix: str,
        default_value: int,
    ) -> None:
        super().__init__(coordinator, unique_suffix)
        self._attr_native_value = default_value

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last_number_data := await self.async_get_last_number_data()) is not None:
            restored_value = last_number_data.native_value
            if restored_value is not None:
                self._attr_native_value = int(restored_value)

        self._apply_value(int(self._attr_native_value))
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        return super().available

    async def async_set_native_value(self, value: float) -> None:
        native_value = int(value)
        self._attr_native_value = native_value
        self._apply_value(native_value)
        self.async_write_ha_state()

    def _apply_value(self, value: int) -> None:
        raise NotImplementedError


class AsmokeQuickTargetTemperatureNumber(AsmokeQuickSettingNumber):
    _attr_translation_key = "quick_target_temperature"
    _attr_native_min_value = MIN_TARGET_TEMPERATURE
    _attr_native_max_value = MAX_TARGET_TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = NumberDeviceClass.TEMPERATURE

    def __init__(self, coordinator: AsmokeDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "quick_target_temperature", DEFAULT_TARGET_TEMPERATURE)

    def _apply_value(self, value: int) -> None:
        self.coordinator.quick_settings.target_temp = value


class AsmokeQuickTargetTimeNumber(AsmokeQuickSettingNumber):
    _attr_translation_key = "quick_target_time"
    _attr_native_min_value = MIN_TARGET_TIME
    _attr_native_max_value = MAX_TARGET_TIME
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator: AsmokeDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "quick_target_time", DEFAULT_QUICK_TARGET_TIME)

    def _apply_value(self, value: int) -> None:
        self.coordinator.quick_settings.target_time = value

