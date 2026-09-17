"""Secura Center animated entrance splash screen (PySide6)."""

from pathlib import Path

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from secura import __version__

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "secura_logo.jpg"


class SecuraSplashScreen(QWidget):
    """Futuristic, animated splash screen that plays at application startup."""

    finished = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(560, 480)

        # Center on active screen
        self._center_window()
        self._build_ui()

        self._stages = [
            (15, "[+] Initializing Secura Core Security Engine..."),
            (35, "[+] Verifying Non-Root Least Privilege Boundary..."),
            (60, "[+] Loading Target Scope Database & Containment Engine..."),
            (80, "[+] Querying System Hardware & Hypervisor Vitals..."),
            (95, "[+] Finalizing Defensive Modules & Tools Catalog..."),
            (100, "[+] Secura Center Ready."),
        ]
        self._current_stage = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance_progress)
        self._timer.start(280)

    def _center_window(self):
        from PySide6.QtWidgets import QApplication

        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - self.width()) // 2
            y = (geo.height() - self.height()) // 2
            self.move(QPoint(x, y))

    def _build_ui(self):
        # Card Container with dark cyber styling
        card = QWidget(self)
        card.setObjectName("splashCard")
        card.setStyleSheet("""
            QWidget#splashCard {
                background-color: #070B14;
                border: 2px solid #00F0FF;
                border-radius: 16px;
            }
        """)

        # Drop shadow glow
        glow = QGraphicsDropShadowEffect(self)
        glow.setColor(QColor(0, 240, 255, 140))
        glow.setBlurRadius(35)
        glow.setOffset(0, 0)
        card.setGraphicsEffect(glow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(14)
        card_layout.setAlignment(Qt.AlignCenter)

        # Logo display
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        if LOGO_PATH.exists():
            pix = QPixmap(str(LOGO_PATH))
            scaled = pix.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        else:
            self.logo_label.setText("<b style='font-size: 40px; color: #00F0FF;'>[ S ]</b>")

        card_layout.addWidget(self.logo_label)

        # Title
        title = QLabel(
            f"SECURA OS <span style='font-size: 14px; color: #38BDF8;'>v{__version__}</span>"
        )
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: 900;
            letter-spacing: 6px;
            color: #FFFFFF;
        """)
        card_layout.addWidget(title)

        subtitle = QLabel("CYBERSECURITY & DEFENSIVE ANALYSIS HUB")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2.5px;
            color: #00F0FF;
        """)
        card_layout.addWidget(subtitle)

        # Animated Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #111827;
                border: 1px solid #1E293B;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #00F0FF);
                border-radius: 3px;
            }
        """)
        card_layout.addWidget(self.progress_bar)

        # Status Line
        self.status_label = QLabel("INITIALIZING SECURA SYSTEM...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 12px;
            font-weight: bold;
            color: #10B981;
        """)
        card_layout.addWidget(self.status_label)

        # Outer layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(card)

    def _advance_progress(self):
        if self._current_stage < len(self._stages):
            pct, msg = self._stages[self._current_stage]
            self.progress_bar.setValue(pct)
            self.status_label.setText(msg)
            self._current_stage += 1
        else:
            self._timer.stop()
            QTimer.singleShot(250, self._finish)

    def _finish(self):
        self.finished.emit()
        self.close()
