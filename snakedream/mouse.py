"""Handle mouse movements and actions."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import uinput
from bleak import BleakGATTCharacteristic

from snakedream.base import BaseCallback
from snakedream.device import DaydreamController
from snakedream.models import Buttons

type InputEvent = tuple[int, int]


@dataclass
class ButtonMapping:
    """Dataclass to associate action and arguments with button name."""

    button: str
    action: str
    args: Iterable[Any]


class BaseMouse(BaseCallback, uinput.Device):
    """Subclass of uinput device to handle mouse methods."""

    def __init__(
        self,
        controller: DaydreamController,
        sensitivity: int = 8,
        buttons: Iterable[ButtonMapping] = [
            ButtonMapping(button="click", action="click", args=(uinput.BTN_LEFT,)),
            ButtonMapping(button="app", action="click", args=(uinput.BTN_RIGHT,)),
            ButtonMapping(button="home", action="click", args=(uinput.BTN_MIDDLE,)),
            ButtonMapping(button="volume_up", action="scroll", args=(1,)),
            ButtonMapping(button="volume_down", action="scroll", args=(-1,)),
        ],
        events: Iterable[InputEvent] = [
            uinput.REL_X,
            uinput.REL_Y,
            uinput.REL_WHEEL,
            uinput.BTN_LEFT,
            uinput.BTN_MIDDLE,
            uinput.BTN_RIGHT,
        ],
        name: str = DaydreamController.DEVICE_NAME,
        *args,
        **kwargs,
    ) -> None:
        """Initialise instance of mouse device."""
        super().__init__(controller, events, name, *args, **kwargs)
        self.sensitivity = sensitivity
        self.buttons = buttons

    async def move(self, x: int, y: int) -> None:
        """Move mouse to specified location."""
        self.emit(uinput.REL_X, x)
        self.emit(uinput.REL_Y, y)

    async def scroll(self, value: int) -> None:
        """Scroll view by specified value."""
        self.emit(uinput.REL_WHEEL, value)

    async def click(self, button: InputEvent = uinput.BTN_LEFT) -> None:
        """Click specified mouse button."""
        self.emit(button, 1)
        self.emit(button, 0)

    async def handle_buttons(self, buttons: Buttons) -> None:
        """Handle button input according to current button mapping."""
        for mapping in self.buttons:
            if getattr(buttons, mapping.button):
                await getattr(self, mapping.action)(*mapping.args)

    def _calculate_movement(self, x: float, y: float) -> tuple[int, int]:
        """Return tuple of calculated x, y adjusted for sensitivity."""
        return round(x * self.sensitivity), round(y * self.sensitivity)


class TouchpadMouse(BaseMouse):
    """Mouse subclass to use Daydream controller touchpad for mouse control."""

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Define callback to handle mouse events."""
        await self.handle_buttons(self.controller.buttons)

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
        await self.handle_buttons(self.controller.buttons)

        # Gyroscope attributes refer to axes of rotation, hence the
        # y-coordinate relates to rotation about the x-axis.
        y, x = -self.controller.gyroscope.x, -self.controller.gyroscope.y
        await self.move(*self._calculate_movement(x, y))
