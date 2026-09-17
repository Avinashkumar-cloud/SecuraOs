"""Secura configuration schema definitions using Pydantic."""

from pathlib import Path

from pydantic import BaseModel, Field


class PathsConfig(BaseModel):
    """Paths configuration for Secura runtime directories."""

    config_dir: Path = Field(default_factory=lambda: Path.home() / ".config" / "secura")
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".local" / "share" / "secura")
    logs_dir: Path = Field(default_factory=lambda: Path.home() / ".config" / "secura" / "logs")
    reports_dir: Path = Field(default_factory=lambda: Path.home() / "SecuraReports")
    labs_dir: Path = Field(
        default_factory=lambda: Path.home() / ".local" / "share" / "secura" / "labs"
    )
    catalog_dir: Path = Field(
        default_factory=lambda: Path.home() / ".config" / "secura" / "catalog"
    )


class LoggingConfig(BaseModel):
    """Logging and audit configuration."""

    level: str = "INFO"
    audit_file: str = "audit.jsonl"
    console_output: bool = True
    redact_sensitive_data: bool = True
    max_log_size_mb: int = 50
    backup_count: int = 5


class ScopeConfig(BaseModel):
    """Scope validation and safety configuration."""

    enforce_scope_for_tools: bool = True
    warn_on_public_ip: bool = True
    allow_public_ip_with_confirmation: bool = True
    default_scope_duration_hours: int = 24
    disclaimer: str = "Scope validation is a safety control, not legal authorization."


class UIConfig(BaseModel):
    """User Interface and appearance configuration."""

    theme: str = "dark"
    accent_color: str = "#2563EB"
    show_safety_prompts: bool = True
    compact_mode: bool = False


class SecuraConfig(BaseModel):
    """Root Secura system configuration model."""

    version: str = "0.1.0-alpha"
    environment: str = "production"
    paths: PathsConfig = Field(default_factory=PathsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    scope: ScopeConfig = Field(default_factory=ScopeConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
