"""Generate candump-compatible traces from ClusterEnvironment — omit unknowns."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from opendashcan.adaptation.gating import EncodeMode
from opendashcan.cluster.virtual_donor import VirtualDonorVehicle
from opendashcan.core.state import Confidence, GearPosition, SignalValue, Validity, VehicleState
from opendashcan.replay.simulator import SCENARIOS, iter_scenario

REPO_ROOT = Path(__file__).resolve().parents[2]


def _state_from_scenario_step(step: Any) -> VehicleState:
    state = VehicleState()
    if getattr(step, "rpm", None) is not None:
        state.engine_rpm = SignalValue(
            float(step.rpm), confidence=Confidence.INFERRED, validity=Validity.VALID
        )
    if getattr(step, "speed_kph", None) is not None:
        state.vehicle_speed = SignalValue(
            float(step.speed_kph), confidence=Confidence.INFERRED, validity=Validity.VALID
        )
    if getattr(step, "gear", None) is not None:
        g = step.gear
        if isinstance(g, GearPosition):
            state.gear = SignalValue(g, confidence=Confidence.INFERRED, validity=Validity.VALID)
        else:
            state.gear = SignalValue(
                str(g), confidence=Confidence.INFERRED, validity=Validity.VALID
            )
    return state


def generate_trace(
    *,
    cluster: str,
    scenario: str,
    encode_mode: EncodeMode = EncodeMode.SYNTHETIC,
) -> dict[str, Any]:
    """Build candump lines + manifest of omissions. Synthetic only."""
    if scenario not in SCENARIOS:
        raise KeyError(f"unknown scenario: {scenario}; choose from {sorted(SCENARIOS)}")

    donor = VirtualDonorVehicle(cluster_key=cluster, encode_mode=encode_mode)
    lines: list[str] = []
    frames_emitted = 0
    omissions: list[str] = [
        "SYNTHETIC research frames — not a physical capture",
        "Unknown/undocumented signals omitted (not invented)",
        "Default production EncodeMode is NO_OUTPUT; this run uses SYNTHETIC explicitly",
    ]

    # Signals we know we cannot encode from public DBC
    omissions.extend(
        [
            "fuel.level omitted — ABSENT from public DBC",
            "powertrain.coolant_temperature omitted — ABSENT from public DBC",
            "cluster RX confirmation omitted — not claimed",
        ]
    )

    for step, state in iter_scenario(scenario):
        frames = donor.emit(state, timestamp=float(step.t))
        for fr in frames:
            # candump classic: (timestamp) interface id#data
            data_hex = fr.data.hex().upper() if isinstance(fr.data, (bytes, bytearray)) else ""
            iface = "can0"
            aid = fr.arbitration_id
            lines.append(f"({step.t:012.6f}) {iface} {aid:03X}#{data_hex}")
            frames_emitted += 1

    omissions.extend(donor.omissions)
    # Dedupe omissions preserving order
    seen: set[str] = set()
    uniq_omit = []
    for o in omissions:
        if o not in seen:
            seen.add(o)
            uniq_omit.append(o)

    return {
        "cluster": cluster,
        "scenario": scenario,
        "encode_mode": encode_mode.value if hasattr(encode_mode, "value") else str(encode_mode),
        "frame_count": frames_emitted,
        "candump_lines": lines,
        "manifest": {
            "omissions": uniq_omit,
            "label": "SOFTWARE VALIDATION ONLY / SYNTHETIC",
            "note": "Do not treat as CLUSTER_RX_CONFIRMED or BENCH_VERIFIED evidence",
        },
    }


def write_trace(
    cluster: str,
    scenario: str,
    *,
    output: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Path]:
    result = generate_trace(cluster=cluster, scenario=scenario)
    out = output or (
        REPO_ROOT / "dist" / "traces" / f"{cluster}_{scenario}.candump.log"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "\n".join(result["candump_lines"]) + ("\n" if result["candump_lines"] else ""),
        encoding="utf-8",
    )
    if manifest_path is not None:
        man = manifest_path
    elif out.name.endswith(".candump.log"):
        man = out.parent / (out.name[: -len(".candump.log")] + ".manifest.json")
    else:
        man = out.with_name(out.stem + ".manifest.json")
    man.write_text(
        json.dumps(
            {
                "cluster": result["cluster"],
                "scenario": result["scenario"],
                "encode_mode": result["encode_mode"],
                "frame_count": result["frame_count"],
                "manifest": result["manifest"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"candump": out, "manifest": man}
