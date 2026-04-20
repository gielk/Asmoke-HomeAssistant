from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.helpers import entity_registry as er

from custom_components.asmoke_cloud.const import DOMAIN


async def test_quick_target_time_number_shows_live_runtime_value_during_active_quick(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.cook_settings.target_time = 12
    coordinator.async_set_updated_data(
        {
            "broker_connected": True,
            "mode": "QUICK",
            "status": "running",
            "cook_active": True,
            "target_time": 70,
        }
    )
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "number",
        DOMAIN,
        f"{coordinator.runtime.device_id}_quick_target_time",
    )
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert int(float(state.state)) == 70


async def test_quick_target_time_number_publishes_live_update_during_active_quick(
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
            "mode": "QUICK",
            "status": "running",
            "cook_active": True,
            "target_time": 70,
        }
    )
    coordinator.runtime.async_publish_quick_target_time = AsyncMock()
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "number",
        DOMAIN,
        f"{coordinator.runtime.device_id}_quick_target_time",
    )
    assert entity_id is not None

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": entity_id, "value": 71},
        blocking=True,
    )

    coordinator.runtime.async_publish_quick_target_time.assert_awaited_once_with(71)
    assert coordinator.cook_settings.target_time == 71

    state = hass.states.get(entity_id)
    assert state is not None
    assert int(float(state.state)) == 71