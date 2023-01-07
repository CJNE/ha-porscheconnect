"""The Porsche Connect integration."""
import asyncio
import logging
import operator
from datetime import timedelta
from functools import reduce

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import slugify
from pyporscheconnectapi.client import Client
from pyporscheconnectapi.connection import Connection
from pyporscheconnectapi.exceptions import PorscheException

from .const import BinarySensorMeta
from .const import DATA_MAP
from .const import DOMAIN
from .const import LockMeta
from .const import NumberMeta
from .const import STARTUP_MESSAGE
from .const import SwitchMeta
from .services import setup_services
from .services import unload_services


# from homeassistant.const import ATTR_BATTERY_CHARGING
# from homeassistant.const import ATTR_BATTERY_LEVEL
# from .const import PORSCHE_COMPONENTS

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=300)

PLATFORMS = ["device_tracker", "sensor", "binary_sensor", "switch", "lock", "number"]


class PinError(PorscheException):
    pass


def getFromDict(dataDict, keyString):
    mapList = keyString.split(".")
    safe_getitem = (
        lambda latest_value, key: None
        if latest_value is None or key not in latest_value
        else operator.getitem(latest_value, key)
    )
    return reduce(safe_getitem, mapList, dataDict)


@callback
def _async_save_tokens(hass, config_entry, access_tokens):
    _LOGGER.debug("Saving tokens")
    hass.config_entries.async_update_entry(
        config_entry,
        data={
            **config_entry.data,
            CONF_ACCESS_TOKEN: access_tokens,
        },
    )


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    websession = aiohttp_client.async_get_clientsession(hass)

    connection = Connection(
        entry.data.get("email"),
        entry.data.get("password"),
        tokens=entry.data.get(CONF_ACCESS_TOKEN, None),
        websession=websession,
    )
    lang = "de"
    country = "de"
    controller = Client(connection, country, lang)

    access_tokens = await controller.getAllTokens()
    _async_save_tokens(hass, entry, access_tokens)

    coordinator = PorscheConnectDataUpdateCoordinator(
        hass, config_entry=entry, controller=controller
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    setup_services(hass)

    return True


class PorscheConnectDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Porsche data."""

    def __init__(self, hass, config_entry, controller):
        """Initialize global Porsche data updater."""
        _LOGGER.debug("Init new data update coordinator")
        self.controller = controller
        self.vehicles = None
        self.config_entry = config_entry

        self.data = {}

        scan_interval = timedelta(
            seconds=config_entry.options.get(
                CONF_SCAN_INTERVAL,
                config_entry.data.get(
                    CONF_SCAN_INTERVAL, SCAN_INTERVAL.total_seconds()
                ),
            )
        )

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=scan_interval)

    def getDataByVIN(self, vin, key):
        # if self.data is None:
        #     return None
        return getFromDict(self.data.get(vin, {}), key)

    async def _update_data_for_vehicle(self, vehicle):
        vin = vehicle["vin"]
        model = vehicle["capabilities"]["carModel"]
        vdata = {
            **await self.controller.getStoredOverview(vin),
            **await self.controller.getEmobility(vin, model),
        }

        vdata["services"] = await self.controller.getServices(vin)
        if vdata.get("chargingProfiles", None) is not None:
            vdata["chargingProfilesDict"] = {}
            vdata["chargingProfilesDict"].update(
                {
                    item["profileId"]: item
                    for item in vdata["chargingProfiles"]["profiles"]
                }
            )
        if vehicle["services"]["vehicleServiceEnabledMap"]["CF"] == "ENABLED":
            vdata.update(await self.controller.getPosition(vin))
        return vdata

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        if self.controller.isTokenRefreshed():
            _LOGGER.debug("Saving new tokens in config_entry")
            access_tokens = await self.controller.getAllTokens()
            _async_save_tokens(self.hass, self.config_entry, access_tokens)

        data = {}
        try:
            if self.vehicles is None:
                self.vehicles = []
                all_vehicles = await self.controller.getVehicles()

                for vehicle in all_vehicles:
                    vin = vehicle["vin"]
                    permission_for_vin = await self.controller.isAllowed(vin)
                    if not permission_for_vin["allowed"]:
                        _LOGGER.warning(
                            "User is not granted access to vehicle VIN %s, reason %s",
                            vin,
                            permission_for_vin["reason"],
                        )
                        continue
                    _LOGGER.info(f"User is authorized for vehicle vin {vin}")
                    summary = await self.controller.getSummary(vin)
                    _LOGGER.debug("Fetching initial data for vehicle %s", vin)
                    vehicle["name"] = summary["nickName"] or summary["modelDescription"]
                    vehicle["capabilities"] = await self.controller.getCapabilities(vin)
                    vehicle["services"] = await self.controller.getServices(vin)
                    # Find out what sensors are supported and store in vehicle
                    vdata = {}
                    vdata = await self._update_data_for_vehicle(vehicle)
                    vehicle["components"] = {
                        "sensor": [],
                        "switch": [],
                        "lock": [],
                        "binary_sensor": [],
                        "number": [],
                    }
                    _LOGGER.debug(vdata)
                    for sensor_meta in DATA_MAP:
                        sensor_data = getFromDict(vdata, sensor_meta.key)
                        _LOGGER.debug(
                            "Appending entity for sensor if data is not none: %s %s %s",
                            sensor_meta.key,
                            sensor_meta,
                            sensor_data,
                        )
                        if sensor_data is not None:
                            ha_type = "sensor"
                            if isinstance(sensor_meta, SwitchMeta):
                                ha_type = "switch"
                            if isinstance(sensor_meta, LockMeta):
                                ha_type = "lock"
                            if isinstance(sensor_meta, NumberMeta):
                                ha_type = "number"
                            elif isinstance(sensor_meta, BinarySensorMeta):
                                ha_type = "binary_sensor"
                            vehicle["components"][ha_type].append(sensor_meta)

                    _LOGGER.debug(f"Found vehicle {vehicle['name']}")
                    _LOGGER.debug(vehicle)
                    self.vehicles.append(vehicle)
                    data[vin] = vdata
            else:
                async with async_timeout.timeout(30):
                    for vehicle in self.vehicles:
                        vin = vehicle["vin"]
                        vdata = await self._update_data_for_vehicle(vehicle)
                        data[vin] = vdata
                    # _LOGGER.debug(data)
        except PorscheException as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        return data


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            unload_services(hass)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


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
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self.vehicle["vin"])},
            "name": self.vehicle["name"],
            "manufacturer": "Porsche",
            "model": self.vehicle["modelDescription"],
        }
