import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Request
from app.services.rate_limiter import RateLimiter, RateLimitRule, RateLimitType


@pytest.fixture
def rate_limiter():
    """Create rate limiter instance for testing."""
    return RateLimiter()


@pytest.fixture
def mock_request():
    """Create mock FastAPI request."""
    request = MagicMock(spec=Request)
    request.url.path = "/test/endpoint"
    request.client.host = "192.168.1.1"
    request.headers = {"X-Forwarded-For": "203.0.113.1"}
    return request


@pytest.fixture
def mock_redis_service():
    """Create mock Redis service."""
    mock_service = AsyncMock()
    mock_service.redis_client = AsyncMock()
    return mock_service


class TestRateLimiter:
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self, rate_limiter, mock_request):
        """Test rate limit check when request is allowed."""
        with patch.object(rate_limiter, '_check_limit', return_value=True):
            result = await rate_limiter.check_rate_limit(mock_request)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_blocked(self, rate_limiter, mock_request):
        """Test rate limit check when request is blocked."""
        with patch.object(rate_limiter, '_check_limit', return_value=False):
            result = await rate_limiter.check_rate_limit(mock_request)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_with_user_id(self, rate_limiter, mock_request):
        """Test rate limit check with user ID."""
        with patch.object(rate_limiter, '_check_limit', return_value=True) as mock_check:
            result = await rate_limiter.check_rate_limit(mock_request, user_id=123)
            
            assert result is True
            # Should check user-based limit in addition to others
            assert mock_check.call_count >= 4  # IP, endpoint, global, user
    
    def test_get_client_ip_forwarded_for(self, rate_limiter, mock_request):
        """Test client IP extraction from X-Forwarded-For header."""
        mock_request.headers = {"X-Forwarded-For": "203.0.113.1, 192.168.1.1"}
        
        ip = rate_limiter._get_client_ip(mock_request)
        
        assert ip == "203.0.113.1"
    
    def test_get_client_ip_real_ip(self, rate_limiter, mock_request):
        """Test client IP extraction from X-Real-IP header."""
        mock_request.headers = {"X-Real-IP": "203.0.113.2"}
        
        ip = rate_limiter._get_client_ip(mock_request)
        
        assert ip == "203.0.113.2"
    
    def test_get_client_ip_direct(self, rate_limiter, mock_request):
        """Test client IP extraction from direct client."""
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.100"
        
        ip = rate_limiter._get_client_ip(mock_request)
        
        assert ip == "192.168.1.100"
    
    def test_get_client_ip_unknown(self, rate_limiter):
        """Test client IP extraction when no IP available."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.client = None
        
        ip = rate_limiter._get_client_ip(mock_request)
        
        assert ip == "unknown"
    
    def test_get_rule_for_endpoint_specific(self, rate_limiter):
        """Test getting endpoint-specific rule."""
        rule = rate_limiter._get_rule_for_endpoint("/auth/otp/request", RateLimitType.ENDPOINT_BASED)
        
        assert rule.requests == 5
        assert rule.window == 300
    
    def test_get_rule_for_endpoint_default(self, rate_limiter):
        """Test getting default rule for endpoint."""
        rule = rate_limiter._get_rule_for_endpoint("/unknown/endpoint", RateLimitType.IP_BASED)
        
        assert rule.requests == 100
        assert rule.window == 60
    
    @pytest.mark.asyncio
    async def test_check_limit_redis_success(self, rate_limiter, mock_redis_service):
        """Test Redis-based rate limit check."""
        with patch('app.services.rate_limiter.redis_service', mock_redis_service):
            # Mock Redis pipeline operations
            mock_pipe = AsyncMock()
            mock_pipe.execute.return_value = [None, 5, None, None]  # Current count is 5
            mock_redis_service.redis_client.pipeline.return_value = mock_pipe
            
            rule = RateLimitRule(requests=10, window=60)
            result = await rate_limiter._check_limit_redis("test_key", rule, int(time.time()), int(time.time()) - 60)
            
            assert result is True  # 5 < 10, so allowed
    
    @pytest.mark.asyncio
    async def test_check_limit_redis_exceeded(self, rate_limiter, mock_redis_service):
        """Test Redis-based rate limit check when limit exceeded."""
        with patch('app.services.rate_limiter.redis_service', mock_redis_service):
            # Mock Redis pipeline operations
            mock_pipe = AsyncMock()
            mock_pipe.execute.return_value = [None, 15, None, None]  # Current count is 15
            mock_redis_service.redis_client.pipeline.return_value = mock_pipe
            
            rule = RateLimitRule(requests=10, window=60)
            result = await rate_limiter._check_limit_redis("test_key", rule, int(time.time()), int(time.time()) - 60)
            
            assert result is False  # 15 >= 10, so blocked
    
    @pytest.mark.asyncio
    async def test_check_limit_redis_fallback(self, rate_limiter, mock_redis_service):
        """Test Redis fallback to memory when Redis fails."""
        with patch('app.services.rate_limiter.redis_service', mock_redis_service):
            # Mock Redis failure
            mock_redis_service.redis_client.pipeline.side_effect = Exception("Redis error")
            
            rule = RateLimitRule(requests=10, window=60)
            current_time = int(time.time())
            
            # Should fallback to memory-based limiting
            with patch.object(rate_limiter, '_check_limit_memory', return_value=True) as mock_memory:
                result = await rate_limiter._check_limit_redis("test_key", rule, current_time, current_time - 60)
                
                assert result is True
                mock_memory.assert_called_once()
    
    def test_check_limit_memory_allowed(self, rate_limiter):
        """Test memory-based rate limit check when allowed."""
        rule = RateLimitRule(requests=10, window=60)
        current_time = int(time.time())
        window_start = current_time - 60
        
        # Clear any existing cache
        rate_limiter.memory_cache = {}
        
        result = rate_limiter._check_limit_memory("test_key", rule, current_time, window_start)
        
        assert result is True
        assert "test_key" in rate_limiter.memory_cache
        assert len(rate_limiter.memory_cache["test_key"]) == 1
    
    def test_check_limit_memory_exceeded(self, rate_limiter):
        """Test memory-based rate limit check when exceeded."""
        rule = RateLimitRule(requests=2, window=60)
        current_time = int(time.time())
        window_start = current_time - 60
        
        # Pre-populate cache with requests at limit
        rate_limiter.memory_cache["test_key"] = {
            str(current_time - 30): current_time - 30,
            str(current_time - 20): current_time - 20
        }
        
        result = rate_limiter._check_limit_memory("test_key", rule, current_time, window_start)
        
        assert result is False
    
    def test_check_limit_memory_cleanup_old_entries(self, rate_limiter):
        """Test memory cache cleanup of old entries."""
        rule = RateLimitRule(requests=10, window=60)
        current_time = int(time.time())
        window_start = current_time - 60
        
        # Add old entries that should be cleaned up
        old_time = current_time - 120  # Outside window
        rate_limiter.memory_cache["test_key"] = {
            str(old_time): old_time,
            str(current_time - 30): current_time - 30
        }
        
        result = rate_limiter._check_limit_memory("test_key", rule, current_time, window_start)
        
        assert result is True
        # Old entry should be removed
        assert str(old_time) not in rate_limiter.memory_cache["test_key"]
        # Recent entry should remain
        assert str(current_time - 30) in rate_limiter.memory_cache["test_key"]
    
    @pytest.mark.asyncio
    async def test_get_rate_limit_info(self, rate_limiter, mock_request):
        """Test getting rate limit information."""
        with patch.object(rate_limiter, '_get_current_count', return_value=5):
            info = await rate_limiter.get_rate_limit_info(mock_request, user_id=123)
            
            assert "ip" in info
            assert "endpoint" in info
            assert "limits" in info
            assert "ip" in info["limits"]
            assert "endpoint" in info["limits"]
            assert "global" in info["limits"]
            assert "user" in info["limits"]
            
            # Check limit structure
            ip_limit = info["limits"]["ip"]
            assert "current" in ip_limit
            assert "limit" in ip_limit
            assert "window" in ip_limit
            assert "remaining" in ip_limit
            assert "reset_time" in ip_limit
    
    @pytest.mark.asyncio
    async def test_get_current_count_redis(self, rate_limiter, mock_redis_service):
        """Test getting current count from Redis."""
        with patch('app.services.rate_limiter.redis_service', mock_redis_service):
            mock_redis_service.redis_client.zcount.return_value = 7
            
            count = await rate_limiter._get_current_count("test_key")
            
            assert count == 7
            mock_redis_service.redis_client.zcount.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_count_memory_fallback(self, rate_limiter):
        """Test getting current count from memory cache."""
        # Set up memory cache
        rate_limiter.memory_cache["test_key"] = {
            "req1": time.time(),
            "req2": time.time(),
            "req3": time.time()
        }
        
        with patch('app.services.rate_limiter.redis_service') as mock_redis:
            mock_redis.redis_client = None
            
            count = await rate_limiter._get_current_count("test_key")
            
            assert count == 3
    
    @pytest.mark.asyncio
    async def test_reset_rate_limit_redis(self, rate_limiter, mock_redis_service):
        """Test resetting rate limit in Redis."""
        with patch('app.services.rate_limiter.redis_service', mock_redis_service):
            mock_redis_service.delete.return_value = True
            
            result = await rate_limiter.reset_rate_limit("test_key")
            
            assert result is True
            mock_redis_service.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_reset_rate_limit_memory(self, rate_limiter):
        """Test resetting rate limit in memory cache."""
        # Set up memory cache
        rate_limiter.memory_cache["test_key"] = {"req1": time.time()}
        
        with patch('app.services.rate_limiter.redis_service') as mock_redis:
            mock_redis.redis_client = None
            
            result = await rate_limiter.reset_rate_limit("test_key")
            
            assert result is True
            assert "test_key" not in rate_limiter.memory_cache
    
    @pytest.mark.asyncio
    async def test_reset_rate_limit_error(self, rate_limiter, mock_redis_service):
        """Test reset rate limit error handling."""
        with patch('app.services.rate_limiter.redis_service', mock_redis_service):
            mock_redis_service.delete.side_effect = Exception("Redis error")
            
            result = await rate_limiter.reset_rate_limit("test_key")
            
            assert result is False