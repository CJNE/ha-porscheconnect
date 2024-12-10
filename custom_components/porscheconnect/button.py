"""Support for Porsche Connect button entities."""

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyporscheconnectapi.exceptions import PorscheException
from pyporscheconnectapi.vehicle import PorscheVehicle

from . import (
    PorscheBaseEntity,
    PorscheConnectDataUpdateCoordinator,
)
from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class PorscheButtonEntityDescription(ButtonEntityDescription):
    """Class describing Porsche Connect button entities."""

    remote_function: Callable[[PorscheVehicle], Coroutine[Any, Any, Any]]
    is_available: Callable[[PorscheVehicle], bool] = lambda v: v.has_remote_services


BUTTON_TYPES: tuple[PorscheButtonEntityDescription, ...] = (
    PorscheButtonEntityDescription(
        key="get_current_overview",
        translation_key="get_current_overview",
        remote_function=lambda v: v.get_current_overview(),
    ),
    PorscheButtonEntityDescription(
        key="flash_indicators",
        translation_key="flash_indicators",
        remote_function=lambda v: v.remote_services.flash_indicators(),
    ),
    PorscheButtonEntityDescription(
        key="honk_and_flash_indicators",
        translation_key="honk_and_flash_indicators",
        remote_function=lambda v: v.remote_services.honk_and_flash_indicators(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Porsche buttons from config entry."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities: list[PorscheButton] = []

    for vehicle in coordinator.vehicles:
        entities.extend(
            [
                PorscheButton(coordinator, vehicle, description)
                for description in BUTTON_TYPES
                if description.is_available(vehicle)
            ],
        )

    async_add_entities(entities)


class PorscheButton(PorscheBaseEntity, ButtonEntity):
    """Representation of a Porsche Connect button."""

    entity_description: PorscheButtonEntityDescription

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
        description: PorscheButtonEntityDescription,
    ) -> None:
        """Initialize Porsche Connect button."""
        super().__init__(coordinator, vehicle)
        self.entity_description = description
        self._attr_unique_id = f"{vehicle.vin}-{description.key}"

    async def async_press(self) -> None:
        """Press the button."""
        try:
            await self.entity_description.remote_function(self.vehicle)
        except PorscheException as ex:
            raise HomeAssistantError(ex) from ex

        self.coordinator.async_update_listeners()
