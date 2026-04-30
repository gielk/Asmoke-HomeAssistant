from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE_ID

from custom_components.asmoke_cloud.const import DOMAIN
from custom_components.asmoke_cloud.mqtt import AsmokeAuthenticationError, AsmokeDiscoveryError

CONNECTION_INPUT = {
    "name": "Asmoke Backyard",
    "host": "47.253.1.220",
    "port": 1883,
    "username": "test-user",
    "password": "test-pass",
    "keepalive": 60,
}


async def _start_user_flow(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )


async def _submit_credentials(hass, flow_id: str, user_input=None):
    with patch(
        "custom_components.asmoke_cloud.config_flow.async_validate_broker_connection",
        new_callable=AsyncMock,
    ) as validate:
        result = await hass.config_entries.flow.async_configure(
            flow_id,
            user_input or CONNECTION_INPUT,
        )

    validate.assert_awaited_once()
    return result


async def _choose_setup_method(hass, flow_id: str, step_id: str):
    return await hass.config_entries.flow.async_configure(
        flow_id,
        {"next_step_id": step_id},
    )


async def test_user_flow_validates_credentials_then_shows_setup_menu(
    hass,
    bypass_runtime_start,
) -> None:
    result = await _start_user_flow(hass)

    assert result["type"] == "form"
    assert result["step_id"] == "user"

    result = await _submit_credentials(hass, result["flow_id"])

    assert result["type"] == "menu"
    assert set(result["menu_options"]) == {"discover", "manual"}
    assert result["step_id"] == "setup_method"


async def test_user_flow_shows_error_on_auth_failure(
    hass,
    bypass_runtime_start,
) -> None:
    result = await _start_user_flow(hass)

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_validate_broker_connection",
        new_callable=AsyncMock,
        side_effect=AsmokeAuthenticationError,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            CONNECTION_INPUT,
        )

    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"]["base"] == "invalid_auth"


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
    result = await _start_user_flow(hass)
    result = await _submit_credentials(hass, result["flow_id"])

    result = await _choose_setup_method(hass, result["flow_id"], "manual")

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEVICE_ID: "A08241009A12582"},
    )

    assert result["type"] == "create_entry"
    assert result["title"] == "Asmoke Backyard"
    assert result["data"] == {
        **CONNECTION_INPUT,
        CONF_DEVICE_ID: "A08241009A12582",
    }


async def test_discover_flow_creates_entry(hass, bypass_runtime_start) -> None:
    result = await _start_user_flow(hass)
    result = await _submit_credentials(hass, result["flow_id"])

    result = await _choose_setup_method(hass, result["flow_id"], "discover")
    assert result["type"] == "form"
    assert result["step_id"] == "discover"

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
    ) as discover:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {},
        )

    discover.assert_awaited_once_with(CONNECTION_INPUT, timeout=45.0)
    assert result["type"] == "form"
    assert result["step_id"] == "confirm_discovery"
    assert "A08241009A12582" in result["description_placeholders"]["candidates"]

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEVICE_ID: "A08241009A12582"},
    )

    assert result["type"] == "create_entry"
    assert result["title"] == "Asmoke Backyard"
    assert result["data"]["device_id"] == "A08241009A12582"


async def test_discover_flow_requires_user_to_choose_candidate(
    hass,
    bypass_runtime_start,
) -> None:
    result = await _start_user_flow(hass)
    result = await _submit_credentials(hass, result["flow_id"])
    result = await _choose_setup_method(hass, result["flow_id"], "discover")

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_discover_devices",
        new_callable=AsyncMock,
        return_value=[
            {CONF_DEVICE_ID: "A08241009A12582", "message_count": 3},
            {CONF_DEVICE_ID: "A08241009A99999", "message_count": 1},
        ],
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {},
        )

    assert result["type"] == "form"
    assert result["step_id"] == "confirm_discovery"
    assert result["description_placeholders"]["candidate_count"] == "2"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEVICE_ID: "A08241009A99999"},
    )

    assert result["type"] == "create_entry"
    assert result["data"][CONF_DEVICE_ID] == "A08241009A99999"


async def test_discover_flow_shows_error_when_no_device_found(
    hass,
    bypass_runtime_start,
) -> None:
    result = await _start_user_flow(hass)
    result = await _submit_credentials(hass, result["flow_id"])
    result = await _choose_setup_method(hass, result["flow_id"], "discover")

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_discover_devices",
        new_callable=AsyncMock,
        side_effect=AsmokeDiscoveryError,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {},
        )

    assert result["type"] == "form"
    assert result["step_id"] == "discover"
    assert result["errors"]["base"] == "device_not_found"
