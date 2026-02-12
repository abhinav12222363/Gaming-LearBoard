import redis
import json

# Connect to local Redis instance
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

LEADERBOARD_TOP_CACHE_KEY = "leaderboard_top_10"
PLAYER_RANK_CACHE_KEY_PREFIX = "player_rank_"
PLAYER_RANK_CACHE_VERSION_KEY = "player_rank_cache_version"


def cache_set(key, value, ex=30):
    r.set(key, json.dumps(value), ex=ex)


def cache_get(key):
    val = r.get(key)
    return json.loads(val) if val else None


def cache_delete(key):
    r.delete(key)


def cache_delete_pattern(pattern: str):
    keys = list(r.scan_iter(match=pattern))
    if keys:
        r.delete(*keys)


def get_rank_cache_version() -> int:
    version = r.get(PLAYER_RANK_CACHE_VERSION_KEY)
    return int(version) if version else 1


def bump_rank_cache_version() -> int:
    return r.incr(PLAYER_RANK_CACHE_VERSION_KEY)
