"""Tests for scope management, validation, CIDR containment, and expiration."""

from datetime import UTC, datetime, timedelta

from secura.scope.manager import ScopeManager
from secura.scope.models import TargetType
from secura.scope.validator import TargetValidator


def test_validator_private_ipv4():
    res = TargetValidator.validate("192.168.1.50")
    assert res.is_valid is True
    assert res.target_type == TargetType.IPV4
    assert res.is_private is True
    assert res.warning is None


def test_validator_public_ipv4():
    res = TargetValidator.validate("93.184.216.34")
    assert res.is_valid is True
    assert res.target_type == TargetType.IPV4
    assert res.is_private is False
    assert res.warning is not None
    assert "Public IP" in res.warning


def test_validator_broad_cidr():
    res = TargetValidator.validate("10.0.0.0/8")
    assert res.is_valid is True
    assert res.target_type == TargetType.CIDR_V4
    assert res.warning is not None
    assert "Suspiciously broad" in res.warning


def test_validator_domain_and_localhost():
    res_local = TargetValidator.validate("localhost")
    assert res_local.is_valid is True
    assert res_local.target_type == TargetType.DOMAIN
    assert res_local.is_private is True

    res_dom = TargetValidator.validate("scanme.nmap.org")
    assert res_dom.is_valid is True
    assert res_dom.target_type == TargetType.DOMAIN
    assert res_dom.is_private is False


def test_validator_invalid_input():
    res = TargetValidator.validate("not_a_valid_target_%%%")
    assert res.is_valid is False
    assert res.error is not None


def test_scope_manager_add_and_remove(scope_manager: ScopeManager):
    target, val = scope_manager.add_target(
        "192.168.1.100",
        description="Local test host",
        duration_hours=12,
    )
    assert target is not None
    assert val.is_valid is True
    assert target.is_private is True

    # List targets
    targets = scope_manager.list_targets()
    assert len(targets) == 1
    assert targets[0].target == "192.168.1.100"

    # Remove target
    removed = scope_manager.remove_target("192.168.1.100")
    assert removed is True
    assert len(scope_manager.list_targets()) == 0


def test_scope_authorization_and_cidr_containment(scope_manager: ScopeManager):
    # Add a /24 subnet to scope
    target, _ = scope_manager.add_target("172.16.50.0/24", description="Lab Network")
    assert target is not None

    # Test an IP inside this subnet
    is_auth, matched, note = scope_manager.is_target_in_scope("172.16.50.15")
    assert is_auth is True
    assert matched is not None
    assert matched.target == "172.16.50.0/24"
    assert "Authorized under CIDR" in (note or "")

    # Test an IP outside this subnet
    is_auth_ext, matched_ext, _ = scope_manager.is_target_in_scope("172.16.51.15")
    assert is_auth_ext is False
    assert matched_ext is None


def test_scope_expiration(scope_manager: ScopeManager):
    target, _ = scope_manager.add_target("10.0.0.15", duration_hours=1)
    assert target is not None
    assert target.is_currently_active() is True

    # Manually backdate expiration to 2 hours ago
    expired_time = datetime.now(UTC) - timedelta(hours=2)
    target.expires_at = expired_time.isoformat()
    assert target.is_currently_active() is False
