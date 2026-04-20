from __future__ import annotations

import json
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_ENTRY_ID,
    ATTR_INGREDIENT_CATEGORY,
    ATTR_K_VALUE,
    ATTR_MODE,
    ATTR_PAYLOAD,
    ATTR_PROBE_TEMP,
    ATTR_TARGET_TEMP,
    ATTR_TARGET_TIME,
    DOMAIN,
    SERVICE_PUBLISH_RAW_ACTION,
    SERVICE_START_COOK,
    SERVICE_STOP_COOK,
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

SERVICE_START_COOK_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional("device_id"): cv.string,
        vol.Required(ATTR_MODE): cv.string,
        vol.Required(ATTR_TARGET_TEMP): vol.Coerce(int),
        vol.Optional(ATTR_PROBE_TEMP): vol.Coerce(int),
        vol.Optional(ATTR_INGREDIENT_CATEGORY): cv.string,
        vol.Optional(ATTR_K_VALUE): cv.string,
        vol.Optional(ATTR_TARGET_TIME): vol.Coerce(int),
    }
)

SERVICE_STOP_COOK_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional("device_id"): cv.string,
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

    async def handle_start_cook(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        mode = _normalize_cook_mode(call.data[ATTR_MODE])
        target_time = call.data.get(ATTR_TARGET_TIME)
        probe_temp = call.data.get(ATTR_PROBE_TEMP)
        ingredient_category = call.data.get(ATTR_INGREDIENT_CATEGORY)
        k_value = call.data.get(ATTR_K_VALUE)

        if mode == "quick" and target_time is None:
            raise ServiceValidationError("target_time is required for quick mode")
        if mode == "roast" and target_time is None:
            raise ServiceValidationError("target_time is required for roast mode")
        if mode == "roast" and probe_temp is None:
            raise ServiceValidationError("probe_temp is required for roast mode")
        if mode == "roast" and ingredient_category is None:
            raise ServiceValidationError("ingredient_category is required for roast mode")
        if mode == "roast" and k_value is None:
            raise ServiceValidationError("k_value is required for roast mode")

        await coordinator.runtime.async_publish_cook_start(
            mode,
            call.data[ATTR_TARGET_TEMP],
            target_time,
            probe_temp,
            ingredient_category,
            k_value,
        )

    async def handle_stop_cook(call: ServiceCall) -> None:
        coordinator = _resolve_coordinator(hass, call)
        await coordinator.runtime.async_publish_stop()

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
    hass.services.async_register(
        DOMAIN,
        SERVICE_START_COOK,
        handle_start_cook,
        schema=SERVICE_START_COOK_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_COOK,
        handle_stop_cook,
        schema=SERVICE_STOP_COOK_SCHEMA,
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


def _normalize_cook_mode(mode: Any) -> str:
    normalized = str(mode).strip().lower()
    if normalized in {"smoke", "quick", "roast"}:
        return normalized

    raise ServiceValidationError("mode must be 'smoke', 'quick' or 'roast'")
