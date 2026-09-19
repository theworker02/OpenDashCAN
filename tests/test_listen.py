"""Listen-only session + TX guard + CLI smoke (no hardware required)."""

from __future__ import annotations

from pathlib import Path

import pytest

from opendashcan.core.encoder import EncodeMode
from opendashcan.core.frame import BusRole, CANFrame
from opendashcan.core.state import Confidence, VehicleState
from opendashcan.hardware.bus import NullBridge, TransmitMode
from opendashcan.hardware.interfaces import BusConfig, DualBusConfig, LinkMode, NullDualBusAdapter
from opendashcan.hw.listen import (
    HardwareUnavailableError,
    iter_capture_frames,
    open_listen_bus,
    python_can_available,
    resolve_virtual_fixture,
)
from opendashcan.hw.session import ListenSession
from opendashcan.hw.tx_guard import TX_ENV_FLAG, assert_tx_permitted, refuse_send_message, tx_env_enabled
from opendashcan.protocols.honda.civic10.decoder import Civic10VehicleDecoder
from opendashcan.protocols.honda.civic10.encoder import Civic10Encoder
from opendashcan.registry import get_decoder

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "captures" / "synthetic" / "idle_scenario.log"


def test_refuse_send_message_mentions_listen_only() -> None:
    msg = refuse_send_message()
    assert "LISTEN ONLY" in msg
    assert TX_ENV_FLAG in msg


def test_tx_guard_default_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(TX_ENV_FLAG, raising=False)
    assert not tx_env_enabled()
    with pytest.raises(PermissionError, match="TX refused"):
        assert_tx_permitted(0x158, allowlist={0x158})


def test_tx_guard_env_without_allowlist_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TX_ENV_FLAG, "1")
    with pytest.raises(PermissionError, match="allowlist"):
        assert_tx_permitted(0x158, allowlist=set())


def test_tx_guard_env_and_allowlist_passes_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TX_ENV_FLAG, "1")
    assert_tx_permitted(0x158, allowlist={0x158})  # does not raise


def test_null_bridge_send_blocked() -> None:
    bridge = NullBridge(transmit_mode=TransmitMode.DISABLED)
    with pytest.raises(RuntimeError, match="TX blocked"):
        bridge.send(CANFrame(arbitration_id=0x158, data=b"\x00" * 8, timestamp=0.0))


def test_null_adapter_write_blocked_even_if_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(TX_ENV_FLAG, "1")
    cfg = DualBusConfig(
        source=BusConfig(role=BusRole.SOURCE, channel="s"),
        target=BusConfig(role=BusRole.TARGET, channel="t"),
        mode=LinkMode.BIDIRECTIONAL,
        tx_enabled=True,
        tx_allowlist={0x158},
    )
    adapter = NullDualBusAdapter(cfg)
    # Env+allowlist pass assert_tx_permitted, then Null impl still cannot TX
    with pytest.raises(RuntimeError, match="cannot transmit"):
        adapter.write_target(CANFrame(arbitration_id=0x158, data=b"\x00" * 8, timestamp=0.0))


def test_mock_bus_decoder_state() -> None:
    """Mock frames (encoder SYNTHETIC) → Civic10VehicleDecoder → VehicleState."""
    enc = Civic10Encoder(encode_mode=EncodeMode.SYNTHETIC)
    state = VehicleState()
    state.set("powertrain.engine_rpm", 1500.0, confidence=Confidence.DOCUMENTED)
    state.set("vehicle.speed", 0.0, confidence=Confidence.DOCUMENTED)
    frames = enc.encode(state, timestamp=1.0)
    assert frames

    session = ListenSession(decoder=Civic10VehicleDecoder())
    for fr in frames:
        session.ingest(fr)
    assert session.frame_count == len(frames)
    assert session.state.engine_rpm.value == 1500.0
    assert "engine_rpm" in session.state.known_signals() or any(
        "rpm" in n for n in session.state.known_signals()
    )
    rows = session.id_rate_rows()
    assert rows
    assert any(r.arbitration_id == 0x158 for r in rows)


def test_session_from_synthetic_capture() -> None:
    assert SYNTH.is_file()
    decoder = get_decoder("honda.civic.gen10.us")
    session = ListenSession(decoder=decoder)
    for fr in iter_capture_frames(SYNTH):
        session.ingest(fr)
    assert session.frame_count >= 10
    assert session.signal_rows()
    assert session.id_rate_rows()


def test_resolve_virtual_fixture() -> None:
    path = resolve_virtual_fixture()
    assert path.is_file()
    assert path.name == "idle_scenario.log"


def test_open_listen_without_python_can(monkeypatch: pytest.MonkeyPatch) -> None:
    import opendashcan.hw.listen as listen_mod

    monkeypatch.setattr(listen_mod, "python_can_available", lambda: False)

    # Force ImportError path inside open_listen_bus
    import builtins

    real_import = builtins.__import__

    def _block_can(name: str, *args: object, **kwargs: object):
        if name == "can" or name.startswith("can."):
            raise ImportError("blocked for test")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", _block_can)
    with pytest.raises(HardwareUnavailableError, match="python-can"):
        open_listen_bus(bustype="socketcan", channel="can0")


def test_cli_listen_virtual() -> None:
    from opendashcan.cli import main

    with pytest.raises(SystemExit) as exc:
        main(["listen", "--virtual", "--max-frames", "5", "--print-every", "100"])
    assert exc.value.code == 0


def test_cli_listen_capture() -> None:
    from opendashcan.cli import main

    with pytest.raises(SystemExit) as exc:
        main(
            [
                "listen",
                "--capture",
                str(SYNTH),
                "--vehicle",
                "honda.civic.gen10.us",
                "--max-frames",
                "8",
            ]
        )
    assert exc.value.code == 0


def test_python_can_available_is_bool() -> None:
    assert isinstance(python_can_available(), bool)
