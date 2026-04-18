from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AsmokeDataUpdateCoordinator


class AsmokeCoordinatorEntity(CoordinatorEntity[AsmokeDataUpdateCoordinator]):
    """Base entity for all Asmoke coordinator entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AsmokeDataUpdateCoordinator, unique_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.runtime.device_id}_{unique_suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.runtime.device_id)},
            manufacturer="Asmoke",
            model="Cloud Smoker",
            name=self.coordinator.runtime.name,
        )

    @property
    def available(self) -> bool:
        return bool(self.coordinator.data)
