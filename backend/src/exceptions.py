"""Custom exceptions for the application."""

from typing import Optional, Dict, Any
from fastapi import HTTPException


class BaseCustomException(Exception):
    """Base custom exception."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(BaseCustomException):
    """Resource not found exception."""

    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier {identifier} not found"
        super().__init__(message)


class ValidationError(BaseCustomException):
    """Validation error exception."""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message, details)


class ConflictError(BaseCustomException):
    """Conflict error exception."""

    def __init__(self, message: str):
        super().__init__(message)


class AuthenticationError(BaseCustomException):
    """Authentication error exception."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message)


class AuthorizationError(BaseCustomException):
    """Authorization error exception."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message)


def create_http_exception(
    status_code: int, message: str, details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create HTTP exception with standardized format."""
    return HTTPException(
        status_code=status_code, detail={"error": message, "details": details or {}}
    )


# Convenience functions
def not_found_exception(resource: str, identifier: Any) -> HTTPException:
    """Create 404 Not Found exception."""
    return create_http_exception(
        status_code=404, message=f"{resource} with identifier {identifier} not found"
    )


def validation_exception(message: str, field: Optional[str] = None) -> HTTPException:
    """Create 422 Validation Error exception."""
    details = {"field": field} if field else {}
    return create_http_exception(status_code=422, message=message, details=details)


def conflict_exception(message: str) -> HTTPException:
    """Create 409 Conflict exception."""
    return create_http_exception(status_code=409, message=message)


def unauthorized_exception(message: str = "Authentication required") -> HTTPException:
    """Create 401 Unauthorized exception."""
    return create_http_exception(status_code=401, message=message)


def forbidden_exception(message: str = "Insufficient permissions") -> HTTPException:
    """Create 403 Forbidden exception."""
    return create_http_exception(status_code=403, message=message)
