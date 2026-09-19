"""Evidence confidence helpers and YAML loading/validation hooks.

Evidence policy (Milestone 0.1):
- VERIFIED requires at least one cited source and must not be claimed lightly.
- SUPPORTED_BY_MULTIPLE_SOURCES is appropriate for public MIT DBCs / multi-cite research.
- COMMUNITY_REPORTED is for forum/wiki IDs without byte layouts or bench proof.
- INFERRED is for reasoned guesses — never presented as known fact.
- UNKNOWN is the default; unknown stays unknown (never invent fake values).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from opendashcan.core.state import Confidence

# Re-export for callers that import Confidence from evidence
__all__ = [
    "Confidence",
    "ALLOWED_CONFIDENCE",
    "load_evidence_yaml",
    "validate_evidence_document",
    "require_sources_for_verified",
]

ALLOWED_CONFIDENCE = frozenset(c.value for c in Confidence)


def load_evidence_yaml(path: Path | str) -> dict[str, Any]:
    """Load an evidence YAML document from disk."""
    p = Path(path)
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"evidence root must be a mapping: {p}")
    return raw


def require_sources_for_verified(entry: dict[str, Any], *, path: str = "") -> list[str]:
    """Reject VERIFIED entries that lack non-empty sources."""
    errors: list[str] = []
    conf = entry.get("confidence", "UNKNOWN")
    if conf == Confidence.VERIFIED.value:
        sources = entry.get("sources") or entry.get("source_refs") or []
        if not sources:
            loc = f" ({path})" if path else ""
            errors.append(f"VERIFIED requires at least one source{loc}")
    return errors


def validate_evidence_document(doc: dict[str, Any], *, path: str = "") -> list[str]:
    """Lightweight structural validation (schema tools do full JSON Schema checks)."""
    errors: list[str] = []
    if "vehicle_id" not in doc and "cluster_id" not in doc and "id" not in doc:
        errors.append(f"missing vehicle_id/cluster_id/id{f' in {path}' if path else ''}")

    signals = doc.get("signals") or []
    if isinstance(signals, dict):
        iterable = signals.items()
        for name, entry in iterable:
            if not isinstance(entry, dict):
                errors.append(f"signal {name} must be a mapping")
                continue
            conf = entry.get("confidence", "UNKNOWN")
            if conf not in ALLOWED_CONFIDENCE:
                errors.append(f"invalid confidence {conf!r} for signal {name}")
            errors.extend(require_sources_for_verified(entry, path=f"{path}:{name}"))
    elif isinstance(signals, list):
        for i, entry in enumerate(signals):
            if not isinstance(entry, dict):
                errors.append(f"signals[{i}] must be a mapping")
                continue
            name = entry.get("name", f"index-{i}")
            conf = entry.get("confidence", "UNKNOWN")
            if conf not in ALLOWED_CONFIDENCE:
                errors.append(f"invalid confidence {conf!r} for signal {name}")
            errors.extend(require_sources_for_verified(entry, path=f"{path}:{name}"))
    elif signals:
        errors.append("signals must be a list or mapping")

    messages = doc.get("messages") or []
    if isinstance(messages, list):
        for i, entry in enumerate(messages):
            if not isinstance(entry, dict):
                errors.append(f"messages[{i}] must be a mapping")
                continue
            conf = entry.get("confidence", "UNKNOWN")
            if conf not in ALLOWED_CONFIDENCE:
                errors.append(f"invalid confidence {conf!r} for message index {i}")
            errors.extend(require_sources_for_verified(entry, path=f"{path}:msg[{i}]"))

    return errors
