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
        """Warn if the application runs as root/superuser.

        On Kali Linux and similar pentesting distros, root is the default user.
        Instead of hard-blocking, we emit a visible warning and continue.
        Set SECURA_ALLOW_ROOT=1 to suppress the warning entirely.
        """
        if cls.is_root():
            if "SECURA_ALLOW_ROOT" in os.environ or allow_root_override:
                return  # Silently allow when explicitly permitted
            # Kali and pentest distros run as root by design — warn but don't crash
            warning = (
                f"[!] WARNING: {app_name} is running as root/superuser.\n"
                "    This is acceptable on Kali Linux, but avoid root on production systems.\n"
                "    Set SECURA_ALLOW_ROOT=1 to suppress this warning.\n"
            )
            sys.stderr.write(f"\n{warning}\n")

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
