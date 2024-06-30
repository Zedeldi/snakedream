"""Provide methods and attributes to handle a Daydream controller."""

import json
from collections.abc import Awaitable, Callable

from bleak import BleakClient, BleakGATTCharacteristic, BleakScanner

from snakedream.constants import (
    ACCELEROMETER_MODEL,
    BUTTONS_MODEL,
    GYROSCOPE_MODEL,
    ORIENTATION_MODEL,
    SEQUENCE_MODEL,
    TIME_MODEL,
    TOUCHPAD_MODEL,
)
from snakedream.models import BaseModel, ModelJSONEncoder


class DaydreamController(BleakClient):
    """
    Class to provide methods for Daydream controller.

    See https://stackoverflow.com/a/40753551 for more information.
    """

    DEVICE_NAME = "Daydream controller"
    SERVICE_UUID = "0000fe55-0000-1000-8000-00805f9b34fb"
    CHARACTERISTIC_UUID = "00000001-1000-1000-8000-00805f9b34fb"
    MODEL_DEFINITIONS = [
        ACCELEROMETER_MODEL,
        BUTTONS_MODEL,
        GYROSCOPE_MODEL,
        ORIENTATION_MODEL,
        SEQUENCE_MODEL,
        TIME_MODEL,
        TOUCHPAD_MODEL,
    ]

    def __init__(self, *args, **kwargs) -> None:
        """Initialise instance of Daydream controller."""
        super().__init__(*args, **kwargs)
        self._data: dict[str, float | BaseModel] = {}
        self._callbacks: list[
            Callable[[BleakGATTCharacteristic, bytearray], Awaitable[None]]
        ] = []

    @classmethod
    async def from_name(
        cls: type["DaydreamController"], name: str = DEVICE_NAME, timeout: float = 10
    ) -> "DaydreamController":
        """Return controller instance from device name."""
        device = await BleakScanner.find_device_by_name(name, timeout)
        if not device:
            raise RuntimeError(f"Cannot find device with name {name}")
        return cls(device)

    async def to_json(self) -> str:
        """Return JSON string of current data."""
        return json.dumps(self._data, cls=ModelJSONEncoder)

    async def start(self) -> None:
        """Start listening for GATT notifications for characteristic."""
        service = self.services.get_service(self.SERVICE_UUID)
        characteristic = service.get_characteristic(self.CHARACTERISTIC_UUID)
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
        return {model.name: model.from_bytes(data) for model in self.MODEL_DEFINITIONS}
