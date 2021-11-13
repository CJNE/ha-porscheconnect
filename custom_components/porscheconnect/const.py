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
MIN_SCAN_INTERVAL = 60
HA_SENSOR = "sensor"
HA_DEVICE_TRACKER = "device_tracker"
HA_BINARY_SENSOR = "binary_sensor"
PORSCHE_COMPONENTS = [HA_SENSOR, HA_DEVICE_TRACKER, HA_BINARY_SENSOR]


@dataclass
class SensorMeta:
    name: str
    key: str
    ha_type: str
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
        HA_SENSOR,
        "mdi:counter",
        attributes=[SensorAttr("oil level", "oilLevel")],
    ),
    SensorMeta(
        "battery sensor", "batteryLevel", HA_SENSOR, "mdi:battery", DEVICE_CLASS_BATTERY
    ),
    SensorMeta("fuel sensor", "fuelLevel", HA_SENSOR, "mdi:gauge"),
    SensorMeta(
        "range sensor",
        "remainingRanges.electricalRange.distance",
        HA_SENSOR,
        "mdi:gauge",
    ),
    SensorMeta(
        "range sensor",
        "remainingRanges.conventionalRange.distance",
        HA_SENSOR,
        "mdi:gauge",
    ),
    SensorMeta("parking brake", "parkingBreak", HA_BINARY_SENSOR, "mdi:lock"),
    SensorMeta("doors", "doors.overallLockStatus", HA_SENSOR, "mdi:lock"),
    SensorMeta("lock", "overallOpenStatus", HA_SENSOR, "mdi:lock"),
    SensorMeta(
        "charger sensor",
        "batteryChargeStatus.plugState",
        HA_SENSOR,
        "mdi:ev-station",
        attributes=[
            SensorAttr("charging state", "batteryChargeStatus.chargingState"),
            SensorAttr("lock state", "batteryChargeStatus.lockState"),
            SensorAttr("charging mode", "batteryChargeStatus.chargingMode"),
            SensorAttr("charging mode", "batteryChargeStatus.chargingMode"),
            SensorAttr("error type", "batteryChargeStatus.errorType"),
            SensorAttr("remaining charge time to 100%", "batteryChargeStatus.remainingChargeTimeUntil100PercentInMinutes"),
            SensorAttr("charging power", "batteryChargeStatus.chargingPower"),
            SensorAttr("charge rate", "batteryChargeStatus.chargeRate.value")
        ]
    )
]

SENSOR_KEYS = [
    "mileage",
    "batteryLevel",
    "fuelLevel",
    "oilLevel",
    "remainingRanges.conventionalRange.distance",
    "remainingRanges.electricalRange.distance",
    "batteryChargeStatus.plugState",
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
    "batteryChargeStatus.plugState": "charger sensor"
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
