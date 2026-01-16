import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from fastapi import HTTPException, Request
import logging

from .redis_service import redis_service

logger = logging.getLogger(__name__)


class RateLimitType(str, Enum):
    IP_BASED = "ip"
    USER_BASED = "user"
    ENDPOINT_BASED = "endpoint"
    GLOBAL = "global"


@dataclass
class RateLimitRule:
    """Rate limit rule configuration."""
    requests: int  # Number of requests allowed
    window: int    # Time window in seconds
    burst: Optional[int] = None  # Burst allowance (optional)


class RateLimiter:
    """Redis-based rate limiter with multiple strategies."""
    
    def __init__(self):
        # Default rate limit rules
        self.default_rules = {
            RateLimitType.IP_BASED: RateLimitRule(requests=100, window=60),  # 100 req/min per IP
            RateLimitType.USER_BASED: RateLimitRule(requests=1000, window=3600),  # 1000 req/hour per user
            RateLimitType.ENDPOINT_BASED: RateLimitRule(requests=10, window=60),  # 10 req/min per endpoint
            RateLimitType.GLOBAL: RateLimitRule(requests=10000, window=60)  # 10k req/min globally
        }
        
        # Endpoint-specific rules
        self.endpoint_rules = {
            "/auth/otp/request": RateLimitRule(requests=5, window=300),  # 5 OTP requests per 5 min
            "/auth/otp/verify": RateLimitRule(requests=10, window=300),  # 10 verify attempts per 5 min
            "/auth/magic/request": RateLimitRule(requests=3, window=300),  # 3 magic links per 5 min
            "/commerce/orders": RateLimitRule(requests=200, window=3600),  # 200 orders per hour
            "/marketplace/products": RateLimitRule(requests=5, window=60, burst=10),  # 5 products/min, burst 10
        }
        
        # In-memory fallback for when Redis is unavailable
        self.memory_cache: Dict[str, Dict[str, float]] = {}
    
    async def check_rate_limit(self, request: Request, user_id: Optional[int] = None) -> bool:
        """
        Check if request should be rate limited.
        Returns True if request is allowed, False if rate limited.
        """
        client_ip = self._get_client_ip(request)
        endpoint = request.url.path
        
        # Check different rate limit types
        checks = [
            (RateLimitType.IP_BASED, f"ip:{client_ip}"),
            (RateLimitType.ENDPOINT_BASED, f"endpoint:{endpoint}:{client_ip}"),
            (RateLimitType.GLOBAL, "global")
        ]
        
        if user_id:
            checks.append((RateLimitType.USER_BASED, f"user:{user_id}"))
        
        for limit_type, key in checks:
            rule = self._get_rule_for_endpoint(endpoint, limit_type)
            if not await self._check_limit(key, rule):
                logger.warning(f"Rate limit exceeded for {limit_type.value}: {key}")
                return False
        
        return True
    
    async def _check_limit(self, key: str, rule: RateLimitRule) -> bool:
        """Check rate limit for a specific key and rule."""
        current_time = int(time.time())
        window_start = current_time - rule.window
        
        # Try Redis first
        if redis_service.redis_client:
            return await self._check_limit_redis(key, rule, current_time, window_start)
        else:
            return self._check_limit_memory(key, rule, current_time, window_start)
    
    async def _check_limit_redis(self, key: str, rule: RateLimitRule, 
                               current_time: int, window_start: int) -> bool:
        """Redis-based rate limiting using sliding window."""
        try:
            # Use Redis sorted set for sliding window
            pipe = redis_service.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, rule.window + 1)
            
            results = await pipe.execute()
            current_count = results[1]  # Count after removing old entries
            
            return current_count < rule.requests
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fallback to memory-based limiting
            return self._check_limit_memory(key, rule, current_time, window_start)
    
    def _check_limit_memory(self, key: str, rule: RateLimitRule, 
                          current_time: int, window_start: int) -> bool:
        """Memory-based rate limiting fallback."""
        if key not in self.memory_cache:
            self.memory_cache[key] = {}
        
        # Clean old entries
        cache = self.memory_cache[key]
        old_keys = [k for k, v in cache.items() if v < window_start]
        for old_key in old_keys:
            del cache[old_key]
        
        # Check current count
        current_count = len(cache)
        
        if current_count < rule.requests:
            cache[str(current_time)] = current_time
            return True
        
        return False
    
    def _get_rule_for_endpoint(self, endpoint: str, limit_type: RateLimitType) -> RateLimitRule:
        """Get rate limit rule for specific endpoint and type."""
        if limit_type == RateLimitType.ENDPOINT_BASED and endpoint in self.endpoint_rules:
            return self.endpoint_rules[endpoint]
        
        return self.default_rules[limit_type]
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def get_rate_limit_info(self, request: Request, user_id: Optional[int] = None) -> Dict[str, any]:
        """Get current rate limit status for debugging/monitoring."""
        client_ip = self._get_client_ip(request)
        endpoint = request.url.path
        
        info = {
            "ip": client_ip,
            "endpoint": endpoint,
            "limits": {}
        }
        
        checks = [
            (RateLimitType.IP_BASED, f"ip:{client_ip}"),
            (RateLimitType.ENDPOINT_BASED, f"endpoint:{endpoint}:{client_ip}"),
            (RateLimitType.GLOBAL, "global")
        ]
        
        if user_id:
            checks.append((RateLimitType.USER_BASED, f"user:{user_id}"))
        
        for limit_type, key in checks:
            rule = self._get_rule_for_endpoint(endpoint, limit_type)
            current_count = await self._get_current_count(key)
            
            info["limits"][limit_type.value] = {
                "current": current_count,
                "limit": rule.requests,
                "window": rule.window,
                "remaining": max(0, rule.requests - current_count),
                "reset_time": int(time.time()) + rule.window
            }
        
        return info
    
    async def _get_current_count(self, key: str) -> int:
        """Get current request count for a key."""
        current_time = int(time.time())
        
        if redis_service.redis_client:
            try:
                # Count entries in current window
                window_start = current_time - self.default_rules[RateLimitType.IP_BASED].window
                count = await redis_service.redis_client.zcount(key, window_start, current_time)
                return count
            except Exception:
                pass
        
        # Fallback to memory cache
        if key in self.memory_cache:
            return len(self.memory_cache[key])
        
        return 0
    
    async def reset_rate_limit(self, key: str) -> bool:
        """Reset rate limit for a specific key (admin function)."""
        try:
            if redis_service.redis_client:
                await redis_service.delete(key)
            
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            return True
        except Exception as e:
            logger.error(f"Failed to reset rate limit for {key}: {e}")
            return False


# Global rate limiter instance
rate_limiter = RateLimiter()