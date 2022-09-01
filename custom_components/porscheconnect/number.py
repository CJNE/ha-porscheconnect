"""Support for the Porsche Connect number entities."""
import logging

from homeassistant.components.number import NumberEntity

from . import DOMAIN as PORSCHE_DOMAIN
from . import PorscheDevice
from .const import DEVICE_NAMES
from .const import HA_NUMBER
from .const import NumberMeta

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Porsche charging levels entries."""
    coordinator = hass.data[PORSCHE_DOMAIN][config_entry.entry_id]
    entities = []
    for vehicle in coordinator.vehicles:
        for number in vehicle["components"][HA_NUMBER]:
            profiles = coordinator.getDataByVIN(vehicle["vin"], number.key)
            print(profiles)
            for profile in profiles.keys():
                entities.append(
                    PorscheChargingLevel(
                        vehicle, coordinator, number, profiles[profile]
                    )
                )
    async_add_entities(entities, True)


class PorscheChargingLevel(PorscheDevice, NumberEntity):
    """Representation of Porsche charging level entity."""

    def __init__(self, vehicle, coordinator, number_meta: NumberMeta, profile):
        """Initialize the charge level entity."""
        super().__init__(vehicle, coordinator)
        self.key = number_meta.key
        self.meta = number_meta
        self.profile_id = profile["profileId"]
        self.profile_id_str = str(self.profile_id)
        self.profile_name = profile["profileName"]
        self.profile_level = profile["chargingOptions"]["minimumChargeLevel"]
        device_name = DEVICE_NAMES.get(self.key, self.key)
        self._name = f"{self._name} {device_name} {self.profile_id_str}"
        self._unique_id = f"{super().unique_id}_{self.key}_{self.profile_id_str}"

    async def async_set_native_value(self, value: int) -> None:
        """Set a new value."""
        await self.coordinator.controller.updateChargingProfile(
            self.vin, None, self.profile_id, minimumChargeLevel=value
        )
        await self.coordinator.async_request_refresh()

    @property
    def native_min_value(self):
        return 25

    @property
    def native_max_value(self):
        return 100

    @property
    def native_step(self):
        return 1

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the number."""
        attrdict = {}
        attrdict["profile_id"] = self.profile_id
        attrdict["profile_name"] = self.profile_name
        return attrdict

    @property
    def native_value(self):
        """Return the current value."""
        data = self.coordinator.getDataByVIN(self.vin, self.key)
        return data[self.profile_id]["chargingOptions"]["minimumChargeLevel"]
