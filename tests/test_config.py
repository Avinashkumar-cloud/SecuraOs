"""Tests for configuration loading, serialization, and directory management."""

from pathlib import Path

from secura.config.manager import ConfigManager


def test_default_config_creation(temp_dir: Path):
    cfg_file = temp_dir / "test_config.yaml"
    mgr = ConfigManager(config_path=cfg_file)
    cfg = mgr.get_config()

    assert cfg.version == "0.1.0-alpha"
    assert cfg.logging.redact_sensitive_data is True
    assert cfg.scope.warn_on_public_ip is True
    assert cfg_file.exists()


def test_config_save_and_reload(temp_dir: Path):
    cfg_file = temp_dir / "test_config.yaml"
    mgr = ConfigManager(config_path=cfg_file)
    cfg = mgr.get_config()

    cfg.ui.theme = "light"
    cfg.scope.default_scope_duration_hours = 48
    mgr.save(cfg)

    # Reload from disk
    new_mgr = ConfigManager(config_path=cfg_file)
    reloaded = new_mgr.load()

    assert reloaded.ui.theme == "light"
    assert reloaded.scope.default_scope_duration_hours == 48


def test_directory_initialization(temp_dir: Path):
    cfg_file = temp_dir / "test_config.yaml"
    mgr = ConfigManager(config_path=cfg_file)
    cfg = mgr.get_config()

    test_logs = temp_dir / "custom_logs"
    cfg.paths.logs_dir = test_logs
    mgr.save(cfg)

    mgr.initialize_directories()
    assert test_logs.exists()
    assert test_logs.is_dir()
