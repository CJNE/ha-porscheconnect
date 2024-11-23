"""Support for the Porsche Connect binary sensors"""
import logging
from dataclasses import dataclass
from collections.abc import Callable

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

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PorscheBinarySensorEntityDescription(BinarySensorEntityDescription):
    measurement_node: str | None = None
    measurement_leaf: str | None = None
    value_fn: Callable[[PorscheVehicle], bool] | None = None
    attr_fn: Callable[[PorscheVehicle], dict[str, str]] | None = None
    # is_available: Callable[[PorscheVehicle], bool] = lambda v: v.is_mf_enabled


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
        name="Closed",
        key="vehicle_closed",
        translation_key="vehicle_closed",
        value_fn=lambda v: v.vehicle_closed,
        attr_fn=lambda v: v.doors_and_lids,
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
        PorscheBinarySensor(coordinator, vehicle, description)
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
    ) -> None:
        """Initialize of the sensor"""
        super().__init__(coordinator, vehicle)

        self.entity_description = description
        self._attr_unique_id = f'{vehicle.data["name"]}-{description.key}'

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.entity_description.value_fn:
            self._attr_is_on = self.entity_description.value_fn(self.vehicle)
        else:
            self._attr_is_on = self.coordinator.getVehicleDataLeaf(
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
                self.vehicle
            )

        super()._handle_coordinator_update()
