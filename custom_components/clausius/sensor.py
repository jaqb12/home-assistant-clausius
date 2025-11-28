"""Clausius Heat Pump sensors."""

from __future__ import annotations

import asyncio
import re
import logging
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
                CLAUSIUS_INFORMACION_PATH,
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
                _LOGGER.warning(
                    "No data received from any endpoint - setting offline mode"
                )
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
            "pump_status": "OFFLINE",
            "spf_year": None,
            "spf_month": None,
            "spf_day": None,
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
                timeout=aiohttp.ClientTimeout(total=15),  # 15 second timeout
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
        """Parse temperaturas endpoint content."""
        results = {}
        lines = content.split("\n")

        _LOGGER.debug(f"Parsing temperaturas - total lines: {len(lines)}")

        # Look for temperature data patterns
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Outiside tempareture in in next line after line containing exterior.png
            if "exterior.png" in line_lower:
                _LOGGER.debug(f"Found exterior.png at line {i}: {line[:100]}")
                # Safely get the next line if it exists
                if i + 1 < len(lines):
                    match = re.search(r"<span>([-+]?\d*\.?\d+)</span>", lines[i + 1])
                    value = float(match.group(1)) if match else None
                    if value is not None:
                        results["outside_temp"] = value
                        _LOGGER.debug(f"Found outside_temp: {value}")

            # CWU temperature pattern
            # CWU temperature is in the next line after line containing 'src="img/shower.png"></div></div>'
            elif 'shower.png' in line_lower:
                _LOGGER.debug(f"Found shower.png at line {i}: {line[:100]}")
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    _LOGGER.debug(f"Next line after shower.png (line {i+1}): {next_line[:100]}")
                    match = re.search(r">([-+]?\d*\.?\d+|\d+) &ordm;C", next_line)
                    if not match:
                        # Try alternative patterns
                        _LOGGER.debug(f"First regex didn't match, trying alternative")
                        match = re.search(r">([-+]?\d*\.?\d+)", next_line)
                    value = float(match.group(1)) if match else None
                    if value is not None:
                        results["cwu_temp"] = value
                        _LOGGER.debug(f"Found cwu_temp: {value}")
                    else:
                        _LOGGER.debug(f"Could not parse CWU temperature from: {next_line[:100]}")

            # Pump level
            elif "radiant.png" in line_lower:
                _LOGGER.debug(f"Found radiant.png at line {i}: {line[:100]}")
                # Safely get the next line if it exists
                if i + 1 < len(lines):
                    match = re.search(r"Level\s+(\d+)", lines[i + 1])
                    if match:
                        value = f"Level {match.group(1)}"
                        results["pump_level"] = value
                        _LOGGER.debug(f"Found pump_level: {value}")

        _LOGGER.debug(f"Final results from _parse_temperaturas: {results}")
        return results

    def _parse_status(self, content: str) -> dict[str, Any]:
        """Parse status endpoint content."""
        results = {}
        lines = content.split("\n")

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Power status
            if "id=\"button" in line_lower:
                _LOGGER.debug(f"Found button at line {i}: {line[:100]}")
                # Safely get the number from the button ID
                match = re.search(r"(\d+)", line)
                if match:
                    value = int(match.group(1))
                    results["on_off"] = value
                    # results["on_off"] = self._extract_powerstatus_value(value)
                    _LOGGER.debug(f"Found on_off: {value}")

            # Compressor status
            elif "img id=\"compresor" in line_lower:
                _LOGGER.debug(f"Found compresor status at line {i}")
                # Safely get the number from the compresor
                match = re.search(r"data-value-type=\"(\d+)", line)
                if match:
                    value = match.group(1)
                    results["compressor_status"] = self._extract_status_value(value)
                    _LOGGER.debug(f"Found compressor_status: {value}")

            # Pump status
            elif "id=\"estado" in line_lower:
                _LOGGER.debug(f"Found pump status at line {i}")
                # Safely get the number from the pump
                match = re.search(r"data-value-type=\"(\d+)", line)
                if match:
                    value = match.group(1)
                    results["pump_status"] = self._extract_pump_status_value(value)
                    _LOGGER.debug(f"Found compressor_status: {value}")

            # Mode
            elif "id=\"modo" in line_lower:
                _LOGGER.debug(f"Found mode at line {i}")
                # Safely get the number from the mode
                match = re.search(r"data-value-type=\"(\d+)", line)
                if match:
                    value = match.group(1)
                    status_map = {
                        "0": "Zima",
                        "1": "Lato",
                        "2": "Auto"
                    }
                    results["mode"] = status_map.get(value, "Unknown")
                    _LOGGER.debug(f"Found mode: {value}")

        return results

    def _parse_informacion(self, content: str) -> dict[str, Any]:
        """Parse informacion endpoint content."""
        results = {}
        lines = content.split("\n")
        offset = 2

        # Water pressure
        water_presure_static_line = lines[306 - offset]
        match_0 = re.search(r"(\d.\d) bar", water_presure_static_line)
        if match_0:
            value = float(match_0.group(1))
            results["water_presure"] = value
            _LOGGER.debug(f"Found glycol_pressure: {value}")

        # Glycol pressure
        gicol_presure_static_line = lines[329 - offset]
        match_1 = re.search(r"(\d.\d) bar", gicol_presure_static_line)
        if match_1:
            value = float(match_1.group(1))
            results["glycol_pressure"] = value
            _LOGGER.debug(f"Found glycol_pressure: {value}")

        # Glycol input temperature
        glycol_input_temp_static_line = lines[327 - offset]
        match_2 = re.search(r"([-+]?\d*\.?\d+) &ordm;C", glycol_input_temp_static_line)
        if match_2:
            value = float(match_2.group(1))
            results["glycol_input_temp"] = value
            _LOGGER.debug(f"Found glycol_input_temp: {value}")

        # Glycol output temperature
        glycol_output_temp_static_line = lines[324 - offset]
        match_3 = re.search(r"([-+]?\d*\.?\d+) &ordm;C", glycol_output_temp_static_line)
        if match_3:
            value = float(match_3.group(1))
            results["glycol_output_temp"] = value
            _LOGGER.debug(f"Found glycol_output_temp: {value}")

        # SPF value for Day
        spf_day_static_line = lines[61 - offset]
        match_spf_day = re.search(r"(\d*\.?\d+)", spf_day_static_line)
        if match_spf_day:
            value = float(match_spf_day.group(1))
            results["spf_day"] = value
            _LOGGER.debug(f"Found spf_day: {value}")

        # SPF value for Month
        spf_month_static_line = lines[70 - offset]
        match_spf_month = re.search(r"(\d*\.?\d+)", spf_month_static_line)
        if match_spf_month:
            value = float(match_spf_month.group(1))
            results["spf_month"] = value
            _LOGGER.debug(f"Found spf_month: {value}")

        # SPF value for Year
        spf_year_static_line = lines[52 - offset]
        match_spf_year = re.search(r"(\d*\.?\d+)", spf_year_static_line)
        if match_spf_year:
            value = float(match_spf_year.group(1))
            results["spf_year"] = value
            _LOGGER.debug(f"Found spf_year: {value}")

        # Water heating out temperature
        water_heating_out_temp_static_line = lines[304 - offset]
        match_water_out_tmp = re.search(r"([-+]?\d*\.?\d+) &ordm;C", water_heating_out_temp_static_line)
        if match_water_out_tmp:
            value = float(match_water_out_tmp.group(1))
            results["water_heating_out_temp"] = value
            _LOGGER.debug(f"Found water_heating_out_temp: {value}")

        # Water heating in temperature
        water_heating_in_temp_static_line = lines[301 - offset]
        match_water_in_tmp = re.search(r"([-+]?\d*\.?\d+) &ordm;C", water_heating_in_temp_static_line)
        if match_water_in_tmp:
            value = float(match_water_in_tmp.group(1))
            results["water_heating_in_temp"] = value
            _LOGGER.debug(f"Found water_heating_in_temp: {value}")

        return results

    def _extract_pump_status_value(self, text: str) -> Optional[str]:
        """Extract pump status from text."""
        text = text.strip().lower()
        status_map = {
                "0": "Alarm",
                "1": "OK"
            }
        return status_map.get(text)

    def _extract_powerstatus_value(self, text: str) -> Optional[str]:
        """Extract power status from text."""
        text = text.strip().lower()
        status_map = {
                "0": "Off",
                "1": "On"
            }
        return status_map.get(text)

    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text."""
        import re

        # Look for numbers with optional decimal part
        match = re.search(r"[-+]?\d*\.?\d+", text)
        if match:
            try:
                return float(match.group().replace(",", "."))
            except ValueError:
                pass
        return None

    def _extract_status_value(self, text: str) -> Optional[str]:
        """Extract status string from text."""
        value = text.strip().lower()
        # Find index for number in text. it is placed inside data-value-type, f.ex.: data-value-type="5"
        # Extract the value after data-value-type=" and before the next "
        if value:
            # number = match.group(1)
            status_map = {
                "0": "Compressor On",
                "1": "Powering On",
                "2": "Powering Off",
                "3": "Wait",
                "4": "Stop",
                "5": "OK"
            }
            return status_map.get(value, "Unknown")
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
        self._attr_unique_id = f"clausius_{entity_id}"
        self._attr_icon = description.get("icon")
        
        # Use translation_key instead of hardcoded name
        self._attr_translation_key = description.get("translation_key")
        self._attr_has_entity_name = True
        
        if "device_class" in description:
            self._attr_device_class = description.get("device_class")
        self._attr_unit_of_measurement = description.get("unit_of_measurement")
        self._attr_native_unit_of_measurement = description.get("unit_of_measurement")

        # Build entity description with only valid keys
        entity_desc_kwargs = {
            "key": entity_id,
            "translation_key": description.get("translation_key"),
        }
        if "icon" in description:
            entity_desc_kwargs["icon"] = description.get("icon")
        if "device_class" in description:
            entity_desc_kwargs["device_class"] = description.get("device_class")
        if "unit_of_measurement" in description:
            entity_desc_kwargs["native_unit_of_measurement"] = description.get("unit_of_measurement")
        entity_desc_kwargs["state_class"] = SensorStateClass.MEASUREMENT

        self._entity_description = SensorEntityDescription(**entity_desc_kwargs)
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
