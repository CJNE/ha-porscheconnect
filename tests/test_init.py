"""Test Porsche Connect setup process."""
import pytest
from custom_components.porscheconnect import async_reload_entry
from custom_components.porscheconnect import async_setup_entry
from custom_components.porscheconnect import async_unload_entry
from custom_components.porscheconnect import configured_instances
from custom_components.porscheconnect import PorscheConnectDataUpdateCoordinator
from custom_components.porscheconnect.const import (
    DOMAIN,
)
from homeassistant.exceptions import ConfigEntryNotReady
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.
async def test_setup_unload_and_reload_entry(hass, bypass_get_data):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the PorscheConnectDataUpdateCoordinator.async_get_data
    # call, no code from custom_components/porscheconnect/api.py actually runs.
    assert await async_setup_entry(hass, config_entry)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        == PorscheConnectDataUpdateCoordinator
    )

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        == PorscheConnectDataUpdateCoordinator
    )

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]
    instances = configured_instances(hass)
    print(instances)
    assert "test_username" in instances


async def test_setup_entry_exception(hass, error_on_get_data):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_on_get_data` fixture which simulates
    # an error.
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)


# Here we simiulate a successful config flow from the backend.
# Note that we use the `bypass_get_data` fixture here because
# we want the config flow validation to succeed during the test.
# async def test_configured_instances(hass, bypass_connection_connect):
#     """Test a successful config flow."""
#     # Initialize a config flow
#     await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )
