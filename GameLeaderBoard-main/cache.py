import redis
import json

# Connect to local Redis instance
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

LEADERBOARD_TOP_CACHE_KEY = "leaderboard_top_10"
PLAYER_RANK_CACHE_KEY_PREFIX = "player_rank_"

def cache_set(key, value, ex=30):
    r.set(key, json.dumps(value), ex=ex)

def cache_get(key):
    val = r.get(key)
    return json.loads(val) if val else None


def cache_delete(key):
    r.delete(key)


def cache_delete_pattern(pattern: str):
    keys = r.keys(pattern)
    if keys:
        r.delete(*keys)
