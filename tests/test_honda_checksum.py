"""Honda checksum tests — opendbc algorithm with SYNTHETIC payloads."""

from __future__ import annotations

from opendashcan.protocols.honda.checksum import (
    honda_compute_checksum,
    honda_set_checksum,
    honda_verify_checksum,
)


def test_honda_checksum_roundtrip_synthetic() -> None:
    # SYNTHETIC payload — not a real Civic frame
    raw = bytearray(8)
    raw[0] = 0x12
    raw[1] = 0x34
    framed = honda_set_checksum(0x158, raw)
    assert honda_verify_checksum(0x158, framed)
    assert (framed[-1] & 0x0F) == honda_compute_checksum(0x158, framed)


def test_honda_checksum_changes_with_data() -> None:
    a = honda_set_checksum(0x158, bytes([1, 0, 0, 0, 0, 0, 0, 0]))
    b = honda_set_checksum(0x158, bytes([2, 0, 0, 0, 0, 0, 0, 0]))
    assert a != b
    assert honda_verify_checksum(0x158, a)
    assert honda_verify_checksum(0x158, b)


def test_empty_payload_rejected() -> None:
    try:
        honda_set_checksum(0x158, b"")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
