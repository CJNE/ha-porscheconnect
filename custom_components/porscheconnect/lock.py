"""Lock platform for Porsche Connect."""
import logging

from homeassistant.components.lock import LockEntity

from . import DOMAIN as PORSCHE_DOMAIN
from . import PorscheDevice
from .const import DEVICE_NAMES
from .const import HA_LOCK
from .const import LockMeta

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup lock platform."""
    coordinator = hass.data[PORSCHE_DOMAIN][entry.entry_id]
    entities = []
    for vehicle in coordinator.vehicles:
        for lock in vehicle["components"][HA_LOCK]:
            entities.append(PorscheConnectLock(vehicle, coordinator, lock))
    async_add_entities(entities)


class PorscheConnectLock(PorscheDevice, LockEntity):
    """Porsche Connect lock class."""

    def __init__(self, vehicle, coordinator, lock_meta: LockMeta):
        """Initialize the lock."""
        super().__init__(vehicle, coordinator)
        self.key = lock_meta.key
        self.meta = lock_meta
        device_name = DEVICE_NAMES.get(self.key, self.key)
        self._name = f"{self._name} {device_name}"
        self._unique_id = f"{super().unique_id}_{self.key}"

    async def async_lock(self, **kwargs):  # pylint: disable=unused-argument
        """Lock the vechicle."""
        _LOGGER.debug("Locking %s", self._name)
        await self.coordinator.controller.lock(self.vin, True)
        await self.coordinator.async_request_refresh()

    async def async_unlock(self, **kwargs):  # pylint: disable=unused-argument
        """Unlock the vechicle."""
        _LOGGER.debug("Unlocking %s", self._name)
        PIN = kwargs["code"] or None
        await self.coordinator.controller.unlock(self.vin, PIN, True)
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def icon(self):
        """Return the icon of this switch."""
        return self.meta.icon

    @property
    def is_locked(self):
        """Return true if the vehicle is locked."""
        data = self.coordinator.getDataByVIN(self.vin, self.key)
        return data == "CLOSED_LOCKED"
