"""Global exception handler middleware"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from handlers.exceptions import EventPlannerException
from mysql.connector import Error as MySQLError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for all unhandled exceptions"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "detail": str(exc) if logger.level == logging.DEBUG else None
        }
    )


async def eventplanner_exception_handler(request: Request, exc: EventPlannerException) -> JSONResponse:
    """Handler for custom EventPlanner exceptions"""
    logger.warning(f"EventPlanner exception: {type(exc).__name__}: {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for FastAPI validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid input data",
            "details": errors
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler for HTTP exceptions"""
    logger.info(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail
        }
    )


async def mysql_exception_handler(request: Request, exc: MySQLError) -> JSONResponse:
    """Handler for MySQL database errors"""
    logger.error(f"MySQL error: {exc.errno} - {exc.msg}", exc_info=True)
    
    # Map common MySQL errors to user-friendly messages
    error_messages = {
        1062: "Duplicate entry. This record already exists.",
        1451: "Cannot delete or update. This record is referenced by other records.",
        1452: "Invalid foreign key reference.",
        1045: "Database access denied. Please check your credentials.",
        2003: "Cannot connect to database server.",
        2006: "Database server has gone away."
    }
    
    message = error_messages.get(exc.errno, "Database operation failed")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DatabaseError",
            "message": message,
            "detail": str(exc) if logger.level == logging.DEBUG else None
        }
    )

