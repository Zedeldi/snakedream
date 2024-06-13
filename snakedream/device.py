"""Provide methods and attributes to handle a Daydream controller."""

import json
import math
from typing import Awaitable, Callable, Type

from bleak import BleakClient, BleakGATTCharacteristic, BleakScanner

from snakedream.models import BaseModel, Buttons, ModelJSONEncoder, Movement, Position


class DaydreamController(BleakClient):
    """Class to provide methods for Daydream controller."""

    DEVICE_NAME = "Daydream controller"
    CHARACTERISTIC_UUID = "00000001-1000-1000-8000-00805f9b34fb"
    DATA_MAPPING: dict[str, int | slice] = {
        "time": slice(0, 2),
        "seq": 1,
        "buttons": 18,
        "orientation": slice(1, 7),
        "accelerometer": slice(6, 12),
        "gyroscope": slice(11, 17),
        "touchpad": slice(16, 19),
    }

    def __init__(self, *args, **kwargs) -> None:
        """Initialise instance of Daydream controller."""
        super().__init__(*args, **kwargs)
        self._data: dict[str, float | BaseModel] = {}
        self._callbacks: list[
            Callable[[BleakGATTCharacteristic, bytearray], Awaitable[None]]
        ] = []

    @classmethod
    async def from_name(
        cls: Type["DaydreamController"], name: str = DEVICE_NAME
    ) -> "DaydreamController":
        """Return controller instance from device name."""
        device = await BleakScanner.find_device_by_name(name)
        if not device:
            raise RuntimeError(f"Cannot find device with name {name}")
        return cls(device)

    async def to_json(self) -> str:
        """Return JSON string of current data."""
        return json.dumps(self._data, cls=ModelJSONEncoder)

    async def start(self) -> None:
        """Start listening for GATT notifications for characteristic."""
        characteristic = self.services.get_characteristic(self.CHARACTERISTIC_UUID)
        await self.start_notify(characteristic, self.callback)

    async def register_callback(
        self, callback: Callable[[BleakGATTCharacteristic, bytearray], Awaitable[None]]
    ) -> None:
        """Register callback to be executed on notification."""
        self._callbacks.append(callback)

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Define callback for characteristic notifications."""
        self._data = await self.parse_data(data)
        self.__dict__.update(self._data)
        for callback in self._callbacks:
            await callback(sender, data)

    async def parse_data(self, data: bytearray) -> dict[str, float | BaseModel]:
        """Return dictionary of parsed data."""
        time = self.calculate_time(data[self.DATA_MAPPING["time"]])
        seq = self.calculate_seq(data[self.DATA_MAPPING["seq"]])

        button_data = self.calculate_buttons(data[self.DATA_MAPPING["buttons"]])
        buttons = Buttons(**button_data)

        orientation_data = self.calculate_orientation(
            data[self.DATA_MAPPING["orientation"]]
        )
        orientation = Movement(*orientation_data)

        accelerometer_data = self.calculate_accelerometer(
            data[self.DATA_MAPPING["accelerometer"]]
        )
        accelerometer = Movement(*accelerometer_data)

        gyroscope_data = self.calculate_gyroscope(data[self.DATA_MAPPING["gyroscope"]])
        gyroscope = Movement(*gyroscope_data)

        touchpad_data = self.calculate_touchpad(data[self.DATA_MAPPING["touchpad"]])
        touchpad = Position(*touchpad_data)

        return {
            "time": time,
            "seq": seq,
            "buttons": buttons,
            "orientation": orientation,
            "accelerometer": accelerometer,
            "gyroscope": gyroscope,
            "touchpad": touchpad,
        }

    @staticmethod
    def calculate_time(data: bytearray) -> float:
        """Calculate time value."""
        return (data[0] & 0xFF) << 1 | (data[1] & 0x80) >> 7

    @staticmethod
    def calculate_seq(value: int) -> float:
        """Calculate seq value."""
        return (value & 0x7C) >> 2

    @staticmethod
    def calculate_buttons(value: int) -> dict[str, bool]:
        return {
            "click": (value & 0x1) > 0,
            "app": (value & 0x4) > 0,
            "home": (value & 0x2) > 0,
            "volume_down": (value & 0x8) > 0,
            "volume_up": (value & 0x10) > 0,
        }

    @staticmethod
    def calculate_orientation(data: bytearray) -> tuple[float, float, float]:
        """Calculate orientation values."""
        values = [
            (data[0] & 0x03) << 11 | (data[1] & 0xFF) << 3 | (data[2] & 0x80) >> 5,
            (data[2] & 0x1F) << 8 | (data[3] & 0xFF),
            (data[4] & 0xFF) << 5 | (data[5] & 0xF8) >> 3,
        ]
        for idx, value in enumerate(values):
            value = (value << 19) >> 19
            value *= 2 * math.pi / 4095.0
            values[idx] = value
        return tuple(values)

    @staticmethod
    def calculate_accelerometer(data: bytearray) -> tuple[float, float, float]:
        """Calculate accelerometer values."""
        values = [
            (data[0] & 0x07) << 10 | (data[1] & 0xFF) << 2 | (data[2] & 0xC0) >> 6,
            (data[2] & 0x3F) << 7 | (data[3] & 0xFE) >> 1,
            (data[3] & 0x01) << 12 | (data[4] & 0xFF) << 4 | (data[5] & 0xF0) >> 4,
        ]
        for idx, value in enumerate(values):
            value = (value << 19) >> 19
            value *= 8 * 9.8 / 4095.0
            values[idx] = value
        return tuple(values)

    @staticmethod
    def calculate_gyroscope(data: bytearray) -> tuple[float, float, float]:
        """Calculate gyroscope values."""
        values = [
            (data[0] & 0x0F) << 9 | (data[1] & 0xFF) << 1 | (data[2] & 0x80) >> 7,
            (data[2] & 0x7F) << 6 | (data[3] & 0xFC) >> 2,
            (data[3] & 0x03) << 11 | (data[4] & 0xFF) << 3 | (data[5] & 0xE0) >> 5,
        ]
        for idx, value in enumerate(values):
            value = (value << 19) >> 19
            value *= 2048 / 180 * math.pi / 4095.0
            values[idx] = value
        return tuple(values)

    @staticmethod
    def calculate_touchpad(data: bytearray) -> tuple[float, float]:
        """Calculate touchpad values."""
        return (
            ((data[0] & 0x1F) << 3 | (data[1] & 0xE0) >> 5) / 255.0,
            ((data[1] & 0x1F) << 3 | (data[2] & 0xE0) >> 5) / 255.0,
        )
