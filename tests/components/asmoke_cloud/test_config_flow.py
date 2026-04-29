from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE_ID

from custom_components.asmoke_cloud.const import DOMAIN
from custom_components.asmoke_cloud.mqtt import AsmokeAuthenticationError, AsmokeDiscoveryError


async def test_user_flow_shows_intro_then_setup_menu(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] == "form"
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {},
    )

    assert result["type"] == "menu"
    assert set(result["menu_options"]) == {"discover", "manual"}
    assert result["step_id"] == "setup_method"


async def test_user_flow_shows_clear_missing_local_auth_status(
    hass, bypass_runtime_start
) -> None:
    with patch(
        "custom_components.asmoke_cloud.config_flow.has_local_auth_defaults",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

    assert result["description_placeholders"]["local_auth"] == (
        "not present yet on this Home Assistant instance; broker fields will not "
        "be prefilled automatically"
    )


def test_setup_method_menu_option_translations_exist() -> None:
    translation_path = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "asmoke_cloud"
        / "translations"
        / "en.json"
    )
    translations = json.loads(translation_path.read_text())

    assert translations["config"]["step"]["setup_method"]["menu_options"] == {
        "discover": "Auto-discover device ID",
        "manual": "Enter device ID manually",
    }


async def test_manual_flow_creates_entry(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {},
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
        {},
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
        {},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"next_step_id": "discover"},
    )

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_discover_devices",
        new_callable=AsyncMock,
        return_value=[
            {
                CONF_DEVICE_ID: "A08241009A12582",
                "message_count": 2,
                "status": "idle",
                "mode": "QUICK",
                "battery_level": 47,
                "grill_temp_1": 135,
                "grill_temp_2": 159,
            }
        ],
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
    assert result2["step_id"] == "confirm_discovery"
    assert "A08241009A12582" in result2["description_placeholders"]["candidates"]

    result3 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEVICE_ID: "A08241009A12582"},
    )

    assert result3["type"] == "create_entry"
    assert result3["title"] == "Asmoke Backyard"
    assert result3["data"]["device_id"] == "A08241009A12582"


async def test_discover_flow_requires_user_to_choose_candidate(
    hass,
    bypass_runtime_start,
) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"next_step_id": "discover"},
    )

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_discover_devices",
        new_callable=AsyncMock,
        return_value=[
            {CONF_DEVICE_ID: "A08241009A12582", "message_count": 3},
            {CONF_DEVICE_ID: "A08241009A99999", "message_count": 1},
        ],
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
    assert result2["step_id"] == "confirm_discovery"
    assert result2["description_placeholders"]["candidate_count"] == "2"

    result3 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEVICE_ID: "A08241009A99999"},
    )

    assert result3["type"] == "create_entry"
    assert result3["data"][CONF_DEVICE_ID] == "A08241009A99999"


async def test_discover_flow_shows_error_when_no_device_found(hass, bypass_runtime_start) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"next_step_id": "discover"},
    )

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_discover_devices",
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
