class AppError(Exception):
    status_code: int = 500
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str = None):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message

class ValidationError(AppError):
    status_code = 400
    default_message = "Validation failed."

    def __init__(self, message: str = None, errors: dict = None):
        super().__init__(message)
        self.errors = errors or {}

class ResourceNotFound(AppError):
    status_code = 404
    default_message = "Resource not found."

class Unauthorized(AppError):
    status_code = 401
    default_message = "Authentication required."

class Forbidden(AppError):
    status_code = 403
    default_message = "You do not have permission to perform this action."

class ConflictError(AppError):
    status_code = 409
    default_message = "A conflicting resource already exists."
