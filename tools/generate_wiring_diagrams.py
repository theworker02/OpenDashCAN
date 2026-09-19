"""Generate OpenDashCAN wiring diagram PNGs (project-owned; not OEM art)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "assets" / "wiring"

BG = (16, 18, 22)
FG = (220, 224, 230)
AMBER = (230, 184, 77)
TEAL = (94, 196, 176)
MUTED = (139, 147, 158)
BOX = (34, 40, 48)
BORDER = (70, 80, 92)
DANGER = (240, 120, 120)


def _font(size: int) -> ImageFont.ImageFont:
    for name in (
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "segoeui.ttf",
        "arial.ttf",
        "DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


F = _font(18)
FS = _font(14)
FT = _font(22)


def _rounded(draw: ImageDraw.ImageDraw, xy, fill, outline, r: int = 10) -> None:
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=2)


def _arrow(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, color=TEAL) -> None:
    draw.line((x1, y1, x2, y2), fill=color, width=3)
    if x2 > x1:
        draw.polygon([(x2, y2), (x2 - 10, y2 - 6), (x2 - 10, y2 + 6)], fill=color)


def _label(draw: ImageDraw.ImageDraw, text: str, xy, f=F, fill=FG) -> None:
    draw.text(xy, text, font=f, fill=fill)


def _box_text(draw, x1, y1, x2, y2, text: str) -> None:
    lines = text.split("\n")
    ty = y1 + 36
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=FS)
        tw = bbox[2] - bbox[0]
        draw.text((x1 + (x2 - x1 - tw) // 2, ty), line, font=FS, fill=FG)
        ty += 22


def gen_obd() -> None:
    im = Image.new("RGB", (1100, 420), BG)
    d = ImageDraw.Draw(im)
    _label(d, "OBD -> adapter -> OpenDashCAN Desktop (LISTEN_ONLY)", (40, 24), FT, AMBER)
    _label(d, "Not affiliated with Honda Motor Co., Ltd.  |  No TX", (40, 56), FS, MUTED)
    boxes = [
        (40, 140, 240, 280, "OBD-II\npins 6/14 CAN\n4/5 GND"),
        (300, 140, 560, 280, "CAN adapter\nMCP2515 / PCAN\n/ slcan / SocketCAN"),
        (620, 140, 860, 280, "Host PC / Pi\ncandump RX"),
        (920, 140, 1060, 280, "OpenDashCAN\nDesktop\nLive tab"),
    ]
    for x1, y1, x2, y2, t in boxes:
        _rounded(d, (x1, y1, x2, y2), BOX, TEAL)
        _box_text(d, x1, y1, x2, y2, t)
    for x in (240, 560, 860):
        _arrow(d, x + 8, 210, x + 52, 210)
    _label(d, "DOCUMENTED: OBD HS-CAN pins (AiM/Racelogic/Pi design)", (40, 320), FS, MUTED)
    _label(
        d,
        "Confidence: listen path DOCUMENTED · cluster control NOT claimed",
        (40, 350),
        FS,
        AMBER,
    )
    im.save(OUT / "01_obd_listen_path.png")


def gen_dual() -> None:
    im = Image.new("RGB", (1100, 520), BG)
    d = ImageDraw.Draw(im)
    _label(d, "Conceptual dual-bus bridge — FUTURE / NO TX default", (40, 24), FT, AMBER)
    _label(
        d,
        "EncodeMode.NO_OUTPUT · DOCUMENTATION_ONLY · NOT a service manual",
        (40, 56),
        FS,
        MUTED,
    )
    _rounded(d, (40, 120, 320, 280), BOX, BORDER)
    _label(d, "Source vehicle", (60, 140), F, TEAL)
    _label(d, "F-CAN ~500k", (60, 175), FS)
    _label(d, "B-CAN ~33.3k", (60, 200), FS)
    _label(d, "Gateway pin map UNKNOWN", (60, 230), FS, AMBER)

    _rounded(d, (400, 140, 700, 300), BOX, AMBER)
    _label(d, "Adapter / bridge", (420, 160), F, AMBER)
    _label(d, "FUTURE capability", (420, 195), FS)
    _label(d, "Default: NO TX", (420, 220), FS, DANGER)
    _label(d, "LISTEN_ONLY today", (420, 245), FS, TEAL)

    _rounded(d, (780, 120, 1060, 280), BOX, BORDER)
    _label(d, "Donor cluster", (800, 140), F, TEAL)
    _label(d, "Digital gauge", (800, 175), FS)
    _label(d, "RX set UNKNOWN", (800, 205), FS, AMBER)
    _label(d, "REQUIRES_BENCH", (800, 235), FS, AMBER)

    _arrow(d, 320, 200, 392, 200)
    _arrow(d, 700, 200, 772, 200)
    _label(d, "Do not invent pinouts. Capture + bench before any TX path.", (40, 360), FS, MUTED)
    _label(d, "Vehicle-bus DBC != cluster RX confirmed.", (40, 390), FS, MUTED)
    im.save(OUT / "02_dual_bus_future.png")


def gen_harness() -> None:
    im = Image.new("RGB", (1100, 640), BG)
    d = ImageDraw.Draw(im)
    _label(d, "Harness interfaces (confidence-labeled)", (40, 24), FT, AMBER)
    _label(
        d,
        "Civic8->Civic10 style research checklist — not OEM instructions",
        (40, 56),
        FS,
        MUTED,
    )
    rows = [
        ("Power (+12V / ACC)", "REQUIRES_BENCH", AMBER),
        ("Ground", "REQUIRES_BENCH", AMBER),
        ("CAN-H / CAN-L", "DOCUMENTED bus / UNKNOWN cluster", TEAL),
        ("Ignition sense", "UNKNOWN", MUTED),
        ("Illumination / dimmer", "UNKNOWN", MUTED),
        ("Speakers / chimes", "UNKNOWN", MUTED),
        ("Immobilizer / gateway", "UNKNOWN / REQUIRES_BENCH", AMBER),
        ("ABS / SAS feeds", "DOCUMENTED vehicle / UNKNOWN RX", TEAL),
    ]
    y = 110
    for name, conf, color in rows:
        _rounded(d, (40, y, 1060, y + 50), BOX, BORDER, r=8)
        _label(d, name, (60, y + 14), F, FG)
        bbox = d.textbbox((0, 0), conf, font=FS)
        tw = bbox[2] - bbox[0]
        _label(d, conf, (1040 - tw - 20, y + 16), FS, color)
        y += 58
    _label(d, "OpenDashCAN Desktop -> Wiring tab  |  docs/wiring/", (40, 600), FS, MUTED)
    im.save(OUT / "03_harness_interfaces.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gen_obd()
    gen_dual()
    gen_harness()
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
