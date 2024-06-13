"""Provide main entry point for snakedream."""

import asyncio
import sys
from pprint import pprint
from typing import NoReturn

from snakedream.device import DaydreamController
from snakedream.mouse import Mouse


async def dump_json(interval: float = 1.0) -> NoReturn:
    """Connect to device and dump controller state every interval."""
    try:
        controller = await DaydreamController.from_name()
        mouse = Mouse(controller)
    except RuntimeError:
        print("Device not found. Please check it is powered on.")
        print("Try pressing the Home button or charging the device.")
        sys.exit(1)
    async with controller:
        await controller.start()
        await controller.register_callback(mouse.callback)
        while True:
            await asyncio.sleep(interval)
            pprint(await controller.to_json())


def main() -> NoReturn:
    """Start asyncio loop for main entry point."""
    asyncio.run(dump_json())


if __name__ == "__main__":
    main()
