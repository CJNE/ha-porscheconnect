"""The Porsche Connect integration."""

import operator
import logging

from datetime import timedelta

from functools import reduce

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.typing import ConfigType
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.device_registry import DeviceInfo

from pyporscheconnectapi.exceptions import PorscheException
from pyporscheconnectapi.vehicle import PorscheVehicle
from pyporscheconnectapi.account import PorscheConnectAccount
from pyporscheconnectapi.connection import Connection


from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, PLATFORMS

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)


def getFromDict(dataDict, keyString):
    mapList = keyString.split(".")

    def safe_getitem(latest_value, key):
        if latest_value is None or key not in latest_value:
            return None
        return operator.getitem(latest_value, key)

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


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    async_client = get_async_client(hass)
    connection = Connection(
        entry.data.get("email"),
        entry.data.get("password"),
        asyncClient=async_client,
        token=entry.data.get(CONF_ACCESS_TOKEN, None),
    )

    controller = PorscheConnectAccount(
        connection=connection,
    )

    coordinator = PorscheConnectDataUpdateCoordinator(
        hass, config_entry=entry, controller=controller
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry, [platform for platform in PLATFORMS]
    )

    _async_save_token(hass, entry, controller.token)

    return True


class PorscheConnectDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Porsche data."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, controller):
        self.controller = controller
        self.vehicles = []
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

    def getVehicleDataLeaf(self, vehicle, node, leaf):
        return getFromDict(getFromDict(vehicle.data, node), leaf)

    async def _async_update_data(self):
        """Fetch data from API endpoint."""

        try:
            if len(self.vehicles) == 0:
                self.vehicles = await self.controller.get_vehicles()

                for vehicle in self.vehicles:
                    await vehicle.get_stored_overview()
                    await vehicle.get_picture_locations()

            else:
                async with async_timeout.timeout(30):
                    for vehicle in self.vehicles:
                        await vehicle.get_stored_overview()
            return {}

        except PorscheException as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


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
    _LOGGER.info(f"Reloading config entry: {entry}")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class PorscheBaseEntity(CoordinatorEntity):
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
            identifiers={(DOMAIN, self.vehicle.vin)},
            name=vehicle.data["name"],
            model=vehicle.data["modelName"],
            manufacturer="Porsche",
            serial_number=vehicle.vin,
        )

    @property
    def vin(self) -> str:
        """Get the VIN (vehicle identification number) of the vehicle."""
        return self.vehicle.vin

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
