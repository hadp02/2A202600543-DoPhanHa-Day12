"""
Rate Limiting with Redis (Sliding Window)
"""
import time
from fastapi import HTTPException
from app.config import settings

def check_rate_limit(r, key: str):
    """
    Check if the user has exceeded the rate limit using Redis Sliding Window.
    """
    if not r:
        # Fallback if Redis is not available
        return
        
    now = time.time()
    redis_key = f"rate_limit:{key}"
    window = 60  # 1 minute window
    
    pipe = r.pipeline()
    # Remove old entries outside the window
    pipe.zremrangebyscore(redis_key, 0, now - window)
    # Count current requests
    pipe.zcard(redis_key)
    # Add the new request
    pipe.zadd(redis_key, {str(now): now})
    # Set expiration to cleanup old keys
    pipe.expire(redis_key, window)
    
    results = pipe.execute()
    
    current_requests = results[1]
    
    if current_requests >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": str(window)},
        )
