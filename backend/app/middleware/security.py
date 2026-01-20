import secrets
import time
from typing import Dict, Set, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import re
import html
import jwt
import os


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware to protect against XSS attacks by sanitizing request data."""
    
    def __init__(self, app):
        super().__init__(app)
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip XSS protection for certain content types or paths
        if self._should_skip_protection(request):
            return await call_next(request)
        
        # Check request body for XSS patterns if it's JSON
        if request.headers.get("content-type", "").startswith("application/json"):
            try:
                # XSS protection in JSON is complex and regex is prone to false positives
                # Modern frontend frameworks (React/Vue/Angular) handle output escaping
                # We'll rely on that for now and only block obvious script tags
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8')
                    # Less aggressive check for JSON - mainly looking for script injection
                    if r'<script' in body_str.lower() or r'javascript:' in body_str.lower():
                         if self._contains_xss_patterns(body_str):
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "error": "security_violation",
                                    "message": "Request contains potentially malicious content"
                                }
                            )
            except Exception:
                # If we can't decode the body, let it pass through
                pass
        
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
    
    def _should_skip_protection(self, request: Request) -> bool:
        """Check if XSS protection should be skipped for this request."""
        # Skip for file uploads or specific endpoints
        skip_paths = ["/docs", "/openapi.json", "/redoc"]
        return any(request.url.path.startswith(path) for path in skip_paths)
    
    def _contains_xss_patterns(self, content: str) -> bool:
        """Check if content contains XSS patterns."""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return True
        return False


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware to protect against CSRF attacks."""
    
    def __init__(self, app):
        super().__init__(app)
        self.csrf_tokens: Dict[str, float] = {}  # token -> expiry_time
        self.token_expiry = 3600  # 1 hour
        self.state_changing_methods = {"POST", "PUT", "PATCH", "DELETE"}
        self.exempt_paths = {
            "/auth/login",
            "/auth/register",
            "/auth/otp/request",
            "/auth/otp/verify", 
            "/auth/magic/request",
            "/auth/magic/verify",
            "/auth/refresh",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/health"
        }
    
    async def dispatch(self, request: Request, call_next):
        # Clean up expired tokens
        self._cleanup_expired_tokens()
        
        # Skip CSRF protection for safe methods and exempt paths
        if (request.method not in self.state_changing_methods or 
            request.url.path in self.exempt_paths or
            request.url.path.startswith("/auth/oauth/")):
            return await call_next(request)
        
        # Skip CSRF for requests with Bearer token (API authentication)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)
        
        # Check for CSRF token in headers
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token or not self._is_valid_csrf_token(csrf_token):
            return JSONResponse(
                status_code=403,
                content={
                    "error": "csrf_token_missing",
                    "message": "CSRF token is missing or invalid"
                }
            )
        
        response = await call_next(request)
        return response
    
    def _is_valid_csrf_token(self, token: str) -> bool:
        """Validate CSRF token."""
        if token not in self.csrf_tokens:
            return False
        
        if time.time() > self.csrf_tokens[token]:
            del self.csrf_tokens[token]
            return False
        
        return True
    
    def _cleanup_expired_tokens(self):
        """Remove expired CSRF tokens."""
        current_time = time.time()
        expired_tokens = [
            token for token, expiry in self.csrf_tokens.items() 
            if current_time > expiry
        ]
        for token in expired_tokens:
            del self.csrf_tokens[token]
    
    def generate_csrf_token(self) -> str:
        """Generate a new CSRF token."""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[token] = time.time() + self.token_expiry
        return token


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add comprehensive security headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'"
        )
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(self, app):
        super().__init__(app)
        # Import here to avoid circular imports
        from ..services.rate_limiter import rate_limiter
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        # Extract user ID from JWT token if present
        user_id = self._extract_user_id(request)
        
        # Check rate limits
        if not await self.rate_limiter.check_rate_limit(request, user_id):
            # Get rate limit info for response headers
            limit_info = await self.rate_limiter.get_rate_limit_info(request, user_id)
            
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60  # Default retry after 1 minute
                }
            )
            
            # Add rate limit headers
            if "ip" in limit_info["limits"]:
                ip_limit = limit_info["limits"]["ip"]
                response.headers["X-RateLimit-Limit"] = str(ip_limit["limit"])
                response.headers["X-RateLimit-Remaining"] = str(ip_limit["remaining"])
                response.headers["X-RateLimit-Reset"] = str(ip_limit["reset_time"])
            
            response.headers["Retry-After"] = "60"
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        try:
            limit_info = await self.rate_limiter.get_rate_limit_info(request, user_id)
            if "ip" in limit_info["limits"]:
                ip_limit = limit_info["limits"]["ip"]
                response.headers["X-RateLimit-Limit"] = str(ip_limit["limit"])
                response.headers["X-RateLimit-Remaining"] = str(ip_limit["remaining"])
                response.headers["X-RateLimit-Reset"] = str(ip_limit["reset_time"])
        except Exception:
            # Don't fail the request if we can't add headers
            pass
        
        return response
    
    def _extract_user_id(self, request: Request) -> Optional[int]:
        """Extract user ID from JWT token."""
        try:
            authorization = request.headers.get("authorization", "")
            if not authorization.lower().startswith("bearer "):
                return None
            
            token = authorization.split(" ", 1)[1]
            jwt_secret = os.getenv("JWT_SECRET", "devsecret")
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            return int(payload.get("sub"))
        except Exception:
            return None


# Global instances for CSRF token management
csrf_middleware_instance = None


def get_csrf_middleware() -> CSRFProtectionMiddleware:
    """Get the global CSRF middleware instance."""
    global csrf_middleware_instance
    return csrf_middleware_instance


def set_csrf_middleware(middleware: CSRFProtectionMiddleware):
    """Set the global CSRF middleware instance."""
    global csrf_middleware_instance
    csrf_middleware_instance = middleware