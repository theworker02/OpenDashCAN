"""Signal discovery entrypoints."""

from __future__ import annotations

from opendashcan.analysis.correlation import (
    correlate_byte_with_series,
    find_candidate_signals,
    summarize_ids,
)

__all__ = ["correlate_byte_with_series", "find_candidate_signals", "summarize_ids"]
