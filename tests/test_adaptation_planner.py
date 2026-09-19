"""Tests for adaptation planner."""

from __future__ import annotations

from opendashcan.adaptation.planner import plan
from opendashcan.adaptation.readiness import Readiness


def test_plan_civic8_to_civic10():
    p = plan("honda:civic:8", "honda:civic:10:digital")
    assert p.mode == "DOCUMENTATION_ONLY"
    assert p.cluster_id in (
        "honda:civic:10:digital",
        "honda.civic.gen10.cluster.digital",
    )
    assert p.source_platform.platform_id in ("honda:civic:8", "honda.civic.gen8.us")
    assert len(p.rows) > 0
    by_sig = {r.signal: r for r in p.rows}
    assert "powertrain.engine_rpm" in by_sig
    rpm = by_sig["powertrain.engine_rpm"]
    assert rpm.source_confidence == "UNKNOWN"
    assert rpm.target_confidence == "DOCUMENTED"
    # Source encodings unknown; target donor documented → translation blocked on source only.
    assert rpm.readiness == Readiness.BLOCKED_SOURCE
    assert rpm.translation == "BLOCKED_SOURCE"
    summary = p.readiness_summary()
    assert summary.get(Readiness.BLOCKED_SOURCE.value, 0) >= 1


def test_plan_accepts_r18_auto_alias():
    p = plan("honda:civic:8:r18:auto", "honda:civic:10:digital")
    assert p.source_platform.platform_id in ("honda:civic:8", "honda.civic.gen8.us")


def test_plan_text_mentions_documentation_only():
    text = plan("honda:civic:8", "honda:civic:10:digital").format_text()
    assert "DOCUMENTATION_ONLY" in text
    assert "SOURCE VEHICLE" in text
    assert "TARGET CLUSTER" in text
