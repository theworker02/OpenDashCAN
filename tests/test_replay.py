"""Replay reader / synthetic simulator tests."""

from __future__ import annotations

import json
from pathlib import Path

from opendashcan.replay.reader import read_candump, read_capture, read_json
from opendashcan.replay.simulator import iter_scenario, synthetic_source_frames
from opendashcan.replay.writer import write_candump, write_json

FIXTURES = Path(__file__).parent / "fixtures"


def test_read_synthetic_candump() -> None:
    frames = list(read_candump(FIXTURES / "synthetic_candump.log"))
    assert len(frames) >= 1
    assert frames[0].meta.get("format") == "candump"


def test_synthetic_source_frames_marked() -> None:
    frames = synthetic_source_frames("idle")
    assert frames
    assert all(fr.meta.get("SYNTHETIC") == "true" for fr in frames)


def test_iter_scenario() -> None:
    steps = list(iter_scenario("idle"))
    assert steps
    assert steps[0][1].engine_rpm.value is not None


def test_write_and_read_roundtrip(tmp_path: Path) -> None:
    frames = synthetic_source_frames("accelerate")
    path = tmp_path / "out.log"
    write_candump(path, frames)
    back = list(read_capture(path))
    assert len(back) == len(frames)
    assert back[0].arbitration_id == frames[0].arbitration_id


def test_json_write(tmp_path: Path) -> None:
    frames = synthetic_source_frames("idle")
    path = tmp_path / "out.json"
    write_json(path, frames, label="SYNTHETIC")
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert "SYNTHETIC" in (raw.get("warning") or "").upper() or raw.get("label")
    back = list(read_json(path))
    assert len(back) == len(frames)
