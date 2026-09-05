"""Config flow for Porsche Connect integration."""

from __future__ import annotations

import base64
import logging

import voluptuous as vol
from homeassistant import exceptions
from homeassistant.config_entries import (
    CONN_CLASS_CLOUD_POLL,
    SOURCE_REAUTH,
    SOURCE_RECONFIGURE,
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from pyporscheconnectapi.connection import Connection
from pyporscheconnectapi.exceptions import (
    PorscheCaptchaRequiredError,
    PorscheExceptionError,
    PorscheWrongCredentialsError,
)

from .const import (
    CONF_CAPTCHA_CODE,
    CONF_CODE_VERIFIER,
    CONF_OAUTH_STATE,
    DOMAIN,
    TRANSIENT_AUTH_FIELDS,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({CONF_EMAIL: str, CONF_PASSWORD: str})
CHANGE_PASSWORD_SCHEMA = vol.Schema({CONF_PASSWORD: str})


async def validate_input(data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    token = {}
    try:
        conn = Connection(
            email=data[CONF_EMAIL],
            password=data[CONF_PASSWORD],
            captcha_code=data.get(CONF_CAPTCHA_CODE),
            state=data.get(CONF_OAUTH_STATE),
            code_verifier=data.get(CONF_CODE_VERIFIER),
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
            CONF_OAUTH_STATE: exc.state,
            CONF_CODE_VERIFIER: exc.code_verifier,
        }
    except PorscheWrongCredentialsError as exc:
        _LOGGER.info("Wrong credentials.")
        raise InvalidAuth from exc
    except PorscheExceptionError as exc:
        _LOGGER.info("Authentication flow error: %s", exc.message)
        raise InvalidAuth from exc
    except Exception as exc:
        _LOGGER.info("Login failed: %s", exc)
        raise InvalidAuth from exc

    return {"title": data[CONF_EMAIL], CONF_ACCESS_TOKEN: token}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Porsche Connect."""

    VERSION = 2
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    email = None
    password = None
    captcha = None
    state = None
    code_verifier = None

    @callback
    def _get_entry_for_current_flow(self):
        """Return the existing entry for reauth/reconfigure flows."""
        if self.source == SOURCE_REAUTH:
            return self._get_reauth_entry()
        if self.source == SOURCE_RECONFIGURE:
            return self._get_reconfigure_entry()
        return None

    @callback
    def _get_expected_unique_id(self) -> str | None:
        """Return the account identifier for the current flow.

        Older entries may not have a unique_id yet, so fall back to the stored email.
        """
        if entry := self._get_entry_for_current_flow():
            return entry.unique_id or entry.data.get(CONF_EMAIL)
        return self.unique_id

    @callback
    def _abort_if_account_mismatch(self) -> None:
        """Abort if reauth/reconfigure targets a different account."""
        expected_unique_id = self._get_expected_unique_id()
        if expected_unique_id is None or self.unique_id == expected_unique_id:
            return
        self._abort_if_unique_id_mismatch()

    @callback
    def _get_entry_data(self, email: str, password: str, access_token) -> dict:
        """Build persistent config entry data without transient auth fields."""
        entry = self._get_entry_for_current_flow()
        entry_data = dict(entry.data) if entry else {}
        for field in TRANSIENT_AUTH_FIELDS:
            entry_data.pop(field, None)
        entry_data.update(
            {
                CONF_EMAIL: email,
                CONF_PASSWORD: password,
                CONF_ACCESS_TOKEN: access_token,
            },
        )
        return entry_data

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}
        _LOGGER.debug("Validating input.")

        unique_id = f"{user_input[CONF_EMAIL]}"
        await self.async_set_unique_id(unique_id)

        try:
            info = await validate_input(user_input)
            if info.get("captcha") and info.get("state"):
                self.email = info.get("email")
                self.password = info.get("password")
                self.captcha = info.get("captcha")
                self.state = info.get("state")
                self.code_verifier = info.get("code_verifier")
                return self._async_form_captcha()
            entry_data = self._get_entry_data(
                user_input[CONF_EMAIL],
                user_input[CONF_PASSWORD],
                info.get(CONF_ACCESS_TOKEN),
            )

            if self.source == SOURCE_REAUTH:
                self._abort_if_account_mismatch()
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    unique_id=self.unique_id,
                    data=entry_data,
                )

            if self.source == SOURCE_RECONFIGURE:
                self._abort_if_account_mismatch()
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(),
                    unique_id=self.unique_id,
                    data=entry_data,
                )

            return self.async_create_entry(
                title=info["title"],
                data=entry_data,
            )

        except InvalidAuth:
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, user_input=None) -> ConfigFlowResult:
        """Handle configuration by re-auth."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"],
        )
        await self.async_set_unique_id(
            self._get_expected_unique_id(),
            raise_on_progress=False,
        )
        return await self.async_step_user()

    async def async_step_reconfigure(self, user_input=None) -> ConfigFlowResult:
        """Handle a reconfiguration flow initialized by the user."""
        self._existing_entry_data = dict(self._get_reconfigure_entry().data)
        await self.async_set_unique_id(
            self._get_expected_unique_id(),
            raise_on_progress=False,
        )
        return await self.async_step_change_password()

    async def async_step_change_password(self, user_input=None) -> ConfigFlowResult:
        """Show the change password step."""
        if user_input is not None:
            return await self.async_step_user(
                {
                    CONF_EMAIL: self._existing_entry_data[CONF_EMAIL],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
            )

        return self.async_show_form(
            step_id="change_password",
            data_schema=CHANGE_PASSWORD_SCHEMA,
            description_placeholders={
                CONF_EMAIL: self._existing_entry_data[CONF_EMAIL],
            },
        )

    async def async_step_captcha(
        self,
        user_input: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        """Captcha verification step."""
        if user_input is not None:
            user_input = {
                CONF_EMAIL: self.email,
                CONF_PASSWORD: self.password,
                CONF_CAPTCHA_CODE: user_input[CONF_CAPTCHA_CODE],
                CONF_OAUTH_STATE: self.state,
                CONF_CODE_VERIFIER: self.code_verifier,
            }
            errors = {}
            try:
                info = await validate_input(user_input)

                # Handle case where another captcha is required
                if info.get("captcha") and info.get("state"):
                    self.captcha = info.get("captcha")
                    self.state = info.get("state")
                    self.code_verifier = info.get("code_verifier")
                    return self._async_form_captcha()

                entry_data = self._get_entry_data(
                    user_input[CONF_EMAIL],
                    user_input[CONF_PASSWORD],
                    info.get(CONF_ACCESS_TOKEN),
                )

                if self.source == SOURCE_REAUTH:
                    self._abort_if_account_mismatch()
                    return self.async_update_reload_and_abort(
                        self._get_reauth_entry(),
                        unique_id=self.unique_id,
                        data=entry_data,
                    )

                if self.source == SOURCE_RECONFIGURE:
                    self._abort_if_account_mismatch()
                    return self.async_update_reload_and_abort(
                        self._get_reconfigure_entry(),
                        unique_id=self.unique_id,
                        data=entry_data,
                    )

                return self.async_create_entry(
                    title=info["title"],
                    data=entry_data,
                )

            except InvalidAuth:
                errors["base"] = "invalid_auth"
                return self.async_show_form(
                    step_id="captcha",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                CONF_CAPTCHA_CODE,
                                default=vol.UNDEFINED,
                            ): str,
                        },
                    ),
                    errors=errors,
                    description_placeholders={
                        "captcha_img": '<img src="' + self.captcha + '" />',
                    },
                )

        return self._async_form_captcha()

    @callback
    def _async_form_captcha(
        self,
    ) -> ConfigFlowResult:
        """Captcha verification form."""
        # We edit the SVG for better visibility

        (header, payload) = self.captcha.split(",")
        svg = base64.b64decode(payload)
        svg = svg.replace(
            b'width="150" height="50"',
            b'width="300" height="100" style="background-color:white"',
        )
        payload = base64.b64encode(svg)
        self.captcha = header + "," + payload.decode("ascii")

        return self.async_show_form(
            step_id="captcha",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CAPTCHA_CODE, default=vol.UNDEFINED): str,
                },
            ),
            description_placeholders={
                "captcha_img": '<img src="' + self.captcha + '" />',
            },
        )


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class CaptchaRequired(exceptions.HomeAssistantError):
    """Error to indicate captcha verification is required."""
