from __future__ import annotations

from unittest.mock import AsyncMock

from custom_components.asmoke_cloud.const import (
    ATTR_TARGET_TEMP,
    DOMAIN,
    SERVICE_PUBLISH_RAW_ACTION,
    SERVICE_SET_SMOKE_TARGET_TEMP,
)
from custom_components.asmoke_cloud.mqtt import AsmokeMqttRuntime


async def test_publish_raw_action_service(hass, mock_entry, bypass_runtime_start) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.runtime.async_publish_action = AsyncMock()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_PUBLISH_RAW_ACTION,
        {"command": "Smoke", "payload": {"targetTemp": 110}},
        blocking=True,
    )

    coordinator.runtime.async_publish_action.assert_awaited_once_with(
        "Smoke", {"targetTemp": 110}
    )


async def test_set_target_temp_service(hass, mock_entry, bypass_runtime_start) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.runtime.async_publish_smoke_target_temp = AsyncMock()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_SMOKE_TARGET_TEMP,
        {ATTR_TARGET_TEMP: 125},
        blocking=True,
    )

    coordinator.runtime.async_publish_smoke_target_temp.assert_awaited_once_with(125)


async def test_runtime_smoke_target_temp_uses_vendor_payload_key(hass, mock_entry) -> None:
    runtime = AsmokeMqttRuntime(hass, mock_entry.entry_id, mock_entry.data, mock_entry.options)
    runtime.async_publish_action = AsyncMock()

    await runtime.async_publish_smoke_target_temp(125)

    runtime.async_publish_action.assert_awaited_once_with(
        "Smoke", {"targetTemp": 125}
    )
