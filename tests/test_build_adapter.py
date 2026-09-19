"""Tests for build-adapter compiler."""

from __future__ import annotations

import json
from pathlib import Path

from opendashcan.adaptation.compiler import build_adapter


def test_build_adapter_writes_artifacts(tmp_path: Path):
    out = build_adapter(
        "honda:civic:8:r18:auto",
        "honda:civic:10:digital",
        output_root=tmp_path,
    )
    assert out.is_dir()
    for name in (
        "adapter_manifest.json",
        "signal_map.json",
        "required_messages.json",
        "unknowns.json",
        "evidence.json",
        "software_test_report.json",
        "adaptation_plan.json",
    ):
        assert (out / name).is_file(), name
    manifest = json.loads((out / "adapter_manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "DOCUMENTATION_ONLY"
    assert "SOFTWARE VALIDATION ONLY" in manifest["label"]
    report = json.loads((out / "software_test_report.json").read_text(encoding="utf-8"))
    assert report["label"] == "SOFTWARE VALIDATION ONLY"
    assert report["encoder_available"] is True
    assert report["frames_emitted"] >= 1
