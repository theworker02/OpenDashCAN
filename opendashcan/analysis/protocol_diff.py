"""Compare two protocol platforms (buses/messages/signals) — unknowns stay visible."""

from __future__ import annotations

from dataclasses import dataclass, field

from opendashcan.registry import get_registry
from opendashcan.registry.models import PlatformPackage


@dataclass
class ProtocolDiff:
    source_id: str
    target_id: str
    shared_signals: list[str] = field(default_factory=list)
    source_only_signals: list[str] = field(default_factory=list)
    target_only_signals: list[str] = field(default_factory=list)
    changed_ids: list[str] = field(default_factory=list)
    changed_confidence: list[str] = field(default_factory=list)
    bus_notes: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)

    def format_text(self) -> str:
        lines = [
            f"PROTOCOL DIFF: {self.source_id}  vs  {self.target_id}",
            "",
            f"Shared signals ({len(self.shared_signals)}):",
        ]
        lines += [f"  {s}" for s in self.shared_signals] or ["  (none)"]
        lines += ["", f"Source-only ({len(self.source_only_signals)}):"]
        lines += [f"  {s}" for s in self.source_only_signals] or ["  (none)"]
        lines += ["", f"Target-only ({len(self.target_only_signals)}):"]
        lines += [f"  {s}" for s in self.target_only_signals] or ["  (none)"]
        lines += ["", "Changed arbitration IDs / confidence:"]
        lines += [f"  {c}" for c in self.changed_ids + self.changed_confidence] or [
            "  (none documented)"
        ]
        lines += ["", "Buses:"]
        lines += [f"  {b}" for b in self.bus_notes] or ["  (none)"]
        lines += ["", "Unknowns / gaps:"]
        lines += [f"  {u}" for u in self.unknowns] or ["  (none flagged)"]
        lines.append("")
        lines.append("Unknown fields remain UNKNOWN - this is not a compatibility claim.")
        return "\n".join(lines)


def diff_platforms(source_id: str, target_id: str) -> ProtocolDiff:
    reg = get_registry()
    a: PlatformPackage = reg.get(source_id)
    b: PlatformPackage = reg.get(target_id)
    sa = a.signal_map()
    sb = b.signal_map()
    shared = sorted(set(sa) & set(sb))
    result = ProtocolDiff(
        source_id=a.platform_id,
        target_id=b.platform_id,
        shared_signals=shared,
        source_only_signals=sorted(set(sa) - set(sb)),
        target_only_signals=sorted(set(sb) - set(sa)),
    )
    for name in shared:
        ea, eb = sa[name], sb[name]
        if (ea.arbitration_id or "UNKNOWN") != (eb.arbitration_id or "UNKNOWN"):
            result.changed_ids.append(
                f"{name}: {ea.arbitration_id or 'UNKNOWN'} -> {eb.arbitration_id or 'UNKNOWN'}"
            )
        if ea.confidence != eb.confidence:
            result.changed_confidence.append(
                f"{name}: {ea.confidence.value} -> {eb.confidence.value}"
            )
        if ea.arbitration_id is None or eb.arbitration_id is None:
            result.unknowns.append(f"{name}: arbitration_id UNKNOWN on one or both sides")

    buses_a = {x.bus_id: x for x in a.buses}
    buses_b = {x.bus_id: x for x in b.buses}
    for bid in sorted(set(buses_a) | set(buses_b)):
        ba, bb = buses_a.get(bid), buses_b.get(bid)
        if ba and bb:
            result.bus_notes.append(
                f"{bid}: both present "
                f"(bitrate {ba.bitrate}/{bb.bitrate}, "
                f"{ba.confidence.value}/{bb.confidence.value})"
            )
        elif ba:
            result.bus_notes.append(f"{bid}: source only ({ba.confidence.value})")
        else:
            assert bb is not None
            result.bus_notes.append(f"{bid}: target only ({bb.confidence.value})")

    if not a.messages:
        result.unknowns.append(f"{a.platform_id}: no documented messages")
    if not b.messages:
        result.unknowns.append(f"{b.platform_id}: no documented messages")
    return result
