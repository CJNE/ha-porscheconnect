"""Test porscheconnect climate entity."""
from unittest.mock import MagicMock

import pytest
from custom_components.porscheconnect import DOMAIN
from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_HVAC_MODES,
    DOMAIN as CLIMATE_DOMAIN,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_TEMPERATURE,
    HVACMode,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from . import setup_mock_porscheconnect_config_entry

TEST_CLIMATE_ENTITY_ID = "climate.taycan_turbo_s_climatisation"


@pytest.mark.asyncio
async def test_climate_state(hass: HomeAssistant, mock_connection) -> None:
    """Verify the climate entity reflects the reported climatisation state."""

    await setup_mock_porscheconnect_config_entry(hass)

    state = hass.states.get(TEST_CLIMATE_ENTITY_ID)
    assert state
    assert state.state == HVACMode.OFF
    assert state.attributes[ATTR_HVAC_MODES] == [HVACMode.OFF, HVACMode.HEAT_COOL]
    assert state.attributes[ATTR_TEMPERATURE] == 20.0


@pytest.mark.asyncio
async def test_climate_running(hass: HomeAssistant, mock_connection) -> None:
    """Verify a running climatisation shows the temperature in use."""
    mock_connection.data["HVAC_SUMMARY"]["status"] = "ON"
    mock_connection.data["HVAC_SUMMARY"]["targetTemperature"] = 295.15

    await setup_mock_porscheconnect_config_entry(hass)

    state = hass.states.get(TEST_CLIMATE_ENTITY_ID)
    assert state.state == HVACMode.HEAT_COOL
    assert state.attributes[ATTR_TEMPERATURE] == 22.0


@pytest.mark.asyncio
async def test_climate_default_temperature(hass: HomeAssistant, mock_connection) -> None:
    """Verify a default target temperature is used when none is reported."""
    del mock_connection.data["HVAC_SUMMARY"]["targetTemperature"]

    await setup_mock_porscheconnect_config_entry(hass)

    state = hass.states.get(TEST_CLIMATE_ENTITY_ID)
    assert state.attributes[ATTR_TEMPERATURE] == 20.0


@pytest.mark.asyncio
async def test_climate_not_created_without_remote_climatisation(
    hass: HomeAssistant, mock_connection
) -> None:
    """Verify no climate entity is created when the vehicle cannot climatise."""
    del mock_connection.data["HVAC_SUMMARY"]

    await setup_mock_porscheconnect_config_entry(hass)

    assert hass.states.get(TEST_CLIMATE_ENTITY_ID) is None


@pytest.mark.asyncio
async def test_climate_turn_on_off(
    hass: HomeAssistant, mock_set_climate_on: MagicMock, mock_set_climate_off: MagicMock
) -> None:
    """Verify turning on and off sends the climatisation commands."""

    await setup_mock_porscheconnect_config_entry(hass)

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: TEST_CLIMATE_ENTITY_ID},
        blocking=True,
    )
    mock_set_climate_on.assert_awaited_once_with(
        target_temperature=pytest.approx(293.15),
        front_left=False,
        front_right=False,
        rear_left=False,
        rear_right=False,
    )

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {ATTR_ENTITY_ID: TEST_CLIMATE_ENTITY_ID, ATTR_HVAC_MODE: HVACMode.OFF},
        blocking=True,
    )
    mock_set_climate_off.assert_awaited_once_with()

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: TEST_CLIMATE_ENTITY_ID},
        blocking=True,
    )
    assert mock_set_climate_off.await_count == 2


@pytest.mark.asyncio
async def test_climate_set_temperature_while_off(
    hass: HomeAssistant, mock_connection, mock_set_climate_on: MagicMock
) -> None:
    """Verify a temperature set while off is kept for the next start."""

    config_entry = await setup_mock_porscheconnect_config_entry(hass)

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {ATTR_ENTITY_ID: TEST_CLIMATE_ENTITY_ID, ATTR_TEMPERATURE: 23.5},
        blocking=True,
    )
    mock_set_climate_on.assert_not_awaited()
    assert hass.states.get(TEST_CLIMATE_ENTITY_ID).attributes[ATTR_TEMPERATURE] == 23.5

    # A poll reporting the previous temperature must not override the choice.
    await hass.data[DOMAIN][config_entry.entry_id].async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(TEST_CLIMATE_ENTITY_ID).attributes[ATTR_TEMPERATURE] == 23.5

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {ATTR_ENTITY_ID: TEST_CLIMATE_ENTITY_ID, ATTR_HVAC_MODE: HVACMode.HEAT_COOL},
        blocking=True,
    )
    assert mock_set_climate_on.await_args.kwargs["target_temperature"] == pytest.approx(
        296.65
    )


@pytest.mark.asyncio
async def test_climate_set_temperature_while_running(
    hass: HomeAssistant, mock_connection, mock_set_climate_on: MagicMock
) -> None:
    """Verify changing the temperature while running restarts with the seat heating."""
    mock_connection.data["HVAC_SUMMARY"]["status"] = "ON"
    mock_connection.data["HVAC_SUMMARY"]["climateZonesEnabled"]["frontLeft"] = True

    await setup_mock_porscheconnect_config_entry(hass)

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {ATTR_ENTITY_ID: TEST_CLIMATE_ENTITY_ID, ATTR_TEMPERATURE: 22.5},
        blocking=True,
    )
    mock_set_climate_on.assert_awaited_once_with(
        target_temperature=pytest.approx(295.65),
        front_left=True,
        front_right=False,
        rear_left=False,
        rear_right=False,
    )


@pytest.mark.asyncio
async def test_climate_command_error(
    hass: HomeAssistant, mock_set_climate_on: MagicMock
) -> None:
    """Verify a rejected command surfaces as a Home Assistant error."""
    mock_set_climate_on.side_effect = ValueError("outside the vehicle's allowed range")

    await setup_mock_porscheconnect_config_entry(hass)

    with pytest.raises(HomeAssistantError, match="allowed range"):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: TEST_CLIMATE_ENTITY_ID},
            blocking=True,
        )
