"""Pytest test fixtures and temporary environment isolation."""

from pathlib import Path

import pytest

from secura.config.manager import ConfigManager
from secura.config.schema import SecuraConfig
from secura.logging.audit import AuditLogger
from secura.scope.manager import ScopeManager


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a pristine temporary directory for test isolation."""
    return tmp_path


@pytest.fixture
def test_config(temp_dir: Path) -> SecuraConfig:
    """Generate a test configuration pointing all storage paths to temporary directories."""
    config_file = temp_dir / "config.yaml"
    mgr = ConfigManager(config_path=config_file)
    cfg = mgr.get_config()

    cfg.paths.config_dir = temp_dir / "config"
    cfg.paths.data_dir = temp_dir / "data"
    cfg.paths.logs_dir = temp_dir / "logs"
    cfg.paths.reports_dir = temp_dir / "reports"
    cfg.paths.labs_dir = temp_dir / "labs"
    cfg.paths.catalog_dir = temp_dir / "catalog"

    mgr.save(cfg)
    mgr.initialize_directories()
    return cfg


@pytest.fixture
def audit_logger(temp_dir: Path) -> AuditLogger:
    """Provide an AuditLogger instance writing to an isolated temporary log file."""
    log_file = temp_dir / "logs" / "audit.jsonl"
    return AuditLogger(log_path=log_file)


@pytest.fixture
def scope_manager(temp_dir: Path, audit_logger: AuditLogger) -> ScopeManager:
    """Provide a ScopeManager instance writing to an isolated temporary storage file."""
    scopes_file = temp_dir / "scopes.json"
    return ScopeManager(storage_path=scopes_file, audit_logger=audit_logger)
