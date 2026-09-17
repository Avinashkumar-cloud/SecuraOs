"""Tests for local training laboratory definitions and lifecycle abstraction."""

from secura.labs.manager import LabManager
from secura.labs.models import LabCategory, LabStatus
from secura.logging.audit import AuditLogger


def test_standard_labs_defined(audit_logger: AuditLogger):
    mgr = LabManager(audit_logger=audit_logger)
    labs = mgr.list_labs()
    assert len(labs) >= 5

    categories = [lab.category for lab in labs]
    assert LabCategory.NETWORK_DISCOVERY in categories
    assert LabCategory.WEB_SECURITY in categories
    assert LabCategory.LINUX_SECURITY in categories
    assert LabCategory.TRAFFIC_ANALYSIS in categories
    assert LabCategory.SECURE_CODING in categories


def test_get_lab_by_id_and_name(audit_logger: AuditLogger):
    mgr = LabManager(audit_logger=audit_logger)
    lab1 = mgr.get_lab("lab-01-discovery")
    assert lab1 is not None
    assert lab1.name == "network_discovery"

    lab2 = mgr.get_lab("web_security")
    assert lab2 is not None
    assert lab2.id == "lab-02-websec"


def test_lab_lifecycle_placeholder(audit_logger: AuditLogger):
    mgr = LabManager(audit_logger=audit_logger)

    # Test stop lab
    ok, msg = mgr.stop_lab("lab-01-discovery")
    assert ok is True
    lab = mgr.get_lab("lab-01-discovery")
    assert lab is not None
    assert lab.status == LabStatus.STOPPED

    # Test non-existent lab
    ok_fake, msg_fake = mgr.start_lab("non-existent-lab-id")
    assert ok_fake is False
    assert "not found" in msg_fake
