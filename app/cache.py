import json

import redis

from .config import CACHE_TTL_SECONDS, REDIS_URL

r = redis.Redis.from_url(REDIS_URL)


def cache_profile(user_id: int, name: str):
    # Only what the UI needs, with an expiry.
    r.set(f"profile:{user_id}", json.dumps({"name": name}), ex=CACHE_TTL_SECONDS)


def forget_profile(user_id: int):
    r.delete(f"profile:{user_id}")
