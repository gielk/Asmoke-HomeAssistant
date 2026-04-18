from __future__ import annotations

from custom_components.asmoke_cloud.const import DOMAIN


async def test_setup_entry(hass, mock_entry, bypass_runtime_start) -> None:
    mock_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data
    assert mock_entry.entry_id in hass.data[DOMAIN]
    bypass_runtime_start.assert_awaited_once()


async def test_unload_entry(
    hass,
    mock_entry,
    bypass_runtime_start,
    bypass_runtime_stop,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(mock_entry.entry_id)
    await hass.async_block_till_done()

    assert bypass_runtime_stop.await_count >= 1
