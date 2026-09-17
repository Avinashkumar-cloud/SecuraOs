"""Tests for Calamares installer configuration, live session hooks, deb package, and install CLI."""

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from secura.cli.main import app

PROJECT_ROOT = Path(__file__).resolve().parent.parent
runner = CliRunner()


def test_calamares_settings_syntax():
    settings_file = PROJECT_ROOT / "packaging" / "calamares" / "settings.conf"
    assert settings_file.exists()

    with open(settings_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "sequence" in data
    assert "branding" in data
    assert data["branding"] == "secura"
    assert data["prompt-install"] is True

    # Verify execution sequence contains critical installation steps
    exec_steps = []
    for stage in data["sequence"]:
        if "exec" in stage:
            exec_steps.extend(stage["exec"])

    assert "partition" in exec_steps
    assert "mount" in exec_steps
    assert "unpackfs" in exec_steps
    assert "users" in exec_steps
    assert "bootloader" in exec_steps


def test_calamares_modules_syntax():
    modules_dir = PROJECT_ROOT / "packaging" / "calamares" / "modules"
    assert modules_dir.exists()

    expected_modules = [
        "welcome.conf",
        "locale.conf",
        "keyboard.conf",
        "partition.conf",
        "users.conf",
        "unpackfs.conf",
        "bootloader.conf",
        "packages.conf",
        "finished.conf",
    ]

    for mod in expected_modules:
        mod_file = modules_dir / mod
        assert mod_file.exists(), f"Missing expected module: {mod}"
        with open(mod_file, encoding="utf-8") as f:
            content = yaml.safe_load(f)
        assert isinstance(content, dict), f"Module {mod} does not parse as a valid YAML mapping"


def test_calamares_branding_descriptor():
    desc_file = PROJECT_ROOT / "packaging" / "calamares" / "branding" / "secura" / "branding.desc"
    assert desc_file.exists()

    with open(desc_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["componentName"] == "secura"
    assert "Secura" in data["strings"]["productName"]


def test_desktop_installer_shortcuts():
    app_desktop = (
        PROJECT_ROOT
        / "build"
        / "includes.chroot"
        / "usr"
        / "share"
        / "applications"
        / "install-secura.desktop"
    )
    skel_desktop = (
        PROJECT_ROOT
        / "build"
        / "includes.chroot"
        / "etc"
        / "skel"
        / "Desktop"
        / "install-secura.desktop"
    )

    assert app_desktop.exists()
    assert skel_desktop.exists()

    content = app_desktop.read_text(encoding="utf-8")
    assert "[Desktop Entry]" in content
    assert "Exec=secura-installer" in content
    assert "Name=Install Secura OS" in content


def test_polkit_installer_rules():
    rule_file = (
        PROJECT_ROOT
        / "build"
        / "includes.chroot"
        / "etc"
        / "polkit-1"
        / "rules.d"
        / "40-calamares.rules"
    )
    assert rule_file.exists()
    content = rule_file.read_text(encoding="utf-8")
    assert "calamares" in content
    assert "sudo" in content


def test_live_build_chroot_hooks():
    hooks_dir = PROJECT_ROOT / "build" / "live-build" / "config" / "hooks" / "live"
    assert (hooks_dir / "01-secura-live-user.hook.chroot").exists()
    assert (hooks_dir / "02-calamares-setup.hook.chroot").exists()


def test_debian_package_builder_and_archive(tmp_path: Path):
    from build.scripts.build_deb import build_deb_package

    test_deb = tmp_path / "secura-core-test.deb"
    built = build_deb_package(test_deb)

    assert built.exists()
    assert built.stat().st_size > 1000

    # Read binary header to ensure valid ar archive
    header = built.read_bytes()[:8]
    assert header == b"!<arch>\n"


def test_cli_install_command():
    result = runner.invoke(app, ["install", "--no-gui"])
    assert result.exit_code == 0
    assert "Secura OS System Installer" in result.stdout
    assert "CRITICAL DATA SAFETY WARNING" in result.stdout
    assert "Installation Hardware Pre-flight Check" in result.stdout


def test_cli_install_command_json():
    result = runner.invoke(app, ["install", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "is_live_environment" in data
    assert "meets_requirements" in data
    assert "ram_mb" in data
    assert "cpu_cores" in data
    assert "disk_warning" in data
