from __future__ import annotations

from custom_components.asmoke_cloud.const import DOMAIN
from custom_components.asmoke_cloud.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics_redacts_sensitive_fields(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.runtime._state["broker_connected"] = True
    coordinator.runtime._state["client_id"] = "secret-client-id"

    diagnostics = await async_get_config_entry_diagnostics(hass, mock_entry)

    assert diagnostics["entry"].get("password") == "**REDACTED**"
    assert diagnostics["runtime"].get("client_id") == "**REDACTED**"
