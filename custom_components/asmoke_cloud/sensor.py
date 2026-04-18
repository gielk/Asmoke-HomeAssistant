from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AsmokeDataUpdateCoordinator
from .entity import AsmokeCoordinatorEntity


@dataclass(frozen=True, kw_only=True)
class AsmokeSensorDescription(SensorEntityDescription):
    value_key: str
    always_available: bool = False


SENSOR_DESCRIPTIONS: tuple[AsmokeSensorDescription, ...] = (
    AsmokeSensorDescription(
        key="grill_temperature_1",
        translation_key="grill_temperature_1",
        value_key="grill_temp_1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
    ),
    AsmokeSensorDescription(
        key="grill_temperature_2",
        translation_key="grill_temperature_2",
        value_key="grill_temp_2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
    ),
    AsmokeSensorDescription(
        key="probe_a_temperature",
        translation_key="probe_a_temperature",
        value_key="probe_a_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
    ),
    AsmokeSensorDescription(
        key="probe_b_temperature",
        translation_key="probe_b_temperature",
        value_key="probe_b_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
    ),
    AsmokeSensorDescription(
        key="battery_level",
        translation_key="battery_level",
        value_key="battery_level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        suggested_display_precision=0,
    ),
    AsmokeSensorDescription(
        key="roast_progress",
        translation_key="roast_progress",
        value_key="roast_progress",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
    AsmokeSensorDescription(
        key="target_time",
        translation_key="target_time",
        value_key="target_time",
        suggested_display_precision=0,
    ),
    AsmokeSensorDescription(
        key="mode",
        translation_key="mode",
        value_key="mode",
    ),
    AsmokeSensorDescription(
        key="wifi_status",
        translation_key="wifi_status",
        value_key="wifi_status",
    ),
    AsmokeSensorDescription(
        key="last_result_message",
        translation_key="last_result_message",
        value_key="last_result_message",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AsmokeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        AsmokeSensorEntity(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class AsmokeSensorEntity(AsmokeCoordinatorEntity, SensorEntity):
    entity_description: AsmokeSensorDescription

    def __init__(
        self,
        coordinator: AsmokeDataUpdateCoordinator,
        description: AsmokeSensorDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_translation_key = description.translation_key

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_description.value_key)

    @property
    def available(self) -> bool:
        value = self.native_value
        if self.entity_description.always_available:
            return super().available
        return bool(
            self.coordinator.data.get("broker_connected") and value is not None
        )
