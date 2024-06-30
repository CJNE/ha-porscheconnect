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

# from .services import setup_services
# from .services import unload_services

import json  # only for formatting debug outpu

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=900)

# PLATFORMS = [ "switch", "lock", "number"]
PLATFORMS = ["sensor", "binary_sensor", "device_tracker"]

BASE_DATA = ["vin", "modelName", "customName", "modelType", "systemInfo"]


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

    # setup_services(hass)

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
        bdata = {}
        mdata = {}
        try:
            vdata = await self.controller.getStoredOverview(vin)
        except PorscheException as err:
            _LOGGER.error("Could not get stored overview, error communicating with API: '%s", err)
            _LOGGER.debug(
                "Payload for stored overview query was: %s",
                json.dumps(vdata, indent=2),
            )


        if "vin" not in vdata:
            try:
                vdata = await self.controller.getCurrentOverview(vin)
            except PorscheException as err:
                _LOGGER.error("Could not get current overview, error communicating with API: '%s", err)
                _LOGGER.debug(
                    "Payload for current overview query was: %s",
                    json.dumps(vdata, indent=2),
                )


        if "vin" in vdata:
            bdata = dict((k, vdata[k]) for k in BASE_DATA)

            _LOGGER.debug(
                "Got base data for vehicle '%s': %s",
                vin,
                json.dumps(bdata, indent=2),
            )

            if "measurements" in vdata:
                tdata = [
                    m for m in vdata["measurements"] if m["status"]["isEnabled"] == True
                ]

                for m in tdata:
                    mdata[m["key"]] = m["value"]
                _LOGGER.debug(
                    "Got measurement data for vehicle '%s': %s",
                    vin,
                    json.dumps(mdata, indent=2),
                )

                # Here we do some measurements translations to make them accessible

                if "BATTERY_CHARGING_STATE" in mdata:
                    if "chargingRate" in mdata["BATTERY_CHARGING_STATE"]:
                        # Convert charging rate from km/min to km/h
                        mdata["BATTERY_CHARGING_STATE"]["chargingRate"] = mdata["BATTERY_CHARGING_STATE"]["chargingRate"] * 60 
                    else:
                        # Charging is currently not ongoing, but we should still feed som data to the sensor
                        mdata["BATTERY_CHARGING_STATE"]["chargingRate"] = 0

                    if "chargingPower" not in mdata["BATTERY_CHARGING_STATE"]:
                        # Charging is currently not ongoing, but we should still feed som data to the sensor
                        mdata["BATTERY_CHARGING_STATE"]["chargingPower"] = 0


            else:
                _LOGGER.debug("Measurement data missing for vehicle '%s", vin)
                _LOGGER.debug(
                    "Payload for current overview query was: %s",
                    json.dumps(vdata, indent=2),
                )

        else:
            _LOGGER.debug("Base data missing for vehicle '%s", vin)
            _LOGGER.debug(
                "Payload for current overview query was: %s",
                json.dumps(vdata, indent=2),
            )

        return bdata | mdata

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
                    vdata = await self._update_data_for_vehicle(vehicle)

                    self.vehicles.append(vehicle)
                    data[vin] = vdata
            else:
                async with async_timeout.timeout(30):
                    for vehicle in self.vehicles:
                        vin = vehicle["vin"]
                        vdata = await self._update_data_for_vehicle(vehicle)
                        data[vin] = vdata

        except PorscheException as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        return data


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry"""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, [platform for platform in PLATFORMS]
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    print("WILL RELOAD")
    print(entry)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class PorscheVehicle:
    """Placeholder för representation of a Porsche vehicle"""

    def __init__(
        self,
        data: dict,
    ) -> None:
        self.data = data

    @property
    def vin(self) -> str:
        """Get the VIN (vehicle identification number) of the vehicle."""
        return self.data["vin"]


class PorscheBaseEntity(CoordinatorEntity[PorscheConnectDataUpdateCoordinator]):
    """Common base for entities"""

    coordinator: PorscheConnectDataUpdateCoordinator
    _attr_has_entity_name = True

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

    @property
    def vin(self) -> str:
        """Get the VIN (vehicle identification number) of the vehicle."""
        return self.vehicle["vin"]

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
