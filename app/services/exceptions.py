"""
app/services/exceptions.py
───────────────────────────
Custom exception hierarchy for domain errors.

Raising typed exceptions from service methods lets the global error
handler (middleware/error_handler.py) convert them to the right HTTP
status code without cluttering service code with Flask imports.
"""


class AppError(Exception):
    """Base class for all application-level errors."""
    status_code: int = 500
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str = None):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message


class ValidationError(AppError):
    """Raised when input data fails business-rule validation."""
    status_code = 400
    default_message = "Validation failed."

    def __init__(self, message: str = None, errors: dict = None):
        super().__init__(message)
        # Field-level errors dict, e.g. {"amount": ["Must be positive"]}
        self.errors = errors or {}


class ResourceNotFound(AppError):
    """Raised when a requested resource does not exist."""
    status_code = 404
    default_message = "Resource not found."


class Unauthorized(AppError):
    """Raised when the caller is not authenticated."""
    status_code = 401
    default_message = "Authentication required."


class Forbidden(AppError):
    """Raised when the caller is authenticated but lacks permission."""
    status_code = 403
    default_message = "You do not have permission to perform this action."


class ConflictError(AppError):
    """Raised when a create/update would violate a uniqueness constraint."""
    status_code = 409
    default_message = "A conflicting resource already exists."
