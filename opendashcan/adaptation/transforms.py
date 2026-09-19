"""Unit / scale helpers — no invented CAN encodings."""

from __future__ import annotations


def mph_to_kph(mph: float) -> float:
    return mph * 1.609344


def kph_to_mph(kph: float) -> float:
    return kph / 1.609344


def celsius_to_fahrenheit(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0


def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32.0) * 5.0 / 9.0


def apply_scale_offset(raw: float, *, scale: float, offset: float = 0.0) -> float:
    """Generic DBC-style physical = raw * scale + offset."""
    return raw * scale + offset


def invert_scale_offset(physical: float, *, scale: float, offset: float = 0.0) -> float:
    if scale == 0:
        raise ValueError("scale must be non-zero")
    return (physical - offset) / scale
