"""Test porscheconnect sensor."""
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_mock_porscheconnect_config_entry

TEST_MILEAGE_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_mileage"
TEST_CHARGING_STATUS_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_charging_status"
TEST_VEHICLE_DATA_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_vehicle_data_from"


@pytest.mark.asyncio
async def test_mileage_sensor(hass: HomeAssistant, mock_connection) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_MILEAGE_SENSOR_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "13247"


@pytest.mark.asyncio
async def test_charger_sensor(hass: HomeAssistant, mock_connection) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_CHARGING_STATUS_SENSOR_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "not_charging"


@pytest.mark.asyncio
async def test_vehicle_data_timestamp_sensor(
    hass: HomeAssistant, mock_connection
) -> None:
    """Verify the vehicle-reported data timestamp is exposed as a timestamp sensor."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_VEHICLE_DATA_SENSOR_ENTITY_ID)
    assert entity_state
    assert entity_state.state == "2026-10-04T16:17:58+00:00"
    assert entity_state.attributes["device_class"] == "timestamp"
    entry = er.async_get(hass).async_get(TEST_VEHICLE_DATA_SENSOR_ENTITY_ID)
    assert entry
    assert entry.entity_category is None  # a normal sensor, shown with the others
