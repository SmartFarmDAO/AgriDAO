"""
Logging middleware for enhanced request/response logging.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from app.core.logging import log_request, get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details and response metrics."""
        start_time = time.time()
        
        # Get logger
        logger = get_logger("http.request")
        
        # Log request start
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            method=request.method,
            endpoint=request.url.path,
            query_params=str(request.query_params),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
            content_type=request.headers.get("content-type"),
            content_length=request.headers.get("content-length"),
        )
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful response
            log_request(
                request=request,
                response_status=response.status_code,
                duration_ms=duration_ms,
                content_length=response.headers.get("content-length"),
                content_type=response.headers.get("content-type"),
            )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                method=request.method,
                endpoint=request.url.path,
                duration_ms=duration_ms,
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True,
            )
            raise


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor request performance."""
        start_time = time.time()
        
        response = await call_next(request)
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log performance metrics
        from app.core.logging import log_performance_metric
        log_performance_metric(
            metric_name="request_duration",
            value=duration_ms,
            unit="ms",
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
        )
        
        # Log slow requests
        if duration_ms > 1000:  # Requests taking more than 1 second
            logger = get_logger("performance")
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path}",
                method=request.method,
                endpoint=request.url.path,
                duration_ms=duration_ms,
                status_code=response.status_code,
            )
        
        return response