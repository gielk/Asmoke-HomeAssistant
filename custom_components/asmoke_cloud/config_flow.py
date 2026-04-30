from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlowWithReload
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEBUG_LOGGING,
    CONF_EXTRA_TOPICS,
    CONF_KEEPALIVE,
    CONF_OFFLINE_TIMEOUT,
    DEFAULT_BROKER_HOST,
    DEFAULT_BROKER_PORT,
    DEFAULT_KEEPALIVE,
    DEFAULT_OFFLINE_TIMEOUT,
    DOMAIN,
)
from .mqtt import (
    AsmokeAuthenticationError,
    AsmokeConnectionError,
    AsmokeDiscoveryError,
    async_discover_devices,
    async_validate_broker_connection,
)


def _string_default(value: Any, fallback: str = "") -> str:
    return fallback if value is None else str(value)


def _int_default(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _connection_defaults(values: Mapping[str, Any] | None = None) -> dict[str, Any]:
    values = values or {}
    return {
        CONF_NAME: _string_default(values.get(CONF_NAME)),
        CONF_HOST: _string_default(values.get(CONF_HOST), DEFAULT_BROKER_HOST),
        CONF_PORT: _int_default(values.get(CONF_PORT), DEFAULT_BROKER_PORT),
        CONF_USERNAME: _string_default(values.get(CONF_USERNAME)),
        CONF_PASSWORD: _string_default(values.get(CONF_PASSWORD)),
        CONF_KEEPALIVE: _int_default(values.get(CONF_KEEPALIVE), DEFAULT_KEEPALIVE),
    }


def _connection_config(values: Mapping[str, Any]) -> dict[str, Any]:
    config = _connection_defaults(values)
    config[CONF_NAME] = str(config[CONF_NAME]).strip()
    config[CONF_HOST] = str(config[CONF_HOST]).strip()
    config[CONF_USERNAME] = str(config[CONF_USERNAME]).strip()
    config[CONF_PASSWORD] = str(config[CONF_PASSWORD])
    return config


def _candidate_label(candidate: Mapping[str, Any]) -> str:
    parts = [str(candidate[CONF_DEVICE_ID])]

    if message_count := candidate.get("message_count"):
        parts.append(f"{message_count} messages")
    if status := candidate.get("status"):
        parts.append(f"status {status}")
    if mode := candidate.get("mode"):
        parts.append(f"mode {mode}")
    battery = candidate.get("battery_level")
    if battery is not None:
        parts.append(f"battery {battery}%")

    grill_temps = [
        str(value)
        for value in (candidate.get("grill_temp_1"), candidate.get("grill_temp_2"))
        if value is not None
    ]
    if grill_temps:
        parts.append(f"grill {'/'.join(grill_temps)} C")

    return " - ".join(parts)


class AsmokeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._connection_config: dict[str, Any] | None = None
        self._discovery_candidates: dict[str, dict[str, Any]] = {}
        self._reauth_entry: ConfigEntry | None = None

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithReload:
        return AsmokeOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        defaults = _connection_defaults(user_input)

        if user_input is not None:
            connection_config = _connection_config(user_input)

            try:
                await async_validate_broker_connection(connection_config)
            except AsmokeAuthenticationError:
                errors["base"] = "invalid_auth"
            except AsmokeConnectionError:
                errors["base"] = "cannot_connect"
            else:
                self._connection_config = connection_config
                return await self.async_step_setup_method()

        return self.async_show_form(
            step_id="user",
            data_schema=self._connection_schema(defaults),
            errors=errors,
        )

    async def async_step_setup_method(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if self._connection_config is None:
            return await self.async_step_user()

        return self.async_show_menu(
            step_id="setup_method",
            menu_options=["discover", "manual"],
        )

    async def async_step_discover(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if self._connection_config is None:
            return await self.async_step_user()

        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                discovered = await async_discover_devices(
                    self._connection_config,
                    timeout=45.0,
                )
            except AsmokeAuthenticationError:
                errors["base"] = "invalid_auth"
            except AsmokeDiscoveryError:
                errors["base"] = "device_not_found"
            except AsmokeConnectionError:
                errors["base"] = "cannot_connect"
            else:
                self._discovery_candidates = {
                    str(candidate[CONF_DEVICE_ID]): candidate
                    for candidate in discovered
                }
                return await self.async_step_confirm_discovery()

        return self.async_show_form(
            step_id="discover",
            data_schema=vol.Schema({}),
            errors=errors,
        )

    async def async_step_confirm_discovery(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if self._connection_config is None or not self._discovery_candidates:
            return await self.async_step_discover()

        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = str(user_input[CONF_DEVICE_ID])
            if device_id not in self._discovery_candidates:
                errors["base"] = "unknown_device"
            else:
                merged = {**self._connection_config, CONF_DEVICE_ID: device_id}
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()

                title = str(merged.get(CONF_NAME) or f"Asmoke {device_id}")
                return self.async_create_entry(title=title, data=merged)

        candidate_labels = [
            _candidate_label(candidate)
            for candidate in self._discovery_candidates.values()
        ]
        return self.async_show_form(
            step_id="confirm_discovery",
            data_schema=self._confirm_discovery_schema(),
            errors=errors,
            description_placeholders={
                "candidate_count": str(len(candidate_labels)),
                "candidates": "\n".join(candidate_labels),
            },
        )

    async def async_step_manual(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if self._connection_config is None:
            return await self.async_step_user()

        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = str(user_input[CONF_DEVICE_ID]).strip()
            merged = {**self._connection_config, CONF_DEVICE_ID: device_id}
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()

            title = str(merged.get(CONF_NAME) or f"Asmoke {device_id}")
            return self.async_create_entry(title=title, data=merged)

        return self.async_show_form(
            step_id="manual",
            data_schema=self._manual_schema(user_input or {}),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        self._reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if self._reauth_entry is None:
            return self.async_abort(reason="unknown")

        errors: dict[str, str] = {}
        defaults = _connection_defaults({**self._reauth_entry.data, **(user_input or {})})

        if user_input is not None:
            merged = _connection_config({**self._reauth_entry.data, **user_input})

            try:
                await async_validate_broker_connection(merged)
            except AsmokeAuthenticationError:
                errors["base"] = "invalid_auth"
            except AsmokeConnectionError:
                errors["base"] = "cannot_connect"
            else:
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry,
                    data={**self._reauth_entry.data, **merged},
                )
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=self._reauth_schema(defaults),
            errors=errors,
        )

    def _connection_schema(self, defaults: Mapping[str, Any]) -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional(
                    CONF_NAME,
                    default=_string_default(defaults.get(CONF_NAME)),
                ): str,
                vol.Required(
                    CONF_HOST,
                    default=_string_default(defaults.get(CONF_HOST), DEFAULT_BROKER_HOST),
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=int(defaults.get(CONF_PORT, DEFAULT_BROKER_PORT)),
                ): int,
                vol.Required(
                    CONF_USERNAME,
                    default=_string_default(defaults.get(CONF_USERNAME)),
                ): str,
                vol.Required(
                    CONF_PASSWORD,
                    default=_string_default(defaults.get(CONF_PASSWORD)),
                ): str,
                vol.Required(
                    CONF_KEEPALIVE,
                    default=int(defaults.get(CONF_KEEPALIVE, DEFAULT_KEEPALIVE)),
                ): int,
            }
        )

    def _confirm_discovery_schema(self) -> vol.Schema:
        options = {
            device_id: _candidate_label(candidate)
            for device_id, candidate in self._discovery_candidates.items()
        }
        default = next(iter(options))

        return vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID, default=default): vol.In(options),
            }
        )

    def _manual_schema(self, defaults: Mapping[str, Any]) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(
                    CONF_DEVICE_ID,
                    default=_string_default(defaults.get(CONF_DEVICE_ID)),
                ): vol.All(str, vol.Length(min=1)),
            }
        )

    def _reauth_schema(self, defaults: Mapping[str, Any]) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=_string_default(defaults.get(CONF_HOST), DEFAULT_BROKER_HOST),
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=int(defaults.get(CONF_PORT, DEFAULT_BROKER_PORT)),
                ): int,
                vol.Required(
                    CONF_USERNAME,
                    default=_string_default(defaults.get(CONF_USERNAME)),
                ): str,
                vol.Required(
                    CONF_PASSWORD,
                    default=_string_default(defaults.get(CONF_PASSWORD)),
                ): str,
                vol.Required(
                    CONF_KEEPALIVE,
                    default=int(defaults.get(CONF_KEEPALIVE, DEFAULT_KEEPALIVE)),
                ): int,
            }
        )


class AsmokeOptionsFlow(OptionsFlowWithReload):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_OFFLINE_TIMEOUT): int,
                        vol.Optional(CONF_EXTRA_TOPICS): str,
                        vol.Required(CONF_DEBUG_LOGGING): bool,
                    }
                ),
                {
                    CONF_OFFLINE_TIMEOUT: self.config_entry.options.get(
                        CONF_OFFLINE_TIMEOUT, DEFAULT_OFFLINE_TIMEOUT
                    ),
                    CONF_EXTRA_TOPICS: self.config_entry.options.get(CONF_EXTRA_TOPICS, ""),
                    CONF_DEBUG_LOGGING: self.config_entry.options.get(
                        CONF_DEBUG_LOGGING, False
                    ),
                },
            ),
        )
