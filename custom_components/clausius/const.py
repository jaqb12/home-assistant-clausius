"""Constants for the Clausius integration."""
from __future__ import annotations

import logging
from typing import TypedDict

_LOGGER = logging.getLogger(__name__)

DOMAIN = "clausius"

# Default configuration
DEFAULT_SCAN_INTERVAL = 120  # seconds

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"

# Clausius API endpoints
CLAUSIUS_BASE_URL = "http://{host}:{port}/http/clausius"
CLAUSIUS_TEMPERATURAS_PATH = "temperaturas.html"
CLAUSIUS_STATUS_PATH = "status.html"
CLAUSIUS_INFORMACION_PATH = "informacion.html"

# Entity definitions - translation keys only
CLAUSIUS_ENTITIES = {
    # Temperature sensors
    "outside_temp": {
        "translation_key": "clausius_outside_temp",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "icon": "mdi:thermometer",
    },
    "cwu_temp": {
        "translation_key": "clausius_cwu_temp",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "icon": "mdi:water-thermometer",
    },
    # Status sensors
    "on_off": {
        "translation_key": "clausius_on_off",
        "icon": "mdi:power-plug",
    },
    "mode": {
        "translation_key": "clausius_mode",
        "icon": "mdi:cog",
    },
    "compressor_status": {
        "translation_key": "clausius_compressor_status",
        "icon": "mdi:engine",
    },
    "pump_status": {
        "translation_key": "clausius_pump_status",
        "icon": "mdi:pump",
    },
    # Level/Meter sensors
    "pump_level": {
        "translation_key": "clausius_pump_level",
        "icon": "mdi:heat-pump-outline",
    },
    "glycol_pressure": {
        "translation_key": "clausius_glycol_pressure",
        "device_class": "pressure",
        "unit_of_measurement": "bar",
        "icon": "mdi:gauge",
    },
    "glycol_input_temp": {
        "translation_key": "clausius_glycol_input_temp",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "icon": "mdi:water-thermometer",
    },
    "glycol_output_temp": {
        "translation_key": "clausius_glycol_output_temp",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "icon": "mdi:water-thermometer",
    },
    "water_presure": {
        "translation_key": "clausius_water_presure",
        "device_class": "pressure",
        "unit_of_measurement": "bar",
        "icon": "mdi:gauge",
    },
    "water_heating_out_temp": {
        "translation_key": "clausius_water_heating_out_temp",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "icon": "mdi:heating-coil",
    },
    "water_heating_in_temp": {
        "translation_key": "clausius_water_heating_in_temp",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "icon": "mdi:heating-coil",
    },
    # SPF statistics
    "spf_year": {
        "translation_key": "clausius_spf_year",
        "icon": "mdi:chart-line",
        "unit_of_measurement": "SPF",
    },
    "spf_month": {
        "translation_key": "clausius_spf_month",
        "icon": "mdi:chart-bar",
        "unit_of_measurement": "SPF",
    },
    "spf_day": {
        "translation_key": "clausius_spf_day",
        "icon": "mdi:chart-bell-curve",
        "unit_of_measurement": "SPF",
    }
}

# Default values for configuration
DEFAULT_CONFIG = {
    CONF_HOST: "",
    CONF_PORT: 80,
    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL
}

# Error messages
ERROR_INVALID_CONFIG = "Invalid configuration for Clausius integration"
ERROR_CONNECTION_FAILED = "Failed to connect to Clausius device"
ERROR_AUTHENTICATION_FAILED = "Authentication failed for Clausius device"
ERROR_DATA_PARSING_FAILED = "Failed to parse data from Clausius device"

# Exported symbols
LOGGER = _LOGGER