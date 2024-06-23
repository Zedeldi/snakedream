"""Collection of abstract base classes."""

from abc import ABC, abstractmethod

from bleak import BleakGATTCharacteristic

from snakedream.device import DaydreamController


class BaseCallback(ABC):
    """Base class to support registering a callback for a Daydream controller."""

    def __init__(self, controller: DaydreamController, *args, **kwargs) -> None:
        """Initialise instance with controller attribute."""
        self.controller = controller
        super().__init__(*args, **kwargs)

    async def start(self) -> None:
        """Register mouse callback for controller."""
        await self.controller.register_callback(self.callback)

    @abstractmethod
    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Abstract method for controller callback to be implemented by subclass."""
        ...
