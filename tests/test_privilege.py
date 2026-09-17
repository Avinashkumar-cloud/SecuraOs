"""Tests for privilege separation and non-root execution policies."""

import pytest

from secura.security.privilege import PrivilegeManager


def test_is_root_type():
    assert isinstance(PrivilegeManager.is_root(), bool)


def test_build_elevated_command():
    base_cmd = ["systemctl", "restart", "NetworkManager"]
    elevated = PrivilegeManager.build_elevated_command(base_cmd)
    assert len(elevated) >= len(base_cmd)
    assert base_cmd[0] in elevated


def test_build_elevated_command_empty_fails():
    with pytest.raises(ValueError, match="Command cannot be empty"):
        PrivilegeManager.build_elevated_command([])


def test_enforce_unprivileged_runs_safely():
    # In standard unprivileged test runner, this should not raise
    if not PrivilegeManager.is_root():
        PrivilegeManager.enforce_unprivileged("Test Harness")
