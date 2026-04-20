from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.helpers import entity_registry as er

from custom_components.asmoke_cloud.const import DOMAIN


async def test_climate_turn_on_starts_smoke_with_shared_target_temperature(
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
    assert climate_entity_id is not None

    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {"entity_id": climate_entity_id, "hvac_mode": "heat"},
        blocking=True,
    )

    coordinator.runtime.async_publish_cook_start.assert_awaited_once_with(
        "smoke",
        110,
    )


async def test_climate_quick_mode_uses_one_shared_target_temperature(
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

    assert climate_entity_id is not None
    assert time_entity_id is not None

    await hass.services.async_call(
        "climate",
        "set_temperature",
        {"entity_id": climate_entity_id, "temperature": 165},
        blocking=True,
    )
    await hass.services.async_call(
        "climate",
        "set_preset_mode",
        {"entity_id": climate_entity_id, "preset_mode": "quick"},
        blocking=True,
    )
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": time_entity_id, "value": 12},
        blocking=True,
    )

    coordinator.runtime.async_publish_cook_start.assert_not_called()

    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {"entity_id": climate_entity_id, "hvac_mode": "heat"},
        blocking=True,
    )

    coordinator.runtime.async_publish_cook_start.assert_awaited_once_with(
        "quick",
        165,
        12,
    )


async def test_climate_turn_off_publishes_stop(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.async_set_updated_data(
        {
            "broker_connected": True,
            "mode": "SMOKE",
            "target_temp": 130,
            "ignition_status": True,
        }
    )
    coordinator.runtime.async_publish_stop = AsyncMock()

    entity_registry = er.async_get(hass)
    climate_entity_id = entity_registry.async_get_entity_id(
        "climate",
        DOMAIN,
        f"{coordinator.runtime.device_id}_pit_controller",
    )
    assert climate_entity_id is not None

    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {"entity_id": climate_entity_id, "hvac_mode": "off"},
        blocking=True,
    )

    coordinator.runtime.async_publish_stop.assert_awaited_once_with()


async def test_mode_specific_target_temperature_numbers_are_not_created(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    entity_registry = er.async_get(hass)

    assert entity_registry.async_get_entity_id(
        "climate",
        DOMAIN,
        f"{coordinator.runtime.device_id}_pit_controller",
    ) is not None
    assert entity_registry.async_get_entity_id(
        "number",
        DOMAIN,
        f"{coordinator.runtime.device_id}_quick_target_time",
    ) is not None
    assert entity_registry.async_get_entity_id(
        "number",
        DOMAIN,
        f"{coordinator.runtime.device_id}_smoke_target_temperature",
    ) is None
    assert entity_registry.async_get_entity_id(
        "number",
        DOMAIN,
        f"{coordinator.runtime.device_id}_quick_target_temperature",
    ) is None