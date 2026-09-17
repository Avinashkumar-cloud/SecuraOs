"""Tests validating Secura Center GUI themes, splash screen, assets, and entry point."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from secura.gui.theme import DARK_CYBER_THEME

ASSETS_DIR = Path(__file__).resolve().parent.parent / "src" / "secura" / "assets"
PLYMOUTH_DIR = (
    Path(__file__).resolve().parent.parent
    / "build"
    / "includes.chroot"
    / "usr"
    / "share"
    / "plymouth"
    / "themes"
    / "secura"
)


def test_theme_stylesheet_content():
    assert "QMainWindow" in DARK_CYBER_THEME
    assert "#00F0FF" in DARK_CYBER_THEME
    assert "#0B0F19" in DARK_CYBER_THEME
    assert "QTabWidget" in DARK_CYBER_THEME
    assert "QTableWidget" in DARK_CYBER_THEME
    assert "QPushButton" in DARK_CYBER_THEME


def test_logo_and_entrance_animation_assets():
    """Verify that the official logo, vector SVG, and entrance animation exist."""
    assert (ASSETS_DIR / "secura_logo.jpg").exists()
    assert (ASSETS_DIR / "secura_logo.svg").exists()
    assert (ASSETS_DIR / "entrance_animation.html").exists()

    svg_content = (ASSETS_DIR / "secura_logo.svg").read_text(encoding="utf-8")
    assert "<svg" in svg_content
    assert "#00F0FF" in svg_content
    assert "SECURA" in svg_content

    html_content = (ASSETS_DIR / "entrance_animation.html").read_text(encoding="utf-8")
    assert "particleCanvas" in html_content
    assert "secura_logo.jpg" in html_content
    assert "SECURA" in html_content


def test_plymouth_boot_theme_assets():
    """Verify that the Plymouth boot animation theme is properly defined."""
    assert (PLYMOUTH_DIR / "secura.plymouth").exists()
    assert (PLYMOUTH_DIR / "secura.script").exists()
    assert (PLYMOUTH_DIR / "secura_logo.jpg").exists()

    theme_def = (PLYMOUTH_DIR / "secura.plymouth").read_text(encoding="utf-8")
    assert "Name=Secura OS Cyber Shield" in theme_def
    assert "ScriptFile=/usr/share/plymouth/themes/secura/secura.script" in theme_def

    script_content = (PLYMOUTH_DIR / "secura.script").read_text(encoding="utf-8")
    assert "Plymouth.SetBootProgressFunction" in script_content
    assert "Plymouth.SetUpdateStatusFunction" in script_content


def test_gui_main_root_guard():
    """Verify Secura Center refuses to run if user is root."""
    from secura.gui.main import main

    with patch("secura.security.privilege.PrivilegeManager.is_root", return_value=True):
        with pytest.raises(PermissionError):
            main()


def test_gui_main_missing_pyside6(capsys):
    """Verify informative error message when PySide6 is not installed."""
    from secura.gui.main import main

    with patch("secura.security.privilege.PrivilegeManager.is_root", return_value=False):
        # Force PySide6 import failure
        with patch.dict(sys.modules, {"PySide6": None, "PySide6.QtWidgets": None}):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "requires 'PySide6'" in captured.err


def test_gui_main_missing_display_on_linux(capsys):
    """Verify display check on Linux when $DISPLAY and $WAYLAND_DISPLAY are unset."""
    from secura.gui.main import main

    mock_qtwidgets = MagicMock()
    mock_app_mod = MagicMock()

    with patch("secura.security.privilege.PrivilegeManager.is_root", return_value=False):
        with patch("sys.platform", "linux"):
            with patch.dict("os.environ", {}, clear=True):
                with patch.dict(
                    sys.modules,
                    {
                        "PySide6": MagicMock(),
                        "PySide6.QtWidgets": mock_qtwidgets,
                        "secura.gui.app": mock_app_mod,
                        "secura.gui.splash": MagicMock(),
                    },
                ):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
                    assert exc_info.value.code == 1
                    captured = capsys.readouterr()
                    assert "No graphical display server detected" in captured.err
