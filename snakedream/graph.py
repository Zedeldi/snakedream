"""Draw events on graphs with matplotlib."""

import time

import matplotlib.pyplot as plt
from bleak import BleakGATTCharacteristic

from snakedream.base import Callback
from snakedream.device import DaydreamController


class InputGraph(Callback):
    """Handle graph methods and attributes."""

    def __init__(self, controller: DaydreamController, fps: int = 120) -> None:
        """Initialise graphs."""
        super().__init__(controller)
        self.fps = fps
        self._last_update = time.time()
        self.figure = plt.figure()
        self.touchpad = self.figure.add_subplot(1, 1, 1)

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Handle callback method to plot graph on GATT notification."""
        if time.time() - self._last_update > 1 / self.fps:
            self.plot_touchpad(self.controller.touchpad.x, self.controller.touchpad.y)
            plt.draw()
            plt.pause(0.0001)
            self._last_update = time.time()

    def plot_touchpad(self, x: float, y: float) -> None:
        self.touchpad.cla()
        self.touchpad.set_xlim(-1, 1)
        self.touchpad.set_ylim(-1, 1)

        if x != 0 or y != 0:
            x = self.controller.touchpad.x * 2 - 1
            y = self.controller.touchpad.y * 2 - 1
            point = plt.Circle((x, -y), radius=0.1, color="blue")
            self.touchpad.add_patch(point)
