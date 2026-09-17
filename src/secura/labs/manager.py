"""Local training laboratory manager abstraction."""

import shutil

from secura.labs.models import LabCategory, LabDefinition, LabStatus
from secura.logging.audit import AuditLogger


class LabManager:
    """Manages lifecycle of local, isolated training laboratories."""

    STANDARD_LABS = [
        LabDefinition(
            id="lab-01-discovery",
            name="network_discovery",
            title="Lab 1: Network Discovery & Port Scanning",
            category=LabCategory.NETWORK_DISCOVERY,
            description="Perform host discovery, TCP SYN scanning, and service version enumeration on an isolated target container.",
            learning_outcomes=[
                "Understand difference between ICMP echo discovery and TCP SYN probing",
                "Identify common open service ports (SSH, HTTP, DNS)",
                "Enumerate service version banners safely",
            ],
            target_subnet="10.88.10.0/24",
            exposed_ports=[22, 80, 53],
            container_image="secura/lab-network-discovery:0.1.0",
        ),
        LabDefinition(
            id="lab-02-websec",
            name="web_security",
            title="Lab 2: Web Application Security Basics",
            category=LabCategory.WEB_SECURITY,
            description="Examine a deliberately vulnerable web service running on localhost to understand input validation and authentication flaws.",
            learning_outcomes=[
                "Inspect HTTP requests, headers, and parameters",
                "Recognize SQL injection patterns and defense mechanisms",
                "Learn directory traversal risks and path sanitization",
            ],
            target_subnet="127.0.0.1/32",
            exposed_ports=[8080],
            container_image="secura/lab-web-security:0.1.0",
        ),
        LabDefinition(
            id="lab-03-linuxsec",
            name="linux_security",
            title="Lab 3: Linux System Security & Hardening",
            category=LabCategory.LINUX_SECURITY,
            description="Audit permissions, dangerous SUID binaries, and firewall rules in an isolated container environment.",
            learning_outcomes=[
                "Inspect Linux file permissions, ACLs, and SUID bit",
                "Audit system services and open listening ports",
                "Configure UFW firewall rules for defense",
            ],
            target_subnet="127.0.0.1/32",
            exposed_ports=[],
            container_image="secura/lab-linux-hardening:0.1.0",
        ),
        LabDefinition(
            id="lab-04-traffic",
            name="traffic_analysis",
            title="Lab 4: Network Traffic Analysis",
            category=LabCategory.TRAFFIC_ANALYSIS,
            description="Investigate pre-captured malicious and reconnaissance traffic using Wireshark and TShark display filters.",
            learning_outcomes=[
                "Apply Wireshark display filters to isolate anomalous TCP handshakes",
                "Reconstruct unencrypted HTTP sessions",
                "Identify port scan patterns from packet logs",
            ],
            target_subnet="N/A (Offline PCAP)",
            exposed_ports=[],
            container_image="secura/lab-traffic-analysis:0.1.0",
        ),
        LabDefinition(
            id="lab-05-securecode",
            name="secure_coding",
            title="Lab 5: Secure Code Review",
            category=LabCategory.SECURE_CODING,
            description="Analyze source repositories for common static security bugs using Bandit and static analysis tools.",
            learning_outcomes=[
                "Identify hardcoded credentials and tokens in source code",
                "Detect unsafe deserialization and command injection patterns",
                "Write remediation patches for vulnerable code",
            ],
            target_subnet="N/A (Offline Repository)",
            exposed_ports=[],
            container_image="secura/lab-secure-code:0.1.0",
        ),
    ]

    def __init__(self, audit_logger: AuditLogger | None = None):
        self.audit_logger = audit_logger or AuditLogger()
        self._labs: dict[str, LabDefinition] = {
            lab.id: lab.model_copy() for lab in self.STANDARD_LABS
        }

    def is_podman_available(self) -> bool:
        """Check if rootless podman container runtime is installed on the host."""
        return shutil.which("podman") is not None

    def list_labs(self) -> list[LabDefinition]:
        """Return all available laboratory specifications."""
        return list(self._labs.values())

    def get_lab(self, lab_id: str) -> LabDefinition | None:
        """Fetch a specific lab definition by ID or name."""
        if lab_id in self._labs:
            return self._labs[lab_id]
        for lab in self._labs.values():
            if lab.name == lab_id:
                return lab
        return None

    def start_lab(self, lab_id: str) -> tuple[bool, str]:
        """Launch an isolated laboratory environment.

        NOTE: Milestone 1 defines the interface and lifecycle tracking.
        Full container runtime orchestration is implemented in Milestone 5.
        """
        lab = self.get_lab(lab_id)
        if not lab:
            return False, f"Laboratory '{lab_id}' not found."

        if not self.is_podman_available():
            return False, "Podman container engine is not installed. Labs require rootless Podman."

        # TODO (Milestone 5): Implement rootless Podman container launch with bridge network isolation
        lab.status = LabStatus.STARTING
        self.audit_logger.log_action(
            action="lab_start_requested",
            details={"lab_id": lab.id, "image": lab.container_image},
        )
        return True, f"Lab '{lab.title}' launch requested (Milestone 5 Container Integration)."

    def stop_lab(self, lab_id: str) -> tuple[bool, str]:
        """Stop an active laboratory environment."""
        lab = self.get_lab(lab_id)
        if not lab:
            return False, f"Laboratory '{lab_id}' not found."

        # TODO (Milestone 5): Terminate Podman container and release network interfaces
        lab.status = LabStatus.STOPPED
        self.audit_logger.log_action(
            action="lab_stop_requested",
            details={"lab_id": lab.id},
        )
        return True, f"Lab '{lab.title}' stopped."
