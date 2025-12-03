import os
import json
import asyncio
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for caching, session management, and rate limiting."""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client: Optional[Redis] = None
        self._connection_pool = None
    
    async def connect(self):
        """Initialize Redis connection."""
        try:
            self._connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                decode_responses=True,
                max_connections=20
            )
            self.redis_client = Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # For development, we'll continue without Redis
            self.redis_client = None
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            if self._connection_pool:
                await self._connection_pool.disconnect()
    
    async def ping(self) -> bool:
        """Ping Redis to check if connection is alive."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.ping()
            return result is True
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.set(key, value, ex=expire)
            return result is True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def incr(self, key: str) -> Optional[int]:
        """Increment counter in Redis."""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.incr(key)
        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return None
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.expire(key, seconds)
            return result is True
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> Optional[int]:
        """Get time to live for key."""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return None
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def hset(self, name: str, mapping: Dict[str, Any]) -> bool:
        """Set hash fields."""
        if not self.redis_client:
            return False
        
        try:
            # Convert values to strings for Redis
            string_mapping = {k: json.dumps(v) if not isinstance(v, str) else v 
                            for k, v in mapping.items()}
            result = await self.redis_client.hset(name, mapping=string_mapping)
            return result >= 0
        except Exception as e:
            logger.error(f"Redis HSET error for hash {name}: {e}")
            return False
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value."""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.hget(name, key)
        except Exception as e:
            logger.error(f"Redis HGET error for hash {name}, key {key}: {e}")
            return None
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """Get all hash fields."""
        if not self.redis_client:
            return {}
        
        try:
            return await self.redis_client.hgetall(name)
        except Exception as e:
            logger.error(f"Redis HGETALL error for hash {name}: {e}")
            return {}
    
    async def hdel(self, name: str, *keys: str) -> bool:
        """Delete hash fields."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.hdel(name, *keys)
            return result > 0
        except Exception as e:
            logger.error(f"Redis HDEL error for hash {name}: {e}")
            return False
    
    # Session management methods
    async def store_session(self, session_id: str, session_data: Dict[str, Any], 
                          expire_seconds: int = 3600) -> bool:
        """Store session data."""
        session_key = f"session:{session_id}"
        return await self.hset(session_key, session_data) and \
               await self.expire(session_key, expire_seconds)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        session_key = f"session:{session_id}"
        session_data = await self.hgetall(session_key)
        
        if not session_data:
            return None
        
        # Convert JSON strings back to objects
        result = {}
        for key, value in session_data.items():
            try:
                result[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                result[key] = value
        
        return result
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        session_key = f"session:{session_id}"
        return await self.delete(session_key)
    
    async def extend_session(self, session_id: str, expire_seconds: int = 3600) -> bool:
        """Extend session expiration."""
        session_key = f"session:{session_id}"
        return await self.expire(session_key, expire_seconds)
    
    # List operations for analytics and event tracking
    async def lpush(self, key: str, *values: str) -> Optional[int]:
        """Push values to the left of a list."""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.lpush(key, *values)
        except Exception as e:
            logger.error(f"Redis LPUSH error for key {key}: {e}")
            return None
    
    async def rpush(self, key: str, *values: str) -> Optional[int]:
        """Push values to the right of a list."""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.rpush(key, *values)
        except Exception as e:
            logger.error(f"Redis RPUSH error for key {key}: {e}")
            return None
    
    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get a range of elements from a list."""
        if not self.redis_client:
            return []
        
        try:
            return await self.redis_client.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Redis LRANGE error for key {key}: {e}")
            return []
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim a list to the specified range."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.ltrim(key, start, end)
            return result is True
        except Exception as e:
            logger.error(f"Redis LTRIM error for key {key}: {e}")
            return False
    
    async def llen(self, key: str) -> Optional[int]:
        """Get the length of a list."""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.llen(key)
        except Exception as e:
            logger.error(f"Redis LLEN error for key {key}: {e}")
            return None


# Global Redis service instance
redis_service = RedisService()