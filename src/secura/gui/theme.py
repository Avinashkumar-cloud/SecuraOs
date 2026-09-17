"""Modern cybersecurity dark theme stylesheet (QSS) for Secura Center."""

DARK_CYBER_THEME = """
QMainWindow, QDialog, QWidget {
    background-color: #0B0F19;
    color: #E2E8F0;
    font-family: 'Segoe UI', 'Ubuntu', 'DejaVu Sans', sans-serif;
    font-size: 13px;
}

/* Tab Widget Styling */
QTabWidget::pane {
    border: 1px solid #1E293B;
    background-color: #0F172A;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #111827;
    color: #94A3B8;
    padding: 10px 20px;
    margin-right: 3px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
}

QTabBar::tab:hover {
    background-color: #1F2937;
    color: #38BDF8;
}

QTabBar::tab:selected {
    background-color: #0F172A;
    color: #00F0FF;
    border-bottom: 2px solid #00F0FF;
}

/* GroupBox / Card Styling */
QGroupBox {
    border: 1px solid #1E293B;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 18px;
    background-color: #111827;
    font-weight: bold;
    color: #38BDF8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    background-color: #111827;
    border-radius: 4px;
}

/* Buttons */
QPushButton {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #0284C7;
    border-color: #38BDF8;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #0369A1;
}

QPushButton:disabled {
    background-color: #1E293B;
    color: #64748B;
    border-color: #334155;
}

/* Special Primary Accent Button */
QPushButton#primaryBtn {
    background-color: #0284C7;
    border: 1px solid #38BDF8;
    color: #FFFFFF;
}

QPushButton#primaryBtn:hover {
    background-color: #0EA5E9;
}

/* Danger / Warning Buttons */
QPushButton#dangerBtn {
    background-color: #991B1B;
    border: 1px solid #EF4444;
    color: #FFFFFF;
}

QPushButton#dangerBtn:hover {
    background-color: #DC2626;
}

/* Form Inputs */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #00F0FF;
}

/* Tables & Lists */
QTableWidget, QTableView, QListWidget {
    background-color: #0F172A;
    color: #E2E8F0;
    border: 1px solid #1E293B;
    border-radius: 6px;
    gridline-color: #1E293B;
    selection-background-color: #0369A1;
    selection-color: #FFFFFF;
}

QHeaderView::section {
    background-color: #1E293B;
    color: #38BDF8;
    padding: 8px;
    border: none;
    border-right: 1px solid #0F172A;
    font-weight: bold;
}

/* Progress Bars */
QProgressBar {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    text-align: center;
    color: #FFFFFF;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #00F0FF);
    border-radius: 5px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #0B0F19;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #0284C7;
}

/* Status Bar */
QStatusBar {
    background-color: #080C14;
    color: #94A3B8;
    border-top: 1px solid #1E293B;
}
"""
