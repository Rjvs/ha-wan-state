"""Config flow for WAN Failover Monitor."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_ENABLE_CELLULAR, CONF_NAME, CONF_TOPIC_PREFIX, DEFAULT_NAME, DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_TOPIC_PREFIX): str,
        vol.Optional(CONF_ENABLE_CELLULAR, default=True): bool,
    }
)


class WanFailoverMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WAN Failover Monitor."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Ask for the MQTT topic prefix a publisher is using."""
        errors: dict[str, str] = {}

        if user_input is not None:
            prefix = user_input[CONF_TOPIC_PREFIX].strip().strip("/")
            if not prefix:
                errors[CONF_TOPIC_PREFIX] = "invalid_prefix"
            else:
                await self.async_set_unique_id(prefix)
                self._abort_if_unique_id_configured()
                user_input[CONF_TOPIC_PREFIX] = prefix
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> WanFailoverMonitorOptionsFlow:
        """Get the options flow for this handler."""
        return WanFailoverMonitorOptionsFlow(config_entry)


class WanFailoverMonitorOptionsFlow(config_entries.OptionsFlow):
    """Options flow: toggle the cellular status sensors after setup."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.options.get(
            CONF_ENABLE_CELLULAR,
            self._config_entry.data.get(CONF_ENABLE_CELLULAR, True),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Optional(CONF_ENABLE_CELLULAR, default=current): bool}
            ),
        )
