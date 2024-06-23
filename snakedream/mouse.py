"""Handle mouse movements and actions."""

from collections.abc import Iterable

import uinput
from bleak import BleakGATTCharacteristic

from snakedream.base import Callback
from snakedream.device import DaydreamController


class BaseMouse(Callback, uinput.Device):
    """Subclass of uinput device to handle mouse methods."""

    def __init__(
        self,
        controller: DaydreamController,
        sensitivity: int = 8,
        events: Iterable[tuple[int, int]] = [
            uinput.REL_X,
            uinput.REL_Y,
            uinput.BTN_LEFT,
            uinput.BTN_RIGHT,
        ],
        name: str = DaydreamController.DEVICE_NAME,
        *args,
        **kwargs,
    ) -> None:
        """Initialise instance of mouse device."""
        super().__init__(controller, events, name, *args, **kwargs)
        self.sensitivity = sensitivity

    async def move(self, x: int, y: int) -> None:
        """Move mouse to specified location."""
        self.emit(uinput.REL_X, x)
        self.emit(uinput.REL_Y, y)

    async def click(self, button: tuple[int, int] = uinput.BTN_LEFT) -> None:
        """Click specified mouse button."""
        self.emit(button, 1)
        self.emit(button, 0)

    def _calculate_movement(self, x: float, y: float) -> tuple[int, int]:
        """Return tuple of calculated x, y adjusted for sensitivity."""
        return round(x * self.sensitivity), round(y * self.sensitivity)


class TouchpadMouse(BaseMouse):
    """Mouse subclass to use Daydream controller touchpad for mouse control."""

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Define callback to handle mouse events."""
        if self.controller.buttons.click:
            await self.click()

        if self.controller.touchpad.x == 0 and self.controller.touchpad.y == 0:
            return None
        # Convert |_ to -|- axes
        x = self.controller.touchpad.x * 2 - 1
        y = self.controller.touchpad.y * 2 - 1
        await self.move(*self._calculate_movement(x, y))


class GyroscopeMouse(BaseMouse):
    """Mouse subclass to use Daydream controller gyroscope for mouse control."""

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Define callback to handle mouse events."""
        if self.controller.buttons.click:
            await self.click()

        # Gyroscope attributes refer to axes of rotation, hence the
        # y-coordinate relates to rotation about the x-axis.
        y, x = -self.controller.gyroscope.x, -self.controller.gyroscope.y
        await self.move(*self._calculate_movement(x, y))
