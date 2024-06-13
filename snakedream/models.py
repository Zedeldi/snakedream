"""Collection of dataclasses to model components of a Daydream controller."""

from abc import ABC
from dataclasses import asdict, dataclass, is_dataclass
from json import JSONEncoder
from typing import Any


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
