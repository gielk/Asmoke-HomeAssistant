from __future__ import annotations

import json
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_ENTRY_ID,
    ATTR_PAYLOAD,
    ATTR_TARGET_TEMP,
    DOMAIN,
    SERVICE_PUBLISH_RAW_ACTION,
    SERVICE_SET_SMOKE_TARGET_TEMP,
)
from .coordinator import AsmokeDataUpdateCoordinator

_SERVICES_FLAG = "__services_registered__"

SERVICE_PUBLISH_RAW_ACTION_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional("device_id"): cv.string,
        vol.Required("command"): cv.string,
        vol.Optional(ATTR_PAYLOAD, default={}): vol.Any(dict, cv.string),
    }
)

SERVICE_SET_SMOKE_TARGET_TEMP_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional("device_id"): cv.string,
        vol.Required(ATTR_TARGET_TEMP): vol.Coerce(int),
    }
)


async def async_register_services(hass: HomeAssistant) -> None:
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(_SERVICES_FLAG):
        return

    async def handle_publish_raw_action(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        payload = _parse_payload(call.data.get(ATTR_PAYLOAD, {}))
        await coordinator.runtime.async_publish_action(call.data["command"], payload)

    async def handle_set_smoke_target_temp(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        await coordinator.runtime.async_publish_smoke_target_temp(call.data[ATTR_TARGET_TEMP])

    hass.services.async_register(
        DOMAIN,
        SERVICE_PUBLISH_RAW_ACTION,
        handle_publish_raw_action,
        schema=SERVICE_PUBLISH_RAW_ACTION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SMOKE_TARGET_TEMP,
        handle_set_smoke_target_temp,
        schema=SERVICE_SET_SMOKE_TARGET_TEMP_SCHEMA,
    )

    domain_data[_SERVICES_FLAG] = True


def _all_coordinators(hass: HomeAssistant) -> list[AsmokeDataUpdateCoordinator]:
    return [
        value
        for value in hass.data.get(DOMAIN, {}).values()
        if isinstance(value, AsmokeDataUpdateCoordinator)
    ]


def _resolve_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
) -> AsmokeDataUpdateCoordinator:
    coordinators = _all_coordinators(hass)
    entry_id = call.data.get(ATTR_ENTRY_ID)
    smoker_device_id = call.data.get("device_id")

    if entry_id:
        coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
        if isinstance(coordinator, AsmokeDataUpdateCoordinator):
            return coordinator
        raise ServiceValidationError(f"Unknown config entry: {entry_id}")

    if smoker_device_id:
        for coordinator in coordinators:
            if coordinator.runtime.device_id == smoker_device_id:
                return coordinator
        raise ServiceValidationError(f"Unknown Asmoke device_id: {smoker_device_id}")

    if len(coordinators) == 1:
        return coordinators[0]

    if not coordinators:
        raise ServiceValidationError("No Asmoke entries are loaded")

    raise ServiceValidationError(
        "Multiple Asmoke entries loaded; provide entry_id or device_id"
    )


def _parse_payload(payload: Any) -> dict[str, Any]:
    if payload in ({}, None, ""):
        return {}

    if isinstance(payload, dict):
        return payload

    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as err:
            raise ServiceValidationError("payload must be valid JSON") from err

        if not isinstance(parsed, dict):
            raise ServiceValidationError("payload JSON must decode to an object")
        return parsed

    raise ServiceValidationError("payload must be an object or JSON string")
