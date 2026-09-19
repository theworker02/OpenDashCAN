"""Signal documentation helpers for Civic 10 — opendbc research notes, not cluster-verified."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opendashcan.core.evidence import load_evidence_yaml

_EVIDENCE_PATH = Path(__file__).with_name("evidence.yaml")


def evidence_path() -> Path:
    return _EVIDENCE_PATH


def load_evidence() -> dict[str, Any]:
    return load_evidence_yaml(_EVIDENCE_PATH)


def documented_signal_confidence() -> dict[str, str]:
    doc = load_evidence()
    out: dict[str, str] = {}
    signals = doc.get("signals") or []
    if isinstance(signals, list):
        for entry in signals:
            if isinstance(entry, dict) and "name" in entry:
                out[str(entry["name"])] = str(entry.get("confidence", "UNKNOWN"))
    elif isinstance(signals, dict):
        for name, entry in signals.items():
            if isinstance(entry, dict):
                out[str(name)] = str(entry.get("confidence", "UNKNOWN"))
            else:
                out[str(name)] = "UNKNOWN"
    return out


# Alias used by older call sites
def signal_confidence_map() -> dict[str, str]:
    return documented_signal_confidence()
