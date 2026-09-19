"""Evidence loading and VERIFIED-without-sources rejection."""

from __future__ import annotations

from pathlib import Path

from opendashcan.core.evidence import (
    load_evidence_yaml,
    require_sources_for_verified,
    validate_evidence_document,
)
from opendashcan.protocols.honda.civic8.signals import evidence_path as civic8_evidence
from opendashcan.protocols.honda.civic10.signals import evidence_path as civic10_evidence


def test_civic8_evidence_loads() -> None:
    doc = load_evidence_yaml(civic8_evidence())
    assert doc["vehicle_id"] == "honda-civic8"
    errors = validate_evidence_document(doc, path="civic8")
    assert errors == []


def test_civic10_evidence_loads() -> None:
    doc = load_evidence_yaml(civic10_evidence())
    assert doc["vehicle_id"] == "honda-civic10"
    errors = validate_evidence_document(doc, path="civic10")
    assert errors == []


def test_verified_requires_sources() -> None:
    errors = require_sources_for_verified(
        {"name": "engine_rpm", "confidence": "VERIFIED"},
        path="test",
    )
    assert errors
    assert "VERIFIED" in errors[0]


def test_verified_with_sources_ok() -> None:
    errors = require_sources_for_verified(
        {
            "name": "engine_rpm",
            "confidence": "VERIFIED",
            "sources": ["https://example.invalid/bench-log"],
        }
    )
    assert errors == []


def test_packaged_evidence_files_exist() -> None:
    assert Path(civic8_evidence()).is_file()
    assert Path(civic10_evidence()).is_file()
