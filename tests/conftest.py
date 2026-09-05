"""Global fixtures for Porsche Connect integration."""

import copy
from unittest.mock import AsyncMock, patch

import pytest
from pyporscheconnectapi.exceptions import PorscheExceptionError
from pyporscheconnectapi.vehicle import PorscheVehicle

MOCK_VEHICLE_DATA = {
    "vin": "WPTAYCAN",
    "name": "Taycan Turbo S",
    "modelName": "Taycan Turbo S",
    "modelType": {"engine": "BEV", "year": "2021"},
    "REMOTE_ACCESS_AUTHORIZATION": {"isEnabled": True},
    "GLOBAL_PRIVACY_MODE": {"isEnabled": False},
    "PARKING_BRAKE": {"isOn": True},
    "PARKING_LIGHT": {"isOn": False},
    "LOCK_STATE_VEHICLE": {"isLocked": True},
    "OPEN_STATE_DOOR_FRONT_LEFT": {"isOpen": False},
    "OPEN_STATE_DOOR_FRONT_RIGHT": {"isOpen": False},
    "TIRE_PRESSURE": {
        "frontLeftTire": {"differenceBar": 0.1},
        "frontRightTire": {"differenceBar": 0.1},
    },
    "BATTERY_LEVEL": {"percent": 96},
    "E_RANGE": {"kilometers": 348},
    "MILEAGE": {"kilometers": 13247},
    "CHARGING_SUMMARY": {
        "minSoC": 25,
        "mode": "PROFILE",
        "status": "NOT_CHARGING",
        "targetDateTimeWithOffset": None,
    },
    "CHARGING_RATE": {"chargingRate-kph": 0, "chargingPower": 0},
    "CLIMATIZER_STATE": {"isOn": False},
}


def create_vehicle() -> PorscheVehicle:
    """Create a vehicle using the current pyporscheconnectapi model."""
    vehicle = PorscheVehicle(
        connection=AsyncMock(),
        data=copy.deepcopy(MOCK_VEHICLE_DATA),
    )
    vehicle.get_stored_overview = AsyncMock()
    vehicle.get_picture_locations = AsyncMock()
    return vehicle


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test directory."""
    yield


@pytest.fixture
def mock_connection():
    """Return one vehicle without making Porsche API requests."""
    vehicle = create_vehicle()
    with patch(
        "pyporscheconnectapi.account.PorscheConnectAccount.get_vehicles",
        AsyncMock(return_value=[vehicle]),
    ):
        yield vehicle


@pytest.fixture
def mock_connection_error():
    """Raise an API error while loading vehicles."""
    with patch(
        "pyporscheconnectapi.account.PorscheConnectAccount.get_vehicles",
        AsyncMock(side_effect=PorscheExceptionError("Test")),
    ):
        yield


@pytest.fixture
def mock_lock_lock(mock_connection):
    """Mock locking a vehicle."""
    with patch(
        "pyporscheconnectapi.remote_services.RemoteServices.lock_vehicle",
        AsyncMock(),
    ) as mock_lock:
        yield mock_lock


@pytest.fixture
def mock_lock_unlock(mock_connection):
    """Mock unlocking a vehicle."""
    with patch(
        "pyporscheconnectapi.remote_services.RemoteServices.unlock_vehicle",
        AsyncMock(),
    ) as mock_unlock:
        yield mock_unlock


@pytest.fixture
def mock_set_charging_level(mock_connection):
    """Mock changing the target state of charge."""
    with patch(
        "pyporscheconnectapi.remote_services.RemoteServices.set_target_soc",
        AsyncMock(),
    ) as set_level:
        yield set_level


@pytest.fixture
def mock_set_climate_on(mock_connection):
    """Mock starting climatisation."""
    with patch(
        "pyporscheconnectapi.remote_services.RemoteServices.climatise_on",
        AsyncMock(),
    ) as climate_on:
        yield climate_on


@pytest.fixture
def mock_set_climate_off(mock_connection):
    """Mock stopping climatisation."""
    with patch(
        "pyporscheconnectapi.remote_services.RemoteServices.climatise_off",
        AsyncMock(),
    ) as climate_off:
        yield climate_off


@pytest.fixture
def mock_set_charge_on(mock_connection):
    """Mock enabling direct charging."""
    with patch(
        "pyporscheconnectapi.remote_services.RemoteServices.direct_charge_on",
        AsyncMock(),
    ) as charge_on:
        yield charge_on


@pytest.fixture
def mock_set_charge_off(mock_connection):
    """Mock disabling direct charging."""
    with patch(
        "pyporscheconnectapi.remote_services.RemoteServices.direct_charge_off",
        AsyncMock(),
    ) as charge_off:
        yield charge_off


@pytest.fixture
def mock_climatisation_start(mock_connection):
    """Mock the climatisation service action."""
    with patch(
        "pyporscheconnectapi.remote_services.RemoteServices.climatise_on",
        AsyncMock(),
    ) as climate_on:
        yield climate_on
