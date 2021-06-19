"""The Porsche Connect integration."""
import asyncio
from datetime import timedelta
from functools import reduce
import logging
import operator

import async_timeout
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    ATTR_BATTERY_CHARGING,
    ATTR_BATTERY_LEVEL,
    CONF_ACCESS_TOKEN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import slugify
from pyporscheconnectapi.client import Client
from pyporscheconnectapi.connection import Connection
from pyporscheconnectapi.exceptions import PorscheException

from .config_flow import (
    CannotConnect,
    InvalidAuth,
    configured_instances,
    validate_input,
)
from .const import (
    DATA_MAP,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
    PORSCHE_COMPONENTS,
    SENSOR_KEYS,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["device_tracker", "sensor"]

def getFromDict(dataDict, keyString):
    mapList = keyString.split('.')
    return reduce(operator.getitem, mapList, dataDict)

@callback
def _async_save_tokens(hass, config_entry, access_tokens):
    hass.config_entries.async_update_entry(
        config_entry,
        data={
            **config_entry.data,
            CONF_ACCESS_TOKEN: access_tokens,
        },
    )


async def async_setup(hass: HomeAssistant, base_config: dict):
    _LOGGER.debug("Porsche async setup")
    """Set up the Porsche Connect component."""

    def _update_entry(email, data=None, options=None):
        _LOGGER.debug("Porsche async setup update entry")
        data = data or {}
        options = options or {CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL}
        for entry in hass.config_entries.async_entries(DOMAIN):
            if email != entry.title:
                continue
            hass.config_entries.async_update_entry(entry, data=data, options=options)

    config = base_config.get(DOMAIN)
    if not config:
        return True
    email = config[CONF_EMAIL]
    password = config[CONF_PASSWORD]
    scan_interval = config[CONF_SCAN_INTERVAL]

    if email in configured_instances(hass):
        try:
            info = await validate_input(hass, config)
        except (CannotConnect, InvalidAuth):
            return False
        _update_entry(
            email,
            data={
                CONF_EMAIL: email,
                CONF_PASSWORD: password,
                CONF_ACCESS_TOKEN: info[CONF_ACCESS_TOKEN],
            },
            options={CONF_SCAN_INTERVAL: scan_interval},
        )
    else:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data={CONF_EMAIL: email, CONF_PASSWORD: password},
            )
        )
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][email] = {CONF_SCAN_INTERVAL: scan_interval}
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up Porsche Connect from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    config = config_entry.data
    websession = aiohttp_client.async_get_clientsession(hass)
    email = config_entry.title
    if email in hass.data[DOMAIN] and CONF_SCAN_INTERVAL in hass.data[DOMAIN][email]:
        _LOGGER.debug("Porsche async setup entry update scan interval")
        scan_interval = hass.data[DOMAIN][email][CONF_SCAN_INTERVAL]
        hass.config_entries.async_update_entry(
            config_entry, options={CONF_SCAN_INTERVAL: scan_interval}
        )
        hass.data[DOMAIN].pop(email)

    try:
        tokens = None
        if CONF_ACCESS_TOKEN in config:
            tokens = config[CONF_ACCESS_TOKEN]
        connection = Connection(
            config["email"],
            config["password"],
            tokens=tokens,
            websession=websession,
        )
        controller = Client(connection)
        vehicles = await controller.getVehicles()


        for vehicle in vehicles:
            summary = await controller.getSummary(vehicle["vin"])
            vehicle["name"] = summary["nickName"] or summary["modelDescription"]
            # Find out what sensors are supported and store in vehicle
            overview = await controller.getStoredOverview(vehicle["vin"])

            vehicle['components'] = {} 
            for sensorMeta in DATA_MAP:
                data = getFromDict(overview, sensorMeta.key)
                if data is not None: 
                    if vehicle['components'].get(sensorMeta.ha_type, None) is None:
                        vehicle['components'][sensorMeta.ha_type] = []
                    vehicle['components'][sensorMeta.ha_type].append(sensorMeta)

            _LOGGER.debug(f"Found vehicle {vehicle['name']}")
            _LOGGER.debug(f"Supported components {vehicle['components']}")

        access_tokens = await controller.getAllTokens()

    except PorscheException as ex:
        _LOGGER.error("Unable to communicate with Porsche Conmnect API: %s", ex.message)
        return False

    _async_save_tokens(hass, config_entry, access_tokens)
    coordinator = PorscheDataUpdateCoordinator(
        hass, config_entry=config_entry, controller=controller, vehicles=vehicles
    )

    entry_data = hass.data[DOMAIN][config_entry.entry_id] = {
        "coordinator": coordinator,
        "vehicles": vehicles,
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


@callback
def _async_save_tokens(hass, config_entry, access_tokens):
    hass.config_entries.async_update_entry(
        config_entry,
        data={**config_entry.data, CONF_ACCESS_TOKEN: access_tokens},
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class PorscheDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Porsche data."""

    def __init__(self, hass, *, config_entry, controller, vehicles):
        """Initialize global Porsche data updater."""
        self.controller = controller
        self.vehicles = vehicles
        self.config_entry = config_entry

        self.data = {}
        update_interval = timedelta(seconds=MIN_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    def getDataByVIN(self, vin, key):
        if(self.data is None): return None
        return getFromDict(self.data.get(vin, {}), key)

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        if self.controller.isTokenRefreshed():
            access_tokens = await self.controller.getAllTokens()
            _async_save_tokens(self.hass, self.config_entry, access_tokens)
            _LOGGER.debug("Saving new tokens in config_entry")

        data = {}
        try:
            async with async_timeout.timeout(30):
                for vehicle in self.vehicles:
                    vin = vehicle["vin"]
                    vdata = {}
                    vdata = {**vdata, **await self.controller.getPosition(vin)}
                    vdata = {**vdata, **await self.controller.getStoredOverview(vin)}
                    data[vin] = vdata
                _LOGGER.debug(data)
        except PorscheException as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        return data


class PorscheDevice(CoordinatorEntity):
    """Representation of a Porsche device."""

    def __init__(self, vehicle, coordinator):
        """Initialise the Porsche device."""
        super().__init__(coordinator)
        self.vehicle = vehicle
        self.vin = vehicle["vin"]
        self._name = vehicle["name"]
        self._unique_id = slugify(vehicle["vin"])
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attr = self._attributes
        return attr

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self.vehicle["vin"])},
            "name": self.vehicle["name"],
            "manufacturer": "Porsche",
            "model": self.vehicle["modelDescription"],
        }

    async def async_added_to_hass(self):
        """Register state update callback."""
        self.async_on_remove(self.coordinator.async_add_listener(self.refresh))

    @callback
    def refresh(self) -> None:
        """Refresh the state of the device.
        This assumes the coordinator has updated the controller.
        """
        self.async_write_ha_state()
