"""Test Porsche Connect setup."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from custom_components.porscheconnect import PorscheConnectDataUpdateCoordinator
from custom_components.porscheconnect.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pyporscheconnectapi.exceptions import PorscheExceptionError

from . import (
    create_mock_porscheconnect_config_entry,
    setup_mock_porscheconnect_config_entry,
)


async def test_setup_unload_and_reload_entry(
    hass: HomeAssistant,
    mock_connection,
) -> None:
    """Test entry setup, unload, and reload."""
    entry = await setup_mock_porscheconnect_config_entry(hass)

    assert entry.state is ConfigEntryState.LOADED
    assert entry.entry_id in hass.data[DOMAIN]
    assert len(hass.data[DOMAIN][entry.entry_id].vehicles) == 1

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert entry.entry_id not in hass.data[DOMAIN]

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    assert entry.entry_id in hass.data[DOMAIN]


async def test_setup_entry_api_error(
    hass: HomeAssistant,
    mock_connection_error,
) -> None:
    """Test an API error schedules config entry setup retry."""
    entry = create_mock_porscheconnect_config_entry(hass)

    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_entry_initial_load(
    hass: HomeAssistant,
    mock_connection,
) -> None:
    """Test the initial vehicle load."""
    entry = await setup_mock_porscheconnect_config_entry(hass)

    assert len(hass.data[DOMAIN][entry.entry_id].vehicles) == 1
    vehicle = hass.data[DOMAIN][entry.entry_id].vehicles[0]
    vehicle.get_stored_overview.assert_awaited_once_with()
    vehicle.get_picture_locations.assert_awaited_once_with()


async def test_coordinator_update_error(hass: HomeAssistant) -> None:
    """Test API errors are exposed as coordinator update failures."""
    entry = create_mock_porscheconnect_config_entry(hass)
    controller = MagicMock()
    controller.get_vehicles = AsyncMock(side_effect=PorscheExceptionError("Test"))
    coordinator = PorscheConnectDataUpdateCoordinator(
        hass,
        config_entry=entry,
        controller=controller,
    )

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
