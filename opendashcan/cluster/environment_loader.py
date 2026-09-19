"""Load isolated cluster environment YAML packages under clusters/."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CLUSTERS_ROOT = REPO_ROOT / "clusters"

# Short CLI aliases → directory names under clusters/
CLUSTER_ALIASES: dict[str, str] = {
    "civic10": "civic10",
    "civic11": "civic11",
    "accord10": "accord10",
    "crv5": "crv5",
    "honda.civic.gen10.cluster.digital": "civic10",
    "honda.civic.gen11.cluster.digital": "civic11",
    "honda.accord.gen10.cluster.digital": "accord10",
    "honda.crv.gen5.cluster.digital": "crv5",
    "honda.civic.gen10.us": "civic10",
    "honda.civic.gen11.us": "civic11",
    "honda.accord.gen10.us": "accord10",
    "honda.crv.gen5.us": "crv5",
}


def resolve_cluster_key(name: str) -> str:
    key = CLUSTER_ALIASES.get(name, name)
    if key not in {"civic10", "civic11", "accord10", "crv5"}:
        # Allow direct directory name
        if (CLUSTERS_ROOT / name).is_dir():
            return name
        raise KeyError(f"unknown cluster env: {name!r}")
    return key


@dataclass
class ClusterEnvPackage:
    key: str
    path: Path
    environment: dict[str, Any] = field(default_factory=dict)
    requirements: dict[str, Any] = field(default_factory=dict)
    rx_messages: dict[str, Any] = field(default_factory=dict)
    startup: dict[str, Any] = field(default_factory=dict)
    integrity: dict[str, Any] = field(default_factory=dict)

    @property
    def cluster_id(self) -> str:
        return str(self.environment.get("cluster_id") or self.key)

    @property
    def platform_id(self) -> str | None:
        return self.environment.get("platform_id")

    def requirement_rows(self) -> list[dict[str, Any]]:
        return list(self.requirements.get("requirements") or [])

    def rx_rows(self) -> list[dict[str, Any]]:
        return list(self.rx_messages.get("messages") or [])


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def load_cluster_env(name: str, *, root: Path | None = None) -> ClusterEnvPackage:
    key = resolve_cluster_key(name)
    base = (root or CLUSTERS_ROOT) / key
    if not base.is_dir():
        raise KeyError(f"cluster env directory missing: {base}")
    return ClusterEnvPackage(
        key=key,
        path=base,
        environment=_load_yaml(base / "environment.yaml"),
        requirements=_load_yaml(base / "requirements.yaml"),
        rx_messages=_load_yaml(base / "rx_messages.yaml"),
        startup=_load_yaml(base / "startup.yaml"),
        integrity=_load_yaml(base / "integrity.yaml"),
    )


def list_cluster_envs(*, root: Path | None = None) -> list[str]:
    base = root or CLUSTERS_ROOT
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir() and (p / "environment.yaml").is_file())
