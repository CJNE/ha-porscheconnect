"""Support for tracking Porsche cars."""
from typing import Optional

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity

from . import PorscheDevice
from .const import DOMAIN as PORSCHE_DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Porsche device tracket by config_entry."""
    coordinator = hass.data[PORSCHE_DOMAIN][config_entry.entry_id]
    entities = []
    for vehicle in coordinator.vehicles:
        entities.append(PorscheTrackerEntity(vehicle, coordinator))
    async_add_entities(entities, True)


class PorscheTrackerEntity(PorscheDevice, TrackerEntity):
    """A class representing a Porsche device."""

    @property
    def latitude(self) -> Optional[float]:
        """Return latitude value of the device."""
        return self.coordinator.getDataByVIN(self.vin, "carCoordinate.latitude")

    @property
    def longitude(self) -> Optional[float]:
        """Return longitude value of the device."""
        return self.coordinator.getDataByVIN(self.vin, "carCoordinate.longitude")

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:crosshairs-gps"

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        heading = self.coordinator.getDataByVIN(self.vin, "heading")
        return {"heading": heading}
