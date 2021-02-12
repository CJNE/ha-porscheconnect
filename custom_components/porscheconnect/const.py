import logging

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_POWER_FACTOR,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
    DEVICE_CLASS_VOLTAGE,
)

"""Constants for the Porsche Connect integration."""

DOMAIN = "porscheconnect"
LOGGER = logging.getLogger(__package__)
DEFAULT_SCAN_INTERVAL = 660
MIN_SCAN_INTERVAL = 60
PORSCHE_COMPONENTS = [
    "sensor",
    "device_tracker",
]

SENSOR_KEYS = ['mileage', 'batteryLevel', 'fuelLevel', 'oilLevel',
        'remainingRanges.conventionalRange.distance',
        'remainingRanges.electricalRange.distance']

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
