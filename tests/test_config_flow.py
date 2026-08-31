"""Test Porsche Connect config flow."""

import base64
from unittest.mock import AsyncMock, call, patch

import pytest
from custom_components.porscheconnect import async_migrate_entry
from custom_components.porscheconnect.const import DOMAIN
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG

MOCK_TOKEN = {"access_token": "test-token"}
MOCK_CAPTCHA = (
    "data:image/svg+xml;base64,"
    + base64.b64encode(
        b'<svg width="150" height="50"></svg>',
    ).decode()
)


@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup of the integration during config flow tests."""
    with (
        patch(
            "custom_components.porscheconnect.async_setup",
            return_value=True,
        ),
        patch(
            "custom_components.porscheconnect.async_setup_entry",
            return_value=True,
        ),
        patch(
            "custom_components.porscheconnect.async_unload_entry",
            return_value=True,
        ),
    ):
        yield


async def test_successful_config_flow(hass: HomeAssistant) -> None:
    """Test a successful config flow without a captcha challenge."""
    with patch(
        "custom_components.porscheconnect.config_flow.validate_input",
        AsyncMock(
            return_value={
                "title": MOCK_CONFIG[CONF_EMAIL],
                CONF_ACCESS_TOKEN: MOCK_TOKEN,
            },
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG,
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == MOCK_CONFIG[CONF_EMAIL]
    assert result["data"] == MOCK_CONFIG | {CONF_ACCESS_TOKEN: MOCK_TOKEN}


async def test_captcha_auth_data_is_not_persisted(hass: HomeAssistant) -> None:
    """Test captcha challenge data is used but not stored."""
    validate = AsyncMock(
        side_effect=[
            {
                **MOCK_CONFIG,
                "captcha": MOCK_CAPTCHA,
                "state": "test-state",
                "code_verifier": "test-verifier",
            },
            {
                "title": MOCK_CONFIG[CONF_EMAIL],
                CONF_ACCESS_TOKEN: MOCK_TOKEN,
            },
        ],
    )
    with patch(
        "custom_components.porscheconnect.config_flow.validate_input",
        validate,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG,
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "captcha"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={"captcha_code": "test-code"},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == MOCK_CONFIG | {CONF_ACCESS_TOKEN: MOCK_TOKEN}
    assert validate.await_args_list == [
        call(MOCK_CONFIG),
        call(
            {
                **MOCK_CONFIG,
                "captcha_code": "test-code",
                "state": "test-state",
                "code_verifier": "test-verifier",
            },
        ),
    ]


async def test_reconfigure_ignores_and_removes_stale_auth_data(
    hass: HomeAssistant,
) -> None:
    """Test reconfigure does not resume a stale captcha challenge."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_CONFIG[CONF_EMAIL],
        data={
            **MOCK_CONFIG,
            CONF_ACCESS_TOKEN: {"access_token": "old-token"},
            "captcha_code": "stale-code",
            "state": "stale-state",
            "code_verifier": "stale-verifier",
            "future_option": True,
        },
        version=2,
    )
    entry.add_to_hass(hass)
    new_password = "new-password"
    validate = AsyncMock(
        return_value={
            "title": MOCK_CONFIG[CONF_EMAIL],
            CONF_ACCESS_TOKEN: MOCK_TOKEN,
        },
    )

    with patch(
        "custom_components.porscheconnect.config_flow.validate_input",
        validate,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "change_password"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_PASSWORD: new_password},
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    validate.assert_awaited_once_with(
        {
            CONF_EMAIL: MOCK_CONFIG[CONF_EMAIL],
            CONF_PASSWORD: new_password,
        },
    )
    assert entry.data == {
        CONF_EMAIL: MOCK_CONFIG[CONF_EMAIL],
        CONF_PASSWORD: new_password,
        CONF_ACCESS_TOKEN: MOCK_TOKEN,
        "future_option": True,
    }


async def test_migrate_entry_removes_transient_auth_data(
    hass: HomeAssistant,
) -> None:
    """Test migration removes authentication challenge data from stored entries."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            **MOCK_CONFIG,
            CONF_ACCESS_TOKEN: MOCK_TOKEN,
            "captcha_code": "stale-code",
            "state": "stale-state",
            "code_verifier": "stale-verifier",
        },
        version=1,
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry)
    assert entry.version == 2
    assert entry.data == MOCK_CONFIG | {CONF_ACCESS_TOKEN: MOCK_TOKEN}
