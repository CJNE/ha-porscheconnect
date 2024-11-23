"""Support for Porsche lock entity."""

import logging
from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import (
    PorscheConnectDataUpdateCoordinator,
    PorscheVehicle,
    PorscheBaseEntity,
)

from pyporscheconnectapi.exceptions import PorscheException

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Porsche Connect lock entity from config entry."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    async_add_entities(
        PorscheLock(coordinator, vehicle) for vehicle in coordinator.vehicles
    )


class PorscheLock(PorscheBaseEntity, LockEntity):
    """Representation of a Porsche vehicle lock."""

    _attr_translation_key = "lock"

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
    ) -> None:
        """Initialize the lock."""
        super().__init__(coordinator, vehicle)

        self._attr_unique_id = f'{vehicle.data["name"]}-lock'
        self.door_lock_state_available = vehicle.has_remote_services

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the vehicle."""
        try:
            await self.vehicle.remote_services.lock_vehicle()
        except PorscheException as ex:
            self._attr_is_locked = None
            self.async_write_ha_state()
            raise HomeAssistantError(ex) from ex
        finally:
            self.coordinator.async_update_listeners()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the vehicle."""
        pin = kwargs.get("code", None)
        if pin:
            try:
                await self.vehicle.remote_services.unlock_vehicle(pin)
            except PorscheException as ex:
                self._attr_is_locked = None
                self.async_write_ha_state()
                raise HomeAssistantError(ex) from ex
            finally:
                self.coordinator.async_update_listeners()
        else:
            raise ValueError("PIN code not provided.")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Updating lock data of %s", self.vehicle.vin)
        self._attr_is_locked = self.vehicle.vehicle_locked

        super()._handle_coordinator_update()
