"""
Custom Exception Classes

Defines application-specific exceptions for better error handling.
"""

from fastapi import HTTPException, status


class QorSenseException(Exception):
    """Base exception for QorSense application."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(QorSenseException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(QorSenseException):
    """Raised when user lacks required permissions."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ResourceNotFoundError(QorSenseException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", status.HTTP_404_NOT_FOUND)


class ValidationError(QorSenseException):
    """Raised when input validation fails."""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class DatabaseError(QorSenseException):
    """Raised when a database operation fails."""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalysisError(QorSenseException):
    """Raised when sensor analysis fails."""
    def __init__(self, message: str = "Analysis failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


def qorsense_exception_handler(exc: QorSenseException) -> HTTPException:
    """
    Convert QorSense exceptions to HTTP exceptions.
    
    Args:
        exc: QorSense exception
        
    Returns:
        HTTPException
    """
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )
