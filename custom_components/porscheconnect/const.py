import logging
from dataclasses import dataclass
from dataclasses import field

from homeassistant.components.sensor import (
    SensorDeviceClass,
)

"""Constants for the Porsche Connect integration."""

DOMAIN = "porscheconnect"
LOGGER = logging.getLogger(__package__)
DEFAULT_SCAN_INTERVAL = 660
HA_SENSOR = "sensor"
HA_SWITCH = "switch"
HA_LOCK = "lock"
HA_NUMBER = "number"
HA_DEVICE_TRACKER = "device_tracker"
HA_BINARY_SENSOR = "binary_sensor"
PORSCHE_COMPONENTS = [
    HA_SENSOR,
    HA_DEVICE_TRACKER,
    HA_BINARY_SENSOR,
    HA_SWITCH,
    HA_LOCK,
]

NAME = "porscheconnect"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.13"
ISSUE_URL = "https://github.com/cjne/ha-porscheconnect/issues"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""


@dataclass
class SensorMeta:
    name: str
    key: str
    icon: str = None
    device_class: str = None
    default_enabled: bool = True
    attributes: list = field(default_factory=list)


@dataclass
class BinarySensorMeta:
    name: str
    key: str
    icon: str = None
    isOnState: any = "ACTIVE"
    device_class: str = None
    default_enabled: bool = True
    attributes: list = field(default_factory=list)


@dataclass
class SwitchMeta:
    name: str
    key: str
    on_action: str
    off_action: str
    icon: str = None
    device_class: str = None
    default_enabled: bool = True
    attributes: list = field(default_factory=list)


@dataclass
class LockMeta:
    name: str
    key: str
    icon: str = None
    device_class: str = None
    default_enabled: bool = True
    attributes: list = field(default_factory=list)


@dataclass
class NumberMeta:
    name: str
    key: str
    icon: str = None
    device_class: str = None
    default_enabled: bool = True
    attributes: list = field(default_factory=list)


@dataclass
class SensorAttr:
    name: str
    key: str


DATA_MAP = [
    SensorMeta(
        "mileage",
        "mileage",
        "mdi:counter",
        attributes=[SensorAttr("oil level", "oilLevel")],
    ),
    SensorMeta("battery", "batteryLevel", "mdi:battery", SensorDeviceClass.BATTERY),
    SensorMeta("fuel", "fuelLevel", "mdi:gauge"),
    SensorMeta(
        "range",
        "remainingRanges.electricalRange.distance",
        "mdi:gauge",
    ),
    SensorMeta(
        "range",
        "remainingRanges.conventionalRange.distance",
        "mdi:gauge",
    ),
    SensorMeta(
        "charging profile",
        "chargingProfiles.currentProfileId",
        "mdi:battery-charging",
        attributes=[SensorAttr("profiles", "chargingProfilesDict")],
    ),
    SwitchMeta(
        "climate",
        "directClimatisation.climatisationState",
        "climate-on",
        "climate-off",
        "mdi:thermometer",
    ),
    SwitchMeta(
        "direct charge",
        "directCharge.isActive",
        "directcharge-on",
        "directcharge-off",
        "mdi:ev-station",
    ),
    BinarySensorMeta("parking brake", "parkingBreak", "mdi:lock"),
    BinarySensorMeta("privacy mode", "services.privacyMode", "mdi:security", True),
    SensorMeta("doors", "overallOpenStatus", "mdi:lock"),
    SensorMeta(
        "charger",
        "chargingStatus",
        "mdi:ev-station",
        attributes=[
            SensorAttr("plug state", "batteryChargeStatus.plugState"),
            SensorAttr("charging state", "batteryChargeStatus.chargingState"),
            SensorAttr("lock state", "batteryChargeStatus.lockState"),
            SensorAttr("charging mode", "batteryChargeStatus.chargingMode"),
            SensorAttr(
                "remaining charge time to 100%",
                "batteryChargeStatus.remainingChargeTimeUntil100PercentInMinutes",
            ),
            SensorAttr("charging power", "batteryChargeStatus.chargingPower"),
        ],
    ),
    LockMeta("doorlock", "doors.overallLockStatus", "mdi:lock"),
    NumberMeta("charging level", "chargingProfilesDict", "mdi:battery-charging"),
]


DEVICE_CLASSES = {
    "batteryLevel": SensorDeviceClass.BATTERY,
}

DEVICE_NAMES = {
    "mileage": "mileage",
    "batteryLevel": "battery",
    "fuelLevel": "fuel",
    "oilLevel": "oil",
    "remainingRanges.conventionalRange.distance": "range",
    "remainingRanges.electricalRange.distance": "range",
    "chargingStatus": "charger",
    "chargingProfiles.currentProfileId": "charging profile",
    "directClimatisation.climatisationState": "climatisation",
    "directCharge.isActive": "direct charge",
    "doors.overallLockStatus": "door lock",
    "overallOpenStatus": "doors",
    "chargingProfilesDict": "charging level",
    "services.privacyMode": "privacy mode",
    "parkingBreak": "parking break",
}

# ICONS = {
#     "battery": "mdi:battery",
#     "range": "mdi:gauge",
#     "mileage": "mdi:counter",
#     "parking brake": "mdi:car-brake-parking",
#     "privacy mode": "mdi:security",
#     "charger": "mdi:ev-station",
#     "charger switch": "mdi:battery-charging",
#     "update switch": "mdi:update",
#     "maxrange switch": "mdi:gauge-full",
#     "temperature": "mdi:thermometer",
#     "location tracker": "mdi:crosshairs-gps",
#     "charging rate": "mdi:speedometer",
#     "sentry mode switch": "mdi:shield-car",
# }
