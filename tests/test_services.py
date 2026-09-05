"""Test Porsche Connect services."""

from custom_components.porscheconnect.const import DOMAIN
from custom_components.porscheconnect.services import SERVICE_CLIMATISATION_START
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from . import setup_mock_porscheconnect_config_entry


def get_device_id(hass: HomeAssistant) -> str:
    """Return the test vehicle device ID."""
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device({(DOMAIN, "WPTAYCAN")})
    assert device
    return device.id


async def test_climatisation_start(
    hass: HomeAssistant,
    mock_climatisation_start,
) -> None:
    """Test starting climatisation through the integration service."""
    await setup_mock_porscheconnect_config_entry(hass)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_CLIMATISATION_START,
        {
            "vehicle": get_device_id(hass),
            "temperature": 20,
            "front_left": True,
        },
        blocking=True,
    )

    mock_climatisation_start.assert_awaited_once_with(
        target_temperature=293.15,
        front_left=True,
        front_right=False,
        rear_left=False,
        rear_right=False,
    )
