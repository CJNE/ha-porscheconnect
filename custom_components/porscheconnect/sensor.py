"""Support for the Porsche Connect sensors."""
import logging
from typing import Optional

from homeassistant.const import LENGTH_KILOMETERS
from homeassistant.const import LENGTH_MILES
from homeassistant.const import PERCENTAGE
from homeassistant.const import TIME_DAYS
from homeassistant.helpers.entity import Entity

from . import DOMAIN as PORSCHE_DOMAIN
from . import PorscheDevice
from .const import DEVICE_NAMES
from .const import HA_SENSOR
from .const import SensorMeta

# from homeassistant.const import TEMP_CELSIUS
# from homeassistant.const import TEMP_FAHRENHEIT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Porsche sensors by config_entry."""
    coordinator = hass.data[PORSCHE_DOMAIN][config_entry.entry_id]
    entities = []
    for vehicle in coordinator.vehicles:
        if vehicle["components"].get(HA_SENSOR, None) is None:
            continue
        for sensor in vehicle["components"][HA_SENSOR]:
            entities.append(PorscheSensor(vehicle, coordinator, sensor))
    async_add_entities(entities, True)


class PorscheSensor(PorscheDevice, Entity):
    """Representation of Porsche sensors."""

    def __init__(self, vehicle, coordinator, sensor_meta: SensorMeta):
        """Initialize of the sensor."""
        super().__init__(vehicle, coordinator)
        self.key = sensor_meta.key
        self.meta = sensor_meta
        device_name = DEVICE_NAMES.get(self.key, self.key)
        self._name = f"{self._name} {device_name}"
        self._unique_id = f"{super().unique_id}_{self.key}"

    @property
    def state(self) -> Optional[float]:
        """Return the state of the sensor."""
        data = self.coordinator.getDataByVIN(self.vin, self.key)
        if data is None:
            return None
        if isinstance(data, str):
            return data
        # _LOGGER.debug(data)
        return data.get("value", None)

    @property
    def unit_of_measurement(self) -> Optional[str]:
        """Return the unit_of_measurement of the device."""
        data = self.coordinator.getDataByVIN(self.vin, self.key)
        if data is None:
            return None
        if isinstance(data, str):
            return None
        units = data.get("unit", None)

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
        return self.meta.device_class

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attrdict = {}
        for attr in self.meta.attributes:
            if attr is not None:
                attrdict[attr.name] = self.coordinator.getDataByVIN(self.vin, attr.key)
        return attrdict
