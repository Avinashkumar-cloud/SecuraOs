"""Structured JSONL audit logger with automated sensitive data redaction."""

import getpass
import json
import os
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from secura.logging.redactor import Redactor


class AuditEvent(BaseModel):
    """Structured audit event schema."""

    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    user: str = Field(
        default_factory=lambda: os.getenv("USER") or os.getenv("USERNAME") or getpass.getuser()
    )
    action: str
    tool: str | None = None
    target: str | None = None
    scope_id: str | None = None
    command: list[str] | None = None
    result: str = "completed"
    exit_code: int | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class AuditLogger:
    """Thread-safe structured audit logger writing to JSONL with credential redaction."""

    def __init__(self, log_path: Path | None = None):
        if log_path:
            self.log_file = Path(log_path)
        else:
            base_dir = Path.home() / ".config" / "secura" / "logs"
            self.log_file = base_dir / "audit.jsonl"

        self._lock = threading.Lock()
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Create parent directory and empty log file if needed."""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.log_file.exists():
                self.log_file.touch(mode=0o600, exist_ok=True)
        except OSError:
            # Fallback for restricted environments
            pass

    def log(self, event: AuditEvent) -> AuditEvent:
        """Sanitize, serialize, and append an audit event to the JSONL log file."""
        self._ensure_log_file()

        # Redact event data before saving
        event_dict = event.model_dump(mode="json")
        sanitized_dict = Redactor.redact_data(event_dict)

        line = json.dumps(sanitized_dict, ensure_ascii=False) + "\n"

        with self._lock:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(line)
                f.flush()

        return AuditEvent.model_validate(sanitized_dict)

    def log_action(
        self,
        action: str,
        tool: str | None = None,
        target: str | None = None,
        scope_id: str | None = None,
        command: list[str] | None = None,
        result: str = "completed",
        exit_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Helper to create and write an audit event in one call."""
        event = AuditEvent(
            action=action,
            tool=tool,
            target=target,
            scope_id=scope_id,
            command=command,
            result=result,
            exit_code=exit_code,
            details=details or {},
        )
        return self.log(event)

    def query(
        self,
        limit: int = 50,
        tool: str | None = None,
        action: str | None = None,
        target: str | None = None,
    ) -> list[AuditEvent]:
        """Query recent audit events with optional filtering."""
        if not self.log_file.exists():
            return []

        events: list[AuditEvent] = []
        with self._lock:
            with open(self.log_file, encoding="utf-8") as f:
                lines = f.readlines()

        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if tool and data.get("tool") != tool:
                    continue
                if action and data.get("action") != action:
                    continue
                if target and data.get("target") != target:
                    continue
                events.append(AuditEvent.model_validate(data))
                if len(events) >= limit:
                    break
            except Exception:
                continue

        return events
