"""Global fixtures for Porsche Connect integration."""
import asyncio
from pyporscheconnectapi.exceptions import PorscheException
from pyporscheconnectapi.exceptions import WrongCredentials
from typing import Any
from unittest.mock import patch

import pytest

# from unittest.mock import Mock

pytest_plugins = "pytest_homeassistant_custom_component"


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


@pytest.fixture(name="auto_enable_custom_integrations", autouse=True)
def auto_enable_custom_integrations(
    hass: Any, enable_custom_integrations: Any  # noqa: F811
) -> None:
    """Enable custom integrations defined in the test dir."""


@pytest.fixture
def mock_connection():
    """Prevent setup."""

    from .fixtures.taycan import GET, POST

    async def mock_get(self, url, params=None):
        print(f"GET {url}")
        print(params)
        ret = GET.get(url, {})
        print(ret)
        return ret

    async def mock_post(self, url, data=None, json=None):
        print(f"POST {url}")
        print(data)
        print(json)
        ret = POST.get(url)
        print(ret)
        return ret

    async def mock_tokens(self, application, wasExpired=False):
        print(f"Request token {application}")
        return {}

    with patch("pyporscheconnectapi.client.Connection.get", mock_get), patch(
        "pyporscheconnectapi.client.Connection.post", mock_post
    ), patch("pyporscheconnectapi.client.Connection._requestToken", mock_tokens):
        yield


@pytest.fixture
def mock_noaccess():
    """Return a mocked client object."""

    async def mock_access(self, vin):
        return False

    with patch("custom_components.porscheconnect.Client.isAllowed", mock_access):
        yield


@pytest.fixture
def mock_lock_lock():
    """Return a mocked client object."""
    with patch("custom_components.porscheconnect.Client.lock") as mock_lock:
        yield mock_lock


@pytest.fixture
def mock_lock_unlock():
    """Return a mocked client object."""
    with patch("custom_components.porscheconnect.Client.unlock") as mock_unlock:
        yield mock_unlock


@pytest.fixture
def mock_set_climate_on():
    """Return a mocked client object."""
    with patch("custom_components.porscheconnect.Client.climateOn") as climate_on:
        yield climate_on


@pytest.fixture
def mock_set_climate_off():
    """Return a mocked client object."""
    with patch("custom_components.porscheconnect.Client.climateOff") as climate_off:
        yield climate_off


@pytest.fixture
def mock_set_charge_on():
    """Return a mocked client object."""
    with patch("custom_components.porscheconnect.Client.directChargeOn") as charge_on:
        yield charge_on


@pytest.fixture
def mock_set_charge_off():
    """Return a mocked client object."""
    with patch("custom_components.porscheconnect.Client.directChargeOff") as charge_off:
        yield charge_off


@pytest.fixture(name="mock_client")
def mock_client_fixture():
    """Prevent setup."""
    with patch("custom_components.porscheconnect.Client") as mock:
        instance = mock.return_value
        instance.getVehicles.return_value = async_return([])
        instance.getAllTokens.return_value = async_return([])
        instance.isTokenRefreshed.return_value = False
        yield


@pytest.fixture(name="mock_client_error")
def mock_client_error_fixture():
    """Prevent setup."""
    with patch("custom_components.porscheconnect.Client") as mock:
        instance = mock.return_value
        instance.getVehicles.return_value = async_return([])
        instance.getVehicles.side_effect = PorscheException("Test")
        instance.getAllTokens.return_value = async_return([])
        yield


@pytest.fixture
def mock_client_update_error():
    """Prevent setup."""
    with patch(
        "custom_components.porscheconnect.Client.getPosition",
        side_effect=PorscheException,
    ):
        yield


# This fixture, when used, will result in calls to async_get_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="bypass_connection_connect")
def bypass_connection_connect_fixture():
    """Skip calls to get data from API."""
    with patch("pyporscheconnectapi.connection.Connection._login"), patch(
        "pyporscheconnectapi.connection.Connection.getAllTokens"
    ):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_connection_connect")
def error_connection_connect_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "pyporscheconnectapi.connection.Connection._login",
        side_effect=Exception,
    ), patch("pyporscheconnectapi.connection.Connection.getAllTokens"):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_connection_login")
def error_connection_login_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "pyporscheconnectapi.connection.Connection._login",
        side_effect=WrongCredentials,
    ), patch("pyporscheconnectapi.connection.Connection.getAllTokens"):
        yield


# This fixture, when used, will result in calls to async_get_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture():
    """Skip calls to get data from API."""
    with patch(
        "custom_components.porscheconnect.PorscheConnectApiClient.async_get_data"
    ):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.porscheconnect.PorscheConnectApiClient.async_get_data",
        side_effect=Exception,
    ):
        yield
