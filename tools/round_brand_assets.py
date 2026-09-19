"""Apply rounded-rect alpha masks to OpenDashCAN brand PNGs.

Leaves transparent corners so README / window icons are not opaque squares.

Usage:
  python tools/round_brand_assets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# Generous corner radius as a fraction of the shorter side (~squircle / app-icon).
RADIUS_FRAC = 0.22


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def round_png(path: Path, *, radius_frac: float = RADIUS_FRAC) -> None:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    radius = max(8, int(min(w, h) * radius_frac))
    mask = _rounded_mask((w, h), radius)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask=mask)
    out.save(path, "PNG", optimize=True)
    print(f"rounded {path.relative_to(ROOT)} ({w}x{h}, r={radius})")


def main() -> int:
    targets = [
        ASSETS / "logo.png",
        ASSETS / "logo-dark.png",
        ASSETS / "banner.png",
    ]
    for path in targets:
        if not path.is_file():
            print(f"skip missing {path.relative_to(ROOT)}")
            continue
        round_png(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
