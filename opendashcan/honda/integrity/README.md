# Honda integrity — documented algorithms only

This package wraps checksum / counter helpers that have **cited** public evidence
(primarily commaai/opendbc, MIT).

| Algorithm | Platforms | Evidence |
|-----------|-----------|----------|
| `honda_nibble_v1` | civic:10, civic:11, accord:10, crv:5 | opendbc `honda_compute_checksum` |
| `honda_2bit_v1` | civic:10, civic:11, accord:10, crv:5 | opendbc COUNTER on PCM msgs |

**Not claimed:** Civic 8th-gen F-CAN checksum/counter behavior.

Passing an undocumented `platform_id` raises `ValueError` — no silent
cross-generation assumptions.
