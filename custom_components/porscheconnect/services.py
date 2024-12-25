"""Porsche Connect services."""

from __future__ import annotations

import logging
from collections.abc import Mapping

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from pyporscheconnectapi.exceptions import PorscheExceptionError
from pyporscheconnectapi.vehicle import PorscheVehicle

from . import (
    PorscheConnectDataUpdateCoordinator,
)
from .const import DOMAIN

LOGGER = logging.getLogger(__name__)

ATTR_VEHICLE = "vehicle"

ATTR_TEMPERATURE = "temperature"
ATTR_FRONT_LEFT = "front_left"
ATTR_FRONT_RIGHT = "front_right"
ATTR_REAR_LEFT = "rear_left"
ATTR_REAR_RIGHT = "rear_right"

SERVICE_VEHICLE_SCHEMA = vol.Schema(
    {
        vol.Required("vehicle"): cv.string,
    }
)

SERVICE_CLIMATISATION_START_SCHEMA = SERVICE_VEHICLE_SCHEMA.extend(
    {
        vol.Optional(ATTR_TEMPERATURE): cv.positive_float,
        vol.Optional(ATTR_FRONT_LEFT): cv.boolean,
        vol.Optional(ATTR_FRONT_RIGHT): cv.boolean,
        vol.Optional(ATTR_REAR_LEFT): cv.boolean,
        vol.Optional(ATTR_REAR_RIGHT): cv.boolean,
    }
)

SERVICE_CLIMATISATION_START = "climatisation_start"

SERVICES = [
    SERVICE_CLIMATISATION_START,
]


def setup_services(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> None:
    """Register the Porsche Connect service actions."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    async def climatisation_start(service_call: ServiceCall) -> None:
        """Start climatisation."""
        temperature: float = service_call.data.get(ATTR_TEMPERATURE)
        front_left: bool = service_call.data.get(ATTR_FRONT_LEFT)
        front_right: bool = service_call.data.get(ATTR_FRONT_RIGHT)
        rear_left: bool = service_call.data.get(ATTR_REAR_LEFT)
        rear_right: bool = service_call.data.get(ATTR_REAR_RIGHT)

        LOGGER.debug(
            "Starting climatisation: %s, %s, %s, %s, %s",
            temperature,
            front_left,
            front_right,
            rear_left,
            rear_right,
        )
        vehicle = get_vehicle(service_call.data)
        try:
            await vehicle.remote_services.climatise_on(
                target_temperature=293.15
                if temperature is None
                else temperature + 273.15,
                front_left=front_left or False,
                front_right=front_right or False,
                rear_left=rear_left or False,
                rear_right=rear_right or False,
            )
        except PorscheExceptionError as ex:
            raise HomeAssistantError(ex) from ex

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLIMATISATION_START,
        climatisation_start,
        schema=SERVICE_CLIMATISATION_START_SCHEMA,
    )

    def get_vehicle(service_call_data: Mapping) -> PorscheVehicle:
        """Get vehicle from service_call data."""
        device_registry = dr.async_get(hass)
        device_id = service_call_data[ATTR_VEHICLE]
        device_entry = device_registry.async_get(device_id)

        if device_entry is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_device_id",
                translation_placeholders={"device_id": device_id},
            )

        for vehicle in coordinator.vehicles:
            if (DOMAIN, vehicle.vin) in device_entry.identifiers:
                return vehicle

        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="no_config_entry_for_device",
            translation_placeholders={"device_id": device_entry.name or device_id},
        )
