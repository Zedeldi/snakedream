"""Draw events on graphs with matplotlib."""

import time
from dataclasses import asdict

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.art3d as art3d
from bleak import BleakGATTCharacteristic
from mpl_toolkits.mplot3d import Axes3D

from snakedream.base import BaseCallback
from snakedream.device import DaydreamController


class InputGraph(BaseCallback):
    """Handle graph methods and attributes."""

    PAUSE_INTERVAL = 0.0001

    def __init__(self, controller: DaydreamController, fps: int = 120) -> None:
        """Initialise graphs."""
        super().__init__(controller)
        self.fps = fps
        self._last_update = time.time()
        self.figure = plt.figure()
        self.touchpad = self.figure.add_subplot(2, 2, 1)
        self.orientation: Axes3D = self.figure.add_subplot(2, 2, 2, projection="3d")
        self.buttons = self.figure.add_subplot(2, 2, 3)
        self.figure.tight_layout(pad=2)

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Handle callback method to plot graph on GATT notification."""
        if time.time() - self._last_update > 1 / self.fps:
            self.plot_touchpad(self.controller.touchpad.x, self.controller.touchpad.y)
            self.plot_orientation(
                self.controller.orientation.x,
                self.controller.orientation.y,
                self.controller.orientation.z,
            )
            self.plot_buttons(asdict(self.controller.buttons))
            plt.draw()
            plt.pause(self.PAUSE_INTERVAL)
            self._last_update = time.time()

    def plot_touchpad(self, x: float, y: float) -> None:
        """Clear, configure and plot touchpad graph."""
        self.touchpad.cla()
        self.touchpad.set_title("Touchpad")
        self.touchpad.set_xlim(-1, 1)
        self.touchpad.set_ylim(-1, 1)

        if x != 0 or y != 0:
            x = x * 2 - 1
            y = y * 2 - 1
            point = plt.Circle((x, -y), radius=0.1, color="blue")
            self.touchpad.add_patch(point)

    def plot_orientation(self, x: float, y: float, z: float) -> None:
        """Clear, configure and plot orientation graph."""
        self.orientation.cla()
        self.orientation.set_title("Orientation")
        self.orientation.set_xlim(-3, 3)
        self.orientation.set_ylim(-3, 3)
        self.orientation.set_zlim(-3, 3)

        patch = plt.Circle((x, y), radius=0.5, color="blue")
        self.orientation.add_patch(patch)
        art3d.pathpatch_2d_to_3d(patch, z=z, zdir="z")

    def plot_buttons(self, buttons: dict[str, bool]) -> None:
        """Clear, configure and display button information from dictionary."""
        self.buttons.cla()
        self.buttons.set_title("Buttons")
        self.buttons.set_ylim(0, len(buttons))
        self.buttons.axis("off")

        for idx, button in enumerate(
            sorted(buttons.items(), key=lambda item: item[0], reverse=True)
        ):
            name, state = button
            self.buttons.text(0, idx, f"{name}: {state}")
