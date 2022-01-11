"""Test porscheconnect number."""
from unittest.mock import MagicMock

from custom_components.porscheconnect.const import DOMAIN as PORSCHE_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from . import setup_mock_porscheconnect_config_entry

SERVICE_HONK_AND_FLASH = "honk_and_flash"
SERVICE_FLASH = "flash"
ATTR_VEHICLE = "vehicle"


def get_device_id(hass: HomeAssistant) -> str:
    """Get device_id."""
    device_registry = dr.async_get(hass)
    identifiers = {(PORSCHE_DOMAIN, "WPTAYCAN")}
    device = device_registry.async_get_device(identifiers)
    return device.id


async def test_honk_and_flash(
    hass: HomeAssistant, mock_honk_and_flash: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)
    data = {
        ATTR_VEHICLE: get_device_id(hass),
    }

    await hass.services.async_call(
        PORSCHE_DOMAIN,
        SERVICE_HONK_AND_FLASH,
        data,
        blocking=False,
    )
    assert mock_honk_and_flash.call_count == 0
    await hass.async_block_till_done()
    assert mock_honk_and_flash.call_count == 1
    mock_honk_and_flash.assert_called_with("WPTAYCAN", True)


async def test_flash(hass: HomeAssistant, mock_flash: MagicMock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_porscheconnect_config_entry(hass)
    data = {
        ATTR_VEHICLE: get_device_id(hass),
    }

    await hass.services.async_call(
        PORSCHE_DOMAIN,
        SERVICE_FLASH,
        data,
        blocking=False,
    )
    assert mock_flash.call_count == 0
    await hass.async_block_till_done()
    assert mock_flash.call_count == 1
    mock_flash.assert_called_with("WPTAYCAN", True)
