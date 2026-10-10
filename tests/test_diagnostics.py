"""Test porscheconnect diagnostics."""
import json

import pytest
from custom_components.porscheconnect import DOMAIN
from homeassistant.components.diagnostics import REDACTED
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pyporscheconnectapi.exceptions import PorscheExceptionError
from pytest_homeassistant_custom_component.components.diagnostics import (
    get_diagnostics_for_config_entry,
)

from . import setup_mock_porscheconnect_config_entry

MOCK_STATUS = {
    "vin": "WPTAYCAN",
    "customName": "My Taycan",
    "modelName": "Taycan Turbo S",
    "measurements": [
        {
            "key": "GPS_LOCATION",
            "status": {"isEnabled": True},
            "value": {"location": "59.334591,18.063240", "direction": 90},
        },
        {
            "key": "PAIRING_CODE",
            "status": {"isEnabled": True},
            "value": {"code": "12345678"},
        },
        {
            "key": "CHARGING_PROFILES",
            "status": {"isEnabled": False, "cause": "NOT_SUPPORTED"},
        },
        {
            "key": "MILEAGE",
            "status": {"isEnabled": True},
            "value": {"kilometers": 13247},
        },
    ],
}


@pytest.mark.asyncio
async def test_diagnostics(hass: HomeAssistant, hass_client, mock_connection) -> None:
    """Verify diagnostics expose the raw payload without personal data."""
    mock_connection.status = MOCK_STATUS
    mock_connection.data["GPS_LOCATION"] = {"location": "59.334591,18.063240"}

    config_entry = await setup_mock_porscheconnect_config_entry(hass)
    diagnostics = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)

    dump = json.dumps(diagnostics)
    for secret in (
        "WPTAYCAN",
        "My Taycan",
        "59.33",
        "18.06",
        "12345678",
        "test_username",
        "test_password",
    ):
        assert secret not in dump

    assert diagnostics["entry"]["data"]["email"] == REDACTED
    assert diagnostics["entry"]["data"]["password"] == REDACTED
    assert diagnostics["coordinator"]["last_update_success"] is True
    assert diagnostics["coordinator"]["last_exception"] is None

    vehicle = diagnostics["vehicles"][0]
    assert vehicle["model_name"] == "Taycan Turbo S"
    assert vehicle["capabilities"]["has_electric_drivetrain"] is True
    assert vehicle["capabilities"]["has_ice_drivetrain"] is False

    measurements = {m["key"]: m for m in vehicle["status"]["measurements"]}
    assert measurements["GPS_LOCATION"]["value"] == REDACTED
    assert measurements["PAIRING_CODE"]["value"] == REDACTED
    assert measurements["CHARGING_PROFILES"]["status"] == {
        "isEnabled": False,
        "cause": "NOT_SUPPORTED",
    }
    assert measurements["MILEAGE"]["value"] == {"kilometers": 13247}

    assert vehicle["data"]["GPS_LOCATION"] == REDACTED
    assert vehicle["data"]["MILEAGE"] == {"kilometers": 13247}


@pytest.mark.asyncio
async def test_diagnostics_last_exception(
    hass: HomeAssistant, hass_client, mock_connection
) -> None:
    """Verify the last update error is described without its message."""
    config_entry = await setup_mock_porscheconnect_config_entry(hass)
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    cause = PorscheExceptionError(429, response_body="state=secret-oauth-state")
    error = UpdateFailed(f"Error communicating with API: {cause.message}")
    error.__cause__ = cause
    coordinator.last_exception = error

    diagnostics = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)

    assert "secret-oauth-state" not in json.dumps(diagnostics)
    assert diagnostics["coordinator"]["last_exception"] == {
        "type": "UpdateFailed",
        "cause": "PorscheExceptionError",
        "http_status": 429,
    }
