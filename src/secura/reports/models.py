"""Security assessment report schemas and severity enumerations."""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SeverityLevel(StrEnum):
    """Vulnerability finding severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(BaseModel):
    """Individual security finding or observation."""

    id: str = Field(default_factory=lambda: f"FIND-{uuid.uuid4().hex[:6].upper()}")
    title: str
    severity: SeverityLevel
    description: str
    affected_target: str
    evidence: str = ""
    recommendation: str = ""
    remediation_notes: str = ""
    references: list[str] = Field(default_factory=list)


class AssessmentReport(BaseModel):
    """Complete security assessment report document."""

    id: str = Field(default_factory=lambda: f"REP-{uuid.uuid4().hex[:8].upper()}")
    title: str
    assessor: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    scope_summary: list[str] = Field(default_factory=list)
    methodology: str = (
        "Authorized security assessment following standard defensive and testing methodologies."
    )
    findings: list[Finding] = Field(default_factory=list)
    audit_events_count: int = 0
    disclaimer: str = (
        "This security assessment report was generated in Secura OS. "
        "Scope validation is a safety control, not legal authorization. "
        "Testing was conducted strictly within authorized scope."
    )
