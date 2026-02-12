import redis
import json

# Connect to local Redis instance
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_set(key, value, ex=30):
    r.set(key, json.dumps(value), ex=ex)

def cache_get(key):
    val = r.get(key)
    return json.loads(val) if val else None
