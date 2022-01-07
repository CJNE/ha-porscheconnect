"""Support for Porsche Connect services."""
# from __future__ import annotations

import logging

from .const import DOMAIN as PORSCHE_DOMAIN

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, device_registry as dr

LOGGER = logging.getLogger(__name__)

ATTR_VEHICLE = "vehicle"


SERVICE_VEHICLE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_VEHICLE): cv.string,
    }
)

SERVICE_HONK_AND_FLASH = "honk_and_flash"
SERVICE_FLASH = "flash"

SERVICES = [
    SERVICE_HONK_AND_FLASH,
    SERVICE_FLASH,
]


def setup_services(hass: HomeAssistant) -> None:
    """Register the Porsche Connect services."""

    async def honk_and_flash(service_call: ServiceCall) -> None:
        """Request honk and flash from vehicle."""

        LOGGER.debug("Honk and flash service request")

        vehicledata = getvehicledata(service_call)
        if "entry_id" in vehicledata:
            coordinator = hass.data[PORSCHE_DOMAIN][vehicledata["entry_id"]]
            await coordinator.controller.honkAndFlash(vehicledata["vin"], True)
        else:
            LOGGER.debug("Vehicle not found")

    async def flash(service_call: ServiceCall) -> None:
        """Request indicator flashes from vehicle."""

        LOGGER.debug("Indicator flash request")

        vehicledata = getvehicledata(service_call)
        if "entry_id" in vehicledata:
            coordinator = hass.data[PORSCHE_DOMAIN][vehicledata["entry_id"]]
            res = await coordinator.controller.flash(vehicledata["vin"], True)
            LOGGER.debug("Indicator flash result: %s", res)
        else:
            LOGGER.debug("Vehicle not found")

    def getvehicledata(service_call: ServiceCall):
        vehicledata = {}
        dev_reg = dr.async_get(hass)
        device = dev_reg.async_get(service_call.data[ATTR_VEHICLE])

        for vdata in hass.data[PORSCHE_DOMAIN].values():
            for vehicle in vdata.vehicles:
                if (PORSCHE_DOMAIN, vehicle["vin"]) in device.identifiers:
                    vehicledata["entry_id"] = list(device.config_entries)[0]
                    vehicledata["vin"] = vehicle["vin"]

        return vehicledata

    hass.services.async_register(
        PORSCHE_DOMAIN,
        SERVICE_HONK_AND_FLASH,
        honk_and_flash,
        schema=SERVICE_VEHICLE_SCHEMA,
    )
    hass.services.async_register(
        PORSCHE_DOMAIN,
        SERVICE_FLASH,
        flash,
        schema=SERVICE_VEHICLE_SCHEMA,
    )


def unload_services(hass: HomeAssistant) -> None:
    """Unload Porsche Connect services."""
    for service in SERVICES:
        hass.services.async_remove(PORSCHE_DOMAIN, service)
