"""Custom exception classes for the EventPlanner API"""


class EventPlannerException(Exception):
    """Base exception for all EventPlanner exceptions"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseException(EventPlannerException):
    """Raised when database operations fail"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)


class DatabaseConnectionException(DatabaseException):
    """Raised when database connection fails"""
    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message, status_code=503)


class ValidationException(EventPlannerException):
    """Raised when input validation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundException(EventPlannerException):
    """Raised when a resource is not found"""
    def __init__(self, resource: str, identifier: str = None):
        if identifier:
            message = f"{resource} with id {identifier} not found"
        else:
            message = f"{resource} not found"
        super().__init__(message, status_code=404)


class PermissionException(EventPlannerException):
    """Raised when user doesn't have permission to perform an action"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class ConflictException(EventPlannerException):
    """Raised when a resource conflict occurs (e.g., duplicate entry)"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class AuthenticationException(EventPlannerException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

