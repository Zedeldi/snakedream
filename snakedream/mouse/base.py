"""Handle base mouse support."""

import sys
from abc import abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any, Literal, Optional

from bleak import BleakGATTCharacteristic

from snakedream import config
from snakedream.base import BaseCallback
from snakedream.device import DaydreamController
from snakedream.models import Buttons

type UInputEvent = tuple[int, int]
type InputEvent = UInputEvent | str


class Button(StrEnum):
    """String enumeration for supported buttons."""

    LEFT = auto()
    RIGHT = auto()
    MIDDLE = auto()


@dataclass
class ButtonMapping:
    """Dataclass to associate action and arguments with button name."""

    button: str
    action: str
    args: Sequence[Any]


class BaseMouse(BaseCallback):
    """Subclass of uinput device to handle mouse methods."""

    _BUTTONS: dict[Button, InputEvent]

    def __init__(
        self,
        controller: DaydreamController,
        sensitivity: int = 8,
        buttons: Iterable[ButtonMapping] = [
            ButtonMapping(button="click", action="click", args=(Button.LEFT,)),
            ButtonMapping(button="app", action="click", args=(Button.RIGHT,)),
            ButtonMapping(button="home", action="click", args=(Button.MIDDLE,)),
            ButtonMapping(button="volume_up", action="scroll", args=(1,)),
            ButtonMapping(button="volume_down", action="scroll", args=(-1,)),
        ],
        *args,
        **kwargs,
    ) -> None:
        """Initialise instance of mouse device."""
        super().__init__(controller, *args, **kwargs)
        self.sensitivity = sensitivity
        self.buttons = buttons
        self._state: dict[str, bool] = {}
        if not hasattr(self, "_BUTTONS"):
            raise NotImplementedError("Class attribute '_BUTTONS' is not defined")

    @abstractmethod
    async def move(self, x: int, y: int) -> None:
        """Move mouse to specified location."""
        ...

    @abstractmethod
    async def scroll(self, value: int) -> None:
        """Scroll view by specified value."""
        ...

    @abstractmethod
    async def click(self, button: InputEvent, value: Optional[int] = None) -> None:
        """Click specified mouse button."""
        ...

    @abstractmethod
    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Define callback to handle mouse events."""
        await self.handle_buttons(self.controller.buttons)

    async def handle_buttons(self, buttons: Buttons) -> None:
        """Handle button input according to current button mapping."""
        for mapping in self.buttons:
            if mapping.action == "click":
                state = getattr(buttons, mapping.button)
                # To avoid repeatedly clicking and allow dragging
                if state != self._state.get(mapping.button):
                    button = self._BUTTONS[mapping.args[0]]
                    await self.click(button, value=int(state))
                self._state[mapping.button] = state
            elif getattr(buttons, mapping.button):
                await getattr(self, mapping.action)(*mapping.args)

    def _calculate_movement(self, x: float, y: float) -> tuple[int, int]:
        """Return tuple of calculated x, y adjusted for sensitivity."""
        return round(x * self.sensitivity), round(y * self.sensitivity)


class MouseFactory:
    """Factory class to provide appropriate mouse implementation for platform."""

    WINDOWS = "win32"
    LINUX = "linux"
    MACOS = "darwin"

    @staticmethod
    def _get_uinput() -> type[BaseMouse]:
        """Return UInput mouse implementation class."""
        from snakedream.mouse.device import UInputMouse

        return UInputMouse

    @staticmethod
    def _get_pyautogui() -> type[BaseMouse]:
        """Return PyAutoGUI mouse implementation class."""
        from snakedream.mouse.gui import PyAutoGUIMouse

        return PyAutoGUIMouse

    @staticmethod
    def _get_default() -> type[BaseMouse]:
        """Return appropriate mouse implementation class for platform."""
        platform = sys.platform

        if platform == MouseFactory.LINUX:
            return MouseFactory._get_uinput()

        return MouseFactory._get_pyautogui()

    @staticmethod
    def get(backend: Literal["default", "uinput", "pyautogui"] = "default"):
        """Return specified mouse implementation or default for platform."""
        if backend == "default":
            return MouseFactory._get_default()
        elif backend == "uinput":
            return MouseFactory._get_uinput()
        elif backend == "pyautogui":
            return MouseFactory._get_pyautogui()
        else:
            raise ValueError(
                f"Invalid backend '{backend}'. Must be 'default', 'uinput' or 'pyautogui'"
            )


class TouchpadMouse(MouseFactory.get(config.MOUSE_BACKEND)):
    """Mouse subclass to use Daydream controller touchpad for mouse control."""

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Define callback to handle mouse events."""
        await super().callback(sender, data)

        if self.controller.touchpad.x == 0 and self.controller.touchpad.y == 0:
            return None
        # Convert |_ to -|- axes
        x = self.controller.touchpad.x * 2 - 1
        y = self.controller.touchpad.y * 2 - 1
        await self.move(*self._calculate_movement(x, y))


class GyroscopeMouse(MouseFactory.get(config.MOUSE_BACKEND)):
    """Mouse subclass to use Daydream controller gyroscope for mouse control."""

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Define callback to handle mouse events."""
        await super().callback(sender, data)

        # Gyroscope attributes refer to axes of rotation, hence the
        # y-coordinate relates to rotation about the x-axis.
        y, x = -self.controller.gyroscope.x, -self.controller.gyroscope.y
        await self.move(*self._calculate_movement(x, y))
