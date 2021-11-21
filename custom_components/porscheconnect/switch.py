"""Switch platform for Porsche Connect."""
from homeassistant.components.switch import SwitchEntity

from . import DOMAIN as PORSCHE_DOMAIN
from . import PorscheDevice
from .const import DEVICE_NAMES
from .const import HA_SWITCH
from .const import SwitchMeta


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup switch platform."""
    coordinator = hass.data[PORSCHE_DOMAIN][entry.entry_id]
    entities = []
    for vehicle in coordinator.vehicles:
        for switch in vehicle["components"][HA_SWITCH]:
            entities.append(PorscheConnectSwitch(vehicle, coordinator, switch))
    async_add_devices(entities)


class PorscheConnectSwitch(PorscheDevice, SwitchEntity):
    """porscheconnect switch class."""

    def __init__(self, vehicle, coordinator, switch_meta: SwitchMeta):
        """Initialize of the sensor."""
        super().__init__(vehicle, coordinator)
        self.key = switch_meta.key
        self.meta = switch_meta
        device_name = DEVICE_NAMES.get(self.key, self.key)
        self._name = f"{self._name} {device_name}"
        self._unique_id = f"{super().unique_id}_{self.key}"

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        if self.meta.on_action == "climate-on":
            await self.coordinator.controller.climateOn(self.vin, True)
        elif self.meta.on_action == "directcharge-on":
            await self.coordinator.controller.directChargeOn(self.vin, None, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        if self.meta.off_action == "climate-off":
            await self.coordinator.controller.climateOff(self.vin, True)
        elif self.meta.off_action == "directcharge-off":
            await self.coordinator.controller.directChargeOff(self.vin, None, True)
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
    def is_on(self):
        """Return true if the switch is on."""
        data = self.coordinator.getDataByVIN(self.vin, self.key)
        if data == "ON" or data == True:
            return True
