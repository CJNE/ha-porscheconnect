"""Device tracker for Porsche vehicles."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import (
    PorscheConnectDataUpdateCoordinator,
    PorscheVehicle,
    PorscheBaseEntity,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the device tracker from config entry."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    entities: list[PorscheDeviceTracker] = []

    for vehicle in coordinator.vehicles:
        entities.append(PorscheDeviceTracker(coordinator, vehicle))
        # if not vehicle.privacy_mode:
        #    _LOGGER.info(
        #        (
        #            "Vehicle %s (%s) is in privacy mode with location tracking,"
        #            " disabled defaulting to unknown"
        #        ),
        #        vehicle.name,
        #        vehicle.vin,
        #    )
    async_add_entities(entities)


class PorscheDeviceTracker(PorscheBaseEntity, TrackerEntity):
    """Porsche Connect device tracker."""

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
    ) -> None:
        """Initialize the device tracker"""
        super().__init__(coordinator, vehicle)

        self._attr_unique_id = vehicle["vin"]
        self._attr_name = f'{vehicle["name"]}'
        self._attr_icon = "mdi:crosshairs-gps"
        self._loc = self.coordinator.getDataByVIN(
            self.vehicle["vin"], "GPS_LOCATION.location"
        )
        self._dir = self.coordinator.getDataByVIN(
            self.vehicle["vin"], "GPS_LOCATION.direction"
        )
        self._x, self._y = self._loc.split(",")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {"direction": float(self._dir)}

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        return float(self._x)

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        return float(self._y)

    @property
    def source_type(self) -> SourceType:
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS
