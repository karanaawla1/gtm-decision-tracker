import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()
cache = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

def get_cached_analysis(decision_id: str):
    try:
        saved = cache.get(f"analysis:{decision_id}")        
        if saved:
            print(f"Cache mila: {decision_id}")
            return json.loads(saved)
        print(f"Cache nahi mila: {decision_id}")
        return None
    except Exception as e:
        print(f"Redis se data lene mein problem: {e}")
        return None
def set_cached_analysis(decision_id: str, analysis: dict, ttl: int = 3600):
    try:
        cache.setex(
            f"analysis:{decision_id}",
            ttl,
            json.dumps(analysis)
        )
    except Exception as e:
        print(f"Redis mein save karne mein problem: {e}")
def invalidate_cache(decision_id: str):
    try:
        cache.delete(f"analysis:{decision_id}")
    except Exception as e:
        print(f"Redis se delete karne mein problem: {e}")