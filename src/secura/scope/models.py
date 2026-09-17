"""Scope target models and enumerations."""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TargetType(StrEnum):
    """Supported target classification types."""

    IPV4 = "ipv4"
    IPV6 = "ipv6"
    CIDR_V4 = "cidr_v4"
    CIDR_V6 = "cidr_v6"
    DOMAIN = "domain"
    LOCAL_LAB = "local_lab"


class ScopeStatus(StrEnum):
    """Scope target lifecycle status."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ScopeTarget(BaseModel):
    """Authorized assessment target specification."""

    id: str = Field(default_factory=lambda: f"scope-{uuid.uuid4().hex[:8]}")
    target: str
    target_type: TargetType
    description: str = ""
    owner_note: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    expires_at: str | None = None
    is_private: bool = True
    status: ScopeStatus = ScopeStatus.ACTIVE
    warning: str | None = None

    def is_currently_active(self) -> bool:
        """Check whether the scope target is valid and unexpired."""
        if self.status != ScopeStatus.ACTIVE:
            return False

        if self.expires_at:
            try:
                exp_dt = datetime.fromisoformat(self.expires_at)
                # Ensure tz-aware comparison
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=UTC)
                now = datetime.now(UTC)
                if now > exp_dt:
                    return False
            except ValueError:
                return False

        return True
