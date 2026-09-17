"""Tests validating common hardware, multimedia, browser, and peripheral package definitions."""

from pathlib import Path

PKG_DIR = (
    Path(__file__).resolve().parent.parent / "build" / "live-build" / "config" / "package-lists"
)


def test_package_lists_exist():
    expected_lists = [
        "secura-base.list.chroot",
        "secura-desktop.list.chroot",
        "secura-hardware.list.chroot",
        "secura-security.list.chroot",
    ]
    for filename in expected_lists:
        pkg_file = PKG_DIR / filename
        assert pkg_file.exists(), f"Missing package list: {filename}"
        assert pkg_file.stat().st_size > 50, f"Package list {filename} is empty or too small"


def _read_packages(filename: str) -> set[str]:
    filepath = PKG_DIR / filename
    packages = set()
    for line in filepath.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            packages.add(line)
    return packages


def test_input_hardware_support():
    """Verify keyboards, mice, and touchpads are supported out-of-the-box."""
    base_pkgs = _read_packages("secura-base.list.chroot")
    hw_pkgs = _read_packages("secura-hardware.list.chroot")
    combined = base_pkgs | hw_pkgs

    assert "xserver-xorg-input-all" in combined
    assert "xserver-xorg-input-libinput" in combined
    assert "libinput-bin" in combined
    assert "kbd" in combined
    assert "xinput" in combined


def test_removable_storage_and_filesystems():
    """Verify USB flash drives, external hard drives, and filesystems are supported."""
    base_pkgs = _read_packages("secura-base.list.chroot")

    assert "udisks2" in base_pkgs
    assert "gvfs" in base_pkgs
    assert "dosfstools" in base_pkgs
    assert "ntfs-3g" in base_pkgs
    assert "exfat-fuse" in base_pkgs


def test_wireless_and_bluetooth_firmware():
    """Verify Wi-Fi and Bluetooth drivers for Intel, Realtek, Broadcom, and Atheros."""
    hw_pkgs = _read_packages("secura-hardware.list.chroot")

    assert "firmware-iwlwifi" in hw_pkgs
    assert "firmware-realtek" in hw_pkgs
    assert "firmware-atheros" in hw_pkgs
    assert "firmware-brcm80211" in hw_pkgs
    assert "bluez" in hw_pkgs
    assert "blueman" in hw_pkgs


def test_audio_and_multimedia_streaming():
    """Verify PipeWire modern audio stack, VLC media player, and codecs for movie playback."""
    desktop_pkgs = _read_packages("secura-desktop.list.chroot")
    hw_pkgs = _read_packages("secura-hardware.list.chroot")

    # Modern audio server
    assert "pipewire" in hw_pkgs
    assert "pipewire-pulse" in hw_pkgs
    assert "wireplumber" in hw_pkgs
    assert "pavucontrol" in desktop_pkgs

    # Video / movie player & codecs
    assert "vlc" in desktop_pkgs
    assert "ffmpeg" in desktop_pkgs
    assert "gstreamer1.0-plugins-good" in desktop_pkgs
    assert "gstreamer1.0-plugins-bad" in desktop_pkgs


def test_web_browsers():
    """Verify standard web browsers for internet browsing and DRM streaming."""
    desktop_pkgs = _read_packages("secura-desktop.list.chroot")

    assert "firefox-esr" in desktop_pkgs
    assert "chromium" in desktop_pkgs
