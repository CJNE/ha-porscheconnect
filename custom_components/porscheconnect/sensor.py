"""Support for the Porsche Connect sensors."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfPower,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyporscheconnectapi.vehicle import PorscheVehicle

from . import DOMAIN as PORSCHE_DOMAIN
from . import (
    PorscheBaseEntity,
    PorscheConnectDataUpdateCoordinator,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PorscheSensorEntityDescription(SensorEntityDescription):
    """Class describing Porsche Connect sensor entities."""

    measurement_node: str | None = None
    measurement_leaf: str | None = None
    is_available: Callable[[PorscheVehicle], bool] = lambda v: v.has_porsche_connect


SENSOR_TYPES: list[PorscheSensorEntityDescription] = [
    PorscheSensorEntityDescription(
        key="charging_target",
        translation_key="charging_target",
        measurement_node="CHARGING_SUMMARY",
        measurement_leaf="minSoC",
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        state_class=None,
        suggested_display_precision=0,
        icon="mdi:battery-high",
        is_available=lambda v: v.has_electric_drivetrain,
    ),
    PorscheSensorEntityDescription(
        key="charging_status",
        translation_key="charging_status",
        measurement_node="CHARGING_SUMMARY",
        measurement_leaf="status",
        icon="mdi:battery-charging",
        device_class=SensorDeviceClass.ENUM,
        is_available=lambda v: v.has_electric_drivetrain,
    ),
    PorscheSensorEntityDescription(
        key="charging_rate",
        translation_key="charging_rate",
        measurement_node="BATTERY_CHARGING_STATE",
        measurement_leaf="chargingRate",
        icon="mdi:speedometer",
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        is_available=lambda v: v.has_electric_drivetrain,
    ),
    PorscheSensorEntityDescription(
        key="charging_power",
        translation_key="charging_power",
        measurement_node="BATTERY_CHARGING_STATE",
        measurement_leaf="chargingPower",
        icon="mdi:lightning-bolt-circle",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        is_available=lambda v: v.has_electric_drivetrain,
    ),
    PorscheSensorEntityDescription(
        key="remaining_range_electric",
        translation_key="remaining_range_electric",
        measurement_node="E_RANGE",
        measurement_leaf="kilometers",
        icon="mdi:gauge",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: v.has_electric_drivetrain,
    ),
    PorscheSensorEntityDescription(
        key="state_of_charge",
        translation_key="state_of_charge",
        measurement_node="BATTERY_LEVEL",
        measurement_leaf="percent",
        icon="mdi:battery-medium",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: v.has_electric_drivetrain,
    ),
    PorscheSensorEntityDescription(
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
    PorscheSensorEntityDescription(
        key="remaining_range",
        translation_key="remaining_range",
        measurement_node="RANGE",
        measurement_leaf="kilometers",
        icon="mdi:gas-station",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: v.has_ice_drivetrain,
    ),
    PorscheSensorEntityDescription(
        key="fuel_level",
        translation_key="fuel_level",
        measurement_node="FUEL_LEVEL",
        measurement_leaf="percent",
        icon="mdi:gas-station",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: v.has_ice_drivetrain,
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
        if description.is_available(vehicle)
    ]

    async_add_entities(entities)


class PorscheSensor(PorscheBaseEntity, SensorEntity):
    """Representation of a Porsche sensor."""

    entity_description: PorscheSensorEntityDescription

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
        description: PorscheSensorEntityDescription,
    ) -> None:
        """Initialize of the sensor."""
        super().__init__(coordinator, vehicle)

        self.entity_description = description
        self._attr_unique_id = f'{vehicle.data["name"]}-{description.key}'

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        state = self.coordinator.get_vechicle_data_leaf(
            self.vehicle,
            self.entity_description.measurement_node,
            self.entity_description.measurement_leaf,
        )

        if type(state) is str:
            state = state.lower()

        _LOGGER.debug(
            "Updating sensor '%s' of %s with state '%s'",
            self.entity_description.key,
            self.vehicle.data["name"],
            state,
        )

        self._attr_native_value = state
        super()._handle_coordinator_update()
