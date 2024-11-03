"""Config flow for Porsche Connect integration."""
import logging
import voluptuous as vol
from collections.abc import Mapping
from typing import Any

from homeassistant import config_entries
from homeassistant import core
from homeassistant import exceptions
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.const import CONF_EMAIL
from homeassistant.const import CONF_PASSWORD
from pyporscheconnectapi.connection import Connection
from pyporscheconnectapi.exceptions import WrongCredentials

from .const import DOMAIN  # pylint:disable=unused-import

# from homeassistant.const import CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({CONF_EMAIL: str, CONF_PASSWORD: str})


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    token = {}
    try:
        conn = Connection(email=data[CONF_EMAIL], password=data[CONF_PASSWORD], token=token)
    except Exception as e:
        _LOGGER.debug(f"Exception {e}")


    _LOGGER.debug("Attempting login")
    try:
        token = await conn.getToken()
    except Exception as e:
        _LOGGER.info(f"Login failed, {e}")
        raise InvalidAuth

    await conn.close()

    # Return info that you want to store in the config entry.
    return {"title": data[CONF_EMAIL], CONF_ACCESS_TOKEN: token}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Porsche Connect."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        _LOGGER.debug("Validating input.")

        try:
            info = await validate_input(self.hass, user_input)
            entry_data = {
                    **user_input,
                    CONF_ACCESS_TOKEN: info.get(CONF_ACCESS_TOKEN),
                }
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except CannotConnect:
            errors["base"] = "cannot_connect"

        if info:
            return self.async_create_entry(
                title=info["title"],
                data=entry_data,
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Handle configuration by re-auth."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_user()

class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
