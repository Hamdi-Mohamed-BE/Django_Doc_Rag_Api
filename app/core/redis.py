from django.conf import settings

import redis


class RedisStorage:
    def __init__(self):
        self.connection = redis.Redis(
            host=settings.REDIS_SERVER,
            db=settings.REDIS_APP_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )


redis_storage = RedisStorage()
