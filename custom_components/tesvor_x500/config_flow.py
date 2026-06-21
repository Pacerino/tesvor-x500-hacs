"""Config flow for the Tesvor X500 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME

from .const import (
    CONF_ESPHOME_PREFIX,
    CONF_TOPIC_PREFIX,
    DEFAULT_ESPHOME_PREFIX,
    DEFAULT_NAME,
    DEFAULT_TOPIC_PREFIX,
    DOMAIN,
)


class TesvorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tesvor X500."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            prefix = user_input[CONF_TOPIC_PREFIX].strip().rstrip("/")
            esphome_prefix = (
                user_input[CONF_ESPHOME_PREFIX].strip().strip(".")
            )
            await self.async_set_unique_id(prefix)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_TOPIC_PREFIX: prefix,
                    CONF_ESPHOME_PREFIX: esphome_prefix,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(
                    CONF_TOPIC_PREFIX, default=DEFAULT_TOPIC_PREFIX
                ): str,
                vol.Required(
                    CONF_ESPHOME_PREFIX, default=DEFAULT_ESPHOME_PREFIX
                ): str,
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
