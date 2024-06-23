"""Provide main entry point for snakedream."""

import asyncio
import json
import sys
from pprint import pprint
from typing import NoReturn

from snakedream.device import DaydreamController
from snakedream.graph import InputGraph
from snakedream.mouse import GyroscopeMouse


async def control_mouse(debug: bool = False, interval: float = 1.0) -> NoReturn:
    """
    Connect to device and control mouse.

    If debug is True, periodically output state of controller as JSON
    and display graphs.
    """
    try:
        controller = await DaydreamController.from_name()
        mouse = GyroscopeMouse(controller)
        graph = InputGraph(controller)
    except RuntimeError:
        print("Device not found. Please check it is powered on.")
        print("Try pressing the Home button or charging the device.")
        sys.exit(1)
    async with controller:
        await controller.start()
        await mouse.start()
        if debug:
            await graph.start()
        while True:
            await asyncio.sleep(interval)
            if debug:
                pprint(json.loads(await controller.to_json()))


def main() -> NoReturn:
    """Start asyncio loop for main entry point."""
    asyncio.run(control_mouse())


if __name__ == "__main__":
    main()
