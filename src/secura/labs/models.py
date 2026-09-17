"""Data structures and schemas for Secura training laboratories."""

from enum import StrEnum

from pydantic import BaseModel, Field


class LabStatus(StrEnum):
    """Execution status of a local laboratory."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


class LabCategory(StrEnum):
    """Categorization of laboratory exercises."""

    NETWORK_DISCOVERY = "network-discovery"
    WEB_SECURITY = "web-security"
    LINUX_SECURITY = "linux-security"
    TRAFFIC_ANALYSIS = "traffic-analysis"
    SECURE_CODING = "secure-coding"


class LabDefinition(BaseModel):
    """Specification of a local containerized training lab."""

    id: str
    name: str
    title: str
    category: LabCategory
    description: str
    learning_outcomes: list[str]
    target_subnet: str = "10.88.10.0/24"
    exposed_ports: list[int] = Field(default_factory=list)
    container_image: str
    status: LabStatus = LabStatus.STOPPED
    details: str | None = None
