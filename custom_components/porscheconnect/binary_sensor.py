"""Support for the Porsche Connect binary sensors"""
import logging
from typing import Optional
from dataclasses import dataclass

from . import DOMAIN as PORSCHE_DOMAIN
from . import (
    PorscheConnectDataUpdateCoordinator,
    PorscheVehicle,
    PorscheBaseEntity,
    getFromDict,
)


from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from homeassistant.const import (
    PERCENTAGE,
    STATE_UNKNOWN,
    UnitOfElectricCurrent,
    UnitOfLength,
    UnitOfVolume,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.unit_system import UnitSystem


import json  # only for formatting debug outpu

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PorscheBinarySensorEntityDescription(BinarySensorEntityDescription):
    measurement_node: str | None = None
    measurement_leaf: str | None = None
    # is_available: Callable[[PorscheVehicle], bool] = lambda v: v.is_mf_enabled


SENSOR_TYPES: list[PorscheBinarySensorEntityDescription] = [
    PorscheBinarySensorEntityDescription(
        name="Privacy mode",
        key="privacy_mode",
        translation_key="privacy_mode",
        measurement_node="GLOBAL_PRIVACY_MODE",
        measurement_leaf="isEnabled",
        device_class=None,
    ),
    PorscheBinarySensorEntityDescription(
        name="Parking brake",
        key="parking_brake",
        translation_key="parking_brake",
        measurement_node="PARKING_BRAKE",
        measurement_leaf="isOn",
        device_class=None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensors from config entry."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[PORSCHE_DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        PorscheBinarySensor(coordinator, vehicle, description, hass.config.units)
        for vehicle in coordinator.vehicles
        for description in SENSOR_TYPES
    ]

    async_add_entities(entities, True)


class PorscheBinarySensor(PorscheBaseEntity, BinarySensorEntity):
    """Representation of a Porsche binary sensor"""

    entity_description: PorscheBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
        description: PorscheBinarySensorEntityDescription,
        unit_system: UnitSystem,
    ) -> None:
        """Initialize of the sensor"""
        super().__init__(coordinator, vehicle)

        self.entity_description = description
        self._unit_system: unitsystem
        self._attr_name = f'{vehicle["name"]} {description.name}'
        self._attr_unique_id = f'{vehicle["name"]}-{description.key}'

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self._attr_is_on = getFromDict(
            self.coordinator.getDataByVIN(
                self.vehicle["vin"], self.entity_description.measurement_node
            ),
            self.entity_description.measurement_leaf,
        )

        # self._attr_is_on = (state == 'True')

        _LOGGER.debug(
            "Updating binary sensor '%s' of %s with state '%s'",
            self.entity_description.key,
            self.vehicle["name"],
            self._attr_is_on,
            # state,
        )

        super()._handle_coordinator_update()
