"""Clausius Heat Pump sensors."""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import timedelta
from typing import Any, Dict, Optional

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfPressure
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CLAUSIUS_ENTITIES,
    CLAUSIUS_BASE_URL,
    CLAUSIUS_TEMPERATURAS_PATH,
    CLAUSIUS_STATUS_PATH,
    CLAUSIUS_INFORMACION_PATH,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Clausius sensors from a config entry."""
    coordinator = ClausiusDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        ClausiusSensor(coordinator, entity_id, description)
        for entity_id, description in CLAUSIUS_ENTITIES.items()
    )


class ClausiusDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Clausius heat pump."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.clausius_config = entry.data
        self.host = self.clausius_config["host"]
        self.port = self.clausius_config["port"]
        self.username = self.clausius_config["username"]
        self.password = self.clausius_config["password"]
        
        update_interval_seconds = entry.options.get("scan_interval", 60)
        update_interval = timedelta(seconds=update_interval_seconds)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        
        self.base_url = CLAUSIUS_BASE_URL.format(host=self.host, port=self.port)
        self._hass = hass

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Clausius device."""
        try:
            data = {}
            successful_endpoints = 0
            
            # Fetch data from all three endpoints
            endpoints = [
                CLAUSIUS_TEMPERATURAS_PATH,
                CLAUSIUS_STATUS_PATH, 
                CLAUSIUS_INFORMACION_PATH
            ]
            
            for endpoint in endpoints:
                try:
                    endpoint_data = await self._fetch_endpoint(endpoint)
                    if endpoint_data:
                        data.update(endpoint_data)
                        successful_endpoints += 1
                        _LOGGER.debug(f"Successfully fetched data from {endpoint}")
                except Exception as err:
                    _LOGGER.warning(f"Failed to fetch {endpoint}: {err}")
                    
            # If no successful endpoints, set offline mode
            if successful_endpoints == 0:
                _LOGGER.warning("No data received from any endpoint - setting offline mode")
                return self._get_offline_data()
                
            return data
            
        except Exception as err:
            _LOGGER.error(f"Error communicating with API: {err}")
            return self._get_offline_data()
            
    def _get_offline_data(self) -> dict[str, Any]:
        """Return offline data when device is not reachable."""
        return {
            "outside_temp": None,
            "cwu_temp": None,
            "pump_level": None,
            "glycol_pressure": None,
            "on_off": None,
            "mode": "OFFLINE", 
            "compressor_status": "OFFLINE",
            "pomp_status": "OFFLINE",
            "spf_year": None,
            "spf_month": None,
            "spf_day": None
        }

    async def _fetch_endpoint(self, endpoint: str) -> dict[str, Any]:
        """Fetch data from a specific Clausius endpoint."""
        import base64
        import asyncio
        
        # Create Basic Auth header
        credentials = f"{self.username}:{self.password}"
        auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        
        headers = {"Authorization": auth_header}
        url = f"{self.base_url}/{endpoint}"
        
        session = async_get_clientsession(self._hass)
        
        try:
            _LOGGER.debug(f"Fetching {endpoint} from {url}")
            
            async with session.get(
                url,
                headers=headers,
                timeout=15  # 15 second timeout
            ) as response:
                if response.status != 200:
                    _LOGGER.warning(f"HTTP {response.status} for {endpoint}: {url}")
                    return {}
                    
                content = await response.text()
                _LOGGER.debug(f"Successfully fetched {endpoint}")
                return self._parse_endpoint_content(endpoint, content)
                
        except asyncio.TimeoutError:
            _LOGGER.warning(f"Timeout connecting to {endpoint}: {url}")
            return {}
        except (aiohttp.ClientError, Exception) as err:
            error_msg = str(err).lower()
            if "dns" in error_msg or "name or service not known" in error_msg:
                _LOGGER.warning(f"DNS resolution failed for {endpoint}: {url} - {err}")
            elif "timeout" in error_msg:
                _LOGGER.warning(f"Connection timeout for {endpoint}: {url} - {err}")
            else:
                _LOGGER.warning(f"Connection error for {endpoint}: {url} - {err}")
            return {}

    def _parse_endpoint_content(self, endpoint: str, content: str) -> dict[str, Any]:
        """Parse content from Clausius endpoint."""
        results = {}
        
        if endpoint == CLAUSIUS_TEMPERATURAS_PATH:
            results = self._parse_temperaturas(content)
        elif endpoint == CLAUSIUS_STATUS_PATH:
            results = self._parse_status(content)
        elif endpoint == CLAUSIUS_INFORMACION_PATH:
            results = self._parse_informacion(content)
            
        return results

    def _parse_temperaturas(self, content: str) -> dict[str, Any]:
        """Parse temperaturas endpoint content based on HTML files."""
        import re
        results = {}
        
        # 1. Temperatura zewnętrzna (outside_temp)
        # Szuka obrazka 'exterior.png' i bierze wartość z następnego bloku vertical-text
        # <img ... src="./Temperaturas - Clausius_files/exterior.png">
        # <div class="vertical-text"><span>11.9</span> ºC</div>
        match_out = re.search(
            r'exterior\.png.*?<div class="vertical-text"><span>([-\d.,]+)</span>', 
            content, 
            re.IGNORECASE | re.DOTALL
        )
        if match_out:
            try:
                results["outside_temp"] = float(match_out.group(1).replace(',', '.'))
            except (ValueError, IndexError):
                _LOGGER.warning("Could not parse outside_temp")

        # 2. Temperatura CWU (cwu_temp)
        # Szuka obrazka 'shower.png' i bierze wartość z następnego bloku vertical-text
        # <img ... src="./Temperaturas - Clausius_files/shower.png">
        # <div class="vertical-text">43.8 ºC</div>
        match_cwu = re.search(
            r'shower\.png.*?<div class="vertical-text">([-\d.,]+)\s*ºC</div>', 
            content, 
            re.IGNORECASE | re.DOTALL
        )
        if match_cwu:
            try:
                # Usuwa <span> jeśli jest, i bierze tylko liczbę
                value_str = re.sub(r'<.*?>', '', match_cwu.group(1)).strip()
                results["cwu_temp"] = float(value_str.replace(',', '.'))
            except (ValueError, IndexError):
                _LOGGER.warning("Could not parse cwu_temp")

        # 3. Poziom pompy (pump_level) - to powinno nadal działać
        # <div class="vertical-text">Level 1</div>
        match_level = re.search(r'Level\s(\d)', content, re.IGNORECASE)
        if match_level:
            try:
                results["pump_level"] = int(match_level.group(1))
            except (ValueError, IndexError):
                _LOGGER.warning("Could not parse pump_level")
        
        _LOGGER.debug(f"Parsed temperaturas: {results}")
        return results

    def _parse_status(self, content: str) -> dict[str, Any]:
        """Parse status endpoint content based on HTML files."""
        import re
        results = {}

        # 1. Zasilanie (on_off)
        # <div class="section on" id="button" data-value-type="1">
        match_on_off = re.search(r'id="button".*?data-value-type="(\d)"', content, re.IGNORECASE)
        if match_on_off:
            results["on_off"] = "On" if match_on_off.group(1) == "1" else "Off"

        # 2. Tryb pracy (mode)
        # <div id="modo" data-value-type="2" ...>
        match_mode = re.search(r'id="modo".*?data-value-type="(\d)"', content, re.IGNORECASE)
        if match_mode:
            mode_val = match_mode.group(1)
            if mode_val == '0':
                results["mode"] = 'Zima'
            elif mode_val == '1':
                results["mode"] = 'Lato'
            elif mode_val == '2':
                results["mode"] = 'Automatyczny'
            else:
                results["mode"] = 'Unknown'

        # 3. Status kompresora (compressor_status)
        # <img id="compresor" ... data-value-type="0">
        match_comp = re.search(r'id="compresor".*?data-value-type="(\d)"', content, re.IGNORECASE | re.DOTALL)
        if match_comp:
            compressor_status_map = {
                '0': 'CompresorON', '1': 'TurningOff', '2': 'TurningOn',
                '3': 'Waiting 321', '4': 'STOP', '5': 'OK',
            }
            status_val = match_comp.group(1)
            results["compressor_status"] = compressor_status_map.get(status_val, 'Problem')

        # 4. Status pompy (pump_status) - Zobacz wyjaśnienie poniżej
        # Ten sensor nie istnieje w pliku Status.html
        results["pump_status"] = None # Ustawiamy na None, ponieważ nie można go znaleźć
        
        _LOGGER.debug(f"Parsed status: {results}")
        return results

    def _parse_informacion(self, content: str) -> dict[str, Any]:
        """Parse informacion endpoint content based on PS script."""
        import re
        results = {}

        # PS: $lines[318].Substring($lines[318].IndexOf('bar') - 4, 3)
        # Find number right before "bar"
        match = re.search(r'([-+]?\d+[.,]?\d*)\s*bar', content, re.IGNORECASE)
        if match:
            try:
                results["glycol_pressure"] = float(match.group(1).replace(',', '.'))
            except (ValueError, IndexError):
                _LOGGER.warning("Could not parse glycol_pressure")

        # PS: SPF values from specific lines (48, 57, 66) and 'text('...
        # We find the keyword (e.g., "spf year") and then the number after the next 'text(' call
        match = re.search(r'(spf.*(roczny|year)).*?text\(\).*?([-+]?\d+[.,]?\d*)', content, re.IGNORECASE | re.DOTALL)
        if match:
            try:
                results["spf_year"] = float(match.group(3).replace(',', '.'))
            except (ValueError, IndexError):
                _LOGGER.warning("Could not parse spf_year")

        match = re.search(r'(spf.*(miesięczny|month)).*?text\(\).*?([-+]?\d+[.,]?\d*)', content, re.IGNORECASE | re.DOTALL)
        if match:
            try:
                results["spf_month"] = float(match.group(3).replace(',', '.'))
            except (ValueError, IndexError):
                _LOGGER.warning("Could not parse spf_month")

        match = re.search(r'(spf.*(dzienny|day)).*?text\(\).*?([-+]?\d+[.,]?\d*)', content, re.IGNORECASE | re.DOTALL)
        if match:
            try:
                results["spf_day"] = float(match.group(3).replace(',', '.'))
            except (ValueError, IndexError):
                _LOGGER.warning("Could not parse spf_day")

        _LOGGER.debug(f"Parsed informacion: {results}")
        return results

    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text."""
        import re
        # Look for numbers with optional decimal part
        match = re.search(r'[-+]?\d*\.?\d+', text)
        if match:
            try:
                return float(match.group().replace(',', '.'))
            except ValueError:
                pass
        return None

    def _extract_status_value(self, text: str) -> Optional[str]:
        """Extract status string from text."""
        text = text.strip().lower()
        # Common status values
        if any(word in text for word in ["on", "włączony", "aktywny"]):
            return "On"
        elif any(word in text for word in ["off", "wyłączony", "nieaktywny"]):
            return "Off"
        elif text:
            return text.title()
        return None

    def _extract_string_value(self, text: str) -> Optional[str]:
        """Extract string value from text."""
        text = text.strip()
        if text:
            return text.title()
        return None



class ClausiusSensor(CoordinatorEntity, SensorEntity):
    """Clausius Heat Pump Sensor."""

    def __init__(
        self,
        coordinator: ClausiusDataUpdateCoordinator,
        entity_id: str,
        description: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_id = f"sensor.clausius_{entity_id}"
        self._attr_name = description["name"]
        self._attr_unique_id = f"clausius_{entity_id}"
        self._attr_icon = description.get("icon")
        self._attr_device_class = description.get("device_class")
        self._attr_unit_of_measurement = description.get("unit_of_measurement")
        self._attr_native_unit_of_measurement = description.get("unit_of_measurement")
        self._entity_description = SensorEntityDescription(
            key=entity_id,
            name=description["name"],
            icon=description.get("icon"),
            device_class=description.get("device_class"),
            native_unit_of_measurement=description.get("unit_of_measurement"),
            state_class=SensorStateClass.MEASUREMENT,
        )
        self._entity_id = entity_id

    @property
    def native_value(self) -> Optional[float | int | str]:
        """Return the state of the sensor."""
        if self.coordinator.data and self._entity_id in self.coordinator.data:
            return self.coordinator.data[self._entity_id]
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attributes = {
            "last_update": self.coordinator.last_update_success,
            "device_name": f"Clausius Heat Pump ({self.coordinator.host})",
        }
        
        # Add description as attribute
        if self._entity_id in CLAUSIUS_ENTITIES:
            attributes["description"] = CLAUSIUS_ENTITIES[self._entity_id]["description"]
            
        return attributes

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            name="Clausius Heat Pump",
            manufacturer="Clausius",
            model="Heat Pump",
            sw_version="Unknown",
            configuration_url=f"http://{self.coordinator.host}:{self.coordinator.port}",
        )