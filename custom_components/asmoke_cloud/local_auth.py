from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant

from .const import (
    DEFAULT_BROKER_HOST,
    DEFAULT_BROKER_PORT,
    DEFAULT_KEEPALIVE,
    CONF_KEEPALIVE,
    LOCAL_AUTH_CONFIG_FILE,
    LOCAL_AUTH_FILE,
)

_AUTH_ENV_MAPPING = {
    CONF_HOST: "ASMOKE_CLOUD_HOST",
    CONF_PORT: "ASMOKE_CLOUD_PORT",
    CONF_USERNAME: "ASMOKE_CLOUD_USERNAME",
    CONF_PASSWORD: "ASMOKE_CLOUD_PASSWORD",
    CONF_KEEPALIVE: "ASMOKE_CLOUD_KEEPALIVE",
    CONF_DEVICE_ID: "ASMOKE_CLOUD_DEVICE_ID",
    CONF_NAME: "ASMOKE_CLOUD_NAME",
}


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return data if isinstance(data, dict) else {}


def _read_environment() -> dict[str, Any]:
    data: dict[str, Any] = {}

    for key, env_name in _AUTH_ENV_MAPPING.items():
        value = os.getenv(env_name)
        if value in (None, ""):
            continue

        data[key] = int(value) if key in {CONF_PORT, CONF_KEEPALIVE} else value

    return data


def load_local_auth_defaults(hass: HomeAssistant | None = None) -> dict[str, Any]:
    """Load optional local auth defaults from ignored files or environment."""

    package_defaults = _read_json_file(Path(__file__).with_name(LOCAL_AUTH_FILE))
    hass_defaults = (
        _read_json_file(Path(hass.config.path(LOCAL_AUTH_CONFIG_FILE)))
        if hass is not None
        else {}
    )
    environment_defaults = _read_environment()

    merged: dict[str, Any] = {
        CONF_HOST: DEFAULT_BROKER_HOST,
        CONF_PORT: DEFAULT_BROKER_PORT,
        CONF_KEEPALIVE: DEFAULT_KEEPALIVE,
    }
    merged.update(package_defaults)
    merged.update(hass_defaults)
    merged.update(environment_defaults)

    if CONF_NAME not in merged and CONF_DEVICE_ID in merged:
        merged[CONF_NAME] = f"Asmoke {merged[CONF_DEVICE_ID]}"

    return merged


def has_local_auth_defaults(hass: HomeAssistant | None = None) -> bool:
    defaults = load_local_auth_defaults(hass)
    return bool(defaults.get(CONF_USERNAME) and defaults.get(CONF_PASSWORD))


def merge_connection_input(
    user_input: Mapping[str, Any] | None,
    hass: HomeAssistant | None = None,
) -> dict[str, Any]:
    """Merge form input with optional local defaults."""

    defaults = load_local_auth_defaults(hass)
    merged = dict(defaults)

    if user_input:
        for key, value in user_input.items():
            if value not in (None, ""):
                merged[key] = value

    merged[CONF_HOST] = str(merged.get(CONF_HOST, DEFAULT_BROKER_HOST))
    merged[CONF_PORT] = int(merged.get(CONF_PORT, DEFAULT_BROKER_PORT))
    merged[CONF_KEEPALIVE] = int(merged.get(CONF_KEEPALIVE, DEFAULT_KEEPALIVE))

    if CONF_NAME not in merged and CONF_DEVICE_ID in merged:
        merged[CONF_NAME] = f"Asmoke {merged[CONF_DEVICE_ID]}"

    return merged


def local_auth_paths(hass: HomeAssistant | None = None) -> list[str]:
    paths = [str(Path(__file__).with_name(LOCAL_AUTH_FILE))]

    if hass is not None:
        paths.append(hass.config.path(LOCAL_AUTH_CONFIG_FILE))

    return paths
