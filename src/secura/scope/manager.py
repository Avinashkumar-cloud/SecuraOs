"""Persistent scope target manager with authorization checks and audit logging."""

import ipaddress
import json
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path

from secura.logging.audit import AuditLogger
from secura.scope.models import ScopeStatus, ScopeTarget, TargetType
from secura.scope.validator import TargetValidator, ValidationResult


class ScopeManager:
    """Manages active, expired, and revoked assessment scopes."""

    def __init__(self, storage_path: Path | None = None, audit_logger: AuditLogger | None = None):
        if storage_path:
            self.storage_file = Path(storage_path)
        else:
            base_dir = Path.home() / ".config" / "secura"
            self.storage_file = base_dir / "scopes.json"

        self.audit_logger = audit_logger or AuditLogger()
        self._lock = threading.Lock()
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        try:
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.storage_file.exists():
                with open(self.storage_file, "w", encoding="utf-8") as f:
                    json.dump([], f)
        except OSError:
            pass

    def _load_all(self) -> list[ScopeTarget]:
        if not self.storage_file.exists():
            return []
        try:
            with open(self.storage_file, encoding="utf-8") as f:
                data = json.load(f)
            return [ScopeTarget.model_validate(item) for item in data]
        except Exception:
            return []

    def _save_all(self, targets: list[ScopeTarget]) -> None:
        self._ensure_storage()
        data = [t.model_dump(mode="json") for t in targets]
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_target(
        self,
        target_str: str,
        description: str = "",
        owner_note: str = "",
        duration_hours: int | None = 24,
    ) -> tuple[ScopeTarget | None, ValidationResult]:
        """Validate, register, and persist a new target into the scope manager."""
        val_res = TargetValidator.validate(target_str)
        if not val_res.is_valid or val_res.target_type is None:
            return None, val_res

        expires_at = None
        if duration_hours and duration_hours > 0:
            exp_dt = datetime.now(UTC) + timedelta(hours=duration_hours)
            expires_at = exp_dt.isoformat()

        target = ScopeTarget(
            target=val_res.canonical_target,
            target_type=val_res.target_type,
            description=description,
            owner_note=owner_note,
            expires_at=expires_at,
            is_private=val_res.is_private,
            status=ScopeStatus.ACTIVE,
            warning=val_res.warning,
        )

        with self._lock:
            targets = self._load_all()
            # De-duplicate existing target if present
            targets = [t for t in targets if t.target != target.target]
            targets.append(target)
            self._save_all(targets)

        # Audit log scope addition
        self.audit_logger.log_action(
            action="scope_added",
            target=target.target,
            scope_id=target.id,
            details={
                "target_type": target.target_type.value,
                "is_private": target.is_private,
                "expires_at": target.expires_at,
                "description": target.description,
                "warning": target.warning,
            },
        )

        return target, val_res

    def remove_target(self, target_or_id: str) -> bool:
        """Remove a target by ID or exact target match."""
        with self._lock:
            targets = self._load_all()
            match = next(
                (t for t in targets if t.id == target_or_id or t.target == target_or_id), None
            )
            if not match:
                return False

            new_targets = [t for t in targets if t.id != match.id]
            self._save_all(new_targets)

        self.audit_logger.log_action(
            action="scope_removed",
            target=match.target,
            scope_id=match.id,
        )
        return True

    def list_targets(self, active_only: bool = False) -> list[ScopeTarget]:
        """Return list of targets, optionally filtering for only active and unexpired."""
        with self._lock:
            targets = self._load_all()

        if active_only:
            return [t for t in targets if t.is_currently_active()]
        return targets

    def get_target(self, target_or_id: str) -> ScopeTarget | None:
        """Fetch a specific target by ID or canonical string."""
        with self._lock:
            targets = self._load_all()
        return next((t for t in targets if t.id == target_or_id or t.target == target_or_id), None)

    def is_target_in_scope(self, query_target: str) -> tuple[bool, ScopeTarget | None, str | None]:
        """Check if an arbitrary query target string is authorized under an active scope.

        Returns:
            Tuple of (is_authorized, matching_scope_target, reason_or_warning)
        """
        val = TargetValidator.validate(query_target)
        if not val.is_valid:
            return False, None, f"Invalid target query: {val.error}"

        canonical = val.canonical_target
        active_scopes = self.list_targets(active_only=True)

        # 1. Exact string match
        for s in active_scopes:
            if s.target.lower() == canonical.lower():
                return True, s, None

        # 2. Check if query is an IP contained within an active CIDR network
        if val.target_type in (TargetType.IPV4, TargetType.IPV6):
            try:
                query_ip = ipaddress.ip_address(canonical)
                for s in active_scopes:
                    if s.target_type in (TargetType.CIDR_V4, TargetType.CIDR_V6):
                        try:
                            net = ipaddress.ip_network(s.target, strict=False)
                            if query_ip in net:
                                return True, s, f"Authorized under CIDR scope {s.target}"
                        except ValueError:
                            continue
            except ValueError:
                pass

        return False, None, "Target is not present within any active, unexpired scope."
