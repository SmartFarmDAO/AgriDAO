from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with user-friendly messages."""
    errors = []
    
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        error_msg = error["msg"]
        error_type = error["type"]
        
        # Create user-friendly error messages
        if error_type == "value_error.missing":
            message = f"{field_path} is required"
        elif error_type == "value_error.email":
            message = f"{field_path} must be a valid email address"
        elif error_type == "value_error.number.not_gt":
            message = f"{field_path} must be greater than {error.get('ctx', {}).get('limit_value', 0)}"
        elif error_type == "value_error.str.regex":
            message = f"{field_path} format is invalid"
        elif error_type == "value_error.list.min_items":
            message = f"{field_path} must contain at least {error.get('ctx', {}).get('limit_value', 1)} item(s)"
        else:
            message = f"{field_path}: {error_msg}"
        
        errors.append({
            "field": field_path,
            "message": message,
            "type": error_type
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Input validation failed",
            "details": errors
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {exc}")
    
    # Extract meaningful error messages from common integrity violations
    error_msg = str(exc.orig)
    
    if "UNIQUE constraint failed" in error_msg:
        if "email" in error_msg:
            message = "An account with this email already exists"
        elif "phone" in error_msg:
            message = "An account with this phone number already exists"
        else:
            message = "This record already exists"
    elif "FOREIGN KEY constraint failed" in error_msg:
        message = "Referenced record does not exist"
    elif "NOT NULL constraint failed" in error_msg:
        field = error_msg.split(".")[-1] if "." in error_msg else "field"
        message = f"Required field '{field}' cannot be empty"
    else:
        message = "Database constraint violation"
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "database_error",
            "message": message
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )