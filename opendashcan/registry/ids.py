"""Canonical dotted platform / cluster / adapter ID helpers.

Canonical forms (Phase 2/3):
  honda.civic.gen8.us
  honda.civic.gen8.us.r18.auto
  honda.civic.gen10.cluster.digital
  adapter: honda.civic.gen8.us.r18.auto__to__honda.civic.gen10.cluster.digital

Legacy aliases (honda_civic_8th_gen, honda:civic:8, honda-civic8) still resolve.
"""

from __future__ import annotations

import contextlib
import re
from pathlib import Path

_DOTTED_PLATFORM_RE = re.compile(
    r"^(?P<mfr>[a-z0-9_]+)\.(?P<model>[a-z0-9_]+)\.gen(?P<gen>[a-z0-9_]+)"
    r"\.(?P<market>[a-z0-9_]+)(?:\.(?P<rest>.+))?$"
)

_COLON_PLATFORM_RE = re.compile(
    r"^(?P<mfr>[a-z0-9_]+):(?P<model>[a-z0-9_]+):(?:gen)?(?P<gen>[a-z0-9_]+)$"
)

LEGACY_ALIASES: dict[str, str] = {
    "honda_civic_8th_gen": "honda.civic.gen8.us",
    "honda_civic_10th_gen": "honda.civic.gen10.us",
    "honda-civic8": "honda.civic.gen8.us",
    "honda-civic10": "honda.civic.gen10.us",
    "honda:civic:7": "honda.civic.gen7.us",
    "honda-civic7": "honda.civic.gen7.us",
    "honda_civic_7th_gen": "honda.civic.gen7.us",
    "honda:civic:8": "honda.civic.gen8.us",
    "honda:civic:9": "honda.civic.gen9.us",
    "honda:civic:10": "honda.civic.gen10.us",
    "honda:civic:11": "honda.civic.gen11.us",
    "honda-civic11": "honda.civic.gen11.us",
    "honda:accord:10": "honda.accord.gen10.us",
    "honda:accord:11": "honda.accord.gen11.us",
    "honda-accord11": "honda.accord.gen11.us",
    "honda:crv:5": "honda.crv.gen5.us",
    "honda:crv:6": "honda.crv.gen6.us",
    "honda-crv6": "honda.crv.gen6.us",
    "honda:fit:3": "honda.fit.gen3.us",
    "honda:insight:3": "honda.insight.gen3.us",
    "honda_insight_3rd_gen": "honda.insight.gen3.us",
    "honda:element:1": "honda.element.gen1.us",
    "honda:hrv:2": "honda.hrv.gen2.us",
    "honda:pilot:3": "honda.pilot.gen3.us",
    "honda:pilot:4": "honda.pilot.gen4.us",
    "honda-pilot4": "honda.pilot.gen4.us",
    "honda:odyssey:5": "honda.odyssey.gen5.us",
    "honda:ridgeline:2": "honda.ridgeline.gen2.us",
    "honda:prelude:5": "honda.prelude.gen5.us",
    "honda:civic:8:r18:auto": "honda.civic.gen8.us.r18.auto",
    "honda:civic:10:digital": "honda.civic.gen10.cluster.digital",
    "honda:civic:11:digital": "honda.civic.gen11.cluster.digital",
    "honda:accord:10:digital": "honda.accord.gen10.cluster.digital",
    "honda:crv:5:digital": "honda.crv.gen5.cluster.digital",
}

CLUSTER_TO_PLATFORM: dict[str, str] = {
    "honda.civic.gen10.cluster.digital": "honda.civic.gen10.us",
    "honda.civic.gen11.cluster.digital": "honda.civic.gen11.us",
    "honda.accord.gen10.cluster.digital": "honda.accord.gen10.us",
    "honda.crv.gen5.cluster.digital": "honda.crv.gen5.us",
    "honda:civic:10:digital": "honda.civic.gen10.us",
    "honda:civic:11:digital": "honda.civic.gen11.us",
    "honda:accord:10:digital": "honda.accord.gen10.us",
    "honda:crv:5:digital": "honda.crv.gen5.us",
}

LEGACY_CLUSTER_IDS: dict[str, str] = {
    "honda:civic:10:digital": "honda.civic.gen10.cluster.digital",
    "honda:civic:11:digital": "honda.civic.gen11.cluster.digital",
    "honda:accord:10:digital": "honda.accord.gen10.cluster.digital",
    "honda:crv:5:digital": "honda.crv.gen5.cluster.digital",
}


def colon_to_dotted_platform(mfr: str, model: str, gen: str, market: str = "us") -> str:
    gen_s = str(gen).removeprefix("gen")
    return f"{mfr}.{model}.gen{gen_s}.{market}"


def platform_to_cluster_id(platform_id: str, display: str = "digital") -> str:
    """honda.civic.gen10.us → honda.civic.gen10.cluster.digital"""
    parts = platform_id.split(".")
    if len(parts) < 4:
        return f"{platform_id}.cluster.{display}"
    # mfr.model.genN.market → mfr.model.genN.cluster.display
    return f"{parts[0]}.{parts[1]}.{parts[2]}.cluster.{display}"


