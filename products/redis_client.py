import redis
from django.conf import settings

class RedisClient:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = redis.Redis.from_url(settings.UPSTASH_REDIS_URL, decode_responses=True)
        return cls._client

redis_client = RedisClient.get_client()