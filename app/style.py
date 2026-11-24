"""
Modern Dark Theme for YT Video Downloader
"""

MODERN_STYLE = """
QMainWindow, QDialog {
    background-color: #0f111a;
    color: #e2e8f0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #e2e8f0;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* Card / GroupBox */
QGroupBox {
    background-color: #161824;
    border: 1px solid #26293d;
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px;
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

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #26293d;
    background-color: #161824;
    border-radius: 8px;
    padding: 10px;
    top: -1px;
}

QTabBar::tab {
    background-color: #12141f;
    color: #94a3b8;
    border: 1px solid #26293d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 7px 18px;
    font-weight: 500;
    margin-right: 4px;
}

QTabBar::tab:hover {
    background-color: #1e2238;
    color: #f1f5f9;
}

QTabBar::tab:selected {
    background-color: #161824;
    color: #818cf8;
    border-color: #4338ca;
    border-bottom: 2px solid #6366f1;
    font-weight: 600;
}

/* Text Inputs */
QPlainTextEdit, QLineEdit, QTextEdit {
    background-color: #1a1d2e;
    border: 1px solid #2e334d;
    border-radius: 7px;
    padding: 6px 10px;
    color: #f8fafc;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
}

QPlainTextEdit:focus, QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #6366f1;
    background-color: #1e2238;
}

QPlainTextEdit:disabled, QLineEdit:disabled {
    background-color: #12141f;
    color: #64748b;
    border: 1px solid #1e2235;
}

/* Combo Box */
QComboBox {
    background-color: #1a1d2e;
    border: 1px solid #2e334d;
    border-radius: 7px;
    padding: 6px 12px;
    color: #f8fafc;
    min-height: 20px;
}

QComboBox:hover {
    border: 1px solid #4338ca;
    background-color: #1e2238;
}

QComboBox:focus {
    border: 1px solid #6366f1;
}

QComboBox:disabled {
    background-color: #12141f;
    color: #64748b;
    border: 1px solid #1e2235;
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
    background-color: #181b2c;
    border: 1px solid #313652;
    border-radius: 6px;
    padding: 4px;
    color: #f8fafc;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
    outline: none;
}

/* Push Buttons */
QPushButton {
    background-color: #23273e;
    color: #e2e8f0;
    border: 1px solid #333956;
    border-radius: 7px;
    padding: 6px 14px;
    font-weight: 500;
    min-height: 18px;
}

QPushButton:hover {
    background-color: #2e3352;
    border-color: #4f46e5;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #1a1d2e;
}

QPushButton:disabled {
    background-color: #141724;
    color: #475569;
    border-color: #1e2235;
}

/* Primary Action Buttons */
QPushButton#pb_download, QPushButton.btn-primary {
    background-color: #4f46e5;
    color: #ffffff;
    border: 1px solid #6366f1;
    font-weight: 600;
}

QPushButton#pb_download:hover, QPushButton.btn-primary:hover {
    background-color: #4338ca;
    border-color: #818cf8;
}

QPushButton#pb_download:disabled {
    background-color: #1f233d;
    color: #4b5280;
    border-color: #272d4d;
}

/* Success Button */
QPushButton.btn-success, QPushButton#pb_add {
    background-color: #10b981;
    color: #ffffff;
    border: 1px solid #34d399;
    font-weight: 600;
}

QPushButton.btn-success:hover, QPushButton#pb_add:hover {
    background-color: #059669;
    border-color: #6ee7b7;
}

/* Danger Button */
QPushButton#pb_clear, QPushButton.btn-danger {
    background-color: #23273e;
    color: #f87171;
    border: 1px solid #3b2c3a;
}

QPushButton#pb_clear:hover, QPushButton.btn-danger:hover {
    background-color: #dc2626;
    color: #ffffff;
    border-color: #ef4444;
}

/* TreeWidget and TableWidget */
QTreeWidget, QTableWidget {
    background-color: #161824;
    alternate-background-color: #1a1d2c;
    border: 1px solid #26293d;
    border-radius: 8px;
    color: #e2e8f0;
    gridline-color: #23263a;
    outline: none;
}

QTreeWidget::item, QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #1c1f30;
}

QTreeWidget::item:hover, QTableWidget::item:hover {
    background-color: #23273f;
    color: #ffffff;
}

QTreeWidget::item:selected, QTableWidget::item:selected {
    background-color: #313759;
    color: #ffffff;
}

/* Header */
QHeaderView::section {
    background-color: #12141f;
    color: #94a3b8;
    padding: 8px 6px;
    border: none;
    border-bottom: 2px solid #26293d;
    font-weight: 600;
    font-size: 12px;
}

QHeaderView::section:hover {
    color: #f1f5f9;
    background-color: #171a28;
}

/* Progress Bar */
QProgressBar {
    background-color: #1a1d2e;
    border: 1px solid #2e334d;
    border-radius: 4px;
    height: 14px;
    text-align: center;
    font-size: 11px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 2px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #06b6d4);
    border-radius: 3px;
}

/* Scroll Bars */
QScrollBar:vertical {
    background: #12141f;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #333956;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4f46e5;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #12141f;
    height: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #333956;
    min-width: 25px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: #4f46e5;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Menu Bar */
QMenuBar {
    background-color: #0f111a;
    color: #94a3b8;
    border-bottom: 1px solid #1e2235;
    padding: 2px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #1e2238;
    color: #f8fafc;
}

QMenu {
    background-color: #161824;
    color: #e2e8f0;
    border: 1px solid #2e334d;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #4f46e5;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #26293d;
    margin: 4px 6px;
}

/* Status Bar */
QStatusBar {
    background-color: #0c0e15;
    color: #64748b;
    border-top: 1px solid #1a1d2c;
    font-size: 12px;
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
    border: 1px solid #3b4263;
    background-color: #1a1d2e;
}

QCheckBox::indicator:hover {
    border-color: #6366f1;
}

QCheckBox::indicator:checked {
    background-color: #4f46e5;
    border-color: #6366f1;
    image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E");
}

/* Tooltips */
QToolTip {
    background-color: #1e2238;
    color: #f8fafc;
    border: 1px solid #4338ca;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
}

/* Labels */
QLabel {
    color: #cbd5e1;
}
"""

