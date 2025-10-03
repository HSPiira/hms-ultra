from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OperationResult:
    """
    Standard service boundary result type.
    - success: operation outcome
    - data: successful payload (domain-specific)
    - error: human-readable message
    - error_code: stable code for programmatic handling
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    @staticmethod
    def ok(data: Optional[Dict[str, Any]] = None) -> "OperationResult":
        return OperationResult(success=True, data=data)

    @staticmethod
    def fail(message: str, error_code: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> "OperationResult":
        return OperationResult(success=False, error=message, error_code=error_code, data=data)


