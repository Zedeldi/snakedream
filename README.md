# snakedream

[![GitHub license](https://img.shields.io/github/license/Zedeldi/snakedream?style=flat-square)](https://github.com/Zedeldi/snakedream/blob/master/LICENSE) [![GitHub last commit](https://img.shields.io/github/last-commit/Zedeldi/snakedream?style=flat-square)](https://github.com/Zedeldi/snakedream/commits) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

Python interface for a Daydream controller.

## Description

Provides a Python interface to a Daydream controller, by subscribing to GATT notifications for a characteristic (UUID: `00000001-1000-1000-8000-00805f9b34fb`).

The `DaydreamController` class can be found in `snakedream.device`.

Byte definitions to interpret returned data are found in `snakedream.constants` (see [this Stack Overflow answer](https://stackoverflow.com/a/40753551) for more information).

Data models to represent returned data and handle byte definition calculations are found in `snakedream.models`.
Please note, `ctypes.c_int32` is used when performing bitwise shifts to intentionally allow overflows.

`snakedream.mouse` and `snakedream.graph` contain callbacks for mouse and graph support, respectively.
Mouse control is currently supported via two backends: `uinput`, creating a virtual mouse device, and `PyAutoGUI`, which controls the cursor directly.
`uinput` is supported on Linux, both Xorg and Wayland.
`PyAutoGUI` supports all known platforms, except Wayland on Linux.
To manually specify which backend is used, set `snakedream.config.MOUSE_BACKEND` to the desired value.

### Callbacks

`snakedream.base` provides an abstract base class, `BaseCallback`, to provide a parent for subclasses which utilise data from the Daydream controller.

To create a new callback class, create a subclass of `BaseCallback`, which implements the `callback` async method, which accepts the following arguments: `sender: BleakGATTCharacteristic, data: bytearray`.
To register the callback for the controller, call the `start` method of the instance.

When new data is available from the controller, the callback will be called.
The subclass will also have a `controller` attribute - passed at instantiation - which can be accessed directly within the callback.

For example:

```py
class ExampleCallback(BaseCallback):
    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        if self.controller.buttons.click:
            print("Button clicked!")

callback = ExampleCallback(controller)
await callback.start()
```

## Installation

### PyPI

1. Install project: `pip install snakedream`
2. Run: `snakedream`

### Source

Alternatively, after cloning the repository with:
`git clone https://github.com/Zedeldi/snakedream.git`

#### Build

1. Install project: `pip install .`
2. Run: `snakedream`

#### Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python -m snakedream`

## Usage

By default, with no arguments, `snakedream` will control the mouse with the gyroscope, using the appropriate backend for the host platform.
Additionally, `snakedream` can output the controller state as JSON or to a graph with `matplotlib`.

For more information, see `snakedream --help`.

## Libraries

- [Bleak](https://pypi.org/project/bleak/) - BLE Client
- [Matplotlib](https://pypi.org/project/matplotlib/) - Graph support
- [python-uinput](https://pypi.org/project/python-uinput/) - Mouse support (device backend)
- [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) - Mouse support (GUI backend)

## Credits

 - [daydream-controller.js](https://github.com/mrdoob/daydream-controller.js) - WebBluetooth Daydream Controller
 - [Forrest Porter](https://stackoverflow.com/a/40753551) - Stack Overflow answer for byte definitions

## License

`snakedream` is licensed under the [MIT Licence](https://mit-license.org/) for everyone to use, modify and share freely.

This project is distributed in the hope that it will be useful, but without any warranty.

## Donate

If you found this project useful, please consider donating. Any amount is greatly appreciated! Thank you :smiley:

[![PayPal](https://www.paypalobjects.com/webstatic/mktg/Logo/pp-logo-150px.png)](https://paypal.me/ZackDidcott)
