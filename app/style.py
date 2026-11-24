"""
Modern, Clean & Attractive Dark Theme for YT Video Downloader
"""

MODERN_STYLE = """
/* Global Window & Typography */
QMainWindow, QDialog {
    background-color: #0b0e14;
    color: #e2e8f0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #e2e8f0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    outline: none;
}

/* Surface Cards */
QFrame#card_input, QFrame#card_queue {
    background-color: #141824;
    border: 1px solid #232b3d;
    border-radius: 12px;
}

QGroupBox {
    background-color: #141824;
    border: 1px solid #232b3d;
    border-radius: 12px;
    margin-top: 10px;
    padding: 12px;
    font-weight: 600;
    font-size: 13px;
    color: #cbd5e1;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 14px;
    color: #818cf8;
    background-color: transparent;
}

/* Modern Segmented Tab Widget */
QTabWidget::pane {
    border: none;
    background-color: transparent;
    padding: 0px;
}

QTabBar {
    background-color: #0f121d;
    border-radius: 8px;
    padding: 3px;
    border: 1px solid #202738;
}

QTabBar::tab {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 6px;
    padding: 7px 20px;
    font-weight: 600;
    font-size: 12px;
    margin-right: 4px;
}

QTabBar::tab:hover {
    color: #f1f5f9;
    background-color: #1a2030;
}

QTabBar::tab:selected {
    background-color: #4f46e5;
    color: #ffffff;
    font-weight: 600;
}

/* Modern Text Inputs */
QPlainTextEdit, QLineEdit, QTextEdit {
    background-color: #1a2030;
    border: 1px solid #2a344d;
    border-radius: 8px;
    padding: 8px 12px;
    color: #f8fafc;
    font-size: 13px;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
}

QPlainTextEdit:focus, QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #6366f1;
    background-color: #1d2436;
}

QPlainTextEdit:disabled, QLineEdit:disabled {
    background-color: #101420;
    color: #64748b;
    border: 1px solid #1a2030;
}

/* Dropdown Combo Boxes */
QComboBox {
    background-color: #1a2030;
    border: 1px solid #2a344d;
    border-radius: 8px;
    padding: 6px 12px;
    color: #f8fafc;
    min-height: 22px;
    font-size: 13px;
    font-weight: 500;
}

QComboBox:hover {
    border: 1px solid #4f46e5;
    background-color: #1e2538;
}

QComboBox:focus {
    border: 1px solid #6366f1;
}

QComboBox:disabled {
    background-color: #101420;
    color: #64748b;
    border: 1px solid #1a2030;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94a3b8;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #181d2c;
    border: 1px solid #2d3752;
    border-radius: 8px;
    padding: 6px;
    color: #f8fafc;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
    outline: none;
}

/* Buttons */
QPushButton {
    background-color: #1e2436;
    color: #e2e8f0;
    border: 1px solid #2e3852;
    border-radius: 8px;
    padding: 7px 16px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #273047;
    border-color: #4f46e5;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #181e2e;
}

QPushButton:disabled {
    background-color: #121622;
    color: #475569;
    border-color: #1b2030;
}

/* Primary Action Button (Start Download) */
QPushButton#pb_download, QPushButton.btn-primary {
    background-color: #4f46e5;
    color: #ffffff;
    border: 1px solid #6366f1;
    font-weight: 700;
    font-size: 13px;
    border-radius: 8px;
    padding: 8px 24px;
}

QPushButton#pb_download:hover, QPushButton.btn-primary:hover {
    background-color: #4338ca;
    border-color: #818cf8;
}

QPushButton#pb_download:pressed, QPushButton.btn-primary:pressed {
    background-color: #3730a3;
}

QPushButton#pb_download:disabled {
    background-color: #1b2038;
    color: #475175;
    border-color: #242c47;
}

/* Success Button (Add to Queue) */
QPushButton#pb_add, QPushButton.btn-success {
    background-color: #059669;
    color: #ffffff;
    border: 1px solid #10b981;
    font-weight: 600;
    border-radius: 8px;
    padding: 7px 18px;
}

QPushButton#pb_add:hover, QPushButton.btn-success:hover {
    background-color: #047857;
    border-color: #34d399;
}

QPushButton#pb_add:disabled {
    background-color: #112620;
    color: #325e51;
    border-color: #16362d;
}

/* Danger / Clear Button */
QPushButton#pb_clear, QPushButton.btn-danger {
    background-color: #1c2030;
    color: #f87171;
    border: 1px solid #3d2a33;
    border-radius: 8px;
    padding: 7px 16px;
    font-weight: 600;
}

QPushButton#pb_clear:hover, QPushButton.btn-danger:hover {
    background-color: #dc2626;
    color: #ffffff;
    border-color: #ef4444;
}

/* Secondary Action Buttons (Paste / Clear Input) */
QPushButton.btn-subtle {
    background-color: #1a2030;
    color: #cbd5e1;
    border: 1px solid #2a344d;
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton.btn-subtle:hover {
    background-color: #242c42;
    border-color: #4f46e5;
    color: #ffffff;
}

/* TreeWidget and TableWidget */
QTreeWidget, QTableWidget {
    background-color: #141824;
    alternate-background-color: #171c2b;
    border: none;
    border-radius: 8px;
    color: #e2e8f0;
    gridline-color: #202638;
    outline: none;
}

QTreeWidget::item, QTableWidget::item {
    padding: 8px 6px;
    border-bottom: 1px solid #1a2030;
}

QTreeWidget::item:hover, QTableWidget::item:hover {
    background-color: #1f273d;
    color: #ffffff;
}

QTreeWidget::item:selected, QTableWidget::item:selected {
    background-color: #2b3552;
    color: #ffffff;
}

/* Table / Tree Header */
QHeaderView::section {
    background-color: #10131d;
    color: #94a3b8;
    padding: 9px 8px;
    border: none;
    border-bottom: 2px solid #232b3d;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QHeaderView::section:hover {
    color: #f1f5f9;
    background-color: #141824;
}

/* Progress Bar */
QProgressBar {
    background-color: #1a2030;
    border: 1px solid #263047;
    border-radius: 4px;
    height: 12px;
    text-align: center;
    font-size: 10px;
    font-weight: bold;
    color: #ffffff;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #06b6d4);
    border-radius: 3px;
}

/* Minimalist Scrollbars */
QScrollBar:vertical {
    background: #0f121d;
    width: 7px;
    margin: 0;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #2a344d;
    min-height: 25px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #4f46e5;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #0f121d;
    height: 7px;
    margin: 0;
    border-radius: 3px;
}

QScrollBar::handle:horizontal {
    background: #2a344d;
    min-width: 25px;
    border-radius: 3px;
}

QScrollBar::handle:horizontal:hover {
    background: #4f46e5;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Menu Bar */
QMenuBar {
    background-color: #0b0e14;
    color: #94a3b8;
    border-bottom: 1px solid #1a2030;
    padding: 3px 6px;
    font-size: 12px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #1a2030;
    color: #f8fafc;
}

QMenu {
    background-color: #141824;
    color: #e2e8f0;
    border: 1px solid #2a344d;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
    font-size: 13px;
}

QMenu::item:selected {
    background-color: #4f46e5;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #232b3d;
    margin: 4px 6px;
}

/* Status Bar */
QStatusBar {
    background-color: #080a0f;
    color: #64748b;
    border-top: 1px solid #161b26;
    font-size: 12px;
    padding: 2px 8px;
}

/* CheckBox */
QCheckBox {
    color: #cbd5e1;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #333f5c;
    background-color: #1a2030;
}

QCheckBox::indicator:hover {
    border-color: #6366f1;
}

QCheckBox::indicator:checked {
    background-color: #4f46e5;
    border-color: #6366f1;
}

/* Tooltips */
QToolTip {
    background-color: #181d2c;
    color: #f8fafc;
    border: 1px solid #3b4666;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
}

/* Labels */
QLabel {
    color: #cbd5e1;
}
"""
