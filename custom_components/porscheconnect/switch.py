"""Support for the Porsche Connect switch entities."""

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    RestoreSwitch,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyporscheconnectapi.exceptions import PorscheExceptionError
from pyporscheconnectapi.vehicle import PorscheVehicle

from . import (
    PorscheBaseEntity,
    PorscheConnectDataUpdateCoordinator,
)
from .const import DOMAIN
from .number import DEFAULT_CLIMATE_TARGET_TEMPERATURE


@dataclass(frozen=True, kw_only=True)
class PorscheSwitchEntityDescription(SwitchEntityDescription):
    """Class describing Porsche Connect switch entities."""

    value_fn: Callable[[PorscheVehicle], bool]
    remote_service_on: Callable[[PorscheVehicle], Coroutine[Any, Any, Any]]
    remote_service_off: Callable[[PorscheVehicle], Coroutine[Any, Any, Any]]
    is_available: Callable[[PorscheVehicle], bool] = lambda _: False


SWITCH_TYPES: list[PorscheSwitchEntityDescription] = [
    PorscheSwitchEntityDescription(
        key="climatise",
        translation_key="climatise",
        is_available=lambda v: v.has_remote_climatisation and v.has_remote_services,
        value_fn=lambda v: v.remote_climatise_on,
        remote_service_on=lambda v: v.remote_services.climatise_on(),
        remote_service_off=lambda v: v.remote_services.climatise_off(),
    ),
    PorscheSwitchEntityDescription(
        key="direct_charging",
        translation_key="direct_charging",
        is_available=lambda v: v.has_direct_charge and v.has_remote_services,
        value_fn=lambda v: v.direct_charge_on,
        remote_service_on=lambda v: v.remote_services.direct_charge_on(),
        remote_service_off=lambda v: v.remote_services.direct_charge_off(),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Porsche switches from config entry."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities: list[SwitchEntity] = []

    for vehicle in coordinator.vehicles:
        entities.extend(
            PorscheSwitch(coordinator, vehicle, description)
            for description in SWITCH_TYPES
            if description.is_available(vehicle)
        )
        if vehicle.has_remote_climatisation and vehicle.has_remote_services:
            entities.extend(
                [
                    PorscheSeatHeatingSwitch(coordinator, vehicle, "front_left"),
                    PorscheSeatHeatingSwitch(coordinator, vehicle, "front_right"),
                ],
            )

    async_add_entities(entities)


class PorscheSwitch(PorscheBaseEntity, SwitchEntity):
    """Representation of a Porsche switch."""

    entity_description: PorscheSwitchEntityDescription

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
        description: PorscheSwitchEntityDescription,
    ) -> None:
        """Initialize a Porsche switch."""
        super().__init__(coordinator, vehicle)
        self.entity_description = description
        self._attr_unique_id = f"{vehicle.vin}-{description.key}"

    @property
    def is_on(self) -> bool:
        """Return the entity value to represent the entity state."""
        return self.entity_description.value_fn(self.vehicle)

    async def async_turn_on(self) -> None:
        """Turn the switch on."""
        try:
            if self.entity_description.key == "climatise":
                temperature = self.coordinator.climate_target_temperatures.get(
                    self.vehicle.vin,
                    DEFAULT_CLIMATE_TARGET_TEMPERATURE,
                )
                seats = self.coordinator.seat_heating_selections.get(
                    self.vehicle.vin, {}
                )
                await self.vehicle.remote_services.climatise_on(
                    target_temperature=temperature + 273.15,
                    front_left=seats.get("front_left", False),
                    front_right=seats.get("front_right", False),
                )
            else:
                await self.entity_description.remote_service_on(self.vehicle)
        except PorscheExceptionError as ex:
            raise HomeAssistantError(ex) from ex

        self.coordinator.async_update_listeners()

    async def async_turn_off(self) -> None:
        """Turn the switch off."""
        try:
            await self.entity_description.remote_service_off(self.vehicle)
        except PorscheExceptionError as ex:
            raise HomeAssistantError(ex) from ex

        self.coordinator.async_update_listeners()


class PorscheSeatHeatingSwitch(PorscheBaseEntity, RestoreSwitch):
    """Locally remembered front seat-heating selection for remote climate."""

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
        seat: str,
    ) -> None:
        """Initialize a front seat-heating switch."""
        super().__init__(coordinator, vehicle)
        self.seat = seat
        self._attr_translation_key = seat
        self._attr_unique_id = f"{vehicle.vin}-{seat}-seat-heating"

    @property
    def is_on(self) -> bool:
        """Return the remembered seat-heating selection."""
        return self.coordinator.seat_heating_selections.get(
            self.vehicle.vin, {}
        ).get(self.seat, False)

    async def async_added_to_hass(self) -> None:
        """Restore the selected state after Home Assistant restarts."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            selected = last_state.state == STATE_ON
        else:
            reported = self.vehicle.seat_heating or {}
            api_key = "frontLeft" if self.seat == "front_left" else "frontRight"
            selected = bool(reported.get(api_key, False))

        selections = self.coordinator.seat_heating_selections.setdefault(
            self.vehicle.vin,
            {"front_left": False, "front_right": False},
        )
        selections[self.seat] = selected
        self.async_write_ha_state()

    async def _async_set_selection(self, selected: bool) -> None:
        """Remember the selection and send it with the remote climate command."""
        selections = self.coordinator.seat_heating_selections.setdefault(
            self.vehicle.vin,
            {"front_left": False, "front_right": False},
        )
        selections[self.seat] = selected
        temperature = self.coordinator.climate_target_temperatures.get(
            self.vehicle.vin,
            DEFAULT_CLIMATE_TARGET_TEMPERATURE,
        )

        try:
            await self.vehicle.remote_services.climatise_on(
                target_temperature=temperature + 273.15,
                front_left=selections.get("front_left", False),
                front_right=selections.get("front_right", False),
            )
        except PorscheExceptionError as ex:
            selections[self.seat] = not selected
            raise HomeAssistantError(ex) from ex

        self.coordinator.async_update_listeners()
        self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        """Enable this front seat heater with remote climatisation."""
        await self._async_set_selection(True)

    async def async_turn_off(self) -> None:
        """Disable this front seat heater in the remote climate request."""
        await self._async_set_selection(False)
