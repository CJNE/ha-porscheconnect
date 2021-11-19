import logging
from dataclasses import dataclass
from dataclasses import field

from homeassistant.const import DEVICE_CLASS_BATTERY

# from homeassistant.const import DEVICE_CLASS_CURRENT
# from homeassistant.const import DEVICE_CLASS_ENERGY
# from homeassistant.const import DEVICE_CLASS_HUMIDITY
# from homeassistant.const import DEVICE_CLASS_ILLUMINANCE
# from homeassistant.const import DEVICE_CLASS_POWER
# from homeassistant.const import DEVICE_CLASS_POWER_FACTOR
# from homeassistant.const import DEVICE_CLASS_PRESSURE
# from homeassistant.const import DEVICE_CLASS_SIGNAL_STRENGTH
# from homeassistant.const import DEVICE_CLASS_TEMPERATURE
# from homeassistant.const import DEVICE_CLASS_TIMESTAMP
# from homeassistant.const import DEVICE_CLASS_VOLTAGE

"""Constants for the Porsche Connect integration."""

DOMAIN = "porscheconnect"
LOGGER = logging.getLogger(__package__)
DEFAULT_SCAN_INTERVAL = 660
HA_SENSOR = "sensor"
HA_SWITCH = "switch"
HA_DEVICE_TRACKER = "device_tracker"
HA_BINARY_SENSOR = "binary_sensor"
PORSCHE_COMPONENTS = [HA_SENSOR, HA_DEVICE_TRACKER, HA_BINARY_SENSOR, HA_SWITCH]

NAME = "porscheconnect"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.0"
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
class SensorAttr:
    name: str
    key: str


DATA_MAP = [
    SensorMeta(
        "mileage sensor",
        "mileage",
        "mdi:counter",
        attributes=[SensorAttr("oil level", "oilLevel")],
    ),
    SensorMeta("battery sensor", "batteryLevel", "mdi:battery", DEVICE_CLASS_BATTERY),
    SensorMeta("fuel sensor", "fuelLevel", "mdi:gauge"),
    SensorMeta(
        "range sensor",
        "remainingRanges.electricalRange.distance",
        "mdi:gauge",
    ),
    SensorMeta(
        "range sensor",
        "remainingRanges.conventionalRange.distance",
        "mdi:gauge",
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
    SensorMeta("doors", "doors.overallLockStatus", "mdi:lock"),
    SensorMeta("lock", "overallOpenStatus", "mdi:lock"),
    SensorMeta(
        "charger sensor",
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
]


DEVICE_CLASSES = {
    "batteryLevel": DEVICE_CLASS_BATTERY,
}

DEVICE_NAMES = {
    "mileage": "mileage sensor",
    "batteryLevel": "battery sensor",
    "fuelLevel": "fuel sensor",
    "oilLevel": "oil sensor",
    "remainingRanges.conventionalRange.distance": "range sensor",
    "remainingRanges.electricalRange.distance": "range sensor",
    "chargingStatus": "charger sensor",
    "directClimatisation.climatisationState": "climatisation",
    "directCharge.isActive": "direct charge"
}

ICONS = {
    "battery sensor": "mdi:battery",
    "range sensor": "mdi:gauge",
    "mileage sensor": "mdi:counter",
    "parking brake sensor": "mdi:car-brake-parking",
    "charger sensor": "mdi:ev-station",
    "charger switch": "mdi:battery-charging",
    "update switch": "mdi:update",
    "maxrange switch": "mdi:gauge-full",
    "temperature sensor": "mdi:thermometer",
    "location tracker": "mdi:crosshairs-gps",
    "charging rate sensor": "mdi:speedometer",
    "sentry mode switch": "mdi:shield-car",
}
