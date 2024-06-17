"""Config flow for Porsche Connect integration."""
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant import core
from homeassistant import exceptions
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.const import CONF_EMAIL
from homeassistant.const import CONF_PASSWORD
from homeassistant.helpers import aiohttp_client
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

    websession = aiohttp_client.async_get_clientsession(hass)
    conn = Connection(data[CONF_EMAIL], data[CONF_PASSWORD], websession=websession)

    _LOGGER.debug("Attempt login...")
    try:
        await conn._login()
    except WrongCredentials:
        _LOGGER.info("Login failed, wrong credentials.")
        raise InvalidAuth

    token = await conn.getToken()
    #    await conn.close()

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
        try:
            info = await validate_input(self.hass, user_input)
        except InvalidAuth:
            errors["base"] = "auth"
        except Exception:
            errors["base"] = "connect"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
