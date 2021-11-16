"""Global fixtures for Porsche Connect integration."""
from typing import Any
from unittest.mock import Mock
from unittest.mock import AsyncMock
from unittest.mock import patch

import asyncio
import pytest
from pyporscheconnectapi.exceptions import WrongCredentials
from pyporscheconnectapi.exceptions import PorscheException

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
        instance.getVehicles.side_effect = PorscheException('Test')
        instance.getAllTokens.return_value = async_return([])
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
