"""Tests for the safe subprocess execution layer."""

import sys

import pytest

from secura.core.runner import SafeRunner
from secura.logging.audit import AuditLogger


def test_safe_runner_execution_success(audit_logger: AuditLogger):
    runner = SafeRunner(audit_logger=audit_logger)
    result = runner.run([sys.executable, "-c", "print('secura_execution_ok')"], timeout=5)

    assert result.exit_code == 0
    assert "secura_execution_ok" in result.stdout
    assert result.timed_out is False
    assert result.duration_seconds >= 0

    # Verify audit event was logged
    events = audit_logger.query(limit=1)
    assert len(events) == 1
    assert events[0].action == "tool_execution"
    assert events[0].result == "success"


def test_safe_runner_rejects_raw_string(audit_logger: AuditLogger):
    runner = SafeRunner(audit_logger=audit_logger)
    with pytest.raises(ValueError, match="Command must be a non-empty sequence"):
        # Passing raw string instead of array of arguments must fail
        runner.run("echo 'malicious string injection'")  # type: ignore[arg-type]


def test_safe_runner_timeout(audit_logger: AuditLogger):
    runner = SafeRunner(audit_logger=audit_logger)
    # Run sleep for 3 seconds with a 1 second timeout
    result = runner.run(
        [sys.executable, "-c", "import time; time.sleep(3)"],
        timeout=1,
    )

    assert result.timed_out is True
    assert "timed out" in (result.error_message or "").lower()

    events = audit_logger.query(limit=1)
    assert len(events) == 1
    assert events[0].result == "timed_out"


def test_safe_runner_missing_binary(audit_logger: AuditLogger):
    runner = SafeRunner(audit_logger=audit_logger)
    result = runner.run(["non_existent_binary_xyz_123"], timeout=5)

    assert result.exit_code == 127
    assert "not found" in (result.error_message or "").lower()
