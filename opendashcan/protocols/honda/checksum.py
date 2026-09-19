"""Honda checksum helpers.

Two layers are provided deliberately:

1. **opendbc address-aware algorithm** (``honda_compute_checksum`` / ``honda_set_checksum``)
   matching commaai/opendbc ``honda.h`` — used by Civic 10 research packing.
2. **Simple nibble helpers** (``honda_checksum_nibble`` / ``apply_honda_checksum``)
   for architecture / unit tests on opaque SYNTHETIC payloads.

Civic 8th-gen F-CAN checksum behavior is NOT claimed here.
"""

from __future__ import annotations


def honda_compute_checksum(address: int, data: bytes) -> int:
    """Compute the Honda 4-bit checksum nibble (opendbc algorithm)."""
    checksum = 0
    addr = address
    while addr:
        checksum += addr & 0xF
        addr >>= 4
    for i, byte in enumerate(data):
        checksum += (byte >> 4) + (byte & 0xF)
        if i == len(data) - 1:
            checksum -= byte & 0xF
    return (8 - (checksum & 0xF)) & 0xF


def honda_set_checksum(address: int, data: bytearray | bytes) -> bytes:
    """Return a copy of ``data`` with Honda checksum in the last byte low nibble."""
    buf = bytearray(data)
    if not buf:
        raise ValueError("empty payload")
    check = honda_compute_checksum(address, bytes(buf))
    buf[-1] = (buf[-1] & 0xF0) | check
    return bytes(buf)


def honda_verify_checksum(address: int, data: bytes) -> bool:
    if not data:
        return False
    expected = honda_compute_checksum(address, data)
    actual = data[-1] & 0xF
    return expected == actual


def honda_set_counter(data: bytes, counter: int) -> bytes:
    """Set 2-bit counter at DBC bits 61-60 (opendbc COUNTER on many Honda msgs)."""
    buf = bytearray(data)
    if not buf:
        raise ValueError("empty payload")
    c = counter & 0x3
    buf[-1] = (buf[-1] & 0xCF) | (c << 4)
    return bytes(buf)


def honda_checksum_nibble(data: bytes | bytearray) -> int:
    """Simple 4-bit sum of bytes (SYNTHETIC / unit-test helper — not opendbc)."""
    return sum(data) & 0xF


def apply_honda_checksum(
    data: bytes | bytearray,
    *,
    checksum_byte_index: int = -1,
    high_nibble: bool = False,
) -> bytes:
    """Embed a simple nibble checksum into ``data`` (architecture helper).

    This is **not** the opendbc address-aware algorithm. Prefer
    ``honda_set_checksum`` for Civic 10 research frames.
    """
    buf = bytearray(data)
    if not buf:
        raise ValueError("empty payload")
    idx = checksum_byte_index if checksum_byte_index >= 0 else len(buf) + checksum_byte_index
    if high_nibble:
        buf[idx] &= 0x0F
    else:
        buf[idx] &= 0xF0
    nibble = honda_checksum_nibble(buf)
    if high_nibble:
        buf[idx] = (buf[idx] & 0x0F) | (nibble << 4)
    else:
        buf[idx] = (buf[idx] & 0xF0) | nibble
    return bytes(buf)
