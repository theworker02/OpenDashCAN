"""Motorola (DBC @0+) helpers aligned with commaai/opendbc Honda packing.

Byte-aligned signals whose ``start_bit % 8 == 7`` occupy consecutive big-endian
bytes starting at ``start_bit // 8`` (matches Civic10Encoder ENGINE_DATA /
CAR_SPEED packing). Narrower fields use Vector bit numbering within those bytes.
"""

from __future__ import annotations


def unpack_be_unsigned(data: bytes, start_bit: int, length: int) -> int:
    if length <= 0:
        return 0
    # Fast path: N-byte BE fields used heavily in Honda DBCs (RPM, speed, odo)
    if length % 8 == 0 and start_bit % 8 == 7:
        byte0 = start_bit // 8
        nbytes = length // 8
        value = 0
        for i in range(nbytes):
            idx = byte0 + i
            value = (value << 8) | (data[idx] if idx < len(data) else 0)
        return value

    value = 0
    bit = start_bit
    for i in range(length):
        byte_i = bit // 8
        bit_i = bit % 8
        if 0 <= byte_i < len(data) and ((data[byte_i] >> bit_i) & 1):
            value |= 1 << (length - 1 - i)
        if bit_i == 0:
            # Continue into the next higher-numbered byte at bit 7 (Vector BE)
            bit = (byte_i + 1) * 8 + 7
        else:
            bit -= 1
    return value


def unpack_be_bool(data: bytes, start_bit: int) -> bool:
    return bool(unpack_be_unsigned(data, start_bit, 1))


def pack_be_unsigned(buf: bytearray, start_bit: int, length: int, value: int) -> None:
    v = int(value) & ((1 << length) - 1 if length < 63 else (1 << 62) - 1)
    if length % 8 == 0 and start_bit % 8 == 7:
        byte0 = start_bit // 8
        nbytes = length // 8
        for i in range(nbytes):
            shift = 8 * (nbytes - 1 - i)
            idx = byte0 + i
            if 0 <= idx < len(buf):
                buf[idx] = (v >> shift) & 0xFF
        return

    bit = start_bit
    for i in range(length):
        byte_i = bit // 8
        bit_i = bit % 8
        if 0 <= byte_i < len(buf):
            mask = 1 << bit_i
            if (v >> (length - 1 - i)) & 1:
                buf[byte_i] |= mask
            else:
                buf[byte_i] &= ~mask & 0xFF
        if bit_i == 0:
            bit = (byte_i + 1) * 8 + 7
        else:
            bit -= 1
