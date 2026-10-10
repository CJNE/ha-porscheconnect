"""Test porscheconnect sensor."""
import pytest
from custom_components.porscheconnect import DOMAIN
from homeassistant.const import EntityCategory, UnitOfPressure
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_mock_porscheconnect_config_entry

TEST_MILEAGE_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_mileage"
TEST_CHARGING_STATUS_SENSOR_ENTITY_ID = "sensor.taycan_turbo_s_charging_status"


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
async def test_tire_pressure_deviation_sensors(
    hass: HomeAssistant, mock_connection
) -> None:
    """Verify each tire gets a pressure deviation sensor, disabled by default."""
    mock_connection.data["TIRE_PRESSURE_REAR_RIGHT"] = {
        "differenceBar": 0.25,
        "actualPressureBar": 2.95,
    }

    config_entry = await setup_mock_porscheconnect_config_entry(hass)

    entity_registry = er.async_get(hass)
    entity_ids = {}
    for position in ("front_left", "front_right", "rear_left", "rear_right"):
        entity_id = entity_registry.async_get_entity_id(
            "sensor", DOMAIN, f"Taycan Turbo S-tire_pressure_deviation_{position}"
        )
        assert entity_id == f"sensor.taycan_turbo_s_tire_pressure_deviation_{position}"
        entry = entity_registry.async_get(entity_id)
        assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
        assert entry.entity_category is EntityCategory.DIAGNOSTIC
        assert hass.states.get(entity_id) is None
        entity_registry.async_update_entity(entity_id, disabled_by=None)
        entity_ids[position] = entity_id

    await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()

    front_left = hass.states.get(entity_ids["front_left"])
    assert front_left
    assert float(front_left.state) == -0.1
    assert front_left.attributes["unit_of_measurement"] == UnitOfPressure.BAR
    assert float(hass.states.get(entity_ids["rear_right"]).state) == 0.25


@pytest.mark.asyncio
async def test_tire_pressure_deviation_sensors_need_tpms(
    hass: HomeAssistant, mock_connection
) -> None:
    """Verify no deviation sensor is created for a tire that is not reported."""
    del mock_connection.data["TIRE_PRESSURE_REAR_LEFT"]

    await setup_mock_porscheconnect_config_entry(hass)

    entity_registry = er.async_get(hass)
    assert not entity_registry.async_get_entity_id(
        "sensor", DOMAIN, "Taycan Turbo S-tire_pressure_deviation_rear_left"
    )
    assert entity_registry.async_get_entity_id(
        "sensor", DOMAIN, "Taycan Turbo S-tire_pressure_deviation_front_left"
    )
