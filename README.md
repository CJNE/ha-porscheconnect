# Porsche Connect

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

This custom component for [home assistant](https://home-assistant.io/) will let you connect your Porsche Connect enabled
car to Home Assistant. 
It does not work with Porsche Car Connect.
Porsche Connect is available for the following Porsche models:

* Taycan
* 911 (from 992)
* Cayenne (from 2017, E3)
* Panamera (from 2021, G2 PA)

A Porsche Connect subscription alse needs to be active.

It is currently in an early stage, more info will be added as the project develops. Feature
requests and ideas are welcome, use the issue tracker for that, thanks!

**This component will set up the following platforms.**

| Platform         | Description                         |
| ---------------- | ----------------------------------- |
| `binary_sensor`  | Show something `True` or `False`.   |
| `sensor`         | Show info from Porsche Connect API. |
| `switch`         | Switch something `True` or `False`. |
| `device_tracker` | Show your vehicles location         |

## HACS Installation

1. Add this repository to "Custom repositories"
2. Add and search for porscheconnect in HACS
3. Install

## Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `porscheconnect`.
4. Download _all_ the files from the `custom_components/porscheconnect/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Porsche Connect"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/porscheconnect/translations/en.json
custom_components/porscheconnect/translations/fr.json
custom_components/porscheconnect/translations/nb.json
custom_components/porscheconnect/translations/sensor.en.json
custom_components/porscheconnect/translations/sensor.fr.json
custom_components/porscheconnect/translations/sensor.nb.json
custom_components/porscheconnect/translations/sensor.nb.json
custom_components/porscheconnect/__init__.py
custom_components/porscheconnect/api.py
custom_components/porscheconnect/binary_sensor.py
custom_components/porscheconnect/config_flow.py
custom_components/porscheconnect/const.py
custom_components/porscheconnect/manifest.json
custom_components/porscheconnect/sensor.py
custom_components/porscheconnect/switch.py
```

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/cjne.coffee
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/CJNE/ha-porscheconnect.svg?style=for-the-badge
[commits]: https://github.com/CJNE/ha-porscheconnect/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
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
