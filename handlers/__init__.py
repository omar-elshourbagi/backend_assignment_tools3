"""Error handling package - exports exceptions and middleware handlers"""

from handlers.exceptions import (
    EventPlannerException,
    DatabaseException,
    DatabaseConnectionException,
    ValidationException,
    NotFoundException,
    PermissionException,
    ConflictException,
    AuthenticationException
)

from handlers.middleware import (
    exception_handler,
    eventplanner_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    mysql_exception_handler
)

__all__ = [
    # Exceptions
    "EventPlannerException",
    "DatabaseException",
    "DatabaseConnectionException",
    "ValidationException",
    "NotFoundException",
    "PermissionException",
    "ConflictException",
    "AuthenticationException",
    # Handlers
    "exception_handler",
    "eventplanner_exception_handler",
    "validation_exception_handler",
    "http_exception_handler",
    "mysql_exception_handler",
]
