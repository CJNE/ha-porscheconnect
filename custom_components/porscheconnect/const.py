"""Constants for the Porsche Connect integration."""

DOMAIN = "porscheconnect"
DEFAULT_SCAN_INTERVAL = 1920

NAME = "porscheconnect"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.0"
ISSUE_URL = "https://github.com/cjne/ha-porscheconnect/issues"

PLATFORMS = [
    "sensor",
    "binary_sensor",
    "device_tracker",
    "number",
    "switch",
    "button",
    "lock",
    "image",
]

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
