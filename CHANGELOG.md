# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Clausius Heat Pump integration
- Support for reading temperature data from Clausius heat pump
- Configuration through Home Assistant UI
- Multiple sensor entities for monitoring:
  - Outside temperature
  - DHW (Domestic Hot Water / CWU) temperature
  - Power state
  - Operating mode
  - Compressor status
  - Pump status
  - Pump level
  - Glycol pressure
  - Glycol input/output temperature
  - Water pressure and heating temperatures
  - Daily, monthly, and annual SPF (Seasonal Performance Factor)
- HACS compatibility
- Automatic entity discovery and management
- Debug logging for troubleshooting

### Changed
- Migrated from variables addon approach to full integration
- Improved HTML parsing with regex patterns for all endpoints
- Enhanced error handling with graceful fallback to offline mode
- Better status mapping for compressor and pump states

### Deprecated
- Support for variables addon approach (use this integration instead)

### Removed
- variables addon dependency

### Fixed
- Fixed CWU temperature parsing to properly extract both outside_temp and cwu_temp values
- Removed invalid device_class 'power' from on_off status sensor
- Fixed pump_level parsing to extract Level values correctly
- Improved device_class and unit handling to prevent Home Assistant validation errors
- Fixed SensorEntityDescription initialization to only include valid parameters
- Added default values ("Unknown") for unmatched status codes in compressor and pump states

### Security
- N/A

## Migration Guide

### From Variables Addon

If you were previously using the `variables` addon to track Clausius heat pump data:

1. Remove the variables configuration from `configuration.yaml`
2. Delete the `var_clausius.yaml` file
3. Install this integration via HACS or manual installation
4. Configure through the Home Assistant UI
5. Update any automations and scripts to use the new sensor entities:
   - Replace `var.clausius_*` with `sensor.clausius_*`

## Planned Features

- [ ] Historical data tracking
- [ ] Energy consumption statistics
- [ ] Custom alert thresholds
- [ ] Integration with energy dashboard
- [ ] Support for multiple heat pump instances
- [ ] Advanced filtering and data visualization options
