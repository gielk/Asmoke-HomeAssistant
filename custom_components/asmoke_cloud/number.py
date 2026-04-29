from __future__ import annotations

from homeassistant.components.number import RestoreNumber
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULT_QUICK_TARGET_TIME,
    DOMAIN,
    MAX_TARGET_TIME,
    MIN_TARGET_TIME,
)
from .coordinator import AsmokeDataUpdateCoordinator
from .entity import AsmokeCoordinatorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AsmokeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AsmokeQuickTargetTimeNumber(coordinator)])


class AsmokeQuickSettingNumber(AsmokeCoordinatorEntity, RestoreNumber):
    """Base class for local mode-specific settings that are restored across restarts."""

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
class AsmokeQuickTargetTimeNumber(AsmokeQuickSettingNumber):
    _attr_translation_key = "quick_target_time"
    _attr_native_min_value = MIN_TARGET_TIME
    _attr_native_max_value = MAX_TARGET_TIME
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator: AsmokeDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "quick_target_time", DEFAULT_QUICK_TARGET_TIME)

    @property
    def native_value(self) -> int:
        if (live_target_time := self._live_target_time()) is not None:
            return live_target_time
        return int(self.coordinator.cook_settings.target_time)

    async def async_set_native_value(self, value: float) -> None:
        native_value = int(value)
        self._attr_native_value = native_value
        self._apply_value(native_value)

        if self._is_active_quick_cook():
            await self.coordinator.runtime.async_publish_quick_target_time(native_value)
            updated = dict(self.coordinator.data or {})
            updated["target_time"] = native_value
            self.coordinator.async_set_updated_data(updated)

        self.async_write_ha_state()

    def _apply_value(self, value: int) -> None:
        self.coordinator.cook_settings.target_time = value

    def _live_target_time(self) -> int | None:
        if not self._is_active_quick_cook():
            return None

        runtime_target_time = (self.coordinator.data or {}).get("target_time")
        if runtime_target_time is None:
            return None
        return int(runtime_target_time)

    def _is_active_quick_cook(self) -> bool:
        data = self.coordinator.data or {}
        mode = data.get("mode")
        if mode is None or str(mode).strip().upper() != "QUICK":
            return False

        cook_active = data.get("cook_active")
        if cook_active is False:
            return False

        return cook_active is True or bool(data.get("ignition_status"))
