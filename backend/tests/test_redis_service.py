import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.services.redis_service import RedisService


@pytest.fixture
def redis_service():
    """Create Redis service instance for testing."""
    service = RedisService()
    return service


@pytest.fixture
def mock_redis_client():
    """Create mock Redis client."""
    mock_client = AsyncMock()
    mock_client.ping.return_value = True
    mock_client.get.return_value = "test_value"
    mock_client.set.return_value = True
    mock_client.delete.return_value = 1
    mock_client.incr.return_value = 1
    mock_client.expire.return_value = True
    mock_client.ttl.return_value = 300
    mock_client.exists.return_value = 1
    mock_client.hset.return_value = 1
    mock_client.hget.return_value = "test_hash_value"
    mock_client.hgetall.return_value = {"key1": "value1", "key2": "value2"}
    mock_client.hdel.return_value = 1
    mock_client.close = AsyncMock()
    return mock_client


class TestRedisService:
    
    @pytest.mark.asyncio
    async def test_connect_success(self, redis_service, mock_redis_client):
        """Test successful Redis connection."""
        with patch('redis.asyncio.ConnectionPool.from_url') as mock_pool, \
             patch('redis.asyncio.Redis') as mock_redis:
            
            mock_redis.return_value = mock_redis_client
            
            await redis_service.connect()
            
            assert redis_service.redis_client is not None
            mock_redis_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, redis_service):
        """Test Redis connection failure."""
        with patch('redis.asyncio.ConnectionPool.from_url', side_effect=Exception("Connection failed")):
            await redis_service.connect()
            assert redis_service.redis_client is None
    
    @pytest.mark.asyncio
    async def test_get_success(self, redis_service, mock_redis_client):
        """Test successful GET operation."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.get("test_key")
        
        assert result == "test_value"
        mock_redis_client.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_get_no_client(self, redis_service):
        """Test GET operation without Redis client."""
        redis_service.redis_client = None
        
        result = await redis_service.get("test_key")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_success(self, redis_service, mock_redis_client):
        """Test successful SET operation."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.set("test_key", "test_value", 300)
        
        assert result is True
        mock_redis_client.set.assert_called_once_with("test_key", "test_value", ex=300)
    
    @pytest.mark.asyncio
    async def test_set_no_client(self, redis_service):
        """Test SET operation without Redis client."""
        redis_service.redis_client = None
        
        result = await redis_service.set("test_key", "test_value")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_success(self, redis_service, mock_redis_client):
        """Test successful DELETE operation."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.delete("test_key")
        
        assert result is True
        mock_redis_client.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_incr_success(self, redis_service, mock_redis_client):
        """Test successful INCR operation."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.incr("counter_key")
        
        assert result == 1
        mock_redis_client.incr.assert_called_once_with("counter_key")
    
    @pytest.mark.asyncio
    async def test_expire_success(self, redis_service, mock_redis_client):
        """Test successful EXPIRE operation."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.expire("test_key", 300)
        
        assert result is True
        mock_redis_client.expire.assert_called_once_with("test_key", 300)
    
    @pytest.mark.asyncio
    async def test_ttl_success(self, redis_service, mock_redis_client):
        """Test successful TTL operation."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.ttl("test_key")
        
        assert result == 300
        mock_redis_client.ttl.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_exists_success(self, redis_service, mock_redis_client):
        """Test successful EXISTS operation."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.exists("test_key")
        
        assert result is True
        mock_redis_client.exists.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_hset_success(self, redis_service, mock_redis_client):
        """Test successful HSET operation."""
        redis_service.redis_client = mock_redis_client
        
        mapping = {"field1": "value1", "field2": {"nested": "value"}}
        result = await redis_service.hset("test_hash", mapping)
        
        assert result is True
        mock_redis_client.hset.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_hget_success(self, redis_service, mock_redis_client):
        """Test successful HGET operation."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.hget("test_hash", "field1")
        
        assert result == "test_hash_value"
        mock_redis_client.hget.assert_called_once_with("test_hash", "field1")
    
    @pytest.mark.asyncio
    async def test_hgetall_success(self, redis_service, mock_redis_client):
        """Test successful HGETALL operation."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.hgetall("test_hash")
        
        assert result == {"key1": "value1", "key2": "value2"}
        mock_redis_client.hgetall.assert_called_once_with("test_hash")
    
    @pytest.mark.asyncio
    async def test_store_session_success(self, redis_service, mock_redis_client):
        """Test successful session storage."""
        redis_service.redis_client = mock_redis_client
        
        session_data = {"user_id": 1, "role": "buyer", "login_time": "2023-01-01"}
        result = await redis_service.store_session("session_123", session_data, 3600)
        
        assert result is True
        mock_redis_client.hset.assert_called_once()
        mock_redis_client.expire.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_session_success(self, redis_service, mock_redis_client):
        """Test successful session retrieval."""
        redis_service.redis_client = mock_redis_client
        mock_redis_client.hgetall.return_value = {
            "user_id": "1",
            "role": "buyer",
            "login_time": "2023-01-01"
        }
        
        result = await redis_service.get_session("session_123")
        
        assert result is not None
        assert "user_id" in result
        mock_redis_client.hgetall.assert_called_once_with("session:session_123")
    
    @pytest.mark.asyncio
    async def test_get_session_not_found(self, redis_service, mock_redis_client):
        """Test session retrieval when session doesn't exist."""
        redis_service.redis_client = mock_redis_client
        mock_redis_client.hgetall.return_value = {}
        
        result = await redis_service.get_session("nonexistent_session")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_session_success(self, redis_service, mock_redis_client):
        """Test successful session deletion."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.delete_session("session_123")
        
        assert result is True
        mock_redis_client.delete.assert_called_once_with("session:session_123")
    
    @pytest.mark.asyncio
    async def test_extend_session_success(self, redis_service, mock_redis_client):
        """Test successful session extension."""
        redis_service.redis_client = mock_redis_client
        
        result = await redis_service.extend_session("session_123", 7200)
        
        assert result is True
        mock_redis_client.expire.assert_called_once_with("session:session_123", 7200)
    
    @pytest.mark.asyncio
    async def test_disconnect(self, redis_service, mock_redis_client):
        """Test Redis disconnection."""
        redis_service.redis_client = mock_redis_client
        redis_service._connection_pool = AsyncMock()
        
        await redis_service.disconnect()
        
        mock_redis_client.close.assert_called_once()
        redis_service._connection_pool.disconnect.assert_called_once()