"""Binary sensor platform for Porsche Connect."""
from typing import Optional

from homeassistant.components.binary_sensor import BinarySensorEntity

from . import DOMAIN as PORSCHE_DOMAIN
from . import PorscheDevice
from .const import DEVICE_NAMES
from .const import HA_BINARY_SENSOR
from .const import SensorMeta


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup binary_sensor platform."""
    coordinator = hass.data[PORSCHE_DOMAIN][config_entry.entry_id]
    entities = []
    for vehicle in coordinator.vehicles:
        if vehicle["components"].get(HA_BINARY_SENSOR, None) is None:
            continue
        for sensor in vehicle["components"][HA_BINARY_SENSOR]:
            entities.append(PorscheBinarySensor(vehicle, coordinator, sensor))
    async_add_entities(entities, True)


class PorscheBinarySensor(PorscheDevice, BinarySensorEntity):
    """porscheconnect binary_sensor class."""

    def __init__(self, vehicle, coordinator, sensor_meta: SensorMeta):
        """Initialize of the sensor."""
        super().__init__(vehicle, coordinator)
        self.key = sensor_meta.key
        self.meta = sensor_meta
        device_name = DEVICE_NAMES.get(self.key, self.key)
        self._name = f"{self._name} {device_name}"
        self._unique_id = f"{super().unique_id}_{self.key}"

    @property
    def device_class(self) -> Optional[str]:
        """Return the device_class of the device."""
        return self.meta.device_class

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        data = self.coordinator.getDataByVIN(self.vin, self.key)
        if data is None:
            return None
        return data == "ACTIVE"
