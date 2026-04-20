from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import ServiceValidationError

from custom_components.asmoke_cloud.const import (
    ATTR_INGREDIENT_CATEGORY,
    ATTR_K_VALUE,
    ATTR_MODE,
    ATTR_PROBE_TEMP,
    ATTR_TARGET_TEMP,
    ATTR_TARGET_TIME,
    DOMAIN,
    SERVICE_PUBLISH_RAW_ACTION,
    SERVICE_START_COOK,
    SERVICE_STOP_COOK,
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


async def test_start_cook_service_smoke(hass, mock_entry, bypass_runtime_start) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.runtime.async_publish_cook_start = AsyncMock()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_START_COOK,
        {ATTR_MODE: "smoke", ATTR_TARGET_TEMP: 130},
        blocking=True,
    )

    coordinator.runtime.async_publish_cook_start.assert_awaited_once_with(
        "smoke", 130, None, None, None, None
    )


async def test_start_cook_service_quick(hass, mock_entry, bypass_runtime_start) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.runtime.async_publish_cook_start = AsyncMock()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_START_COOK,
        {ATTR_MODE: "quick", ATTR_TARGET_TEMP: 160, ATTR_TARGET_TIME: 10},
        blocking=True,
    )

    coordinator.runtime.async_publish_cook_start.assert_awaited_once_with(
        "quick", 160, 10, None, None, None
    )


async def test_start_cook_service_roast(hass, mock_entry, bypass_runtime_start) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.runtime.async_publish_cook_start = AsyncMock()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_START_COOK,
        {
            ATTR_MODE: "roast",
            ATTR_TARGET_TEMP: 200,
            ATTR_TARGET_TIME: 50,
            ATTR_PROBE_TEMP: 65,
            ATTR_INGREDIENT_CATEGORY: "Beef",
            ATTR_K_VALUE: "0.014",
        },
        blocking=True,
    )

    coordinator.runtime.async_publish_cook_start.assert_awaited_once_with(
        "roast", 200, 50, 65, "Beef", "0.014"
    )


async def test_start_cook_service_requires_target_time_for_quick(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError, match="target_time is required"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_START_COOK,
            {ATTR_MODE: "quick", ATTR_TARGET_TEMP: 160},
            blocking=True,
        )


async def test_start_cook_service_requires_probe_temp_for_roast(
    hass,
    mock_entry,
    bypass_runtime_start,
) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError, match="probe_temp is required"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_START_COOK,
            {
                ATTR_MODE: "roast",
                ATTR_TARGET_TEMP: 200,
                ATTR_TARGET_TIME: 50,
                ATTR_INGREDIENT_CATEGORY: "Beef",
                ATTR_K_VALUE: "0.014",
            },
            blocking=True,
        )


async def test_stop_cook_service(hass, mock_entry, bypass_runtime_start) -> None:
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][mock_entry.entry_id]
    coordinator.runtime.async_publish_stop = AsyncMock()

    await hass.services.async_call(
        DOMAIN,
        SERVICE_STOP_COOK,
        {},
        blocking=True,
    )

    coordinator.runtime.async_publish_stop.assert_awaited_once_with()


async def test_runtime_smoke_target_temp_uses_vendor_payload_key(hass, mock_entry) -> None:
    runtime = AsmokeMqttRuntime(hass, mock_entry.entry_id, mock_entry.data, mock_entry.options)
    runtime.async_publish_action = AsyncMock()

    await runtime.async_publish_smoke_target_temp(125)

    runtime.async_publish_action.assert_awaited_once_with(
        "Smoke", {"targetTemp": 125}
    )


async def test_runtime_start_quick_uses_vendor_payload_keys(hass, mock_entry) -> None:
    runtime = AsmokeMqttRuntime(hass, mock_entry.entry_id, mock_entry.data, mock_entry.options)
    runtime.async_publish_action = AsyncMock()

    await runtime.async_publish_cook_start("quick", 160, 10)

    runtime.async_publish_action.assert_awaited_once_with(
        "Quick", {"targetTemp": 160, "targetTime": 10}
    )


async def test_runtime_start_roast_uses_confirmed_vendor_payload(hass, mock_entry) -> None:
    runtime = AsmokeMqttRuntime(hass, mock_entry.entry_id, mock_entry.data, mock_entry.options)
    runtime.async_publish_action = AsyncMock()

    await runtime.async_publish_cook_start(
        "roast", 200, 50, 65, "Beef", "0.014"
    )

    runtime.async_publish_action.assert_awaited_once_with(
        "Roast",
        {
            "targetTemp": 200,
            "targetTime": 50,
            "probeTemp": 65,
            "kValue": "0.014",
            "ingredientCategory": "Beef",
        },
    )


async def test_runtime_stop_uses_confirmed_vendor_payload(hass, mock_entry) -> None:
    runtime = AsmokeMqttRuntime(hass, mock_entry.entry_id, mock_entry.data, mock_entry.options)
    runtime.async_publish_action = AsyncMock()

    await runtime.async_publish_stop()

    runtime.async_publish_action.assert_awaited_once_with("Stop")
