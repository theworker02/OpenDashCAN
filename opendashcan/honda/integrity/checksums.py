"""Documented Honda 4-bit nibble checksum (opendbc) with platform scope."""

from __future__ import annotations

from dataclasses import dataclass

from opendashcan.protocols.honda.checksum import (
    honda_compute_checksum,
    honda_set_checksum,
    honda_set_counter,
    honda_verify_checksum,
)

NIBBLE_CHECKSUM_PLATFORMS = frozenset(
    {
        "honda.civic.gen10.us",
        "honda.civic.gen11.us",
        "honda.accord.gen10.us",
        "honda.crv.gen5.us",
        # Legacy colon aliases still accepted by callers
        "honda:civic:10",
        "honda:civic:11",
        "honda:accord:10",
        "honda:crv:5",
    }
)

EVIDENCE = {
    "algorithm_id": "honda_nibble_v1",
    "source": "commaai/opendbc opendbc/safety/modes/honda.h honda_compute_checksum",
    "url": "https://github.com/commaai/opendbc/blob/master/opendbc/safety/modes/honda.h",
    "license": "MIT",
    "confidence": "DOCUMENTED",
    "notes": (
        "4-bit checksum in low nibble of final payload byte. "
        "Civic 8th-gen F-CAN checksum behavior is NOT claimed."
    ),
}


@dataclass(frozen=True)
class ChecksumSpec:
    algorithm_id: str
    platforms: frozenset[str]
    evidence: dict[str, str]
    confidence: str


NIBBLE_V1 = ChecksumSpec(
    algorithm_id="honda_nibble_v1",
    platforms=NIBBLE_CHECKSUM_PLATFORMS,
    evidence=dict(EVIDENCE),
    confidence="DOCUMENTED",
)


def _guard(platform_id: str | None) -> None:
    if platform_id is not None and platform_id not in NIBBLE_CHECKSUM_PLATFORMS:
        raise ValueError(
            f"honda_nibble_v1 not documented for platform {platform_id!r}; "
            "refusing silent cross-generation assumption"
        )


def compute_nibble_checksum(address: int, data: bytes, *, platform_id: str | None = None) -> int:
    _guard(platform_id)
    return honda_compute_checksum(address, data)


def apply_nibble_checksum(
    address: int, data: bytes | bytearray, *, platform_id: str | None = None
) -> bytes:
    _guard(platform_id)
    return honda_set_checksum(address, data)


def verify_nibble_checksum(
    address: int, data: bytes, *, platform_id: str | None = None
) -> bool:
    _guard(platform_id)
    return honda_verify_checksum(address, data)


__all__ = [
    "ChecksumSpec",
    "EVIDENCE",
    "NIBBLE_CHECKSUM_PLATFORMS",
    "NIBBLE_V1",
    "apply_nibble_checksum",
    "compute_nibble_checksum",
    "honda_compute_checksum",
    "honda_set_checksum",
    "honda_set_counter",
    "honda_verify_checksum",
    "verify_nibble_checksum",
]
