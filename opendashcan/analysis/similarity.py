"""Cross-platform message/signal similarity — leads only, never copy encodings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from opendashcan.analysis.lineage import _load_indexed_messages, compare_encodings
from opendashcan.dbc import taxonomy_implementations_from_imports


@dataclass
class SimilarityHit:
    target_vehicle: str
    candidate_vehicle: str
    signal: str | None
    message: str | None
    arbitration_id: str | None
    score: float
    identical_encoding: bool
    label: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_vehicle": self.target_vehicle,
            "candidate_vehicle": self.candidate_vehicle,
            "signal": self.signal,
            "message": self.message,
            "arbitration_id": self.arbitration_id,
            "score": self.score,
            "identical_encoding": self.identical_encoding,
            "label": self.label,
            "notes": self.notes,
        }


def _score_signals(a: dict[str, Any], b: dict[str, Any]) -> float:
    score = 0.0
    if a.get("arbitration_id") == b.get("arbitration_id"):
        score += 0.35
    if a.get("message") == b.get("message"):
        score += 0.15
    if a.get("start_bit") == b.get("start_bit") and a.get("length") == b.get("length"):
        score += 0.25
    if a.get("scale") == b.get("scale") and a.get("offset") == b.get("offset"):
        score += 0.15
    if a.get("byte_order") == b.get("byte_order"):
        score += 0.05
    if a.get("dbc_signal") == b.get("dbc_signal") or a.get("name") == b.get("name"):
        score += 0.05
    return round(min(score, 1.0), 3)


def correlate_signal(
    *,
    target: str,
    signal: str,
    index_dir: Path | None = None,
) -> list[SimilarityHit]:
    """Find CROSS_PLATFORM_CANDIDATE leads for a taxonomy signal vs target vehicle."""
    cross = taxonomy_implementations_from_imports(index_dir or Path("dbc/opendbc/index"))
    rows = cross.get(signal) or []
    if not rows:
        return []

    target_rows = [r for r in rows if target in str(r.get("vehicle_id") or "")]
    others = [r for r in rows if target not in str(r.get("vehicle_id") or "")]
    hits: list[SimilarityHit] = []

    if not target_rows:
        # Target lacks signal — candidates are leads only
        for r in others:
            hits.append(
                SimilarityHit(
                    target_vehicle=target,
                    candidate_vehicle=str(r.get("vehicle_id")),
                    signal=signal,
                    message=r.get("message"),
                    arbitration_id=r.get("arbitration_id"),
                    score=0.4,
                    identical_encoding=False,
                    label="CROSS_PLATFORM_CANDIDATE",
                    notes=(
                        f"Target {target} has no public DBC mapping for {signal}. "
                        "Do NOT copy candidate encoding into target definition."
                    ),
                )
            )
        return hits

    ref = target_rows[0]
    for r in others:
        score = _score_signals(ref, r)
        identical = score >= 0.95
        hits.append(
            SimilarityHit(
                target_vehicle=target,
                candidate_vehicle=str(r.get("vehicle_id")),
                signal=signal,
                message=r.get("message"),
                arbitration_id=r.get("arbitration_id"),
                score=score,
                identical_encoding=identical,
                label="IDENTICAL_ENCODING" if identical else "CROSS_PLATFORM_CANDIDATE",
                notes=(
                    "Identical public DBC encoding across vehicles"
                    if identical
                    else "Similar but verify bit layout — matching names ≠ identical encoding"
                ),
            )
        )
    hits.sort(key=lambda h: (-h.score, h.candidate_vehicle))
    return hits


def correlate_message_id(
    *,
    target: str,
    arbitration_id: int,
) -> list[dict[str, Any]]:
    msgs = _load_indexed_messages()
    target_msgs = [
        m
        for m in msgs
        if target in str(m.get("vehicle_id") or "") and m.get("id_dec") == arbitration_id
    ]
    others = [
        m
        for m in msgs
        if target not in str(m.get("vehicle_id") or "") and m.get("id_dec") == arbitration_id
    ]
    if not target_msgs:
        return [
            {
                "label": "CROSS_PLATFORM_CANDIDATE",
                "note": f"ID {hex(arbitration_id)} not on target {target}",
                "candidates": [
                    {"vehicle_id": m.get("vehicle_id"), "name": m.get("name"), "dlc": m.get("dlc")}
                    for m in others
                ],
            }
        ]
    ref = target_msgs[0]
    out = []
    for m in others:
        cmp = compare_encodings(ref, m)
        out.append(
            {
                "candidate_vehicle": m.get("vehicle_id"),
                "label": (
                    "IDENTICAL_ENCODING"
                    if cmp["identical_encoding"]
                    else "CROSS_PLATFORM_CANDIDATE"
                ),
                **cmp,
            }
        )
    return out


def build_cross_platform_candidates(
    signals: list[str] | None = None,
    *,
    targets: list[str] | None = None,
) -> dict[str, Any]:
    from opendashcan.core.donor_knowledge import CLUSTER_RELEVANT_TAXONOMY

    sigs = signals or sorted(CLUSTER_RELEVANT_TAXONOMY)
    tgts = targets or [
        "honda.civic.gen10",
        "honda.civic.gen11",
        "honda.accord.gen10",
        "honda.crv.gen5",
    ]
    leads: list[dict[str, Any]] = []
    for target in tgts:
        for signal in sigs:
            for hit in correlate_signal(target=target, signal=signal):
                if hit.label == "CROSS_PLATFORM_CANDIDATE":
                    leads.append(hit.to_dict())
    return {
        "warning": (
            "CROSS_PLATFORM_CANDIDATE leads only. Never copy Accord/CR-V encodings "
            "into Civic without independent evidence."
        ),
        "lead_count": len(leads),
        "leads": leads,
    }
