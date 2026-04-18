from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.asmoke_cloud.const import CONF_KEEPALIVE, DOMAIN

MOCK_CONFIG = {
    CONF_DEVICE_ID: "A08241009A12582",
    CONF_NAME: "Asmoke Backyard",
    CONF_HOST: "47.253.1.220",
    CONF_PORT: 1883,
    CONF_USERNAME: "test-user",
    CONF_PASSWORD: "test-pass",
    CONF_KEEPALIVE: 60,
}


@pytest.fixture
def mock_entry() -> MockConfigEntry:
    return MockConfigEntry(domain=DOMAIN, title="Asmoke Backyard", data=MOCK_CONFIG)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
def bypass_runtime_start() -> Generator[AsyncMock]:
    with patch(
        "custom_components.asmoke_cloud.coordinator.AsmokeMqttRuntime.async_start",
        new_callable=AsyncMock,
    ) as mock_start:
        yield mock_start


@pytest.fixture
def bypass_runtime_stop() -> Generator[AsyncMock]:
    with patch(
        "custom_components.asmoke_cloud.coordinator.AsmokeMqttRuntime.async_stop",
        new_callable=AsyncMock,
    ) as mock_stop:
        yield mock_stop
