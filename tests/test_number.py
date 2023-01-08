"""Test porscheconnect number."""
from unittest.mock import MagicMock

import pytest
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import SERVICE_SET_VALUE
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.core import HomeAssistant

from . import setup_mock_porscheconnect_config_entry

TEST_CHARGING_LEVEL_NUMBER_ENTITY_ID = "number.taycan_turbo_s_charging_level_4"


@pytest.mark.asyncio
async def test_number(hass: HomeAssistant, mock_set_charging_level: MagicMock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_CHARGING_LEVEL_NUMBER_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "25"
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: TEST_CHARGING_LEVEL_NUMBER_ENTITY_ID,
            "value": "58",
        },
        blocking=False,
    )
    assert mock_set_charging_level.call_count == 0
    await hass.async_block_till_done()
    assert mock_set_charging_level.call_count == 1
    mock_set_charging_level.assert_called_with(
        "WPTAYCAN", None, 4, minimumChargeLevel=58.0
    )
