"""Dark automotive stylesheet — charcoal chrome, amber + teal accents.

Not purple Material defaults. High-contrast tables for garage/laptop use.
Qt-free module so smoke tests import without a display.
"""

from __future__ import annotations

# Charcoal tool chrome + amber status + teal documentation accents.
STYLESHEET = """
QWidget {
    background-color: #1a1d21;
    color: #d6d8de;
    font-family: "Segoe UI", "Cascadia Mono", "Consolas", sans-serif;
    font-size: 13px;
}
QMainWindow {
    background-color: #121416;
}
QToolTip {
    background-color: #2a3038;
    color: #e8ecf0;
    border: 1px solid #5a6570;
    padding: 4px 8px;
}
QLabel#Banner {
    background-color: #2a2214;
    color: #e6b84d;
    border: 1px solid #5a4820;
    border-radius: 2px;
    padding: 8px 12px;
    font-weight: 600;
}
QLabel#ListenBanner {
    background-color: #3a1818;
    color: #f0a0a0;
    border: 2px solid #a04040;
    border-radius: 2px;
    padding: 10px 14px;
    font-weight: 800;
    font-size: 14px;
    letter-spacing: 0.6px;
}
QLabel#Title {
    color: #f0f2f5;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.2px;
}
QLabel#Subtitle {
    color: #8b939e;
    font-size: 12px;
}
QLabel#SectionHeader {
    color: #c4a35a;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.4px;
    padding-top: 2px;
}
QLabel#ModeTag {
    background-color: #3a2e12;
    color: #f0c14b;
    border: 1px solid #6a5420;
    padding: 4px 10px;
    font-weight: 700;
    font-size: 11px;
}
QLabel#StatusIdle {
    color: #8b939e;
}
QLabel#StatusLive {
    color: #5ec4b0;
    font-weight: 600;
}
QLabel#StatusError {
    color: #e07070;
    font-weight: 600;
}
QTreeWidget, QTableWidget, QListWidget, QTextEdit, QPlainTextEdit {
    background-color: #101214;
    alternate-background-color: #171a1e;
    border: 1px solid #2c3138;
    selection-background-color: #2f4a4a;
    selection-color: #ffffff;
    gridline-color: #2c3138;
}
QHeaderView::section {
    background-color: #22262c;
    color: #aeb6c0;
    border: 1px solid #2c3138;
    padding: 5px 7px;
    font-weight: 600;
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #101214;
    border: 1px solid #3a424c;
    padding: 5px 8px;
    selection-background-color: #2f4a4a;
    min-height: 22px;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox QAbstractItemView {
    background-color: #1a1d21;
    selection-background-color: #2f4a4a;
    border: 1px solid #3a424c;
}
QPushButton {
    background-color: #2a3038;
    border: 1px solid #454e59;
    color: #e8ecf0;
    padding: 6px 12px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #343c46;
    border-color: #c4a35a;
}
QPushButton:pressed {
    background-color: #1e2329;
}
QPushButton:disabled {
    color: #5a626c;
    border-color: #30363e;
    background-color: #22262c;
}
QPushButton#Primary {
    background-color: #3d3420;
    border-color: #c4a35a;
    color: #f5e6c0;
    font-weight: 600;
}
QPushButton#Teal {
    background-color: #1e3330;
    border-color: #3d8f82;
    color: #b8e8de;
    font-weight: 600;
}
QPushButton#Danger {
    background-color: #3a2020;
    border-color: #a05050;
    color: #f0c0c0;
}
QTabWidget::pane {
    border: 1px solid #2c3138;
    background: #1a1d21;
    top: -1px;
}
QTabBar::tab {
    background: #22262c;
    color: #9aa3ad;
    border: 1px solid #2c3138;
    padding: 8px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #2a323c;
    color: #f0f2f5;
    border-bottom: 2px solid #c4a35a;
}
QTabBar::tab:hover:!selected {
    color: #d0d6de;
    border-color: #3d8f82;
}
QSplitter::handle {
    background: #2c3138;
    width: 3px;
    height: 3px;
}
QStatusBar {
    background: #121416;
    color: #8b939e;
    border-top: 1px solid #2c3138;
}
QStatusBar QLabel {
    padding: 0 6px;
}
QGroupBox {
    border: 1px solid #2c3138;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: #c4a35a;
}
QScrollBar:vertical {
    background: #121416;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #3a424c;
    min-height: 24px;
    border-radius: 2px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #121416;
    height: 10px;
}
QScrollBar::handle:horizontal {
    background: #3a424c;
    min-width: 24px;
    border-radius: 2px;
}
QMenuBar {
    background: #121416;
    color: #c8ced6;
    border-bottom: 1px solid #2c3138;
}
QMenuBar::item:selected {
    background: #2a3038;
}
QMenu {
    background: #1a1d21;
    border: 1px solid #2c3138;
}
QMenu::item:selected {
    background: #2f4a4a;
}
"""

# Hex colors for confidence / knowledge badges (applied in widgets).
CONFIDENCE_COLORS = {
    "high": "#5ec4b0",  # teal — documented / verified
    "mid": "#e6b84d",  # amber — community / partial
    "low": "#c09060",  # copper — inferred
    "unknown": "#8b939e",
}
