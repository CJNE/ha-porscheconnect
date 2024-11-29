# Porsche Connect

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacs_badge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

This custom component for [home assistant](https://home-assistant.io/) will let you connect your Porsche Connect enabled
car to Home Assistant.
It does not work with Porsche Car Connect.
Porsche Connect is available for the following Porsche models:

- Boxster & Cayman (718)
- 911 (from 992)
- Taycan
- Panamera (from 2021, G2 PA)
- Macan (EV, from 2024)
- Cayenne (from 2017, E3)

You can also take a look here, select your model and see if your model has support for Porsche Connect:
https://connect-store.porsche.com/

A Porsche Connect subscription also needs to be active.

Feature requests and ideas are welcome, use the Discussions board for that, thanks!

**This component will set up the following platforms.**

| Platform         | Description                           |
| ---------------- | ------------------------------------- |
| `binary_sensor`  | Show something `True` or `False`.     |
| `button`         | Trigger some action.                  |
| `device_tracker` | Show your vehicles location.          |
| `image`          | Show images of your vehicle.          |
| `lock`           | Control the lock of your vehicle.     |
| `number`         | Sends a number value to your vehicle. |
| `sensor`         | Show info from Porsche Connect API.   |
| `switch`         | Switch something `On` or `Off`.       |

## HACS Installation

1. Search for porscheconnect in HACS
2. Install

## Manual Installation

1. Using the tool of choice to open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `porscheconnect`.
4. Download _all_ the files from the `custom_components/porscheconnect/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Porsche Connect"


## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](https://github.com/CJNE/ha-porscheconnect/blob/main/CONTRIBUTING.md)

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/cjne.coffee
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/CJNE/ha-porscheconnect.svg?style=for-the-badge
[commits]: https://github.com/CJNE/ha-porscheconnect/commits/main
[hacs]: https://hacs.xyz
[hacs_badge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/CJNE/ha-porscheconnect.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40CJNE-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/CJNE/ha-porscheconnect.svg?style=for-the-badge
[releases]: https://github.com/CJNE/ha-porscheconnect/releases
[user_profile]: https://github.com/CJNE
