from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.asmoke_cloud.config_flow import AsmokeConfigFlow
from custom_components.asmoke_cloud.const import (
    CONF_DEBUG_LOGGING,
    CONF_KEEPALIVE,
    CONF_OFFLINE_TIMEOUT,
    DOMAIN,
)
from custom_components.asmoke_cloud.mqtt import AsmokeAuthenticationError

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


def _mock_config_entry(**overrides) -> MockConfigEntry:
    data = {
        **CONNECTION_INPUT,
        CONF_DEVICE_ID: "A08241009A12582",
        **overrides.pop("data", {}),
    }
    return MockConfigEntry(
        domain=DOMAIN,
        title="Asmoke Backyard",
        data=data,
        options=overrides.pop("options", {}),
        unique_id=data[CONF_DEVICE_ID],
        **overrides,
    )


def _options_input(**overrides) -> dict:
    return {
        **CONNECTION_INPUT,
        CONF_DEVICE_ID: "A08241009A12582",
        CONF_OFFLINE_TIMEOUT: 900,
        CONF_DEBUG_LOGGING: False,
        **overrides,
    }


async def _start_options_flow(hass, entry: MockConfigEntry):
    entry.add_to_hass(hass)
    flow = AsmokeConfigFlow.async_get_options_flow(entry)
    flow.hass = hass
    return flow


async def test_user_flow_validates_credentials_then_shows_manual_device_id_form(
    hass,
    bypass_runtime_start,
) -> None:
    result = await _start_user_flow(hass)

    assert result["type"] == "form"
    assert result["step_id"] == "user"

    result = await _submit_credentials(hass, result["flow_id"])

    assert result["type"] == "form"
    assert result["step_id"] == "manual"


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


def test_manual_device_id_translation_uses_app_path() -> None:
    translation_path = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "asmoke_cloud"
        / "translations"
        / "en.json"
    )
    translations = json.loads(translation_path.read_text())

    steps = translations["config"]["step"]
    assert set(steps) == {"user", "manual", "reauth_confirm"}
    assert "Me -> Device" in steps["manual"]["description"]


async def test_manual_flow_creates_entry(hass, bypass_runtime_start) -> None:
    result = await _start_user_flow(hass)
    result = await _submit_credentials(hass, result["flow_id"])

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


async def test_options_flow_opens_without_config_entry_setter_error(hass) -> None:
    entry = _mock_config_entry(options={CONF_OFFLINE_TIMEOUT: 900})
    flow = await _start_options_flow(hass, entry)

    result = await flow.async_step_init()

    assert result["type"] == "form"
    assert result["step_id"] == "init"


async def test_options_flow_updates_connection_device_and_runtime_options(hass) -> None:
    entry = _mock_config_entry(
        options={CONF_OFFLINE_TIMEOUT: 900, "extra_topics": "legacy/topic"}
    )
    flow = await _start_options_flow(hass, entry)
    user_input = _options_input(
        **{
            CONF_HOST: "mqtt.example.com",
            CONF_PORT: 1884,
            CONF_USERNAME: "new-user",
            CONF_PASSWORD: "new-pass",
            CONF_KEEPALIVE: 120,
            CONF_DEVICE_ID: "A08241009A99999",
            CONF_OFFLINE_TIMEOUT: 1200,
            CONF_DEBUG_LOGGING: True,
        }
    )

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_validate_broker_connection",
        new_callable=AsyncMock,
    ) as validate:
        result = await flow.async_step_init(user_input)

    validate.assert_awaited_once_with(
        {
            **CONNECTION_INPUT,
            CONF_HOST: "mqtt.example.com",
            CONF_PORT: 1884,
            CONF_USERNAME: "new-user",
            CONF_PASSWORD: "new-pass",
            CONF_KEEPALIVE: 120,
            CONF_DEVICE_ID: "A08241009A99999",
        }
    )
    assert result["type"] == "create_entry"
    assert entry.data[CONF_HOST] == "mqtt.example.com"
    assert entry.data[CONF_PORT] == 1884
    assert entry.data[CONF_USERNAME] == "new-user"
    assert entry.data[CONF_PASSWORD] == "new-pass"
    assert entry.data[CONF_KEEPALIVE] == 120
    assert entry.data[CONF_DEVICE_ID] == "A08241009A99999"
    assert entry.unique_id == "A08241009A99999"
    assert entry.options[CONF_OFFLINE_TIMEOUT] == 1200
    assert entry.options[CONF_DEBUG_LOGGING] is True
    assert "extra_topics" not in entry.options


async def test_options_flow_shows_auth_error_when_new_credentials_fail(hass) -> None:
    entry = _mock_config_entry(options={CONF_OFFLINE_TIMEOUT: 900})
    flow = await _start_options_flow(hass, entry)

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_validate_broker_connection",
        new_callable=AsyncMock,
        side_effect=AsmokeAuthenticationError,
    ):
        result = await flow.async_step_init(
            _options_input(**{CONF_PASSWORD: "bad-pass"})
        )

    assert result["type"] == "form"
    assert result["step_id"] == "init"
    assert result["errors"]["base"] == "invalid_auth"
    assert entry.data[CONF_PASSWORD] == "test-pass"


async def test_options_flow_skips_broker_validation_for_runtime_options_only(
    hass,
) -> None:
    entry = _mock_config_entry(options={CONF_OFFLINE_TIMEOUT: 900})
    flow = await _start_options_flow(hass, entry)

    with patch(
        "custom_components.asmoke_cloud.config_flow.async_validate_broker_connection",
        new_callable=AsyncMock,
    ) as validate:
        result = await flow.async_step_init(
            _options_input(**{CONF_OFFLINE_TIMEOUT: 1800})
        )

    validate.assert_not_awaited()
    assert result["type"] == "create_entry"
    assert entry.options[CONF_OFFLINE_TIMEOUT] == 1800
