"""Tests for structured audit logging and sensitive data redaction."""

from secura.logging.audit import AuditLogger
from secura.logging.redactor import Redactor


def test_redactor_private_key():
    sample_key = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA04x4aL...secret...content...\n"
        "-----END RSA PRIVATE KEY-----"
    )
    redacted = Redactor.redact_text(sample_key)
    assert "[REDACTED_PRIVATE_KEY]" in redacted
    assert "secret" not in redacted


def test_redactor_cli_passwords():
    cmd_1 = "nmap --password secret_pass_123 192.168.1.1"
    cmd_2 = "curl -p MyP@ssw0rd http://example.com"
    cmd_3 = "login -u admin --password=SuperSecretPass"

    assert "secret_pass_123" not in Redactor.redact_text(cmd_1)
    assert "[REDACTED_SECRET]" in Redactor.redact_text(cmd_1)

    assert "MyP@ssw0rd" not in Redactor.redact_text(cmd_2)
    assert "[REDACTED_SECRET]" in Redactor.redact_text(cmd_2)

    assert "SuperSecretPass" not in Redactor.redact_text(cmd_3)
    assert "[REDACTED_SECRET]" in Redactor.redact_text(cmd_3)


def test_redactor_jwt_and_api_keys():
    jwt = "Bearer " + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." + "eyJzdWIiOiIxMjM0NTY3ODkwIn0." + "dozjgN_placeholder"
    aws_key = "Access: " + "AKIA" + "IOSFODNN7EXAMPLE"
    github_pat = "Token: " + "gh" + "p_1234567890abcdefghijklmnopqrstuvwxyz"
    stripe_key = "sk_" + "test_" + "1234567890abcdefghijklmn"

    assert "[REDACTED_JWT]" in Redactor.redact_text(jwt)
    assert "[REDACTED_AWS_KEY]" in Redactor.redact_text(aws_key)
    assert "[REDACTED_GITHUB_TOKEN]" in Redactor.redact_text(github_pat)
    assert "[REDACTED_STRIPE_KEY]" in Redactor.redact_text(stripe_key)


def test_redactor_nested_data():
    raw_dict = {
        "user": "analyst",
        "api_key": "super_secret_api_key_value",
        "nested": {
            "password": "Password123!",
            "command": ["curl", "-p", "hunter2", "http://127.0.0.1"],
        },
    }

    sanitized = Redactor.redact_data(raw_dict)
    assert sanitized["user"] == "analyst"
    assert sanitized["api_key"] == "[REDACTED_CREDENTIAL]"
    assert sanitized["nested"]["password"] == "[REDACTED_CREDENTIAL]"
    assert "hunter2" not in sanitized["nested"]["command"]
    assert "[REDACTED_SECRET]" in sanitized["nested"]["command"]


def test_audit_logger_write_and_query(audit_logger: AuditLogger):
    # Log several events
    audit_logger.log_action(
        action="tool_execution",
        tool="nmap",
        target="192.168.1.10",
        command=["nmap", "-p", "secret_pass", "192.168.1.10"],
        result="success",
        exit_code=0,
    )

    audit_logger.log_action(
        action="scope_added",
        target="10.0.0.0/24",
        details={"type": "cidr_v4"},
    )

    # Query without filter
    events = audit_logger.query(limit=10)
    assert len(events) == 2
    assert events[0].action == "scope_added"  # Most recent first
    assert events[1].action == "tool_execution"

    # Verify redaction was applied before writing
    assert "secret_pass" not in str(events[1].command)
    assert "[REDACTED_SECRET]" in str(events[1].command)

    # Filter by tool
    nmap_events = audit_logger.query(tool="nmap")
    assert len(nmap_events) == 1
    assert nmap_events[0].tool == "nmap"

    # Filter by action
    scope_events = audit_logger.query(action="scope_added")
    assert len(scope_events) == 1
    assert scope_events[0].target == "10.0.0.0/24"
