"""Test myenergi sensor."""
import pytest
from custom_components.porscheconnect import PinError
from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import ATTR_CODE
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.const import SERVICE_LOCK
from homeassistant.const import SERVICE_UNLOCK
from homeassistant.const import STATE_LOCKED
from homeassistant.core import HomeAssistant

from . import setup_mock_porscheconnect_config_entry

TEST_DOOR_LOCK_ENTITY_ID = "lock.taycan_turbo_s_door_lock"


@pytest.mark.asyncio
async def test_door_lock(hass: HomeAssistant, mock_lock_lock, mock_lock_unlock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_DOOR_LOCK_ENTITY_ID)
    assert entity_state
    assert entity_state.state == STATE_LOCKED
    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_UNLOCK,
        {
            ATTR_ENTITY_ID: TEST_DOOR_LOCK_ENTITY_ID,
            ATTR_CODE: 1234,
        },
        blocking=False,
    )
    assert mock_lock_unlock.call_count == 0
    await hass.async_block_till_done()
    mock_lock_unlock.assert_called_with("WPTAYCAN", "1234", True)
    assert mock_lock_unlock.call_count == 1

    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_LOCK,
        {
            ATTR_ENTITY_ID: TEST_DOOR_LOCK_ENTITY_ID,
        },
        blocking=False,
    )
    assert mock_lock_lock.call_count == 0
    await hass.async_block_till_done()
    mock_lock_lock.assert_called_with("WPTAYCAN", True)
    assert mock_lock_lock.call_count == 1


@pytest.mark.asyncio
async def test_door_unlock_without_pin(hass: HomeAssistant, mock_lock_unlock) -> None:
    """Verify device information includes expected details."""

    with pytest.raises(PinError):
        await setup_mock_porscheconnect_config_entry(hass)
        entity_state = hass.states.get(TEST_DOOR_LOCK_ENTITY_ID)
        assert entity_state
        assert entity_state.state == STATE_LOCKED
        await hass.services.async_call(
            LOCK_DOMAIN,
            SERVICE_UNLOCK,
            {
                ATTR_ENTITY_ID: TEST_DOOR_LOCK_ENTITY_ID,
            },
            blocking=True,
        )
        await hass.async_block_till_done()
