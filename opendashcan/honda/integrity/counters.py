"""Documented Honda 2-bit rolling counter helper (opendbc) with evidence."""

from __future__ import annotations

from dataclasses import dataclass

from opendashcan.protocols.honda.checksum import honda_set_counter

COUNTER_2BIT_PLATFORMS = frozenset(
    {
        "honda:civic:10",
        "honda:civic:11",
        "honda:accord:10",
        "honda:crv:5",
    }
)

EVIDENCE = {
    "algorithm_id": "honda_2bit_v1",
    "source": "commaai/opendbc Honda DBC COUNTER bits + safety honda helpers",
    "url": "https://github.com/commaai/opendbc",
    "license": "MIT",
    "confidence": "DOCUMENTED",
    "notes": (
        "2-bit counter at DBC bits 61-60 (high nibble of last byte) on many PCM messages. "
        "Not claimed for Civic 8."
    ),
}


@dataclass(frozen=True)
class CounterSpec:
    algorithm_id: str
    platforms: frozenset[str]
    evidence: dict[str, str]
    confidence: str
    width_bits: int = 2


COUNTER_2BIT_V1 = CounterSpec(
    algorithm_id="honda_2bit_v1",
    platforms=COUNTER_2BIT_PLATFORMS,
    evidence=dict(EVIDENCE),
    confidence="DOCUMENTED",
    width_bits=2,
)


def apply_2bit_counter(
    data: bytes, counter: int, *, platform_id: str | None = None
) -> bytes:
    if platform_id is not None and platform_id not in COUNTER_2BIT_PLATFORMS:
        raise ValueError(
            f"honda_2bit_v1 not documented for platform {platform_id!r}"
        )
    return honda_set_counter(data, counter)


__all__ = [
    "COUNTER_2BIT_PLATFORMS",
    "COUNTER_2BIT_V1",
    "CounterSpec",
    "EVIDENCE",
    "apply_2bit_counter",
    "honda_set_counter",
]
