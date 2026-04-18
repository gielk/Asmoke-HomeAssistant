from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries

from custom_components.asmoke_cloud.const import DOMAIN
from custom_components.asmoke_cloud.mqtt import AsmokeAuthenticationError


async def test_user_flow_creates_entry(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_validate_broker_connection",
        new_callable=AsyncMock,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "device_id": "A08241009A12582",
                "name": "Asmoke Backyard",
                "host": "47.253.1.220",
                "port": 1883,
                "username": "test-user",
                "password": "test-pass",
                "keepalive": 60,
            },
        )

    assert result2["type"] == "create_entry"
    assert result2["title"] == "Asmoke Backyard"
    assert result2["data"]["device_id"] == "A08241009A12582"


async def test_user_flow_shows_error_on_auth_failure(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_validate_broker_connection",
        new_callable=AsyncMock,
        side_effect=AsmokeAuthenticationError,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "device_id": "A08241009A12582",
                "name": "Asmoke Backyard",
                "host": "47.253.1.220",
                "port": 1883,
                "username": "test-user",
                "password": "test-pass",
                "keepalive": 60,
            },
        )

    assert result2["type"] == "form"
    assert result2["errors"]["base"] == "invalid_auth"
