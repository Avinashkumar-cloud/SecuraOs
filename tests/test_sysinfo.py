"""Tests for system inspection and virtualization detection."""

from secura.core.sysinfo import (
    detect_hypervisor,
    get_disk_info,
    get_memory_info,
    get_system_info,
)


def test_get_system_info_fields():
    info = get_system_info()
    assert info.os_name != ""
    assert info.architecture != ""
    assert info.hostname != ""
    assert info.cpu_count >= 1
    assert info.memory.total_mb > 0
    assert info.disk.total_gb > 0
    assert isinstance(info.is_virtual_machine, bool)
    assert len(info.network_interfaces) > 0


def test_get_memory_info():
    mem = get_memory_info()
    assert mem.total_mb >= 512
    assert mem.available_mb >= 0
    assert mem.used_mb >= 0


def test_get_disk_info():
    disk = get_disk_info()
    assert disk.total_gb > 0
    assert disk.used_gb >= 0
    assert 0.0 <= disk.percent_used <= 100.0


def test_detect_hypervisor_returns_tuple():
    is_vm, name = detect_hypervisor()
    assert isinstance(is_vm, bool)
    if is_vm:
        assert name is not None
