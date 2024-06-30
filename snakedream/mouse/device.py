"""Handle virtual mouse device."""

from collections.abc import Iterable
from typing import Optional

import uinput

from snakedream.device import DaydreamController
from snakedream.mouse.base import BaseMouse, Button, InputEvent, UInputEvent


class UInputMouse(BaseMouse, uinput.Device):
    """UInput implementation of mouse support."""

    _BUTTONS = {
        Button.LEFT: uinput.BTN_LEFT,
        Button.RIGHT: uinput.BTN_RIGHT,
        Button.MIDDLE: uinput.BTN_MIDDLE,
    }

    def __init__(
        self,
        controller: DaydreamController,
        events: Iterable[UInputEvent] = [
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
        super().__init__(controller, events=events, name=name, *args, **kwargs)

    async def move(self, x: int, y: int) -> None:
        """Move mouse to specified location."""
        self.emit(uinput.REL_X, x)
        self.emit(uinput.REL_Y, y)

    async def scroll(self, value: int) -> None:
        """Scroll view by specified value."""
        self.emit(uinput.REL_WHEEL, value)

    async def click(
        self, button: InputEvent = uinput.BTN_LEFT, value: Optional[int] = None
    ) -> None:
        """Click specified mouse button."""
        if value is not None:
            self.emit(button, value)
            return
        self.emit(button, 1)
        self.emit(button, 0)
