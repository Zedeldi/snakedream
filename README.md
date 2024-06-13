# snakedream

[![GitHub license](https://img.shields.io/github/license/Zedeldi/snakedream?style=flat-square)](https://github.com/Zedeldi/snakedream/blob/master/LICENSE) [![GitHub last commit](https://img.shields.io/github/last-commit/Zedeldi/snakedream?style=flat-square)](https://github.com/Zedeldi/snakedream/commits) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

Python interface for a Daydream controller.

## Description

Provides a Python interface to a Daydream controller, by subscribing to GATT notifications for a characteristic (UUID: `00000001-1000-1000-8000-00805f9b34fb`).

## Installation

After cloning the repository with: `git clone https://github.com/Zedeldi/snakedream.git`

### Build

1. Install project: `pip install .`
2. Run: `snakedream-mouse`

### Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python -m snakedream`

#### Libraries:

- [Bleak](https://pypi.org/project/bleak/) - BLE Client

## Credits

 - [daydream-controller.js](https://github.com/mrdoob/daydream-controller.js) - WebBluetooth Daydream Controller

## License

`snakedream` is licensed under the [MIT Licence](https://mit-license.org/) for everyone to use, modify and share freely.

This project is distributed in the hope that it will be useful, but without any warranty.

## Donate

If you found this project useful, please consider donating. Any amount is greatly appreciated! Thank you :smiley:

[![PayPal](https://www.paypalobjects.com/webstatic/mktg/Logo/pp-logo-150px.png)](https://paypal.me/ZackDidcott)
