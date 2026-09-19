"""Honda integrity package — documented checksums and counters only."""

from opendashcan.honda.integrity.checksums import (
    NIBBLE_CHECKSUM_PLATFORMS,
    NIBBLE_V1,
    apply_nibble_checksum,
    compute_nibble_checksum,
    honda_compute_checksum,
    honda_set_checksum,
    honda_verify_checksum,
    verify_nibble_checksum,
)
from opendashcan.honda.integrity.counters import (
    COUNTER_2BIT_PLATFORMS,
    COUNTER_2BIT_V1,
    apply_2bit_counter,
    honda_set_counter,
)

__all__ = [
    "COUNTER_2BIT_PLATFORMS",
    "COUNTER_2BIT_V1",
    "NIBBLE_CHECKSUM_PLATFORMS",
    "NIBBLE_V1",
    "apply_2bit_counter",
    "apply_nibble_checksum",
    "compute_nibble_checksum",
    "honda_compute_checksum",
    "honda_set_checksum",
    "honda_set_counter",
    "honda_verify_checksum",
    "verify_nibble_checksum",
]
