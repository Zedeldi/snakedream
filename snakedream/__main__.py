"""Provide main entry point for snakedream."""

import asyncio
import json
import sys
from argparse import ArgumentParser
from pprint import pprint
from typing import NoReturn

from snakedream.device import DaydreamController
from snakedream.graph import InputGraph
from snakedream.mouse import GyroscopeMouse, TouchpadMouse


def get_parser() -> ArgumentParser:
    """Return ArgumentParser instance for command-line argument parsing."""
    parser = ArgumentParser(
        prog="snakedream",
        description="Python interface for a Daydream controller",
        epilog="Copyright (C) 2024 Zack Didcott",
    )

    parser.add_argument(
        "--graph",
        "-g",
        action="store_true",
        help="display graphs for device information",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=1,
        help="interval between printing device state",
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="output device information in JSON"
    )
    parser.add_argument(
        "--mouse",
        "-m",
        type=str,
        default="gyroscope",
        choices=["gyroscope", "touchpad", "disable"],
        help="enable mouse control",
    )
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        default=DaydreamController.DEVICE_NAME,
        help="Bluetooth device name for Daydream controller",
    )
    parser.add_argument(
        "--sensitivity",
        "-s",
        type=int,
        default=8,
        help="mouse sensitivity",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=float,
        default=10,
        help="timeout for Bluetooth device (negative values wait forever)",
    )

    return parser


async def _main() -> NoReturn:
    """Connect to device and start specified callbacks."""
    parser = get_parser()
    args = parser.parse_args()
    timeout = float("inf") if args.timeout < 0 else args.timeout
    try:
        print(f"Attempting to connect to '{args.name}'...")
        controller = await DaydreamController.from_name(args.name, timeout)
    except RuntimeError:
        print(f"Could not connect to '{args.name}'. Please check it is powered on.")
        print("Try pressing the Home button or charging the device.")
        sys.exit(1)
    async with controller:
        await controller.start()
        if args.mouse != "disable":
            if args.mouse == "gyroscope":
                mouse = GyroscopeMouse(controller, sensitivity=args.sensitivity)
            elif args.mouse == "touchpad":
                mouse = TouchpadMouse(controller, sensitivity=args.sensitivity)
            await mouse.start()
        if args.graph:
            graph = InputGraph(controller)
            await graph.start()
        while True:
            await asyncio.sleep(args.interval)
            if args.json:
                pprint(json.loads(await controller.to_json()))


def main() -> NoReturn:
    """Start asyncio loop for main entry point."""
    asyncio.run(_main())


if __name__ == "__main__":
    main()
