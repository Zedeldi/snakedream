"""Handle mouse movements and actions."""

from collections.abc import Iterable

import uinput
from bleak import BleakGATTCharacteristic

from snakedream.device import DaydreamController


class Mouse(uinput.Device):
    """Subclass of uinput device to handle mouse methods."""

    def __init__(
        self,
        controller: DaydreamController,
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
        super().__init__(events, name, *args, **kwargs)
        self.controller = controller

    async def move(self, x: int, y: int) -> None:
        """Move mouse to specified location."""
        self.emit(uinput.REL_X, x)
        self.emit(uinput.REL_Y, y)

    async def click(self, button: tuple[int, int] = uinput.BTN_LEFT) -> None:
        """Click specified mouse button."""
        self.emit(button, 1)
        self.emit(button, 0)

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Define callback to handle mouse events."""
        if self.controller.buttons.click:
            await self.click()

        if self.controller.touchpad.x == 0 and self.controller.touchpad.y == 0:
            return None
        # Convert |_ to -|- axes
        x = self.controller.touchpad.x * 2 - 1
        y = self.controller.touchpad.y * 2 - 1
        await self.move(round(x), round(y))