def normalize_platform_id(raw: str, *, default_market: str = "us") -> str:
    """Resolve any accepted id form to a canonical dotted *platform* id."""
    key = raw.strip().lower()
    if key in LEGACY_ALIASES:
        resolved = LEGACY_ALIASES[key]
        return CLUSTER_TO_PLATFORM.get(resolved, resolved)
    if key in CLUSTER_TO_PLATFORM:
        return CLUSTER_TO_PLATFORM[key]
    if key in LEGACY_CLUSTER_IDS:
        return CLUSTER_TO_PLATFORM[LEGACY_CLUSTER_IDS[key]]

    dotted = raw.strip().lower().replace("/", ".").replace("-", ".").replace(":", ".")
    # honda.civic.8.us → honda.civic.gen8.us
    parts = dotted.split(".")
    if len(parts) >= 3 and parts[2].isdigit():
        parts[2] = f"gen{parts[2]}"
        dotted = ".".join(parts)

    if dotted in LEGACY_ALIASES:
        resolved = LEGACY_ALIASES[dotted]
        return CLUSTER_TO_PLATFORM.get(resolved, resolved)
    if dotted in CLUSTER_TO_PLATFORM:
        return CLUSTER_TO_PLATFORM[dotted]
    if dotted in LEGACY_CLUSTER_IDS:
        return CLUSTER_TO_PLATFORM[LEGACY_CLUSTER_IDS[dotted]]

    # Full variant id → strip to base platform (first 4 segments)
    m = _DOTTED_PLATFORM_RE.match(dotted)
    if m:
        return f"{m.group('mfr')}.{m.group('model')}.gen{m.group('gen')}.{m.group('market')}"

    # Cluster dotted form
    if ".cluster." in dotted:
        # honda.civic.gen10.cluster.digital → honda.civic.gen10.us
        segs = dotted.split(".")
        if len(segs) >= 4:
            return f"{segs[0]}.{segs[1]}.{segs[2]}.{default_market}"

    colon_key = raw.strip().lower().replace("/", ":").replace("-", ":").replace(":gen", ":")
    if colon_key in LEGACY_ALIASES:
        resolved = LEGACY_ALIASES[colon_key]
        return CLUSTER_TO_PLATFORM.get(resolved, resolved)
    cm = _COLON_PLATFORM_RE.match(colon_key)
    if cm:
        return colon_to_dotted_platform(
            cm.group("mfr"), cm.group("model"), cm.group("gen"), default_market
        )

    raise KeyError(
        f"invalid platform id: {raw!r} "
        f"(expected honda.model.genN.market or legacy honda:model:N)"
    )


def normalize_cluster_id(raw: str) -> str:
    """Resolve to canonical dotted cluster id."""
    key = raw.strip().lower()
    if key in LEGACY_CLUSTER_IDS:
        return LEGACY_CLUSTER_IDS[key]
    if key in LEGACY_ALIASES and ".cluster." in LEGACY_ALIASES[key]:
        return LEGACY_ALIASES[key]
    dotted = key.replace("/", ".").replace("-", ".").replace(":", ".")
    if dotted in LEGACY_CLUSTER_IDS:
        return LEGACY_CLUSTER_IDS[dotted]
    if ".cluster." in dotted:
        return dotted
    # Platform shorthand → default digital cluster
    try:
        pid = normalize_platform_id(raw)
        return platform_to_cluster_id(pid)
    except KeyError:
        return dotted


def normalize_variant_id(raw: str) -> str:
    """Resolve variant ids (may be longer than base platform)."""
    key = raw.strip().lower()
    if key in LEGACY_ALIASES:
        return LEGACY_ALIASES[key]
    dotted = key.replace("/", ".").replace("-", ".").replace(":", ".")
    if dotted in LEGACY_ALIASES:
        return LEGACY_ALIASES[dotted]
    # honda.civic.8.us.r18.auto → insert gen
    parts = dotted.split(".")
    if len(parts) >= 3 and parts[2].isdigit():
        parts[2] = f"gen{parts[2]}"
        dotted = ".".join(parts)
    return dotted


def adapter_id(source: str, target: str) -> str:
    s = normalize_variant_id(source)
    t = normalize_variant_id(target)
    if ".cluster." not in t:
        with contextlib.suppress(Exception):
            t = normalize_cluster_id(t)
    return f"{s}__to__{t}"


def infer_platform_id_from_path(package_dir: Path) -> str | None:
    """Derive honda.civic.gen8.us from .../honda/civic/gen8/us or .../gen8/2006_2011."""
    parts = Path(package_dir).parts
    try:
        protocols_idx = parts.index("protocols")
        mfr = parts[protocols_idx + 1]
        model = parts[protocols_idx + 2]
        gen_dir = parts[protocols_idx + 3]
        market_or_years = parts[protocols_idx + 4] if len(parts) > protocols_idx + 4 else "us"
    except (ValueError, IndexError):
        return None
    gen = gen_dir.removeprefix("gen")
    market = "us" if re.fullmatch(r"\d{4}_\d{4}", market_or_years) else market_or_years.lower()
    return colon_to_dotted_platform(mfr, model, gen, market)
