from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
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


class AsmokeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._connection_config: dict[str, Any] | None = None
        self._reauth_entry: ConfigEntry | None = None

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
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
                return await self.async_step_manual()

        return self.async_show_form(
            step_id="user",
            data_schema=self._connection_schema(defaults),
            errors=errors,
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


class AsmokeOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        entry = self._entry
        errors: dict[str, str] = {}

        if user_input is not None:
            new_data = self._entry_data_from_input(entry.data, user_input)
            new_options = self._options_from_input(entry.options, user_input)
            device_id = str(new_data[CONF_DEVICE_ID])

            if self._device_id_in_use(entry, device_id):
                errors[CONF_DEVICE_ID] = "already_configured"
            elif self._mqtt_settings_changed(entry.data, new_data):
                try:
                    await async_validate_broker_connection(new_data)
                except AsmokeAuthenticationError:
                    errors["base"] = "invalid_auth"
                except AsmokeConnectionError:
                    errors["base"] = "cannot_connect"

            if not errors:
                title = str(new_data.get(CONF_NAME) or f"Asmoke {device_id}")
                self.hass.config_entries.async_update_entry(
                    entry,
                    data=new_data,
                    options=new_options,
                    title=title,
                    unique_id=device_id,
                )
                return self.async_create_entry(title="", data=new_options)

        return self.async_show_form(
            step_id="init",
            data_schema=self._options_schema(entry, user_input),
            errors=errors,
        )

    def _options_schema(
        self,
        entry: ConfigEntry,
        user_input: Mapping[str, Any] | None = None,
    ) -> vol.Schema:
        data_defaults = _connection_defaults({**entry.data, **(user_input or {})})
        options_defaults = {
            CONF_DEVICE_ID: _string_default(
                (user_input or {}).get(CONF_DEVICE_ID, entry.data.get(CONF_DEVICE_ID))
            ),
            CONF_OFFLINE_TIMEOUT: _int_default(
                (user_input or {}).get(
                    CONF_OFFLINE_TIMEOUT,
                    entry.options.get(CONF_OFFLINE_TIMEOUT),
                ),
                DEFAULT_OFFLINE_TIMEOUT,
            ),
            CONF_DEBUG_LOGGING: bool(
                (user_input or {}).get(
                    CONF_DEBUG_LOGGING,
                    entry.options.get(CONF_DEBUG_LOGGING, False),
                )
            ),
        }

        return vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=data_defaults[CONF_HOST],
                ): vol.All(str, vol.Length(min=1)),
                vol.Required(
                    CONF_PORT,
                    default=data_defaults[CONF_PORT],
                ): vol.All(int, vol.Range(min=1, max=65535)),
                vol.Required(
                    CONF_USERNAME,
                    default=data_defaults[CONF_USERNAME],
                ): vol.All(str, vol.Length(min=1)),
                vol.Required(
                    CONF_PASSWORD,
                    default=data_defaults[CONF_PASSWORD],
                ): vol.All(str, vol.Length(min=1)),
                vol.Required(
                    CONF_KEEPALIVE,
                    default=data_defaults[CONF_KEEPALIVE],
                ): vol.All(int, vol.Range(min=5, max=3600)),
                vol.Required(
                    CONF_DEVICE_ID,
                    default=options_defaults[CONF_DEVICE_ID],
                ): vol.All(str, vol.Length(min=1)),
                vol.Required(
                    CONF_OFFLINE_TIMEOUT,
                    default=options_defaults[CONF_OFFLINE_TIMEOUT],
                ): vol.All(int, vol.Range(min=30, max=86400)),
                vol.Required(
                    CONF_DEBUG_LOGGING,
                    default=options_defaults[CONF_DEBUG_LOGGING],
                ): bool,
            }
        )

    def _entry_data_from_input(
        self,
        current: Mapping[str, Any],
        user_input: Mapping[str, Any],
    ) -> dict[str, Any]:
        connection = _connection_config({**current, **user_input})
        device_id = str(user_input[CONF_DEVICE_ID]).strip()
        return {**current, **connection, CONF_DEVICE_ID: device_id}

    def _options_from_input(
        self,
        current: Mapping[str, Any],
        user_input: Mapping[str, Any],
    ) -> dict[str, Any]:
        options = dict(current)
        options.pop("extra_topics", None)
        options[CONF_OFFLINE_TIMEOUT] = int(user_input[CONF_OFFLINE_TIMEOUT])
        options[CONF_DEBUG_LOGGING] = bool(user_input[CONF_DEBUG_LOGGING])
        return options

    def _mqtt_settings_changed(
        self,
        current: Mapping[str, Any],
        new_data: Mapping[str, Any],
    ) -> bool:
        keys = (CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, CONF_KEEPALIVE)
        return any(current.get(key) != new_data.get(key) for key in keys)

    def _device_id_in_use(self, entry: ConfigEntry, device_id: str) -> bool:
        return any(
            other.entry_id != entry.entry_id and other.unique_id == device_id
            for other in self.hass.config_entries.async_entries(DOMAIN)
        )
