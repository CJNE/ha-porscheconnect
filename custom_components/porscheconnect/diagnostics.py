"""Diagnostics support for Porsche Connect."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any

from homeassistant.components.diagnostics import REDACTED, async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from pyporscheconnectapi.vehicle import PorscheVehicle

from . import PorscheConnectDataUpdateCoordinator
from .const import DOMAIN, TRANSIENT_AUTH_FIELDS

TO_REDACT_ENTRY = {CONF_ACCESS_TOKEN, CONF_EMAIL, CONF_PASSWORD, *TRANSIENT_AUTH_FIELDS}

# Keys redacted wherever they appear in the vehicle payloads: identity and
# location details (charging profiles and alarms can carry positions too).
TO_REDACT_VEHICLE = {
    "vin",
    "customName",
    "name",
    "location",
    "latitude",
    "longitude",
    "address",
    "street",
    "city",
    "postalCode",
}

# Measurements whose whole value is personal or secret. Their status (enabled,
# cause) is kept, which is what matters when debugging a missing entity.
REDACTED_MEASUREMENTS = {
    "BLEID_DDADATA",
    "DESTINATIONS",
    "GPS_LOCATION",
    "LOCATION_ALARMS",
    "MDK_PAIRING_PASSWORD",
    "PAIRING_CODE",
    "VTS_CERTIFICATE_LIST",
}

CAPABILITIES = (
    "has_porsche_connect",
    "has_remote_services",
    "has_electric_drivetrain",
    "has_ice_drivetrain",
    "has_remote_climatisation",
    "has_direct_charge",
    "has_tire_pressure_monitoring",
)


def _library_version() -> str | None:
    try:
        return version("pyporscheconnectapi")
    except PackageNotFoundError:
        return None


def _exception_summary(exc: BaseException | None) -> dict[str, Any] | None:
    """Describe the last update error without its message.

    Library error messages can embed the OAuth state or raw API responses.
    """
    if exc is None:
        return None
    cause = exc.__cause__
    code = getattr(cause, "code", None)
    return {
        "type": type(exc).__name__,
        "cause": type(cause).__name__ if cause else None,
        "http_status": code if isinstance(code, int) else None,
    }


def _capability(vehicle: PorscheVehicle, flag: str) -> bool | None:
    """Evaluate a capability flag that decides which entities are created."""
    try:
        return getattr(vehicle, flag)
    except (AttributeError, KeyError, TypeError):
        # A partial payload must not break the whole report.
        return None


def _vehicle_diagnostics(vehicle: PorscheVehicle) -> dict[str, Any]:
    """Return the redacted raw and parsed data of a vehicle."""
    status = dict(vehicle.status or {})
    # Raw API answer, including disabled measurements and the reason why.
    status["measurements"] = [
        {**measurement, "value": REDACTED}
        if measurement.get("key") in REDACTED_MEASUREMENTS and "value" in measurement
        else measurement
        for measurement in status.get("measurements", [])
    ]
    # Data as parsed by the library, which is what the entities read.
    data = {
        key: REDACTED if key in REDACTED_MEASUREMENTS else value
        for key, value in (vehicle.data or {}).items()
    }
    return async_redact_data(
        {
            "model_name": vehicle.data.get("modelName"),
            "capabilities": {flag: _capability(vehicle, flag) for flag in CAPABILITIES},
            "status": status,
            "data": data,
            "remote_capabilities": vehicle.capabilities,
        },
        TO_REDACT_VEHICLE,
    )


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: PorscheConnectDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    update_interval = coordinator.update_interval

    return {
        "library_version": _library_version(),
        "entry": {
            "data": async_redact_data(dict(config_entry.data), TO_REDACT_ENTRY),
            "options": dict(config_entry.options),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_exception": _exception_summary(coordinator.last_exception),
            "update_interval_seconds": update_interval.total_seconds()
            if update_interval
            else None,
        },
        "vehicles": [
            _vehicle_diagnostics(vehicle) for vehicle in coordinator.vehicles
        ],
    }
