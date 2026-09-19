"""Transmit guard — TX stays disabled unless explicit future opt-in.

Default: refuse all sends. Future-only path requires:

1. Environment flag ``OPENDASHCAN_ALLOW_TX=1``
2. A non-empty arbitration-ID allowlist
3. Caller still opts into bidirectional / ENABLED mode

This does **not** enable hardware TX today; it only documents the gate.
"""

from __future__ import annotations

import os
from collections.abc import Collection

# Future-only. Documented in docs/safety.md and README.
TX_ENV_FLAG = "OPENDASHCAN_ALLOW_TX"


def tx_env_enabled() -> bool:
    """True only when OPENDASHCAN_ALLOW_TX is set to a truthy value."""
    raw = os.environ.get(TX_ENV_FLAG, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def assert_tx_permitted(
    arbitration_id: int,
    *,
    allowlist: Collection[int] | None = None,
    mode_label: str = "listen_only",
) -> None:
    """Raise PermissionError unless env flag + allowlist permit this ID.

    Always raises under default install (no env, empty allowlist).
    """
    if not tx_env_enabled():
        raise PermissionError(
            f"TX refused: set {TX_ENV_FLAG}=1 only for future allowlisted bench work "
            f"(current mode={mode_label}). Default is LISTEN_ONLY / no transmit."
        )
    allowed = set(allowlist or ())
    if not allowed:
        raise PermissionError(
            "TX refused: allowlist is empty. Future TX requires an explicit "
            "arbitration-ID allowlist in addition to the env flag."
        )
    if arbitration_id not in allowed:
        raise PermissionError(
            f"TX refused: ID {hex(arbitration_id)} not in allowlist "
            f"({sorted(hex(x) for x in allowed)})"
        )


def refuse_send_message() -> str:
    """Short user-facing refusal string for CLI/GUI."""
    return (
        "LISTEN ONLY - transmit disabled. "
        f"Future TX (not enabled): {TX_ENV_FLAG}=1 AND a non-empty ID allowlist."
    )
