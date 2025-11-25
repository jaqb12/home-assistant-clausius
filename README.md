# Home Assistant Integration for Clausius Heat Pump

This integration allows you to monitor your Clausius heat pump in Home Assistant by reading data directly from the heat pump's web interface. Get real-time insights into temperature, status, performance, and efficiency metrics.

## Features

- 🌡️ Real-time temperature monitoring (outside, DHW, glycol, water heating)
- 📊 Performance metrics (SPF - Seasonal Performance Factor)
- 🔌 System status monitoring (compressor, pump, power state)
- ⚙️ Operating mode tracking
- 💧 Pressure monitoring (glycol, water)
- 🔄 Automatic data refresh with configurable interval
- 🛡️ Secure authentication
- 📱 Full Home Assistant UI integration
- 🔍 Debug logging for troubleshooting

## Requirements

- Home Assistant Core 2023.1 or newer
- Network access to the Clausius heat pump web interface
- Clausius portal/device login credentials
- Python 3.9+

## Installation

### Option 1: HACS (Recommended)

1. Install HACS in Home Assistant
2. Go to HACS > Integrations
3. Click "+" and search for "Clausius Heat Pump"
4. Install the integration
5. Restart Home Assistant

### Option 2: Manual Installation

1. Download the integration source code
2. Copy the `custom_components/clausius/` folder to `config/custom_components/` in Home Assistant
3. Restart Home Assistant

## Configuration

### Through Home Assistant Interface

1. Go to Settings > Devices and Services
2. Click "Create Automation" or "Add integration"
3. Search for "Clausius Heat Pump" or "clausius"
4. Click on the integration
5. Fill in your device details:
   - **Host**: IP address or hostname of your heat pump
   - **Port**: HTTP interface port (default: 80)
   - **Username**: Your login username
   - **Password**: Your login password
   - **Scan Interval**: Data refresh frequency in seconds (default: 60, minimum: 5)

### Configuration Parameters

| Parameter | Description | Required | Default | Notes |
|-----------|-------------|----------|---------|-------|
| Host | IP address or hostname of the heat pump | Yes | - | Can be local IP or domain name |
| Port | HTTP interface port | Yes | 80 | Usually 80 for HTTP |
| Username | Username for authentication | Yes | - | Check your device credentials |
| Password | User password | Yes | - | Stored securely in Home Assistant |
| Scan Interval | Data reading frequency (seconds) | No | 60 | Min: 5s, Max: 3600s |

## Entities

The integration creates the following sensor entities:

### Temperature Sensors 🌡️
- `sensor.clausius_outside_temp` - Outside temperature (°C)
- `sensor.clausius_cwu_temp` - DHW/Hot water temperature (°C)
- `sensor.clausius_glycol_input_temp` - Glycol input temperature (°C)
- `sensor.clausius_glycol_output_temp` - Glycol output temperature (°C)
- `sensor.clausius_water_heating_in_temp` - Water heating input temperature (°C)
- `sensor.clausius_water_heating_out_temp` - Water heating output temperature (°C)

### Status Sensors 🔌
- `sensor.clausius_on_off` - Power state (On/Off)
- `sensor.clausius_mode` - Operating mode
- `sensor.clausius_compressor_status` - Compressor status
- `sensor.clausius_pump_status` - Pump status

### Measurement Sensors 📊
- `sensor.clausius_pump_level` - Pump operating level
- `sensor.clausius_glycol_pressure` - Glycol circuit pressure (bar)
- `sensor.clausius_water_presure` - Water circuit pressure (bar)

### Performance Sensors 📈
- `sensor.clausius_spf_day` - Daily SPF (Seasonal Performance Factor)
- `sensor.clausius_spf_month` - Monthly SPF
- `sensor.clausius_spf_year` - Annual SPF

## Usage Examples

### Lovelace UI Card

```yaml
type: entities
entities:
  - entity: sensor.clausius_outside_temp
    name: Outside Temperature
  - entity: sensor.clausius_cwu_temp
    name: DHW Temperature
  - entity: sensor.clausius_on_off
    name: Power
  - entity: sensor.clausius_mode
    name: Operating Mode
  - entity: sensor.clausius_compressor_status
    name: Compressor
  - entity: sensor.clausius_spf_year
    name: Annual SPF
header:
  title: Clausius Heat Pump
```

### Temperature Monitoring Automation

```yaml
alias: High DHW Temperature Alert
description: Notify when DHW temperature exceeds 60°C
trigger:
  - platform: numeric_state
    entity_id: sensor.clausius_cwu_temp
    above: 60
action:
  - service: notify.mobile_app_your_phone
    data:
      message: "DHW Temperature: {{ states('sensor.clausius_cwu_temp') }}°C"
      title: ⚠️ High DHW Temperature
```

### Energy Efficiency Monitoring

```yaml
alias: Low SPF Alert
description: Notify when daily SPF drops below 3.0
trigger:
  - platform: numeric_state
    entity_id: sensor.clausius_spf_day
    below: 3.0
action:
  - service: notify.persistent_notification
    data:
      message: "Daily SPF is low: {{ states('sensor.clausius_spf_day') }}"
      title: 🔴 Low System Efficiency
```

## Troubleshooting

### Connection Errors

**Error**: "Failed to connect to Clausius device"
- ✅ Check the heat pump's IP address and port are correct
- ✅ Ensure the heat pump's web interface is accessible from your network
- ✅ Verify your login credentials are correct
- ✅ Check if the device is online and responsive
- ✅ Look at Home Assistant logs for detailed error messages

### No Data Appearing

**Error**: "Sensors show unknown state"
- ✅ Wait 1-2 minutes after configuration for first data fetch
- ✅ Check Home Assistant logs (Settings > System > Logs)
- ✅ Verify the refresh interval isn't causing timeout issues
- ✅ Check your network connectivity to the heat pump
- ✅ Enable debug logging (see below)

### Enable Debug Logging

Add this to `configuration.yaml` to see detailed logs:

```yaml
logger:
  logs:
    custom_components.clausius: debug
    homeassistant.components.sensor: debug
```

Then check the logs in Settings > System > Logs.

### Website Structure Changed

If the integration stops working after a device firmware update:
- The HTML structure may have changed
- Open an issue on GitHub with device details
- Include relevant log excerpts

## Migration from Variables Addon

If you previously used the variables addon:

1. Remove variables configuration from `configuration.yaml`
2. Delete the `var_clausius.yaml` file
3. Install this integration via HACS
4. Configure through the Home Assistant UI
5. Update your automations:
   - Replace `var.clausius_outside_temp` with `sensor.clausius_outside_temp`
   - Replace `var.clausius_cwu_temp` with `sensor.clausius_cwu_temp`
   - etc.

## Known Limitations

- Requires network access to heat pump (local network or exposed interface)
- Data is read-only (no control of heat pump settings)
- Update frequency depends on configured scan interval
- Authentication credentials stored in Home Assistant config

## Support

- 📖 Documentation: Check the README and CHANGELOG
- 🐛 Bug reports: [GitHub Issues](https://github.com/jaqb12/home-assistant-clausius/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/jaqb12/home-assistant-clausius/discussions)
- 🏠 Community: [Home Assistant Forum](https://community.home-assistant.io/)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue for bugs and feature requests.
