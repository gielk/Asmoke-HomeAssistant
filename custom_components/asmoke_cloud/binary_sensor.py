from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AsmokeDataUpdateCoordinator
from .entity import AsmokeCoordinatorEntity


@dataclass(frozen=True, kw_only=True)
class AsmokeBinarySensorDescription(BinarySensorEntityDescription):
    value_key: str
    always_available: bool = False


BINARY_SENSOR_DESCRIPTIONS: tuple[AsmokeBinarySensorDescription, ...] = (
    AsmokeBinarySensorDescription(
        key="broker_connected",
        translation_key="broker_connected",
        value_key="broker_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        always_available=True,
    ),
    AsmokeBinarySensorDescription(
        key="device_online",
        translation_key="device_online",
        value_key="device_online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        always_available=True,
    ),
    AsmokeBinarySensorDescription(
        key="ignition_status",
        translation_key="ignition_status",
        value_key="ignition_status",
        device_class=BinarySensorDeviceClass.HEAT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AsmokeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        AsmokeBinarySensorEntity(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class AsmokeBinarySensorEntity(AsmokeCoordinatorEntity, BinarySensorEntity):
    entity_description: AsmokeBinarySensorDescription

    def __init__(
        self,
        coordinator: AsmokeDataUpdateCoordinator,
        description: AsmokeBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_translation_key = description.translation_key

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self.entity_description.value_key)
        return None if value is None else bool(value)

    @property
    def available(self) -> bool:
        if self.entity_description.always_available:
            return super().available
        return bool(
            self.coordinator.data.get("broker_connected") and self.is_on is not None
        )
