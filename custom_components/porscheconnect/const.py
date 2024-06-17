import logging
from dataclasses import dataclass
from dataclasses import field


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
VERSION = "0.1.0"
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
