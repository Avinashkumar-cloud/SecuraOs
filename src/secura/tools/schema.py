"""Tool catalog metadata schemas and validation models."""

from enum import StrEnum

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    """Tool risk classification tier."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolCategory(StrEnum):
    """Categorization for security tools."""

    NETWORK_SECURITY = "network-security"
    WEB_SECURITY = "web-security"
    DEFENSIVE_ANALYSIS = "defensive-analysis"
    CODE_AUDITING = "code-auditing"
    FORENSICS = "forensics"
    SYSTEM_HARDENING = "system-hardening"


class SafeExample(BaseModel):
    """Safe, educational example command."""

    description: str
    command: list[str]


class ToolDefinition(BaseModel):
    """Metadata specification for a security tool."""

    name: str
    display_name: str
    category: ToolCategory
    description: str
    purpose: str
    risk_level: RiskLevel
    authorization_required: bool = True
    binary: str
    package: str
    enabled_by_default: bool = True
    documentation_url: str | None = None
    safe_examples: list[SafeExample] = Field(default_factory=list)
