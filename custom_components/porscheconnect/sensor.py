"""Support for the Porsche Connect sensors."""
import logging
from typing import Optional
from dataclasses import dataclass

from . import DOMAIN as PORSCHE_DOMAIN
from . import PorscheConnectDataUpdateCoordinator, PorscheVehicle, PorscheBaseEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.const import (
    PERCENTAGE,
    STATE_UNKNOWN,
    UnitOfElectricCurrent,
    UnitOfLength,
    UnitOfVolume,
)

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback


import json  # only for formatting debug outpu

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PorscheSensorEntityDescription(SensorEntityDescription):
    measurement_node: str | None = None
    measurement_leaf: str | None = None
    # is_available: Callable[[PorscheVehicle], bool] = lambda v: v.is_mf_enabled


SENSOR_TYPES: list[PorscheSensorEntityDescription] = [
    PorscheSensorEntityDescription(
        name="Mileage",
        key="mileage",
        translation_key="mileage",
        measurement_node="MILEAGE",
        measurement_leaf="kilometers",
        icon="mdi:counter",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
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
        PorscheSensor(coordinator, vehicle, description)
        for vehicle in coordinator.vehicles
        for description in SENSOR_TYPES
    ]

    async_add_entities(entities, True)


class PorscheSensor(PorscheBaseEntity, SensorEntity):
    """Representation of a Porsche sensor"""

    entity_description: PorscheSensorEntityDescription

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
        description: PorscheSensorEntityDescription,
    ) -> None:
        """Initialize of the sensor"""
        super().__init__(coordinator, vehicle)

        self.entity_description = description
        self._attr_name = f'{vehicle["name"]} {description.name}'
        self._attr_unique_id = f'{vehicle["name"]}-{description.key}'

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        state = (
            self.coordinator.getDataByVIN(
                self.vehicle["vin"], self.entity_description.measurement_node
            )
        )[self.entity_description.measurement_leaf]

        _LOGGER.debug(
            "Updating sensor '%s' of %s with state '%s'",
            self.entity_description.key,
            self.vehicle["name"],
            state,
        )

        self._attr_native_value = state
        super()._handle_coordinator_update()
