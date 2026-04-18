from __future__ import annotations

from custom_components.asmoke_cloud.const import DOMAIN


async def test_sensor_state_updates_from_runtime(hass, mock_entry, bypass_runtime_start) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.async_set_updated_data(
        {
            **coordinator.runtime.snapshot(),
            "broker_connected": True,
            "grill_temp_1": 135,
        }
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.asmoke_backyard_grill_temperature_1")

    assert state is not None
    assert state.state == "135"
