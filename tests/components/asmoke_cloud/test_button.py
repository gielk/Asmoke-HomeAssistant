from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.helpers import entity_registry as er

from custom_components.asmoke_cloud.const import DOMAIN


async def test_stop_cook_button_presses_confirmed_stop(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.async_set_updated_data({"broker_connected": True})
    coordinator.runtime.async_publish_stop = AsyncMock()

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "button",
        DOMAIN,
        f"{coordinator.runtime.device_id}_stop_cook",
    )
    assert entity_id is not None

    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": entity_id},
        blocking=True,
    )

    coordinator.runtime.async_publish_stop.assert_awaited_once_with()


async def test_quick_button_uses_shared_climate_target_and_quick_time(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.async_set_updated_data({"broker_connected": True})
    coordinator.runtime.async_publish_cook_start = AsyncMock()

    entity_registry = er.async_get(hass)
    climate_entity_id = entity_registry.async_get_entity_id(
        "climate",
        DOMAIN,
        f"{coordinator.runtime.device_id}_pit_controller",
    )
    time_entity_id = entity_registry.async_get_entity_id(
        "number",
        DOMAIN,
        f"{coordinator.runtime.device_id}_quick_target_time",
    )
    button_entity_id = entity_registry.async_get_entity_id(
        "button",
        DOMAIN,
        f"{coordinator.runtime.device_id}_start_quick_cook",
    )

    assert climate_entity_id is not None
    assert time_entity_id is not None
    assert button_entity_id is not None

    await hass.services.async_call(
        "climate",
        "set_temperature",
        {"entity_id": climate_entity_id, "temperature": 165},
        blocking=True,
    )
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": time_entity_id, "value": 12},
        blocking=True,
    )
    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": button_entity_id},
        blocking=True,
    )

    coordinator.runtime.async_publish_cook_start.assert_awaited_once_with(
        "quick",
        165,
        12,
    )