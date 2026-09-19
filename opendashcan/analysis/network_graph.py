"""Message producer graph: ECU → messages → Cluster (? where unconfirmed)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from opendashcan.cluster.classify import classify_from_dbc_message
from opendashcan.analysis.lineage import _load_indexed_messages

REPO_ROOT = Path(__file__).resolve().parents[2]


# Map DBC sender tokens → logical ECU roles (documentation heuristic only)
SENDER_TO_ECU: dict[str, str] = {
    "PCM": "ECM",
    "ECM": "ECM",
    "ENGINE": "ECM",
    "VSA": "ABS",
    "ABS": "ABS",
    "EPB": "EPB",
    "BODY": "BCM",
    "BCM": "BCM",
    "GW": "Gateway",
    "GATEWAY": "Gateway",
    "ADAS": "ADAS",
    "CAM": "ADAS",
    "RADAR": "ADAS",
    "EON": "Interceptor",
    "INTERCEPTOR": "Interceptor",
    "XXX": "UNKNOWN",
}


def _ecu_role(sender: str | None) -> str:
    if not sender:
        return "UNKNOWN"
    token = sender.upper().split("_")[0]
    return SENDER_TO_ECU.get(sender.upper(), SENDER_TO_ECU.get(token, sender.upper()))


def build_network_graph(
    *,
    messages: list[dict[str, Any]] | None = None,
    cluster_platform_filter: str | None = "civic.gen10",
) -> dict[str, Any]:
    msgs = messages if messages is not None else _load_indexed_messages()
    if cluster_platform_filter:
        msgs = [
            m
            for m in msgs
            if cluster_platform_filter in str(m.get("vehicle_id") or "")
        ] or msgs  # fall back to all if filter empty

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    def ensure(node_id: str, kind: str, **extra: Any) -> None:
        if node_id not in nodes:
            nodes[node_id] = {"id": node_id, "kind": kind, **extra}

    ensure("Cluster", "cluster", rx_status="UNCONFIRMED", note="? until CLUSTER_RX_CONFIRMED")

    by_ecu_msgs: dict[str, set[str]] = defaultdict(set)
    for m in msgs:
        sender = m.get("sender") or "UNKNOWN"
        ecu = _ecu_role(sender)
        mid = m.get("id_hex") or hex(m.get("id_dec") or 0)
        msg_node = f"msg:{mid}:{m.get('name')}"
        ensure(ecu, "ecu", dbc_sender=sender)
        ensure(
            msg_node,
            "message",
            arbitration_id=mid,
            name=m.get("name"),
            dlc=m.get("dlc"),
            vehicles=sorted({m.get("vehicle_id")}),
        )
        # merge vehicles if node exists
        if "vehicles" in nodes[msg_node]:
            vs = set(nodes[msg_node].get("vehicles") or [])
            vs.add(m.get("vehicle_id"))
            nodes[msg_node]["vehicles"] = sorted(v for v in vs if v)

        cand = classify_from_dbc_message(
            {
                "id_dec": m.get("id_dec"),
                "id_hex": mid,
                "name": m.get("name"),
                "signals": m.get("signals") or [],
            },
            platform_hint=str(m.get("vehicle_id") or ""),
        )
        nodes[msg_node]["cluster_candidate_class"] = cand
        by_ecu_msgs[ecu].add(msg_node)
        edges.append(
            {
                "from": ecu,
                "to": msg_node,
                "relation": "produces",
                "confidence": "VEHICLE_PROTOCOL_DOCUMENTED",
            }
        )
        # Cluster edge — confirmed only if class says so
        if cand == "CLUSTER_CONFIRMED_RX":
            edges.append(
                {
                    "from": msg_node,
                    "to": "Cluster",
                    "relation": "cluster_rx",
                    "confidence": "CLUSTER_RX_CONFIRMED",
                }
            )
        elif cand == "CLUSTER_LIKELY_RX":
            edges.append(
                {
                    "from": msg_node,
                    "to": "Cluster",
                    "relation": "cluster_rx?",
                    "confidence": "COMMUNITY_RESEARCH",
                    "note": "LIKELY ≠ CONFIRMED",
                }
            )
        elif cand == "DISPLAY_RELEVANT":
            edges.append(
                {
                    "from": msg_node,
                    "to": "Cluster",
                    "relation": "display_relevant?",
                    "confidence": "INFERRED",
                    "note": "display-relevant ≠ CLUSTER_RX",
                }
            )

    # Deduplicate edges
    seen = set()
    uniq_edges = []
    for e in edges:
        key = (e["from"], e["to"], e["relation"])
        if key in seen:
            continue
        seen.add(key)
        uniq_edges.append(e)

    return {
        "warning": (
            "Producer graph from DBC sender fields + classification heuristics. "
            "Cluster edges with ? are unconfirmed. DBC ≠ BENCH_VERIFIED."
        ),
        "filter": cluster_platform_filter,
        "nodes": list(nodes.values()),
        "edges": uniq_edges,
        "ecu_message_counts": {k: len(v) for k, v in sorted(by_ecu_msgs.items())},
    }


def write_network_graph(path: Path | None = None, **kwargs: Any) -> Path:
    graph = build_network_graph(**kwargs)
    out = path or (REPO_ROOT / "dist" / "honda_network_graph.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    return out
