import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

def get_cached_analysis(decision_id: str):
    """Cache mein analysis hai toh wapas karo"""
    try:
        cached = redis_client.get(f"analysis:{decision_id}")
        if cached:
            print(f"Cache HIT: {decision_id}")
            return json.loads(cached)
        print(f"Cache MISS: {decision_id}")
        return None
    except Exception as e:
        print(f"Redis error: {e}")
        return None

def set_cached_analysis(decision_id: str, analysis: dict, ttl: int = 3600):
    """Analysis ko 1 ghante ke liye cache karo"""
    try:
        redis_client.setex(
            f"analysis:{decision_id}",
            ttl,
            json.dumps(analysis)
        )
    except Exception as e:
        print(f"Redis set error: {e}")

def invalidate_cache(decision_id: str):
    """Decision update hone pe cache delete karo"""
    try:
        redis_client.delete(f"analysis:{decision_id}")
    except Exception as e:
        print(f"Redis delete error: {e}")