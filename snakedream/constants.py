"""Constants and definitions for Daydream controller."""

import math

from snakedream.models import (
    Buttons,
    ByteDefinition,
    ModelDefinition,
    Movement,
    Position,
)

TIME_MODEL = ModelDefinition(
    name="time",
    model=int,
    data=ByteDefinition(index=slice(0, 2), bitmask=(0xFF, 0x80), shift=(1, -7)),
)

SEQUENCE_MODEL = ModelDefinition(
    name="sequence",
    model=int,
    data=ByteDefinition(index=1, bitmask=0x7C, shift=-2),
)

BUTTONS_MODEL = ModelDefinition(
    name="buttons",
    model=Buttons,
    data={
        "click": ByteDefinition(
            index=18,
            bitmask=0x1,
            post_process=lambda value: value > 0,
        ),
        "home": ByteDefinition(
            index=18,
            bitmask=0x2,
            post_process=lambda value: value > 0,
        ),
        "app": ByteDefinition(
            index=18,
            bitmask=0x4,
            post_process=lambda value: value > 0,
        ),
        "volume_down": ByteDefinition(
            index=18,
            bitmask=0x8,
            post_process=lambda value: value > 0,
        ),
        "volume_up": ByteDefinition(
            index=18,
            bitmask=0x10,
            post_process=lambda value: value > 0,
        ),
    },
)

ORIENTATION_MODEL = ModelDefinition(
    name="orientation",
    model=Movement,
    data={
        "x": ByteDefinition(
            index=slice(1, 4),
            bitmask=(0x03, 0xFF, 0xE0),
            shift=(11, 3, -5),
            extend=True,
            post_process=lambda value: value * (2 * math.pi / 4095.0),
        ),
        "y": ByteDefinition(
            index=slice(3, 5),
            bitmask=(0x1F, 0xFF),
            shift=(8, None),
            extend=True,
            post_process=lambda value: value * (2 * math.pi / 4095.0),
        ),
        "z": ByteDefinition(
            index=slice(5, 7),
            bitmask=(0xFF, 0xF8),
            shift=(5, -3),
            extend=True,
            post_process=lambda value: value * (2 * math.pi / 4095.0),
        ),
    },
)

ACCELEROMETER_MODEL = ModelDefinition(
    name="accelerometer",
    model=Movement,
    data={
        "x": ByteDefinition(
            index=slice(6, 9),
            bitmask=(0x07, 0xFF, 0xC0),
            shift=(10, 2, -6),
            extend=True,
            post_process=lambda value: value * (8 * 9.8 / 4095.0),
        ),
        "y": ByteDefinition(
            index=slice(8, 10),
            bitmask=(0x3F, 0xFE),
            shift=(7, -1),
            extend=True,
            post_process=lambda value: value * (8 * 9.8 / 4095.0),
        ),
        "z": ByteDefinition(
            index=slice(9, 12),
            bitmask=(0x01, 0xFF, 0xF0),
            shift=(12, 4, -4),
            extend=True,
            post_process=lambda value: value * (8 * 9.8 / 4095.0),
        ),
    },
)

GYROSCOPE_MODEL = ModelDefinition(
    name="gyroscope",
    model=Movement,
    data={
        "x": ByteDefinition(
            index=slice(11, 14),
            bitmask=(0x0F, 0xFF, 0x80),
            shift=(9, 1, -7),
            extend=True,
            post_process=lambda value: value * (2048 / 180 * math.pi / 4095.0),
        ),
        "y": ByteDefinition(
            index=slice(13, 15),
            bitmask=(0x7F, 0xFC),
            shift=(6, -2),
            extend=True,
            post_process=lambda value: value * (2048 / 180 * math.pi / 4095.0),
        ),
        "z": ByteDefinition(
            index=slice(14, 17),
            bitmask=(0x03, 0xFF, 0xE0),
            shift=(11, 3, -5),
            extend=True,
            post_process=lambda value: value * (2048 / 180 * math.pi / 4095.0),
        ),
    },
)

TOUCHPAD_MODEL = ModelDefinition(
    name="touchpad",
    model=Position,
    data={
        "x": ByteDefinition(
            index=slice(16, 18),
            bitmask=(0x1F, 0xE0),
            shift=(3, -5),
            post_process=lambda value: value / 255.0,
        ),
        "y": ByteDefinition(
            index=slice(17, 19),
            bitmask=(0x1F, 0xE0),
            shift=(3, -5),
            post_process=lambda value: value / 255.0,
        ),
    },
)
