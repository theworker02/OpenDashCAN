"""Capture analysis helpers (correlation / diff / signal finder)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean, pstdev

from opendashcan.core.frame import CANFrame


@dataclass(frozen=True)
class IdStats:
    arbitration_id: int
    count: int
    mean_period_s: float | None
    dlc_set: tuple[int, ...]
    data_hex_samples: tuple[str, ...]


def summarize_ids(frames: list[CANFrame], *, sample_limit: int = 3) -> list[IdStats]:
    by_id: dict[int, list[CANFrame]] = defaultdict(list)
    for fr in frames:
        by_id[fr.arbitration_id].append(fr)
    out: list[IdStats] = []
    for arb, group in sorted(by_id.items()):
        periods: list[float] = []
        for a, b in zip(group, group[1:], strict=False):
            periods.append(b.timestamp - a.timestamp)
        out.append(
            IdStats(
                arbitration_id=arb,
                count=len(group),
                mean_period_s=mean(periods) if periods else None,
                dlc_set=tuple(sorted({fr.dlc or len(fr.data) for fr in group})),
                data_hex_samples=tuple(fr.data_hex() for fr in group[:sample_limit]),
            )
        )
    return out


def diff_ids(a: list[CANFrame], b: list[CANFrame]) -> dict[str, set[int]]:
    sa = {fr.arbitration_id for fr in a}
    sb = {fr.arbitration_id for fr in b}
    return {"only_a": sa - sb, "only_b": sb - sa, "both": sa & sb}


def correlate_byte_with_series(
    frames: list[CANFrame],
    arbitration_id: int,
    series: list[tuple[float, float]],
) -> list[tuple[int, float]]:
    """Heuristic: Pearson-ish correlation of each byte vs an external series.

    Used for signal discovery research — results are INFERRED until verified.
    """
    subset = [fr for fr in frames if fr.arbitration_id == arbitration_id]
    if len(subset) < 3 or len(series) < 3:
        return []

    # Align by nearest timestamp
    ys: list[float] = []
    aligned: list[bytes] = []
    for fr in subset:
        nearest = min(series, key=lambda p: abs(p[0] - fr.timestamp))
        ys.append(nearest[1])
        aligned.append(fr.data)

    width = max((len(d) for d in aligned), default=0)
    results: list[tuple[int, float]] = []
    for idx in range(width):
        xs = [float(d[idx]) if idx < len(d) else 0.0 for d in aligned]
        results.append((idx, _corr(xs, ys)))
    results.sort(key=lambda t: abs(t[1]), reverse=True)
    return results


def _corr(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True))
    dx = pstdev(xs)
    dy = pstdev(ys)
    if dx == 0 or dy == 0:
        return 0.0
    return num / (len(xs) * dx * dy)


def find_candidate_signals(
    frames: list[CANFrame],
    *,
    min_count: int = 10,
) -> list[IdStats]:
    """Return high-frequency IDs as discovery candidates (confidence INFERRED)."""
    return [s for s in summarize_ids(frames) if s.count >= min_count]
