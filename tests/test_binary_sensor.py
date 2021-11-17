"""Test porscheconnect binary sensor."""
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant

from . import setup_mock_porscheconnect_config_entry

TEST_PARKING_BREAK_ENTITY_ID = "binary_sensor.taycan_turbo_s_parkingbreak"


async def test_pargking_break_sensor(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_PARKING_BREAK_ENTITY_ID)
    assert entity_state.state == STATE_ON
