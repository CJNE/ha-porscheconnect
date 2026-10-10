"""Test porscheconnect binary sensor."""
import pytest
from custom_components.porscheconnect import DOMAIN
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import STATE_OFF, STATE_ON, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_mock_porscheconnect_config_entry

TEST_PARKING_BRAKE_ENTITY_ID = "binary_sensor.taycan_turbo_s_parking_brake"


@pytest.mark.asyncio
async def test_pargking_break_sensor(hass: HomeAssistant, mock_connection) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_PARKING_BRAKE_ENTITY_ID)
    assert entity_state
    assert entity_state.state == STATE_ON


@pytest.mark.asyncio
async def test_open_state_sensors(hass: HomeAssistant, mock_connection) -> None:
    """Verify each reported door, lid or window gets its own binary sensor."""
    mock_connection.data["OPEN_STATE_DOOR_FRONT_RIGHT"] = {"isOpen": True}
    mock_connection.data["OPEN_STATE_LID_REAR"] = {"isOpen": False}

    await setup_mock_porscheconnect_config_entry(hass)

    door_left = hass.states.get("binary_sensor.taycan_turbo_s_door_front_left")
    assert door_left
    assert door_left.state == STATE_OFF
    assert door_left.attributes["device_class"] == BinarySensorDeviceClass.DOOR

    door_right = hass.states.get("binary_sensor.taycan_turbo_s_door_front_right")
    assert door_right
    assert door_right.state == STATE_ON

    rear_lid = hass.states.get("binary_sensor.taycan_turbo_s_rear_lid")
    assert rear_lid
    assert rear_lid.state == STATE_OFF


@pytest.mark.asyncio
async def test_open_state_sensors_only_for_reported_parts(
    hass: HomeAssistant, mock_connection
) -> None:
    """Verify no entity is created for a part the vehicle does not report."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_registry = er.async_get(hass)
    assert not entity_registry.async_get_entity_id(
        "binary_sensor", DOMAIN, "Taycan Turbo S-door_rear_left"
    )
    assert not entity_registry.async_get_entity_id(
        "binary_sensor", DOMAIN, "Taycan Turbo S-top"
    )


@pytest.mark.asyncio
async def test_open_state_cosmetic_parts_disabled_by_default(
    hass: HomeAssistant, mock_connection
) -> None:
    """Verify the spoiler and service flap sensors are created disabled."""
    mock_connection.data["OPEN_STATE_SPOILER"] = {"isOpen": False}
    mock_connection.data["OPEN_STATE_SERVICE_FLAP"] = {"isOpen": False}

    await setup_mock_porscheconnect_config_entry(hass)

    entity_registry = er.async_get(hass)
    for key in ("spoiler", "service_flap"):
        entity_id = entity_registry.async_get_entity_id(
            "binary_sensor", DOMAIN, f"Taycan Turbo S-{key}"
        )
        assert entity_id
        entry = entity_registry.async_get(entity_id)
        assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
        assert entry.entity_category is EntityCategory.DIAGNOSTIC
        assert hass.states.get(entity_id) is None
