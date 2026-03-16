"""
Rate limiting middleware
Protect API from abuse
"""

from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


# Create limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"]  # 100 requests per hour per IP
)


# Rate limit decorator for endpoints
def rate_limit(limit: str):
    """
    Decorator for rate limiting endpoints
    
    Usage:
        @rate_limit("10/minute")
        async def my_endpoint():
            ...
    """
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator