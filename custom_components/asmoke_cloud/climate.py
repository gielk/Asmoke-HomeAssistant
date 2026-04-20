from __future__ import annotations

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.components.climate.const import HVACAction, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CLIMATE_PRESET_MODES,
    DOMAIN,
    MAX_TARGET_TEMPERATURE,
    MIN_TARGET_TEMPERATURE,
)
from .coordinator import AsmokeDataUpdateCoordinator
from .entity import AsmokeCoordinatorEntity

ACTIVE_MODE_VALUES = {"SMOKE", "QUICK", "ROAST", "RECIPE"}
ACTIVE_STATUS_VALUES = {"RUNNING"}
INACTIVE_STATUS_VALUES = {"IDLE", "OFF", "STOPPED"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AsmokeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AsmokePitClimate(coordinator)])


class AsmokePitClimate(RestoreEntity, AsmokeCoordinatorEntity, ClimateEntity):
    _attr_translation_key = "pit_controller"
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_preset_modes = list(CLIMATE_PRESET_MODES)
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 10
    _attr_min_temp = MIN_TARGET_TEMPERATURE
    _attr_max_temp = MAX_TARGET_TEMPERATURE

    def __init__(self, coordinator: AsmokeDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "pit_controller")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is None:
            return

        restored_temp = last_state.attributes.get(ATTR_TEMPERATURE)
        if restored_temp is not None:
            self.coordinator.cook_settings.target_temp = int(restored_temp)

        restored_preset = last_state.attributes.get("preset_mode")
        if restored_preset in CLIMATE_PRESET_MODES:
            self.coordinator.cook_settings.mode = restored_preset

    @property
    def available(self) -> bool:
        data = self.coordinator.data or {}
        return bool(data.get("broker_connected"))

    @property
    def current_temperature(self) -> int | None:
        data = self.coordinator.data or {}
        if data.get("grill_temp_1") is not None:
            return int(data["grill_temp_1"])
        if data.get("grill_temp_2") is not None:
            return int(data["grill_temp_2"])
        return None

    @property
    def target_temperature(self) -> int:
        reported_target = (self.coordinator.data or {}).get("target_temp")
        if self.hvac_mode == HVACMode.HEAT and reported_target is not None:
            return int(reported_target)
        return int(self.coordinator.cook_settings.target_temp)

    @property
    def hvac_mode(self) -> HVACMode:
        data = self.coordinator.data or {}
        reported_status = self._reported_status()
        reported_mode = self._reported_mode()

        if reported_status in INACTIVE_STATUS_VALUES:
            return HVACMode.OFF
        if reported_status in ACTIVE_STATUS_VALUES:
            return HVACMode.HEAT
        if reported_mode in ACTIVE_MODE_VALUES or data.get("ignition_status"):
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        if (self.coordinator.data or {}).get("ignition_status"):
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def preset_mode(self) -> str:
        reported_mode = self._reported_mode().lower()
        if reported_mode in CLIMATE_PRESET_MODES:
            return reported_mode
        return self.coordinator.cook_settings.mode

    @property
    def extra_state_attributes(self) -> dict[str, int | str | None]:
        return {
            "quick_target_time": self.coordinator.cook_settings.target_time,
            "reported_mode": (self.coordinator.data or {}).get("mode"),
            "reported_status": (self.coordinator.data or {}).get("status"),
        }

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.runtime.async_publish_stop()
            self._push_optimistic_state(mode=None, status="idle", ignition_status=False)
            return

        if hvac_mode != HVACMode.HEAT:
            raise ValueError(f"Unsupported HVAC mode: {hvac_mode}")

        await self._async_start_selected_mode()

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode not in CLIMATE_PRESET_MODES:
            raise ValueError(f"Unsupported preset mode: {preset_mode}")

        self.coordinator.cook_settings.mode = preset_mode
        if self.hvac_mode == HVACMode.HEAT:
            await self._async_start_selected_mode()
            return

        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return

        self.coordinator.cook_settings.target_temp = int(kwargs[ATTR_TEMPERATURE])
        if self.hvac_mode == HVACMode.HEAT:
            await self._async_start_selected_mode()
            return

        self.async_write_ha_state()

    async def _async_start_selected_mode(self) -> None:
        selected_mode = self.coordinator.cook_settings.mode
        target_temp = self.coordinator.cook_settings.target_temp

        if selected_mode == "quick":
            await self.coordinator.runtime.async_publish_cook_start(
                "quick",
                target_temp,
                self.coordinator.cook_settings.target_time,
            )
        else:
            await self.coordinator.runtime.async_publish_cook_start(
                "smoke",
                target_temp,
            )

        self._push_optimistic_state(
            mode=selected_mode.upper(),
            target_temp=target_temp,
        )

    def _push_optimistic_state(self, **changes) -> None:
        updated = dict(self.coordinator.data or {})
        updated.update(changes)
        self.coordinator.async_set_updated_data(updated)

    def _reported_mode(self) -> str:
        reported_mode = (self.coordinator.data or {}).get("mode")
        if reported_mode is None:
            return ""
        return str(reported_mode).strip().upper()

    def _reported_status(self) -> str:
        reported_status = (self.coordinator.data or {}).get("status")
        if reported_status is None:
            return ""
        return str(reported_status).strip().upper()