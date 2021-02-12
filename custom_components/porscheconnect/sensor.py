"""Support for the Porsche Connect sensors."""
from typing import Optional

from homeassistant.components.sensor import DEVICE_CLASSES
from homeassistant.const import (
    LENGTH_KILOMETERS,
    LENGTH_MILES,
    PERCENTAGE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    TIME_DAYS,
)
from homeassistant.helpers.entity import Entity
from homeassistant.util.distance import convert

from . import DOMAIN as PORSCHE_DOMAIN, PorscheDevice
from .const import DEVICE_CLASSES, DEVICE_NAMES


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Porsche sensors by config_entry."""
    coordinator = hass.data[PORSCHE_DOMAIN][config_entry.entry_id]["coordinator"]
    entities = []
    for vehicle in hass.data[PORSCHE_DOMAIN][config_entry.entry_id]["vehicles"]:
        for sensor in vehicle['sensors']:
            entities.append(
                PorscheSensor(
                    vehicle, hass.data[PORSCHE_DOMAIN][config_entry.entry_id]["coordinator"], sensor
                )
            )
    async_add_entities(entities, True)


class PorscheSensor(PorscheDevice, Entity):
    """Representation of Porsche sensors."""
    def __init__(self, vehicle, coordinator, sensor_meta):
        """Initialize of the sensor."""
        super().__init__(vehicle, coordinator)
        self.key = sensor_meta['key']
        self.meta = sensor_meta
        device_name = DEVICE_NAMES.get(self.key, self.key)
        self._name = f"{self._name} {device_name}"
        self._unique_id = f"{super().unique_id}_{self.key}"

    @property
    def state(self) -> Optional[float]:
        """Return the state of the sensor."""
        data = self.coordinator.getDataByVIN(self.vin, self.key)
        if data is None: return None
        return data.get('value', None)

    @property
    def unit_of_measurement(self) -> Optional[str]:
        """Return the unit_of_measurement of the device."""
        units = self.meta['unit']

        if units == "PERCENT":
            return PERCENTAGE
        if units == "DAYS":
            return TIME_DAYS
        if units == "MILES":
            return LENGTH_MILES
        if units == "KILOMETER":
            return LENGTH_KILOMETERS
        return units

    @property
    def device_class(self) -> Optional[str]:
        """Return the device_class of the device."""
        return DEVICE_CLASSES.get(self.key, None)

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attr = self._attributes.copy()
        return attr
