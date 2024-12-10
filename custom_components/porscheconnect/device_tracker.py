"""Device tracker for Porsche vehicles."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import (
    PorscheConnectDataUpdateCoordinator,
    PorscheBaseEntity,
)
from .const import DOMAIN
from pyporscheconnectapi.vehicle import PorscheVehicle

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
        if not vehicle.privacy_mode:
            entities.append(PorscheDeviceTracker(coordinator, vehicle))
        else:
            _LOGGER.info("Vehicle is in privacy mode with location tracking disabled")

    async_add_entities(entities)


class PorscheDeviceTracker(PorscheBaseEntity, TrackerEntity):
    """Class describing Porsche Connect device tracker."""

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
    ) -> None:
        """Initialize the device tracker"""
        super().__init__(coordinator, vehicle)

        self._attr_unique_id = vehicle.vin
        self._attr_name = vehicle.model_name
        self._tracking_enabled = True
        self._attr_icon = "mdi:crosshairs-gps"

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device.

        Percentage from 0-100.
        """
        return self.vehicle.main_battery_level

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        data = {"updated_at": self.vehicle.location_updated_at}
        if self._tracking_enabled and self.vehicle.location[2] is not None:
            data["direction"] = float(self.vehicle.location[2])
        return data

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        if self._tracking_enabled and self.vehicle.location[0] is not None:
            return float(self.vehicle.location[0])
        else:
            return None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        if self._tracking_enabled and self.vehicle.location[1] is not None:
            return float(self.vehicle.location[1])
        return None

    @property
    def source_type(self) -> SourceType:
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS
