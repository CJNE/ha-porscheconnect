"""Support for the Porsche Connect number entities."""

from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyporscheconnectapi.vehicle import PorscheVehicle

from . import (
    PorscheBaseEntity,
    PorscheConnectDataUpdateCoordinator,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class PorscheNumberEntityDescription(NumberEntityDescription):
    """Describes a Porsche number entity."""

    value_fn: Callable[[PorscheVehicle], float | int | None]
    remote_service: Callable[[PorscheVehicle, float | int], Coroutine[Any, Any, Any]]
    is_available: Callable[[PorscheVehicle], bool] = lambda _: False


NUMBER_TYPES: list[PorscheNumberEntityDescription] = [
    PorscheNumberEntityDescription(
        key="target_soc",
        translation_key="target_soc",
        device_class=NumberDeviceClass.BATTERY,
        is_available=lambda v: v.has_electric_drivetrain and v.has_remote_services,
        native_max_value=100.0,
        native_min_value=25.0,
        native_unit_of_measurement="%",
        native_step=5.0,
        mode=NumberMode.SLIDER,
        value_fn=lambda v: v.charging_target,
        remote_service=lambda v, o: v.remote_services.update_charging_profile(
            minimumChargeLevel=int(o),
        ),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Porsche number from config entry."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities: list[PorscheNumber] = []

    for vehicle in coordinator.vehicles:
        entities.extend(
            [
                PorscheNumber(coordinator, vehicle, description)
                for description in NUMBER_TYPES
                if description.is_available(vehicle)
            ],
        )
    async_add_entities(entities)


class PorscheNumber(PorscheBaseEntity, NumberEntity):
    """Class describing Porsche Connect number entities."""

    entity_description: PorscheNumberEntityDescription

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
        description: PorscheNumberEntityDescription,
    ) -> None:
        """Initialize an Porsche Number."""
        super().__init__(coordinator, vehicle)

        self.entity_description = description
        self._attr_unique_id = f'{vehicle.data["name"]}-{description.key}'

    @property
    def native_value(self) -> float | None:
        """Return the entity value to represent the entity state."""
        return self.entity_description.value_fn(self.vehicle)

    async def async_set_native_value(self, value: float) -> None:
        """Update to the vehicle."""
        _LOGGER.debug(
            "Executing '%s' on vehicle '%s' to value '%s'",
            self.entity_description.key,
            self.vehicle.vin,
            value,
        )
        try:
            await self.entity_description.remote_service(self.vehicle, value)
        except Exception as ex:
            raise HomeAssistantError(ex) from ex

        self.coordinator.async_update_listeners()
