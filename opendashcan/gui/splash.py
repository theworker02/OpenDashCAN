"""Cluster boot splash — Honda-style mark with trademark disclosure.

The splash intentionally evokes a Honda instrument-cluster power-on, not the
OpenDashCAN project logo.

OpenDashCAN does **not** redistribute Honda Motor Co., Ltd. trademark artwork
in this repository. The default emblem is a simplified geometric homage drawn
at runtime. You may optionally place a logo file you are licensed to use at::

    assets/third_party/honda_logo.png

That path is gitignored. See ``docs/TRADEMARKS.md``.
"""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget

from opendashcan import __version__

# Affiliation + trademark / copyright notice (shown on splash + About)
DISCLAIMER = "Not affiliated with, endorsed by, or sponsored by Honda Motor Co., Ltd."

TRADEMARK_NOTICE = (
    "Honda®, the Honda logo, and related marks are trademarks and/or "
    "copyrighted works of Honda Motor Co., Ltd. All rights reserved. "
    "Any Honda branding shown on this splash is for atmospheric / research "
    "context only; OpenDashCAN does not claim ownership of those marks."
)

DEFAULT_SPLASH_MS = 2200


def splash_disabled() -> bool:
    """True when splash should be skipped (tests / CI / user preference)."""
    val = os.environ.get("OPENDASHCAN_NO_SPLASH", "").strip().lower()
    return val in ("1", "true", "yes", "on")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repo_logo_path() -> Path | None:
    """OpenDashCAN project logo (window icon / About — not splash)."""
    root = repo_root()
    for name in ("assets/logo.png", "assets/logo-dark.png", "assets/banner.png"):
        path = root / name
        if path.is_file():
            return path
    return None


def rounded_logo_pixmap(
    path: Path | None = None,
    *,
    radius_frac: float = 0.22,
) -> QPixmap | None:
    """Load project logo and clip to a rounded rectangle (transparent corners).

    Brand PNGs are expected to already ship with alpha-rounded corners; this
    clips again so any square fallback (or stale RGB export) still renders as
    a badge in the window icon / About path.
    """
    logo = path if path is not None else repo_logo_path()
    if logo is None or logo.suffix.lower() != ".png":
        return None
    src = QPixmap(str(logo))
    if src.isNull():
        return None
    w, h = src.width(), src.height()
    if w < 1 or h < 1:
        return None
    radius = max(2.0, min(w, h) * float(radius_frac))
    out = QPixmap(w, h)
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    clip = QPainterPath()
    clip.addRoundedRect(QRectF(0, 0, w, h), radius, radius)
    painter.setClipPath(clip)
    painter.drawPixmap(0, 0, src)
    painter.end()
    return out


def honda_splash_logo_path() -> Path | None:
    """Optional user-supplied Honda logo (not shipped in git)."""
    root = repo_root()
    for name in (
        "assets/third_party/honda_logo.png",
        "assets/third_party/honda_logo.jpg",
        "assets/third_party/honda.png",
    ):
        path = root / name
        if path.is_file():
            return path
    return None


