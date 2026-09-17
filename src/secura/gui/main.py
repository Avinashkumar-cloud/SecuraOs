"""Secura Center graphical user interface launcher (PySide6)."""

import os
import sys

from secura import __version__
from secura.security.privilege import PrivilegeManager


def main():
    """Launch Secura Center GUI."""
    # 1. HARD INVARIANT: Secura Center must never run as root/superuser
    PrivilegeManager.enforce_unprivileged("Secura Center")

    # 2. Check for PySide6 installation
    try:
        from PySide6.QtWidgets import QApplication

        from secura.gui.app import SecuraMainWindow
        from secura.gui.splash import SecuraSplashScreen
        from secura.gui.theme import DARK_CYBER_THEME
    except ImportError:
        sys.stderr.write(
            "\n[!] Secura Center GUI requires 'PySide6'.\n"
            "    Install with: pip install 'secura-os[gui]'\n"
            "    Or use the command line interface: secura status\n\n"
        )
        sys.exit(1)

    # 3. Check for display server (on Linux, X11 or Wayland)
    if sys.platform.startswith("linux") and not (
        os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY")
    ):
        sys.stderr.write(
            "\n[!] No graphical display server detected ($DISPLAY or $WAYLAND_DISPLAY missing).\n\n"
        )
        sys.exit(1)

    # Launch Secura Center GUI application
    app = QApplication(sys.argv)
    app.setApplicationName("Secura Center")
    app.setApplicationVersion(__version__)
    app.setStyleSheet(DARK_CYBER_THEME)

    no_splash = "--no-splash" in sys.argv
    window = SecuraMainWindow()

    if no_splash:
        window.show()
    else:
        splash = SecuraSplashScreen()
        splash.finished.connect(window.show)
        splash.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
