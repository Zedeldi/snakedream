"""Handle GUI mouse movements and actions."""

from typing import Optional

import pyautogui

from snakedream.mouse.base import BaseMouse, Button, InputEvent

pyautogui.PAUSE = 0  # Disable lag between mouse movements
pyautogui.FAILSAFE = False  # Prevent raising exception when moving to corners


class PyAutoGUIMouse(BaseMouse):
    """PyAutoGUI implementation of mouse support."""

    _BUTTONS = {Button.LEFT: "left", Button.RIGHT: "right", Button.MIDDLE: "middle"}

    async def move(self, x: int, y: int) -> None:
        """Move mouse to specified location."""
        pyautogui.move(x, y)

    async def scroll(self, value: int) -> None:
        """Scroll view by specified value."""
        pyautogui.scroll(value)

    async def click(
        self, button: InputEvent = "left", value: Optional[int] = None
    ) -> None:
        """Click specified mouse button."""
        if value is not None:
            if value == 1:
                pyautogui.mouseDown(button=button)
            elif value == 0:
                pyautogui.mouseUp(button=button)
            return
        pyautogui.click(button=button)
