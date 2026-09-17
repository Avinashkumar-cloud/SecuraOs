"""Safe subprocess execution layer enforcing least privilege, shell=False, and audit logging."""

import subprocess
import time
from collections.abc import Sequence

from pydantic import BaseModel

from secura.logging.audit import AuditLogger


class ExecutionResult(BaseModel):
    """Subprocess execution output and metrics."""

    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    error_message: str | None = None


class SafeRunner:
    """Executes external commands safely without shell interpolation, enforcing timeouts and auditing."""

    def __init__(self, audit_logger: AuditLogger | None = None):
        self.audit_logger = audit_logger or AuditLogger()

    def run(
        self,
        command: Sequence[str],
        timeout: int = 60,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
        tool_name: str | None = None,
        target: str | None = None,
        scope_id: str | None = None,
        action_name: str = "tool_execution",
    ) -> ExecutionResult:
        """Execute a command array with strict safety guarantees.

        Args:
            command: A sequence of strings (e.g. ["/usr/bin/nmap", "-sV", "192.168.1.1"]).
            timeout: Maximum execution duration in seconds.
            env: Optional explicit environment variables.
            cwd: Working directory.
            tool_name: Optional identifier for the tool.
            target: Optional target being scanned/tested.
            scope_id: Optional identifier for authorized scope.
            action_name: Audit action name.

        Raises:
            ValueError: If command is not a list/tuple of strings or is empty.
        """
        if not command or not isinstance(command, (list, tuple)):
            raise ValueError(
                "Command must be a non-empty sequence of strings. Strings with shell syntax are disallowed."
            )

        # Ensure all elements are strings to prevent injection
        cmd_list = [str(arg) for arg in command]

        start_time = time.monotonic()
        timed_out = False
        exit_code = -1
        stdout = ""
        stderr = ""
        error_msg = None

        try:
            process = subprocess.run(
                cmd_list,
                shell=False,  # HARD INVARIANT: Never use shell=True
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=cwd,
                check=False,
            )
            stdout = process.stdout
            stderr = process.stderr
            exit_code = process.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = (
                exc.stdout.decode(errors="replace")
                if isinstance(exc.stdout, bytes)
                else (exc.stdout or "")
            )
            stderr = (
                exc.stderr.decode(errors="replace")
                if isinstance(exc.stderr, bytes)
                else (exc.stderr or "")
            )
            error_msg = f"Execution timed out after {timeout} seconds"
        except FileNotFoundError:
            exit_code = 127
            error_msg = f"Binary not found: {cmd_list[0]}"
            stderr = error_msg
        except Exception as exc:
            exit_code = 1
            error_msg = f"Execution failed: {str(exc)}"
            stderr = error_msg

        duration = round(time.monotonic() - start_time, 3)

        result_status = "timed_out" if timed_out else ("success" if exit_code == 0 else "failure")

        # Record event in audit log
        try:
            self.audit_logger.log_action(
                action=action_name,
                tool=tool_name or cmd_list[0],
                target=target,
                scope_id=scope_id,
                command=cmd_list,
                result=result_status,
                exit_code=exit_code,
                details={
                    "duration_seconds": duration,
                    "timed_out": timed_out,
                    "error": error_msg,
                },
            )
        except Exception:
            # Audit logging failure must not crash the caller
            pass

        return ExecutionResult(
            command=cmd_list,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            timed_out=timed_out,
            error_message=error_msg,
        )
