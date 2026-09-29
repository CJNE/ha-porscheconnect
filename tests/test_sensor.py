"""Test porscheconnect sensor."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.porscheconnect.const import DOMAIN

from . import setup_mock_porscheconnect_config_entry

TEST_MILEAGE_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_mileage"
TEST_CHARGING_STATUS_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_charging_status"
TEST_LAST_UPDATED_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_last_updated"


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


@pytest.mark.parametrize(
    ("timestamp", "expected"),
    [
        ("2026-09-29T19:16:36Z", "2026-09-29T19:16:36+00:00"),
        ("2026-09-29T20:16:36+01:00", "2026-09-29T19:16:36+00:00"),
        (None, "unknown"),
        ("", "unknown"),
    ],
)
async def test_last_updated_sensor(
    hass: HomeAssistant,
    mock_connection,
    timestamp,
    expected,
) -> None:
    """Expose the vehicle timestamp as an enabled diagnostic timestamp sensor."""
    mock_connection.data["GLOBAL_TIMESTAMP"] = {"timestamp": timestamp}
    await setup_mock_porscheconnect_config_entry(hass)

    state = hass.states.get(TEST_LAST_UPDATED_SENSOR_ENTITY_ID)
    assert state is not None
    assert state.state == expected
    assert state.attributes["device_class"] == "timestamp"
    assert state.attributes["friendly_name"] == "Taycan Turbo S Last updated"
    entity = er.async_get(hass).async_get(TEST_LAST_UPDATED_SENSOR_ENTITY_ID)
    assert entity is not None
    assert entity.entity_category == er.EntityCategory.DIAGNOSTIC
    assert entity.disabled_by is None


async def test_last_updated_follows_vehicle_report(
    hass: HomeAssistant,
    mock_connection,
) -> None:
    """Polling and SOC/location changes must not invent a vehicle report time."""
    entry = await setup_mock_porscheconnect_config_entry(hass)
    coordinator = hass.data[DOMAIN][entry.entry_id]
    state = hass.states.get(TEST_LAST_UPDATED_SENSOR_ENTITY_ID)
    assert state is not None
    assert state.state == "unknown"

    mock_connection.data["GLOBAL_TIMESTAMP"] = {"timestamp": "2026-09-29T19:00:00Z"}
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert (
        hass.states.get(TEST_LAST_UPDATED_SENSOR_ENTITY_ID).state
        == "2026-09-29T19:00:00+00:00"
    )
    soc = hass.states.get("sensor.taycan_turbo_s_state_of_charge").state

    # A new report with the same SOC still advances the vehicle timestamp.
    mock_connection.data["GLOBAL_TIMESTAMP"]["timestamp"] = "2026-09-29T19:30:00Z"
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    state = hass.states.get(TEST_LAST_UPDATED_SENSOR_ENTITY_ID)
    assert state.state == "2026-09-29T19:30:00+00:00"
    assert hass.states.get("sensor.taycan_turbo_s_state_of_charge").state == soc

    # Fetching cached data, even with other changes, must not advance it.
    mock_connection.data["BATTERY_LEVEL"]["percent"] = 97
    mock_connection.data["GPS_LOCATION"] = {"lastModified": "2026-09-29T20:00:00Z"}
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(TEST_LAST_UPDATED_SENSOR_ENTITY_ID).state == state.state

    # Losing the timestamp must not fall back to a poll, SOC, or location time.
    del mock_connection.data["GLOBAL_TIMESTAMP"]
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(TEST_LAST_UPDATED_SENSOR_ENTITY_ID).state == "unknown"
