"""Support for the Porsche Connect remote climatisation as a climate entity."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyporscheconnectapi.exceptions import PorscheExceptionError
from pyporscheconnectapi.vehicle import PorscheVehicle

from . import (
    PorscheBaseEntity,
    PorscheConnectDataUpdateCoordinator,
)
from .const import DOMAIN

# The Porsche API takes the target temperature in Kelvin.
KELVIN_OFFSET = 273.15
DEFAULT_TEMPERATURE = 20.0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Porsche climate entities from config entry."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    async_add_entities(
        PorscheClimate(coordinator, vehicle)
        for vehicle in coordinator.vehicles
        if vehicle.has_remote_climatisation and vehicle.has_remote_services
    )


class PorscheClimate(PorscheBaseEntity, ClimateEntity):
    """Remote climatisation of a vehicle, as a thermostat."""

    _attr_translation_key = "climatisation"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    # The library checks the requested value against the range reported by the
    # vehicle and rejects anything outside of it.
    _attr_min_temp = 15.0
    _attr_max_temp = 30.0
    _attr_target_temperature_step = 0.5

    def __init__(
        self,
        coordinator: PorscheConnectDataUpdateCoordinator,
        vehicle: PorscheVehicle,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator, vehicle)
        self._attr_unique_id = f"{vehicle.vin}-climatisation"
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT_COOL]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        running = self.vehicle.remote_climatise_on
        self._attr_hvac_mode = HVACMode.HEAT_COOL if running else HVACMode.OFF
        # While running, the vehicle reports the temperature in use. While off,
        # keep the value chosen in Home Assistant for the next start.
        reported = self.vehicle.climatisation_target_temperature
        if reported is not None and (running or self._attr_target_temperature is None):
            self._attr_target_temperature = reported
        elif self._attr_target_temperature is None:
            self._attr_target_temperature = DEFAULT_TEMPERATURE
        super()._handle_coordinator_update()

    async def async_turn_on(self) -> None:
        """Start remote climatisation."""
        await self._async_climatise(turn_on=True)

    async def async_turn_off(self) -> None:
        """Stop remote climatisation."""
        await self._async_climatise(turn_on=False)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Start or stop remote climatisation."""
        await self._async_climatise(turn_on=hvac_mode != HVACMode.OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:  # noqa: ANN401 (Home Assistant signature)
        """Set the target temperature, and apply it if climatisation is running."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        self._attr_target_temperature = temperature
        if self.vehicle.remote_climatise_on:
            await self._async_climatise(turn_on=True)
        else:
            self.async_write_ha_state()

    async def _async_climatise(self, *, turn_on: bool) -> None:
        """Send the start or stop command."""
        try:
            if turn_on:
                # Restarting with a new temperature must not switch off the seat
                # heating that is currently running.
                running = self.vehicle.remote_climatise_on
                seats = (self.vehicle.seat_heating or {}) if running else {}
                await self.vehicle.remote_services.climatise_on(
                    target_temperature=self._attr_target_temperature + KELVIN_OFFSET,
                    front_left=seats.get("frontLeft", False),
                    front_right=seats.get("frontRight", False),
                    rear_left=seats.get("rearLeft", False),
                    rear_right=seats.get("rearRight", False),
                )
            else:
                await self.vehicle.remote_services.climatise_off()
        except (PorscheExceptionError, ValueError) as ex:
            raise HomeAssistantError(ex) from ex

        self.coordinator.async_update_listeners()
