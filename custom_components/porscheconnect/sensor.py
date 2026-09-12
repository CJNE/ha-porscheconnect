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
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.const import EntityCategory
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
    value_fn: Callable[[PorscheVehicle], object] | None = None
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
        measurement_node="CHARGING_RATE",
        measurement_leaf="chargingRate-kph",
        icon="mdi:speedometer",
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        is_available=lambda v: v.has_electric_drivetrain,
    ),
    PorscheSensorEntityDescription(
        key="charging_finished",
        translation_key="charging_finished",
        measurement_node="CHARGING_SUMMARY",
        measurement_leaf="targetDateTimeWithOffset",
        icon="mdi:clock-end",
        device_class=SensorDeviceClass.TIMESTAMP,
        is_available=lambda v: v.has_electric_drivetrain,
    ),
    PorscheSensorEntityDescription(
        key="charging_power",
        translation_key="charging_power",
        measurement_node="CHARGING_RATE",
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
        # --- Identification ---
    PorscheSensorEntityDescription(
        key="vin",
        translation_key="vin",
        value_fn=lambda v: v.vin,
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    PorscheSensorEntityDescription(
        key="model_year",
        translation_key="model_year",
        value_fn=lambda v: v.model_year,
        icon="mdi:calendar",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),

    # --- Entretien principal ---
    PorscheSensorEntityDescription(
        key="main_service_range",
        translation_key="main_service_range",
        measurement_node="MAIN_SERVICE_RANGE",
        measurement_leaf="kilometers",
        icon="mdi:wrench-clock",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: "MAIN_SERVICE_RANGE" in v.data,
    ),
    PorscheSensorEntityDescription(
        key="main_service_time",
        translation_key="main_service_time",
        measurement_node="MAIN_SERVICE_TIME",
        measurement_leaf="days",
        icon="mdi:wrench-clock",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: "MAIN_SERVICE_TIME" in v.data,
    ),

    # --- Vidange ---
    PorscheSensorEntityDescription(
        key="oil_service_range",
        translation_key="oil_service_range",
        measurement_node="OIL_SERVICE_RANGE",
        measurement_leaf="kilometers",
        icon="mdi:oil",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: "OIL_SERVICE_RANGE" in v.data,
    ),
    PorscheSensorEntityDescription(
        key="oil_service_time",
        translation_key="oil_service_time",
        measurement_node="OIL_SERVICE_TIME",
        measurement_leaf="days",
        icon="mdi:oil",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: "OIL_SERVICE_TIME" in v.data,
    ),

    # --- Entretien intermediaire ---
    PorscheSensorEntityDescription(
        key="intermediate_service_range",
        translation_key="intermediate_service_range",
        measurement_node="INTERMEDIATE_SERVICE_RANGE",
        measurement_leaf="kilometers",
        icon="mdi:wrench-outline",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: "INTERMEDIATE_SERVICE_RANGE" in v.data,
    ),
    PorscheSensorEntityDescription(
        key="intermediate_service_time",
        translation_key="intermediate_service_time",
        measurement_node="INTERMEDIATE_SERVICE_TIME",
        measurement_leaf="days",
        icon="mdi:wrench-outline",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: "INTERMEDIATE_SERVICE_TIME" in v.data,
    ),

    PorscheSensorEntityDescription(
        key="oil_level",
        translation_key="oil_level",
        measurement_node="OIL_LEVEL_CURRENT",
        measurement_leaf="percent",
        icon="mdi:oil-level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        is_available=lambda v: "OIL_LEVEL_CURRENT" in v.data,
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
        self._attr_unique_id = f"{vehicle.data['name']}-{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.entity_description.value_fn:
            state = self.entity_description.value_fn(self.vehicle)
        else:
            state = self.coordinator.get_vechicle_data_leaf(
                self.vehicle,
                self.entity_description.measurement_node,
                self.entity_description.measurement_leaf,
            )

        if type(state) is str and self.entity_description.key not in ("vin",):
            state = state.lower()

        _LOGGER.debug(
            "Updating sensor '%s' of %s with state '%s'",
            self.entity_description.key,
            self.vehicle.data["name"],
            state,
        )

        self._attr_native_value = state
        super()._handle_coordinator_update()
