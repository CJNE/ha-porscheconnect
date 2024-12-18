"""Config flow for Porsche Connect integration."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from pyporscheconnectapi.connection import Connection
from pyporscheconnectapi.exceptions import (
    PorscheCaptchaRequiredError,
    PorscheExceptionError,
    PorscheWrongCredentialsError,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({CONF_EMAIL: str, CONF_PASSWORD: str})


async def validate_input(data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    token = {}
    try:
        conn = Connection(
            email=data[CONF_EMAIL],
            password=data[CONF_PASSWORD],
            captcha_code=data.get("captcha_code"),
            state=data.get("state"),
            token=token,
        )
    except PorscheExceptionError as exc:
        _LOGGER.debug("Exception %s", exc)

    _LOGGER.debug("Attempting login")
    try:
        token = await conn.get_token()
    except PorscheCaptchaRequiredError as exc:
        _LOGGER.info("Captcha required to log in: %s", exc.captcha)
        return {
            "email": data[CONF_EMAIL],
            "password": data[CONF_PASSWORD],
            "captcha": exc.captcha,
            "state": exc.state,
        }
    except PorscheWrongCredentialsError as exc:
        _LOGGER.info("Wrong credentials.")
        raise InvalidAuth from exc
    except PorscheExceptionError as exc:
        _LOGGER.info("Authentication flow error: %s", exc)
        raise InvalidAuth from exc
    except Exception as exc:
        _LOGGER.info("Login failed: %s", exc)
        raise InvalidAuth from exc

    return {"title": data[CONF_EMAIL], CONF_ACCESS_TOKEN: token}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Porsche Connect."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    email = None
    password = None
    captcha = None
    state = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}
        _LOGGER.debug("Validating input.")

        try:
            info = await validate_input(user_input)
            if info.get("captcha") and info.get("state"):
                self.email = info.get("email")
                self.password = info.get("password")
                self.captcha = info.get("captcha")
                self.state = info.get("state")
                return self._async_form_captcha()
            entry_data = {
                **user_input,
                CONF_ACCESS_TOKEN: info.get(CONF_ACCESS_TOKEN),
            }
            return self.async_create_entry(
                title=info["title"],
                data=entry_data,
            )

        except InvalidAuth:
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors,
        )

    async def async_step_reauth(
        self,
    ) -> config_entries.ConfigFlowResult:
        """Handle configuration by re-auth."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"],
        )
        return await self.async_step_user()

    async def async_step_captcha(
        self, user_input: dict[str, str] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Captcha verification step."""
        if user_input is not None:
            user_input = {
                "email": self.email,
                "password": self.password,
                "captcha_code": user_input["captcha_code"],
                "state": self.state,
            }
            try:
                info = await validate_input(user_input)
                entry_data = {
                    **user_input,
                    CONF_ACCESS_TOKEN: info.get(CONF_ACCESS_TOKEN),
                }
                return self.async_create_entry(
                    title=info["title"],
                    data=entry_data,
                )

            except Exception as exc:
                _LOGGER.info("Login failed: %s", exc)
                raise InvalidAuth from exc

        return self._async_form_captcha()

    @callback
    def _async_form_captcha(
        self,
    ) -> config_entries.ConfigFlowResult:
        """Captcha verification form."""
        return self.async_show_form(
            step_id="captcha",
            data_schema=vol.Schema(
                {
                    vol.Required("captcha_code", default=vol.UNDEFINED): str,
                },
            ),
            description_placeholders={
                "captcha_img": '<img src="' + self.captcha + '"/>',
            },
        )


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class CaptchaRequired(exceptions.HomeAssistantError):
    """Error to indicate captcha verification is required."""