class _HondaEmblemWidget(QWidget):
    """Honda-style wing H (homage) or optional user-supplied logo file."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(220, 200)
        self._glow = 0.35
        self._pixmap: QPixmap | None = None
        logo = honda_splash_logo_path()
        if logo is not None:
            pm = QPixmap(str(logo))
            if not pm.isNull():
                self._pixmap = pm.scaled(
                    180,
                    120,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

    def _get_glow(self) -> float:
        return self._glow

    def _set_glow(self, value: float) -> None:
        self._glow = max(0.0, min(1.0, float(value)))
        self.update()

    glow = Property(float, _get_glow, _set_glow)

    def paintEvent(self, event) -> None:  # noqa: N802, ARG002
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        cx, cy = self.width() / 2, self.height() / 2
        # Soft white wake — cluster ignition feel
        grad = QRadialGradient(cx, cy, 105)
        a = int(20 + 160 * self._glow)
        grad.setColorAt(0.0, QColor(255, 255, 255, a))
        grad.setColorAt(0.45, QColor(200, 210, 220, int(a * 0.25)))
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx - 105, cy - 105, 210, 210))

        p.setOpacity(0.5 + 0.5 * self._glow)
        if self._pixmap is not None:
            x = int(cx - self._pixmap.width() / 2)
            y = int(cy - self._pixmap.height() / 2)
            p.drawPixmap(x, y, self._pixmap)
        else:
            self._paint_wing_h(p, cx, cy)
        p.setOpacity(1.0)
        p.end()

    def _paint_wing_h(self, p: QPainter, cx: float, cy: float) -> None:
        """Simplified wing-H homage (not an official asset file)."""
        ink = QColor(245, 247, 250)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(ink)

        # Left upright + wing flare
        p.drawRoundedRect(QRectF(cx - 48, cy - 42, 18, 84), 2, 2)
        p.drawRoundedRect(QRectF(cx - 70, cy - 28, 28, 12), 2, 2)
        p.drawRoundedRect(QRectF(cx - 70, cy + 16, 28, 12), 2, 2)

        # Right upright + wing flare
        p.drawRoundedRect(QRectF(cx + 30, cy - 42, 18, 84), 2, 2)
        p.drawRoundedRect(QRectF(cx + 42, cy - 28, 28, 12), 2, 2)
        p.drawRoundedRect(QRectF(cx + 42, cy + 16, 28, 12), 2, 2)

        # Crossbar
        p.drawRoundedRect(QRectF(cx - 36, cy - 8, 72, 16), 2, 2)

        # Thin outer ring (cluster bezel cue)
        pen = QPen(QColor(255, 255, 255, int(80 + 100 * self._glow)))
        pen.setWidthF(1.5)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - 78, cy - 78, 156, 156))


class BootSplash(QWidget):
    """Dark Honda-style boot splash; emits ``finished`` when ready."""

    finished = Signal()

    def __init__(
        self,
        *,
        duration_ms: int = DEFAULT_SPLASH_MS,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SplashScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedSize(540, 420)
        self.setStyleSheet("background-color: #050607;")
        self._duration_ms = max(400, int(duration_ms))
        self._closed = False
        self.logo_path = honda_splash_logo_path()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 20)
        lay.setSpacing(6)
        lay.addStretch(1)

        self._emblem = _HondaEmblemWidget()
        lay.addWidget(self._emblem, alignment=Qt.AlignmentFlag.AlignHCenter)

        brand = QLabel("HONDA")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        brand.setStyleSheet("color: #f5f7fa; letter-spacing: 10px; background: transparent;")
        lay.addWidget(brand)

        cue = QLabel("IGNITION")
        cue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cue.setStyleSheet(
            "color: #9aa3ad; font-size: 11px; letter-spacing: 6px; "
            "font-weight: 600; background: transparent;"
        )
        lay.addWidget(cue)

        lay.addSpacing(8)

        tool = QLabel("OpenDashCAN Desktop")
        tool.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tool.setStyleSheet(
            "color: #c4a35a; font-size: 12px; font-weight: 600; background: transparent;"
        )
        lay.addWidget(tool)

        mode = QLabel("LISTEN_ONLY · RESEARCH")
        mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mode.setStyleSheet("color: #6a727c; font-size: 11px; background: transparent;")
        lay.addWidget(mode)

        lay.addStretch(1)

        disc = QLabel(DISCLAIMER)
        disc.setWordWrap(True)
        disc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        disc.setStyleSheet(
            "color: #7a828c; font-size: 10px; background: transparent; padding: 0 12px;"
        )
        lay.addWidget(disc)

        tm = QLabel(TRADEMARK_NOTICE)
        tm.setWordWrap(True)
        tm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tm.setStyleSheet(
            "color: #5a626c; font-size: 9px; background: transparent; padding: 0 14px;"
        )
        lay.addWidget(tm)

        ver = QLabel(f"v{__version__}")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("color: #3a424c; font-size: 10px; background: transparent;")
        lay.addWidget(ver)

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)

        self._fade_in = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade_in.setDuration(500)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._glow_anim = QPropertyAnimation(self._emblem, b"glow", self)
        self._glow_anim.setDuration(1200)
        self._glow_anim.setStartValue(0.12)
        self._glow_anim.setEndValue(1.0)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        self._finish_timer = QTimer(self)
        self._finish_timer.setSingleShot(True)
        self._finish_timer.timeout.connect(self._complete)

    def start(self) -> None:
        self.show()
        self.raise_()
        self._fade_in.start()
        self._glow_anim.start()
        self._finish_timer.start(self._duration_ms)

    def _complete(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.finished.emit()
        self.close()

    def skip(self) -> None:
        """Abort animation and finish immediately (tests / capture)."""
        self._finish_timer.stop()
        self._fade_in.stop()
        self._glow_anim.stop()
        self._opacity.setOpacity(1.0)
        self._emblem.glow = 1.0
        self._complete()
