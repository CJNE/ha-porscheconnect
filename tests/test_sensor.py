"""Test myenergi sensor."""
from homeassistant.core import HomeAssistant

from . import setup_mock_porscheconnect_config_entry

TEST_MILEAGE_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_mileage_sensor"
TEST_CHARGER_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_charger_sensor"


async def test_mileage_sensor(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_MILEAGE_SENSOR_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "13247"


async def test_charger_sensor(hass: HomeAssistant) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_CHARGER_SENSOR_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "NOT_CHARGING"
