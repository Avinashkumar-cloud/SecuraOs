"""System hardware, virtualization, and environment inspector."""

import os
import platform
import shutil
import socket
from pathlib import Path

from pydantic import BaseModel, Field


class MemoryInfo(BaseModel):
    """Memory (RAM) metrics in Megabytes."""

    total_mb: int = 0
    available_mb: int = 0
    used_mb: int = 0


class DiskInfo(BaseModel):
    """Disk space metrics in Gigabytes."""

    total_gb: float = 0.0
    used_gb: float = 0.0
    free_gb: float = 0.0
    percent_used: float = 0.0


class SystemInfo(BaseModel):
    """Aggregated system diagnostic information."""

    os_name: str
    os_release: str
    kernel_version: str
    architecture: str
    hostname: str
    cpu_count: int
    memory: MemoryInfo
    disk: DiskInfo
    is_virtual_machine: bool
    hypervisor_name: str | None = None
    network_interfaces: list[dict[str, str]] = Field(default_factory=list)


def detect_hypervisor() -> tuple[bool, str | None]:
    """Detect if running inside a virtual machine and identify the hypervisor."""
    # Check Linux DMI vendor table
    dmi_vendor_path = Path("/sys/class/dmi/id/sys_vendor")
    dmi_product_path = Path("/sys/class/dmi/id/product_name")

    vendor = ""
    product = ""

    if dmi_vendor_path.exists():
        try:
            vendor = dmi_vendor_path.read_text().strip().lower()
        except OSError:
            pass

    if dmi_product_path.exists():
        try:
            product = dmi_product_path.read_text().strip().lower()
        except OSError:
            pass

    combined = f"{vendor} {product}".lower()

    if "qemu" in combined or "kvm" in combined or "bochs" in combined:
        return True, "QEMU / KVM"
    if "virtualbox" in combined or "innotek" in combined:
        return True, "Oracle VirtualBox"
    if "vmware" in combined:
        return True, "VMware"
    if "parallels" in combined:
        return True, "Parallels"
    if "microsoft" in combined and "virtual" in combined:
        return True, "Hyper-V / WSL"
    if "apple" in combined and "virtual" in combined:
        return True, "Apple Virtualization / UTM"

    # Check systemd-detect-virt if available on Linux
    systemd_virt = shutil.which("systemd-detect-virt")
    if systemd_virt:
        import subprocess

        try:
            res = subprocess.run([systemd_virt], capture_output=True, text=True, timeout=2)
            virt_out = res.stdout.strip().lower()
            if res.returncode == 0 and virt_out != "none":
                return True, virt_out.capitalize()
        except Exception:
            pass

    return False, None


def get_memory_info() -> MemoryInfo:
    """Retrieve system memory metrics."""
    # Check /proc/meminfo on Linux
    meminfo_path = Path("/proc/meminfo")
    if meminfo_path.exists():
        try:
            mem_total = 0
            mem_avail = 0
            for line in meminfo_path.read_text().splitlines():
                if line.startswith("MemTotal:"):
                    mem_total = int(line.split()[1]) // 1024
                elif line.startswith("MemAvailable:"):
                    mem_avail = int(line.split()[1]) // 1024
            return MemoryInfo(
                total_mb=mem_total,
                available_mb=mem_avail,
                used_mb=max(0, mem_total - mem_avail),
            )
        except Exception:
            pass

    # Fallback using os.sysconf if available (POSIX)
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        phys_pages = os.sysconf("SC_PHYS_PAGES")
        total_mb = (page_size * phys_pages) // (1024 * 1024)
        return MemoryInfo(total_mb=total_mb, available_mb=total_mb // 2, used_mb=total_mb // 2)
    except (AttributeError, ValueError, OSError):
        pass

    # Windows / Fallback default
    return MemoryInfo(total_mb=4096, available_mb=2048, used_mb=2048)


def get_disk_info(target_path: str = "/") -> DiskInfo:
    """Retrieve storage capacity and usage for the primary filesystem."""
    try:
        usage = shutil.disk_usage(target_path)
        total_gb = round(usage.total / (1024**3), 2)
        used_gb = round(usage.used / (1024**3), 2)
        free_gb = round(usage.free / (1024**3), 2)
        percent = round((usage.used / usage.total) * 100, 1) if usage.total > 0 else 0.0
        return DiskInfo(
            total_gb=total_gb,
            used_gb=used_gb,
            free_gb=free_gb,
            percent_used=percent,
        )
    except Exception:
        return DiskInfo(total_gb=25.0, used_gb=10.0, free_gb=15.0, percent_used=40.0)


def get_system_info() -> SystemInfo:
    """Gather complete hardware and operating system status."""
    is_vm, hypervisor = detect_hypervisor()
    hostname = socket.gethostname()

    # Collect active IP
    interfaces = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Connect to RFC5737 TEST-NET-1 (doesn't send actual packet)
        s.connect(("192.0.2.1", 80))
        local_ip = s.getsockname()[0]
        s.close()
        interfaces.append({"name": "primary", "ip": local_ip})
    except Exception:
        interfaces.append({"name": "localhost", "ip": "127.0.0.1"})

    return SystemInfo(
        os_name=platform.system(),
        os_release=platform.release(),
        kernel_version=platform.version(),
        architecture=platform.machine(),
        hostname=hostname,
        cpu_count=os.cpu_count() or 2,
        memory=get_memory_info(),
        disk=get_disk_info(os.path.abspath(os.sep)),
        is_virtual_machine=is_vm,
        hypervisor_name=hypervisor,
        network_interfaces=interfaces,
    )
