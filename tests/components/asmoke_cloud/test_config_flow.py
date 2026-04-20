from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries

from custom_components.asmoke_cloud.const import DOMAIN
from custom_components.asmoke_cloud.mqtt import AsmokeAuthenticationError, AsmokeDiscoveryError


async def test_user_flow_shows_discover_and_manual_menu(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] == "menu"
    assert set(result["menu_options"]) == {"discover", "manual"}


def test_user_flow_menu_option_translations_exist() -> None:
    translation_path = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "asmoke_cloud"
        / "translations"
        / "en.json"
    )
    translations = json.loads(translation_path.read_text())

    assert translations["config"]["step"]["user"]["menu_options"] == {
        "discover": "Discover Asmoke device",
        "manual": "Enter device ID manually",
    }


async def test_manual_flow_creates_entry(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"next_step_id": "manual"},
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


async def test_manual_flow_shows_error_on_auth_failure(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"next_step_id": "manual"},
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


async def test_discover_flow_creates_entry(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"next_step_id": "discover"},
    )

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_discover_device",
        new_callable=AsyncMock,
        return_value={"device_id": "A08241009A12582"},
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
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


async def test_discover_flow_shows_error_when_no_device_found(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"next_step_id": "discover"},
    )

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_discover_device",
        new_callable=AsyncMock,
        side_effect=AsmokeDiscoveryError,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "name": "Asmoke Backyard",
                "host": "47.253.1.220",
                "port": 1883,
                "username": "test-user",
                "password": "test-pass",
                "keepalive": 60,
            },
        )

    assert result2["type"] == "form"
    assert result2["errors"]["base"] == "device_not_found"
