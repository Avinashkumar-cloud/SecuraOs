"""Secura scope management and target safety validation module."""

from secura.scope.manager import ScopeManager
from secura.scope.models import ScopeStatus, ScopeTarget, TargetType
from secura.scope.validator import TargetValidator, ValidationResult

__all__ = [
    "ScopeStatus",
    "ScopeTarget",
    "TargetType",
    "ScopeManager",
    "TargetValidator",
    "ValidationResult",
]
