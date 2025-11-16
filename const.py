"""Constants for the Clausius integration."""
from __future__ import annotations

import logging
from typing import TypedDict

_LOGGER = logging.getLogger(__name__)

DOMAIN = "clausius"

# Default configuration
DEFAULT_SCAN_INTERVAL = 60  # seconds

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

# Entity definitions based on your PowerShell script
CLAUSIUS_ENTITIES = {
    # Temperature sensors
    "outside_temp": {
        "name": "Temperatura zewnętrzna",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "icon": "mdi:thermometer",
        "description": "Temperatura zewnętrzna z pompy ciepła"
    },
    "cwu_temp": {
        "name": "Temperatura CWU",
        "device_class": "temperature", 
        "unit_of_measurement": "°C",
        "icon": "mdi:water-thermometer",
        "description": "Temperatura ciepłej wody użytkowej"
    },
    
    # Status sensors
    "on_off": {
        "name": "Zasilanie",
        "device_class": "power",
        "icon": "mdi:power-plug",
        "description": "Stan zasilania pompy ciepła"
    },
    "mode": {
        "name": "Tryb pracy",
        "icon": "mdi:cog",
        "description": "Aktualny tryb pracy pompy ciepła"
    },
    "compressor_status": {
        "name": "Status kompresora",
        "icon": "mdi:engine",
        "description": "Status pracy kompresora"
    },
    "pump_status": {
        "name": "Status pompy",
        "icon": "mdi:pump",
        "description": "Status pracy pompy obiegowej"
    },
    
    # Level/Meter sensors
    "pump_level": {
        "name": "Poziom pompy",
        "icon": "mdi:gauge",
        "description": "Poziom pracy pompy grzewczej"
    },
    "glycol_pressure": {
        "name": "Ciśnienie glikolu",
        "device_class": "pressure",
        "unit_of_measurement": "bar",
        "icon": "mdi:gauge",
        "description": "Ciśnienie glikolu w układzie"
    },
    
    # SPF statistics
    "spf_year": {
        "name": "SPF Roczny",
        "icon": "mdi:chart-line",
        "unit_of_measurement": "SPF",
        "description": "Roczny współczynnik SPF"
    },
    "spf_month": {
        "name": "SPF Miesięczny",
        "icon": "mdi:chart-bar",
        "unit_of_measurement": "SPF", 
        "description": "Miesięczny współczynnik SPF"
    },
    "spf_day": {
        "name": "SPF Dzienny",
        "icon": "mdi:chart-bell-curve",
        "unit_of_measurement": "SPF",
        "description": "Dzienny współczynnik SPF"
    }
}

# Default values for configuration
DEFAULT_CONFIG = {
    CONF_HOST: "CT0025A23084.sn.ceo2green.com",
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