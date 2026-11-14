"""Test myenergi sensor."""

import pytest

# from custom_components.porscheconnect import PinError
from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import ATTR_CODE
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.const import SERVICE_LOCK
from homeassistant.const import SERVICE_UNLOCK
from homeassistant.components.lock.const import LockState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_mock_porscheconnect_config_entry

TEST_DOOR_LOCK_ENTITY_ID = "lock.taycan_turbo_s_door_lock"


@pytest.mark.asyncio
async def test_door_lock(
    hass: HomeAssistant, mock_connection, mock_lock_lock, mock_lock_unlock
) -> None:
    """Verify unlocking with a PIN and locking without one."""

    async def _unlock(pin: str) -> None:
        # Simulate the vehicle reporting itself unlocked after the remote call,
        # so the entity no longer requires a code for the lock service.
        mock_connection.data.setdefault("LOCK_STATE_VEHICLE", {})["isLocked"] = False

    mock_lock_unlock.side_effect = _unlock

    await setup_mock_porscheconnect_config_entry(hass)

    entity_state = hass.states.get(TEST_DOOR_LOCK_ENTITY_ID)
    assert entity_state
    assert entity_state.state == LockState.LOCKED
    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_UNLOCK,
        {
            ATTR_ENTITY_ID: TEST_DOOR_LOCK_ENTITY_ID,
            ATTR_CODE: 1234,
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    mock_lock_unlock.assert_awaited_once_with("1234")

    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_LOCK,
        {
            ATTR_ENTITY_ID: TEST_DOOR_LOCK_ENTITY_ID,
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    mock_lock_lock.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_door_lock_with_default_code(
    hass: HomeAssistant, mock_lock_lock, mock_lock_unlock
) -> None:
    """Verify lock and unlock work when a default code is set on the entity."""

    await setup_mock_porscheconnect_config_entry(hass)

    entity_registry = er.async_get(hass)
    entity_registry.async_update_entity_options(
        TEST_DOOR_LOCK_ENTITY_ID, LOCK_DOMAIN, {"default_code": "1234"}
    )
    await hass.async_block_till_done()

    # HA adds the default code to the lock service call as well, so
    # async_lock must accept it.
    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_LOCK,
        {ATTR_ENTITY_ID: TEST_DOOR_LOCK_ENTITY_ID},
        blocking=True,
    )
    mock_lock_lock.assert_awaited_once_with()

    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_UNLOCK,
        {ATTR_ENTITY_ID: TEST_DOOR_LOCK_ENTITY_ID},
        blocking=True,
    )
    mock_lock_unlock.assert_awaited_once_with("1234")


# @pytest.mark.asyncio
# async def test_door_unlock_without_pin(hass: HomeAssistant, mock_lock_unlock) -> None:
#     """Verify device information includes expected details."""
#
#     with pytest.raises(PinError):
#         await setup_mock_porscheconnect_config_entry(hass)
#         entity_state = hass.states.get(TEST_DOOR_LOCK_ENTITY_ID)
#         assert entity_state
#         assert entity_state.state == LockState.LOCKED
#         await hass.services.async_call(
#             LOCK_DOMAIN,
#             SERVICE_UNLOCK,
#             {
#                 ATTR_ENTITY_ID: TEST_DOOR_LOCK_ENTITY_ID,
#             },
#             blocking=True,
#         )
#         await hass.async_block_till_done()
