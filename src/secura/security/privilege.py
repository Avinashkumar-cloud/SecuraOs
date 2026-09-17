"""Privilege management, non-root execution enforcement, and elevation helpers."""

import os
import shutil
import sys


class PrivilegeManager:
    """Enforces least privilege and manages safe elevation through Polkit / sudo."""

    @staticmethod
    def is_root() -> bool:
        """Check if current process is running with root / superuser privileges."""
        if hasattr(os, "geteuid"):
            return os.geteuid() == 0  # type: ignore[attr-defined]
        return False

    @classmethod
    def enforce_unprivileged(
        cls, app_name: str = "Secura Application", allow_root_override: bool = False
    ) -> None:
        """Enforce that the application runs as a standard, unprivileged user.

        Raises:
            PermissionError: If executed as root and override is not active.
        """
        if cls.is_root():
            msg = (
                f"SECURITY VIOLATION: {app_name} must NOT be run as root/superuser.\n"
                "Running entire GUI or CLI sessions as root violates the principle of least privilege.\n"
                "Secura uses granular elevation (Polkit / sudo) only for specific operations that require it."
            )
            if not allow_root_override and "SECURA_ALLOW_ROOT" not in os.environ:
                sys.stderr.write(f"\n[!] {msg}\n\n")
                raise PermissionError(msg)

    @staticmethod
    def build_elevated_command(command: list[str], prefer_pkexec: bool = True) -> list[str]:
        """Wrap a specific command array with Polkit (pkexec) or sudo for isolated elevation."""
        if not command:
            raise ValueError("Command cannot be empty")

        if prefer_pkexec and shutil.which("pkexec"):
            return ["pkexec"] + command
        elif shutil.which("sudo"):
            return ["sudo"] + command

        return command
