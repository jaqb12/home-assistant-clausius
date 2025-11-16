"""Config flow for Clausius integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    DEFAULT_CONFIG,
    DOMAIN,
    ERROR_CONNECTION_FAILED,
)

_LOGGER = logging.getLogger(__name__)


class ClausiusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Clausius."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}
        self._errors: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._data.update(user_input)
            # Don't test connection in config flow to avoid errors
            return await self._async_create_entry()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=DEFAULT_CONFIG[CONF_HOST]): cv.string,
                vol.Required(CONF_PORT, default=DEFAULT_CONFIG[CONF_PORT]): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "error_message": self._get_error_message(errors.get("base", ""))
            },
        )

    async def _async_create_entry(self) -> FlowResult:
        """Create the config entry."""
        return self.async_create_entry(
            title=f"Clausius Heat Pump ({self._data[CONF_HOST]})",
            data=self._data,
        )

    @callback
    def _get_error_message(self, error_type: str) -> str:
        """Get error message for error type."""
        error_messages = {
            "connection": ERROR_CONNECTION_FAILED,
            "unknown": "Unknown error occurred",
        }
        return error_messages.get(error_type, ERROR_CONNECTION_FAILED)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return ClausiusOptionsFlow(config_entry)


class ClausiusOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Clausius."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    "scan_interval",
                    default=self._config_entry.options.get("scan_interval", 60),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )