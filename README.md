[![GitHub Release](https://img.shields.io/github/v/release/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant)](https://github.com/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant/releases/latest)
[![GitHub License](https://img.shields.io/github/license/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant?cacheSeconds=60)](./LICENSE)
[![hacs](https://img.shields.io/badge/HACS-default-green.svg)](https://hacs.xyz)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-blue.svg)](https://github.com/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant/pulls)

<!-- [![GitHub watchers](https://img.shields.io/github/watchers/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant.svg?style=social&label=Watch)](https://GitHub.com/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant/watchers/)
[![GitHub forks](https://img.shields.io/github/forks/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant.svg?style=social&label=Fork)](https://GitHub.com/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant/network/)
[![GitHub stars](https://img.shields.io/github/stars/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant.svg?style=social&label=Star)](https://GitHub.com/neznein9/Kasa-Smart-Dimmer-Add-on-for-Home-Assistant/stargazers/) -->



# Kasa Smart Dimmer

## Integration for Home Assistant


This is a custom integration for [Home Assistant](https://www.home-assistant.io/) that adds extra actions for [Kasa Smart](https://www.kasasmart.com/) dimmer switches, such as the [KS220](https://www.kasasmart.com/us/products/smart-switches/kasa-smart-wifi-light-switch-dimmer-ks220).

This is **not** a full replacement integration for Kasa devices. It is intended to work alongside the [TP-Link Smart Home](https://www.home-assistant.io/integrations/tplink/) integration to expose additional capabilities that Home Assistant does not currently surface.


## Features

- [x] Set a dimmer switch's standby brightness without turning on the light

## Installation

### HACS

Click the button to install via [HACS](https://hacs.xyz/):

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=neznein9&repository=Kasa-Smart-Dimmer-Add-on-for-Home-Assistant&category=integration)

Or manually:

1. Open HACS
2. Go to **Integrations**
3. Open the three-dot menu
4. Select **Custom repositories**
5. Paste this repository URL
6. Set category to **Integration**
7. Install **Kasa Smart Dimmer**
8. Restart Home Assistant

### Manual Installation

Copy the `custom_components/kasa_smart_dimmer` directory from this repo into your `custom_components` config directory.

## Usage

Use the action to set a dimmer's brightness without turning on the light:

```yaml
action: kasa_smart_dimmer.set_standby_brightness
data:
  entity_id: light.en_suite_bathroom
  brightness: 100
```

#### Optional override

If the integration cannot automatically resolve the device IP address, you can pass host manually:

```yaml
action: kasa_smart_dimmer.set_standby_brightness
data:
  entity_id: light.en_suite_bathroom
  brightness: 35
  host: 192.168.1.123
```

## Tested Devices
- [x] [Kasa Smart Wi-Fi Light Switch, Dimmer - | KS220](https://www.kasasmart.com/us/products/smart-switches/kasa-smart-wifi-light-switch-dimmer-ks220)
