"""Collection of dataclasses to model components of a Daydream controller."""

from abc import ABC
from collections.abc import Callable, Sequence
from ctypes import c_int32 as int32
from dataclasses import asdict, dataclass, is_dataclass
from json import JSONEncoder
from typing import Any, Optional


class ModelJSONEncoder(JSONEncoder):
    """JSONEncoder subclass to handle dataclass encoding."""

    def default(self, obj: Any) -> Any:
        """Return dataclasses as dictionary or calls base implementation."""
        if is_dataclass(obj):
            return asdict(obj)
        return super().default(obj)


class BaseModel(ABC):
    """Abstract base class for data models."""


@dataclass
class ByteDefinition(BaseModel):
    """
    Dataclass to represent byte definition with bitmask and shift.

    A negative shift represents a right bitwise shift.
    """

    index: int | slice
    bitmask: int | Sequence[int]
    shift: Optional[int] | Sequence[Optional[int]] = None
    extend: bool = False
    post_process: Optional[Callable[[int], float | bool]] = None

    def __post_init__(self) -> None:
        """Verify passed values are appropriate."""
        if isinstance(self.index, int):
            for value in (self.bitmask, self.shift):
                if isinstance(value, Sequence):
                    raise TypeError(
                        "Bitmask and shift must not be a sequence if index is not a slice"
                    )
        elif isinstance(self.index, slice):
            max_size = (self.index.stop - self.index.start) // (self.index.step or 1)
            for value in (self.bitmask, self.shift):
                if not isinstance(value, Sequence):
                    raise TypeError(
                        "Bitmask and shift must be a sequence if index is a slice"
                    )
                elif len(value) != max_size:
                    raise ValueError(
                        "Bitmask and shift must be a sequence of the same size as index"
                    )
        if self.post_process and not callable(self.post_process):
            raise TypeError("Argument 'post_process' must be callable")

    @staticmethod
    def from_byte(byte: int, bitmask: int, shift: Optional[int] = None) -> int:
        """
        Return calculated value from single byte as int32.

        Equivalent to: (byte & bitmask) [<<|>>] shift
        """
        value = byte & bitmask
        if shift and shift > 0:
            value = int32(value << shift).value
        elif shift and shift < 0:
            value = int32(value >> abs(shift)).value
        return value

    @staticmethod
    def extend_integer(value: int) -> int:
        """Sign extend value to 32-bit signed integer."""
        return value if (value >> 12) == 0 else ~0x1FFF | value

    def from_bytes(self, data: bytes) -> float | bool:
        """Return calculated value from data."""
        # Some type errors are ignored in this method as they will be caught
        # in the post_init method, but mypy does not check this.
        if isinstance(self.index, int):
            value = self.from_byte(data[self.index], self.bitmask, self.shift)  # type: ignore[arg-type]
        else:
            value = 0
            for idx, byte in enumerate(data[self.index]):
                value |= self.from_byte(byte, self.bitmask[idx], self.shift[idx])  # type: ignore[index]
        if self.extend:
            value = self.extend_integer(value)
        return self.post_process(value) if self.post_process else value


@dataclass
class ModelDefinition(BaseModel):
    """Class to represent model definition with associated data."""

    name: str
    model: type
    data: ByteDefinition | dict[str, ByteDefinition]

    def from_bytes(self, data: bytes) -> Any:
        """Return instance of model from data."""
        return (
            self.model(
                **{name: byte.from_bytes(data) for name, byte in self.data.items()}
            )
            if isinstance(self.data, dict)
            else self.model(self.data.from_bytes(data))
        )


@dataclass
class Buttons(BaseModel):
    """Dataclass to represent button states."""

    click: bool
    app: bool
    home: bool
    volume_down: bool
    volume_up: bool


@dataclass
class Position(BaseModel):
    """Dataclass to represent a 2D position for trackpad."""

    x: float
    y: float


@dataclass
class Movement(BaseModel):
    """Dataclass to represent movement from accelerometer, gyroscopes, etc."""

    x: float
    y: float
    z: float
