"""Listen-only CAN open via python-can (optional ``opendashcan[hw]``).

Default policy: LinkMode.LISTEN_ONLY — never TX. ``send`` always refuses
unless the future TX guard (env + allowlist) would permit it — and even then
this bus wrapper still refuses unless explicitly constructed for TX (not exposed).
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from opendashcan.core.frame import BusRole, CANFrame, FrameDirection
from opendashcan.hardware.interfaces import LinkMode
from opendashcan.hw.tx_guard import assert_tx_permitted, refuse_send_message

# Interfaces we document for desktop listen (python-can bustype names).
SUPPORTED_BUSTYPES = ("socketcan", "pcan", "slcan", "virtual")

DEFAULT_BITRATE = 500_000
DEFAULT_VEHICLE = "honda.civic.gen10.us"

# Repo-relative synthetic fixture used by --virtual when no hardware.
_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VIRTUAL_FIXTURE = _REPO_ROOT / "captures" / "synthetic" / "idle_scenario.log"


class HardwareUnavailableError(RuntimeError):
    """Raised when python-can or the requested interface cannot be opened."""


def python_can_available() -> bool:
    try:
        import can  # noqa: F401
    except ImportError:
        return False
    return True


def _msg_to_frame(msg: Any, channel: str, bustype: str) -> CANFrame | None:
    if getattr(msg, "is_error_frame", False):
        return None
    return CANFrame(
        arbitration_id=int(msg.arbitration_id),
        data=bytes(msg.data),
        timestamp=float(msg.timestamp or 0.0),
        channel=channel,
        bus=BusRole.SOURCE,
        direction=FrameDirection.RX,
        is_extended=bool(getattr(msg, "is_extended_id", False)),
        meta={
            "format": bustype,
            "listen_only": "true",
            "tx_enabled": "false",
            "link_mode": LinkMode.LISTEN_ONLY.value,
        },
    )


class ListenOnlyBus:
    """Thin wrapper around a python-can Bus — RX only."""

    def __init__(
        self,
        bus: Any,
        *,
        channel: str,
        bustype: str,
        bitrate: int | None,
    ) -> None:
        self._bus = bus
        self.channel = channel
        self.bustype = bustype
        self.bitrate = bitrate
        self.link_mode = LinkMode.LISTEN_ONLY

    def recv(self, timeout: float | None = 1.0) -> CANFrame | None:
        msg = self._bus.recv(timeout=timeout)
        if msg is None:
            return None
        return _msg_to_frame(msg, self.channel, self.bustype)

    def send(self, frame: CANFrame) -> None:
        """Always refuse under default policy (LISTEN_ONLY)."""
        _ = frame
        assert_tx_permitted(
            frame.arbitration_id,
            allowlist=None,
            mode_label=self.link_mode.value,
        )
        # Even if env+allowlist were set, this listen wrapper never TX's.
        raise PermissionError(refuse_send_message())

    def shutdown(self) -> None:
        self._bus.shutdown()

    def __enter__(self) -> ListenOnlyBus:
        return self

    def __exit__(self, *exc: object) -> None:
        self.shutdown()


def open_listen_bus(
    *,
    bustype: str = "socketcan",
    channel: str = "can0",
    bitrate: int | None = DEFAULT_BITRATE,
) -> ListenOnlyBus:
    """Open a python-can interface for listen-only RX.

    Raises ``HardwareUnavailableError`` with a clear message when python-can
    is missing or the interface cannot be opened.
    """
    bustype_l = bustype.lower().strip()
    if bustype_l not in SUPPORTED_BUSTYPES:
        raise HardwareUnavailableError(
            f"Unsupported interface type {bustype!r}. "
            f"Supported: {', '.join(SUPPORTED_BUSTYPES)}"
        )
    try:
        import can  # type: ignore[import-untyped]
    except ImportError as exc:
        raise HardwareUnavailableError(
            "python-can is not installed. "
            'Install hardware support with:  pip install -e ".[hw]"\n'
            "Or use offline modes:  opendashcan listen --virtual\n"
            "                     opendashcan listen --capture path/to.log"
        ) from exc

    kwargs: dict[str, Any] = {
        "bustype": bustype_l,
        "channel": channel,
        "receive_own_messages": False,
        "fd": False,
    }
    # virtual bus ignores bitrate; socketcan may too if already up
    if bitrate is not None and bustype_l != "virtual":
        kwargs["bitrate"] = int(bitrate)

    # Prefer listen-only / silent where the backend supports it.
    if bustype_l == "pcan":
        kwargs.setdefault("fd", False)
    try:
        bus = can.interface.Bus(**kwargs)
    except Exception as exc:  # noqa: BLE001 — surface driver errors clearly
        raise HardwareUnavailableError(
            f"Could not open {bustype_l}:{channel} - {exc}\n"
            "Hints:\n"
            "  * Linux SocketCAN:  sudo ip link set can0 up type can bitrate 500000 listen-only on\n"
            "  * No adapter:       opendashcan listen --virtual\n"
            "  * Offline file:     opendashcan listen --capture captures/synthetic/idle_scenario.log\n"
            "  * Pi recorder:      see hardware/can_recorder_rpi/README.md"
        ) from exc

    return ListenOnlyBus(bus, channel=channel, bustype=bustype_l, bitrate=bitrate)


def iter_bus_frames(
    bus: ListenOnlyBus,
    *,
    max_frames: int | None = None,
) -> Iterator[CANFrame]:
    count = 0
    try:
        while max_frames is None or count < max_frames:
            frame = bus.recv(timeout=1.0)
            if frame is None:
                continue
            yield frame
            count += 1
    finally:
        bus.shutdown()


def iter_capture_frames(path: Path | str) -> Iterator[CANFrame]:
    """Replay an ASC/candump capture as RX frames (offline listen)."""
    from opendashcan.replay.reader import read_capture

    yield from read_capture(path)


def resolve_virtual_fixture(path: Path | str | None = None) -> Path:
    p = Path(path) if path else DEFAULT_VIRTUAL_FIXTURE
    if not p.is_file():
        raise FileNotFoundError(
            f"Virtual/synthetic fixture not found: {p}\n"
            "Expected captures/synthetic/idle_scenario.log in the repo, "
            "or pass --capture PATH."
        )
    return p
