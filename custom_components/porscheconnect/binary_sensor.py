"""Support for the Porsche Connect binary sensors."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant, callback

from . import DOMAIN as PORSCHE_DOMAIN
from . import (
    PorscheBaseEntity,
    PorscheConnectDataUpdateCoordinator,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from pyporscheconnectapi.vehicle import PorscheVehicle

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PorscheBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Porsche Connect binary sensor entities."""

    measurement_node: str | None = None
    measurement_leaf: str | None = None
    value_fn: Callable[[PorscheVehicle], bool] | None = None
    attr_fn: Callable[[PorscheVehicle], dict[str, str]] | None = None
    is_available: Callable[[PorscheVehicle], bool] = lambda v: v.has_porsche_connect


SENSOR_TYPES: list[PorscheBinarySensorEntityDescription] = [
    PorscheBinarySensorEntityDescription(
        name="Remote access",
        key="remote_access",
        translation_key="remote_access",
        measurement_node="REMOTE_ACCESS_AUTHORIZATION",
        measurement_leaf="isEnabled",
        device_class=None,
    ),
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
    PorscheBinarySensorEntityDescription(
        name="Parking light",
        key="parking_light",
        translation_key="parking_light",
        measurement_node="PARKING_LIGHT",
        measurement_leaf="isOn",
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    PorscheBinarySensorEntityDescription(
        name="Doors and lids",
        key="doors_and_lids",
        translation_key="doors_and_lids",
        value_fn=lambda v: not v.vehicle_closed,
        attr_fn=lambda v: v.doors_and_lids,
        device_class=BinarySensorDeviceClass.OPENING,
    ),
    PorscheBinarySensorEntityDescription(
        name="Tire pressure status",
        key="tire_pressure_status",
        translation_key="tire_pressure_status",
        value_fn=lambda v: not v.tire_pressure_status,
        attr_fn=lambda v: v.tire_pressures,
        is_available=lambda v: v.has_tire_pressure_monitoring,
        device_class=BinarySensorDeviceClass.PROBLEM,
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
        PorscheBinarySensor(coordinator, vehicle, description)
        for vehicle in coordinator.vehicles
        for description in SENSOR_TYPES
        if description.is_available(vehicle)
    ]

    async_add_entities(entities)


class PorscheBinarySensor(BinarySensorEntity, PorscheBaseEntity):
    """Representation of a Porsche binary sensor."""

    entity_description: PorscheBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
        description: PorscheBinarySensorEntityDescription,
    ) -> None:
        """Initialize of the sensor."""
        super().__init__(coordinator, vehicle)

        self.coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f'{vehicle.data["name"]}-{description.key}'

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.entity_description.value_fn:
            self._attr_is_on = self.entity_description.value_fn(self.vehicle)
        else:
            self._attr_is_on = self.coordinator.get_vechicle_data_leaf(
                self.vehicle,
                self.entity_description.measurement_node,
                self.entity_description.measurement_leaf,
            )

        _LOGGER.debug(
            "Updating binary sensor '%s' of %s with state '%s'",
            self.entity_description.key,
            self.vehicle.data["name"],
            self._attr_is_on,
            # state,
        )

        if self.entity_description.attr_fn:
            self._attr_extra_state_attributes = self.entity_description.attr_fn(
                self.vehicle,
            )

        super()._handle_coordinator_update()
