"""Evidence confidence model V2 with Phase-1 compatibility aliases.

Promotion rules (CI-enforced):
- PHYSICALLY_VERIFIED / VERIFIED require PHYSICAL_TEST evidence
- CAPTURE_VERIFIED requires CAN_CAPTURE evidence
- DOCUMENTED / SUPPORTED_BY_MULTIPLE_SOURCES require OEM_DOCUMENTATION,
  OPEN_SOURCE_CODE, DBC, or ACADEMIC_RESEARCH
- COMMUNITY_REPORTED may use COMMUNITY_RESEARCH
- INFERRED / HYPOTHESIS never promote to VERIFIED / PHYSICALLY_VERIFIED alone
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Confidence(str, Enum):
    """Phase-2 confidence ladder (includes Phase-1 aliases)."""

    UNKNOWN = "UNKNOWN"
    HYPOTHESIS = "HYPOTHESIS"
    INFERRED = "INFERRED"
    COMMUNITY_REPORTED = "COMMUNITY_REPORTED"
    DOCUMENTED = "DOCUMENTED"
    CAPTURE_VERIFIED = "CAPTURE_VERIFIED"
    PHYSICALLY_VERIFIED = "PHYSICALLY_VERIFIED"
    # Phase-1 aliases (still accepted in YAML)
    SUPPORTED_BY_MULTIPLE_SOURCES = "SUPPORTED_BY_MULTIPLE_SOURCES"
    VERIFIED = "VERIFIED"


class SourceType(str, Enum):
    OEM_DOCUMENTATION = "OEM_DOCUMENTATION"
    OPEN_SOURCE_CODE = "OPEN_SOURCE_CODE"
    DBC = "DBC"
    CAN_CAPTURE = "CAN_CAPTURE"
    ACADEMIC_RESEARCH = "ACADEMIC_RESEARCH"
    COMMUNITY_RESEARCH = "COMMUNITY_RESEARCH"
    COMMERCIAL_DATASHEET = "COMMERCIAL_DATASHEET"
    PHYSICAL_TEST = "PHYSICAL_TEST"
    INFERENCE = "INFERENCE"
    RESEARCH_NOTE = "RESEARCH_NOTE"


# Normalize Phase-1 labels onto the Phase-2 ladder for policy checks.
NORMALIZE: dict[Confidence, Confidence] = {
    Confidence.SUPPORTED_BY_MULTIPLE_SOURCES: Confidence.DOCUMENTED,
    Confidence.VERIFIED: Confidence.PHYSICALLY_VERIFIED,
}

REQUIRED_SOURCE_TYPES: dict[Confidence, frozenset[SourceType]] = {
    Confidence.PHYSICALLY_VERIFIED: frozenset({SourceType.PHYSICAL_TEST}),
    Confidence.CAPTURE_VERIFIED: frozenset({SourceType.CAN_CAPTURE}),
    Confidence.DOCUMENTED: frozenset(
        {
            SourceType.OEM_DOCUMENTATION,
            SourceType.OPEN_SOURCE_CODE,
            SourceType.DBC,
            SourceType.ACADEMIC_RESEARCH,
            SourceType.COMMERCIAL_DATASHEET,
            SourceType.RESEARCH_NOTE,
        }
    ),
    Confidence.COMMUNITY_REPORTED: frozenset({SourceType.COMMUNITY_RESEARCH}),
}


@dataclass(slots=True)
class EvidenceRecord:
    evidence_id: str
    source_type: SourceType
    claim: str
    confidence: Confidence = Confidence.UNKNOWN
    source_url: str | None = None
    title: str | None = None
    author: str | None = None
    date: str | None = None
    license: str | None = None
    vehicle: str | None = None
    bus: str | None = None
    signal: str | None = None
    notes: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceRecord:
        return cls(
            evidence_id=str(data["evidence_id"]),
            source_type=SourceType(data["source_type"]),
            claim=str(data.get("claim", "")),
            confidence=Confidence(data.get("confidence", "UNKNOWN")),
            source_url=data.get("source_url"),
            title=data.get("title"),
            author=data.get("author"),
            date=data.get("date"),
            license=data.get("license"),
            vehicle=data.get("vehicle"),
            bus=data.get("bus"),
            signal=data.get("signal"),
            notes=data.get("notes"),
            extra={
                k: v
                for k, v in data.items()
                if k
                not in {
                    "evidence_id",
                    "source_type",
                    "claim",
                    "confidence",
                    "source_url",
                    "title",
                    "author",
                    "date",
                    "license",
                    "vehicle",
                    "bus",
                    "signal",
                    "notes",
                }
            },
        )


def normalize_confidence(conf: Confidence | str) -> Confidence:
    c = Confidence(conf) if not isinstance(conf, Confidence) else conf
    return NORMALIZE.get(c, c)


def validate_confidence_promotion(
    confidence: Confidence | str,
    evidence: list[EvidenceRecord] | list[dict[str, Any]],
    *,
    path: str = "",
) -> list[str]:
    """Return validation errors if confidence is stronger than evidence allows."""
    errors: list[str] = []
    conf = normalize_confidence(confidence)
    loc = f" ({path})" if path else ""

    records: list[EvidenceRecord] = []
    for item in evidence:
        if isinstance(item, EvidenceRecord):
            records.append(item)
        elif isinstance(item, dict):
            try:
                records.append(EvidenceRecord.from_dict(item))
            except (KeyError, ValueError) as exc:
                errors.append(f"invalid evidence record{loc}: {exc}")
                return errors

    if conf in (Confidence.UNKNOWN, Confidence.HYPOTHESIS, Confidence.INFERRED):
        return errors

    if not records:
        errors.append(f"{conf.value} requires evidence{loc}")
        return errors

    # Inference-only evidence can never support DOCUMENTED+ claims.
    types = {r.source_type for r in records}
    if types <= {SourceType.INFERENCE} and conf not in (
        Confidence.INFERRED,
        Confidence.HYPOTHESIS,
        Confidence.UNKNOWN,
    ):
        errors.append(f"{conf.value} cannot be granted from INFERENCE alone{loc}")

    required = REQUIRED_SOURCE_TYPES.get(conf)
    if required is not None and not (types & required):
        needed = ", ".join(sorted(t.value for t in required))
        errors.append(f"{conf.value} requires one of [{needed}]{loc}")

    # Legacy Phase-1: VERIFIED / PHYSICALLY_VERIFIED also need a URL or citation.
    if conf == Confidence.PHYSICALLY_VERIFIED and not any(r.source_url or r.title for r in records):
        errors.append(f"PHYSICALLY_VERIFIED requires cited physical test source{loc}")

    return errors
