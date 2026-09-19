"""Isolated target cluster environments and gap analysis (Phase 4).

Import Phase 4 modules when present; stubs keep CLI/GUI importable if a
parallel agent is still landing files.
"""

from __future__ import annotations

from typing import Any

from opendashcan.cluster.classify import ClusterCandidateClass, classify_message

__all__ = [
    "CLUSTER_ALIASES",
    "ClusterCandidateClass",
    "ClusterEnvPackage",
    "build_gap_report",
    "classify_message",
    "format_gaps_text",
    "list_cluster_envs",
    "load_cluster_env",
]

try:
    from opendashcan.cluster.environment_loader import (
        CLUSTER_ALIASES,
        ClusterEnvPackage,
        list_cluster_envs,
        load_cluster_env,
    )
except ImportError:
    CLUSTER_ALIASES: dict[str, str] = {}
    ClusterEnvPackage = Any  # type: ignore[misc, assignment]

    def list_cluster_envs(**_kwargs: Any) -> list[Any]:
        return []

    def load_cluster_env(cluster_id: str, **_kwargs: Any) -> Any:
        raise NotImplementedError(
            "opendashcan.cluster.environment_loader is not available yet"
        )


try:
    from opendashcan.cluster.gaps import build_gap_report, format_gaps_text
except ImportError:

    def build_gap_report(cluster_name: str, **_kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("opendashcan.cluster.gaps is not available yet")

    def format_gaps_text(report: dict[str, Any]) -> str:
        return str(report)
