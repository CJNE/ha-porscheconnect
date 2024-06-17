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
from homeassistant.helpers.device_registry import DeviceInfo

from homeassistant.util import slugify
from pyporscheconnectapi.client import Client
from pyporscheconnectapi.connection import Connection
from pyporscheconnectapi.exceptions import PorscheException

from .const import DOMAIN
from .const import STARTUP_MESSAGE
from .services import setup_services
from .services import unload_services


_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=300)

# PLATFORMS = ["device_tracker", "sensor", "binary_sensor", "switch", "lock", "number"]
PLATFORMS = ["sensor"]


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
def _async_save_token(hass, config_entry, access_token):
    hass.config_entries.async_update_entry(
        config_entry,
        data={
            **config_entry.data,
            CONF_ACCESS_TOKEN: access_token,
        },
    )


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    websession = aiohttp_client.async_get_clientsession(hass)

    connection = Connection(
        entry.data.get("email"),
        entry.data.get("password"),
        token=entry.data.get(CONF_ACCESS_TOKEN, None),
        websession=websession,
    )
    controller = Client(connection)

    access_token = await controller.getToken()
    _async_save_token(hass, entry, access_token)

    coordinator = PorscheConnectDataUpdateCoordinator(
        hass, config_entry=entry, controller=controller
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry, [platform for platform in PLATFORMS]
    )

    # for platform in PLATFORMS:
    #    hass.async_add_job(
    #        hass.config_entries.async_forward_entry_setup(entry, platform)
    #    )

    setup_services(hass)

    return True


class PorscheConnectDataUpdateCoordinator(DataUpdateCoordinator[None]):
    """Class to manage fetching Porsche data."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, controller):
        self.controller = controller
        self.vehicles = None
        self.hass = hass
        self.config_entry = config_entry

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
        return getFromDict(self.data.get(vin, {}), key)

    async def _update_data_for_vehicle(self, vehicle):
        vin = vehicle["vin"]
        mdata = {}

        vdata = [
            m
            for m in (await self.controller.getStoredOverview(vin))["measurements"]
            if m["status"]["isEnabled"] == True
        ]

        for m in vdata:
            mdata[m["key"]] = m["value"]

        return mdata

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        if self.controller.isTokenRefreshed():
            access_token = await self.controller.getToken()
            _async_save_token(self.hass, self.config_entry, access_token)

        data = {}
        try:
            if self.vehicles is None:
                self.vehicles = []
                all_vehicles = await self.controller.getVehicles()

                for vehicle in all_vehicles:
                    vin = vehicle["vin"]
                    vehicle["name"] = vehicle["customName"] or vehicle["modelName"]
                    mdata = await self._update_data_for_vehicle(vehicle)

                    vehicle["components"] = {
                        "sensor": [],
                    }

                    self.vehicles.append(vehicle)
                    data[vin] = mdata
            else:
                async with async_timeout.timeout(30):
                    for vehicle in self.vehicles:
                        vin = vehicle["vin"]
                        mdata = await self._update_data_for_vehicle(vehicle)
                        data[vin] = mdata

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
    print("WILL RELOAD")
    print(entry)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class PorscheVehicle:
    """Representation of a Porsche vehicle"""

    def __init__(
        self,
        vehicle_base: dict,
    ) -> None:
        self.data = vehicle_base

    @property
    def vin(self) -> str:
        """Get the VIN (vehicle identification number) of the vehicle."""
        return self.data["vin"]


class PorscheBaseEntity(CoordinatorEntity[PorscheConnectDataUpdateCoordinator]):
    """Common base for entities"""

    coordinator: PorscheConnectDataUpdateCoordinator

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
    ) -> None:
        """Initialise the entity"""
        super().__init__(coordinator)

        self.vehicle = vehicle

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.vehicle["vin"])},
            name=vehicle["name"],
            model=vehicle["modelName"],
            manufacturer="Porsche",
        )

        # self._unique_id = slugify(vehicle["vin"])
        # self._attributes = {}

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
