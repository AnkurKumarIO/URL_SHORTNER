import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Cache TTL setting (default: 24 hours)
DEFAULT_TTL = 86400


def get_cached_url(short_code: str) -> str | None:
    """Retrieve long URL from Redis cache by short_code."""
    try:
        return redis_client.get(f"short:{short_code}")
    except Exception:
        # Fallback gracefully if Redis is down
        return None


def set_cached_url(short_code: str, long_url: str, ttl: int = DEFAULT_TTL):
    """Store short_code -> long_url mapping in Redis cache with TTL."""
    try:
        redis_client.setex(f"short:{short_code}", ttl, long_url)
    except Exception:
        # Fallback gracefully if Redis is down
        pass
