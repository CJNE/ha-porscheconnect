"""Test myenergi sensor."""
from unittest.mock import MagicMock

import pytest
from custom_components.porscheconnect import DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import create_mock_porscheconnect_config_entry
from . import setup_mock_porscheconnect_config_entry

TEST_CHARGE_SWITCH_ENTITY_ID = "switch.taycan_turbo_s_direct_charging"


@pytest.mark.asyncio
async def test_climatisation_switch_removed(
    hass: HomeAssistant, mock_connection: MagicMock
) -> None:
    """The climatisation switch of earlier versions is removed from the registry."""
    config_entry = create_mock_porscheconnect_config_entry(hass)
    entity_registry = er.async_get(hass)
    entity_registry.async_get_or_create(
        SWITCH_DOMAIN,
        DOMAIN,
        "WPTAYCAN-climatise",
        config_entry=config_entry,
        suggested_object_id="taycan_turbo_s_remote_climatisation",
    )

    await setup_mock_porscheconnect_config_entry(hass, config_entry=config_entry)

    assert not entity_registry.async_get_entity_id(
        SWITCH_DOMAIN, DOMAIN, "WPTAYCAN-climatise"
    )
    assert hass.states.get("switch.taycan_turbo_s_remote_climatisation") is None


@pytest.mark.asyncio
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
    await hass.async_block_till_done()
    mock_set_charge_on.assert_awaited_once_with()
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {
            ATTR_ENTITY_ID: TEST_CHARGE_SWITCH_ENTITY_ID,
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    mock_set_charge_off.assert_awaited_once_with()
