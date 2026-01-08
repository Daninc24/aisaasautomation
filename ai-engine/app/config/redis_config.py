import os
import redis.asyncio as redis
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[redis.Redis] = None

async def connect_redis():
    """Connect to Redis"""
    global redis_client
    
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Create Redis client
        redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection
        await redis_client.ping()
        
        logger.info("🔴 Connected to Redis")
        
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        raise

async def get_redis():
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        await connect_redis()
    return redis_client

async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("🔴 Redis connection closed")

# Cache utilities
class RedisCache:
    """Redis cache utilities"""
    
    @staticmethod
    async def get(key: str):
        """Get value from cache"""
        try:
            client = await get_redis()
            value = await client.get(key)
            return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    @staticmethod
    async def set(key: str, value: str, ttl: int = 3600):
        """Set value in cache with TTL"""
        try:
            client = await get_redis()
            await client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    @staticmethod
    async def delete(key: str):
        """Delete key from cache"""
        try:
            client = await get_redis()
            await client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    async def exists(key: str):
        """Check if key exists in cache"""
        try:
            client = await get_redis()
            return await client.exists(key)
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

# Queue utilities for background jobs
class RedisQueue:
    """Redis queue for background jobs"""
    
    @staticmethod
    async def enqueue(queue_name: str, job_data: dict):
        """Add job to queue"""
        try:
            client = await get_redis()
            import json
            await client.lpush(queue_name, json.dumps(job_data))
            return True
        except Exception as e:
            logger.error(f"Queue enqueue error: {e}")
            return False
    
    @staticmethod
    async def dequeue(queue_name: str):
        """Get job from queue"""
        try:
            client = await get_redis()
            job_data = await client.brpop(queue_name, timeout=1)
            if job_data:
                import json
                return json.loads(job_data[1])
            return None
        except Exception as e:
            logger.error(f"Queue dequeue error: {e}")
            return None