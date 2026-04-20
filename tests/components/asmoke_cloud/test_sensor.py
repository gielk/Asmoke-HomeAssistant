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


async def test_probe_temp_499_is_treated_as_disconnected(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.runtime._apply_temperatures_payload(
        {
            "grillTemp1": 135,
            "grillTemp2": 159,
            "probeATemp": 499,
            "probeBTemp": 499,
        }
    )
    coordinator.async_set_updated_data(
        {
            **coordinator.runtime.snapshot(),
            "broker_connected": True,
        }
    )
    await hass.async_block_till_done()

    probe_a_state = hass.states.get("sensor.asmoke_backyard_probe_a_temperature")
    probe_b_state = hass.states.get("sensor.asmoke_backyard_probe_b_temperature")

    assert probe_a_state is not None
    assert probe_b_state is not None
    assert probe_a_state.state == "unavailable"
    assert probe_b_state.state == "unavailable"
