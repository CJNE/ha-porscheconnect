"""Test myenergi sensor."""
from unittest.mock import MagicMock

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant

from . import setup_mock_porscheconnect_config_entry

TEST_CLIMATE_SWITCH_ENTITY_ID = "switch.taycan_turbo_s_climatisation"
TEST_CHARGE_SWITCH_ENTITY_ID = "switch.taycan_turbo_s_direct_charge"


async def test_climate(
    hass: HomeAssistant, mock_set_climate_on: MagicMock, mock_set_climate_off: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_CLIMATE_SWITCH_ENTITY_ID)
    assert entity_state
    assert entity_state.state == STATE_OFF
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {
            ATTR_ENTITY_ID: TEST_CLIMATE_SWITCH_ENTITY_ID,
        },
        blocking=False,
    )
    assert mock_set_climate_on.call_count == 0
    await hass.async_block_till_done()
    assert mock_set_climate_on.call_count == 1
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {
            ATTR_ENTITY_ID: TEST_CLIMATE_SWITCH_ENTITY_ID,
        },
        blocking=False,
    )
    assert mock_set_climate_off.call_count == 0
    await hass.async_block_till_done()
    assert mock_set_climate_off.call_count == 1


async def test_directcharge(
    hass: HomeAssistant, mock_set_charge_on: MagicMock, mock_set_charge_off: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_CHARGE_SWITCH_ENTITY_ID)
    assert entity_state
    assert entity_state.state == STATE_OFF
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {
            ATTR_ENTITY_ID: TEST_CHARGE_SWITCH_ENTITY_ID,
        },
        blocking=False,
    )
    assert mock_set_charge_on.call_count == 0
    await hass.async_block_till_done()
    assert mock_set_charge_on.call_count == 1
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {
            ATTR_ENTITY_ID: TEST_CHARGE_SWITCH_ENTITY_ID,
        },
        blocking=False,
    )
    assert mock_set_charge_off.call_count == 0
    await hass.async_block_till_done()
    assert mock_set_charge_off.call_count == 1
