"""
Enhanced structured logging system with correlation IDs for AgriDAO.
Provides structured logging with correlation IDs for tracking requests across services.
"""

import json
import logging
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for storing correlation ID
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "correlation_id": _correlation_id.get() or str(uuid.uuid4()),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
        if hasattr(record, 'error_message'):
            log_entry['error_message'] = record.error_message
        if hasattr(record, 'stack_trace'):
            log_entry['stack_trace'] = record.stack_trace
            
        # Add any extra attributes
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                          'relativeCreated', 'thread', 'threadName', 'processName', 
                          'process', 'getMessage'] and not key.startswith('_'):
                log_entry[key] = value
                
        return json.dumps(log_entry, ensure_ascii=False)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs to requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Add correlation ID to request context."""
        # Get or create correlation ID
        correlation_id = request.headers.get('X-Correlation-ID') or str(uuid.uuid4())
        
        # Set correlation ID in context
        token = _correlation_id.set(correlation_id)
        
        try:
            response = await call_next(request)
            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = correlation_id
            return response
        finally:
            # Clean up context variable
            _correlation_id.reset(token)


class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def _log_with_context(self, level: int, msg: str, **kwargs):
        """Log with additional context."""
        extra = kwargs.pop('extra', {})
        extra.update(kwargs)
        self.logger.log(level, msg, extra=extra)
    
    def debug(self, msg: str, **kwargs):
        """Debug level logging."""
        self._log_with_context(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs):
        """Info level logging."""
        self._log_with_context(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        """Warning level logging."""
        self._log_with_context(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        """Error level logging."""
        self._log_with_context(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs):
        """Critical level logging."""
        self._log_with_context(logging.CRITICAL, msg, **kwargs)
    
    def exception(self, msg: str, **kwargs):
        """Exception logging with stack trace."""
        kwargs['stack_trace'] = logging.Formatter().formatException(
            kwargs.pop('exc_info', None) or logging.sys.exc_info()
        )
        self._log_with_context(logging.ERROR, msg, **kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Set up structured logging configuration."""
    
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = StructuredFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure uvicorn access logs
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = [console_handler]
    
    # Configure uvicorn error logs
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.handlers = [console_handler]
    
    # Configure sqlalchemy logs
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.WARNING)
    
    # Configure redis logs
    redis_logger = logging.getLogger("redis")
    redis_logger.setLevel(logging.WARNING)


def log_request(request: Request, response_status: int, duration_ms: float, **kwargs):
    """Log HTTP request details."""
    logger = get_logger("http.request")
    logger.info(
        f"{request.method} {request.url.path} - {response_status}",
        method=request.method,
        endpoint=request.url.path,
        status_code=response_status,
        duration_ms=duration_ms,
        **kwargs
    )


def log_security_event(event_type: str, user_id: Optional[str] = None, 
                      details: Optional[Dict[str, Any]] = None, **kwargs):
    """Log security-related events."""
    logger = get_logger("security")
    logger.warning(
        f"Security event: {event_type}",
        event_type=event_type,
        user_id=user_id,
        details=details or {},
        **kwargs
    )


def log_database_operation(operation: str, table: str, duration_ms: float, 
                          rows_affected: Optional[int] = None, **kwargs):
    """Log database operations for performance monitoring."""
    logger = get_logger("database")
    logger.debug(
        f"Database {operation} on {table}",
        operation=operation,
        table=table,
        duration_ms=duration_ms,
        rows_affected=rows_affected,
        **kwargs
    )


def log_payment_event(event_type: str, user_id: Optional[str] = None, 
                     amount: Optional[float] = None, currency: str = "BDT", 
                     **kwargs):
    """Log payment-related events."""
    logger = get_logger("payment")
    logger.info(
        f"Payment event: {event_type}",
        event_type=event_type,
        user_id=user_id,
        amount=amount,
        currency=currency,
        **kwargs
    )


def log_performance_metric(metric_name: str, value: float, unit: str, **kwargs):
    """Log performance metrics."""
    logger = get_logger("performance")
    logger.info(
        f"Performance metric: {metric_name} = {value} {unit}",
        metric_name=metric_name,
        value=value,
        unit=unit,
        **kwargs
    )