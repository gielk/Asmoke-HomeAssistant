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
from .local_auth import has_local_auth_defaults, merge_connection_input
from .mqtt import (
    AsmokeAuthenticationError,
    AsmokeConnectionError,
    AsmokeDiscoveryError,
    async_discover_device,
    async_validate_broker_connection,
)


def _string_default(value: Any, fallback: str = "") -> str:
    return fallback if value is None else str(value)


class AsmokeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def _local_auth_status_text(self) -> str:
        if has_local_auth_defaults(self.hass):
            return (
                "present on this Home Assistant instance; broker fields can be "
                "prefilled automatically"
            )

        return (
            "not present yet on this Home Assistant instance; broker fields will "
            "not be prefilled automatically"
        )

    _reauth_entry: ConfigEntry | None = None

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithReload:
        return AsmokeOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return await self.async_step_setup_method()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={"local_auth": self._local_auth_status_text()},
        )

    async def async_step_setup_method(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return self.async_show_menu(
            step_id="setup_method",
            menu_options=["discover", "manual"],
        )

    async def async_step_discover(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        defaults = merge_connection_input(user_input, self.hass)

        if user_input is not None:
            merged = merge_connection_input(user_input, self.hass)

            try:
                discovered = await async_discover_device(merged)
            except AsmokeAuthenticationError:
                errors["base"] = "invalid_auth"
            except AsmokeDiscoveryError:
                errors["base"] = "device_not_found"
            except AsmokeConnectionError:
                errors["base"] = "cannot_connect"
            else:
                merged[CONF_DEVICE_ID] = str(discovered[CONF_DEVICE_ID])
                await self.async_set_unique_id(str(merged[CONF_DEVICE_ID]))
                self._abort_if_unique_id_configured()

                title = str(merged.get(CONF_NAME) or f"Asmoke {merged[CONF_DEVICE_ID]}")
                return self.async_create_entry(title=title, data=merged)

        return self.async_show_form(
            step_id="discover",
            data_schema=self._discover_schema(defaults),
            errors=errors,
            description_placeholders={"local_auth": self._local_auth_status_text()},
        )

    async def async_step_manual(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        defaults = merge_connection_input(user_input, self.hass)

        if user_input is not None:
            merged = merge_connection_input(user_input, self.hass)
            await self.async_set_unique_id(str(merged[CONF_DEVICE_ID]))
            self._abort_if_unique_id_configured()

            try:
                await async_validate_broker_connection(merged)
            except AsmokeAuthenticationError:
                errors["base"] = "invalid_auth"
            except AsmokeConnectionError:
                errors["base"] = "cannot_connect"
            else:
                title = str(merged.get(CONF_NAME) or f"Asmoke {merged[CONF_DEVICE_ID]}")
                return self.async_create_entry(title=title, data=merged)

        return self.async_show_form(
            step_id="manual",
            data_schema=self._manual_schema(defaults),
            errors=errors,
            description_placeholders={"local_auth": self._local_auth_status_text()},
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
        defaults = merge_connection_input(
            {**self._reauth_entry.data, **(user_input or {})},
            self.hass,
        )

        if user_input is not None:
            merged = merge_connection_input(
                {**self._reauth_entry.data, **user_input},
                self.hass,
            )

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

    def _discover_schema(self, defaults: Mapping[str, Any]) -> vol.Schema:
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
                ): str,
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
