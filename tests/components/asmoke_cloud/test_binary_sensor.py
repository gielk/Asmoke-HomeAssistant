from __future__ import annotations

from custom_components.asmoke_cloud.const import DOMAIN


async def test_cook_active_binary_sensor_tracks_runtime_status(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.runtime._apply_status_payload(
        {
            "status": "running",
            "mode": "QUICK",
            "ignitionStatus": 0,
        }
    )
    coordinator.async_set_updated_data(
        {
            **coordinator.runtime.snapshot(),
            "broker_connected": True,
        }
    )
    await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.asmoke_backyard_cook_active")

    assert state is not None
    assert state.state == "on"

    coordinator.runtime._apply_status_payload(
        {
            "status": "idle",
            "mode": "QUICK",
            "ignitionStatus": 0,
        }
    )
    coordinator.async_set_updated_data(
        {
            **coordinator.runtime.snapshot(),
            "broker_connected": True,
        }
    )
    await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.asmoke_backyard_cook_active")

    assert state is not None
    assert state.state == "off"