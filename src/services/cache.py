import datetime as dt
import logging
from abc import ABC, abstractmethod
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class Cache(ABC):

    @abstractmethod
    async def set(self, *args, **kwargs):
        pass

    @abstractmethod
    def get(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        pass


class RedisCache(Cache):

    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, key: str, data: Any, ex: int | dt.timedelta) -> None:
        try:
            await self.redis.set(key, data, ex=ex)
            logger.info('redis_cache: by key= %s, set data= %s, ex= %s', key, data, ex)
        except RedisError as e:
            logger.error('redis_cache: by key= %s, failed to set data= %s, error= %s', key, data, e)

    async def get(self, key: str) -> bytes | None:
        data = None
        try:
            data = await self.redis.get(key)
            if data is not None:
                logger.info('redis_cache: by key= %s, get data= %s', key, data)
        except RedisError as e:
            logger.error('redis_cache: by key= %s, failed to get data= %s, error= %s', key, data, e)
        return data

    async def delete(self, key: str) -> None:
        data = None
        try:
            data = await self.redis.get(key)
            if data is not None:
                await self.redis.delete(key)
                logger.info('redis_cache: by key= %s, deleted data: %s', key, data)
        except RedisError as e:
            logger.error('redis_cache: by key= %s, failed to delete data= %s, error= %s', key, data, e)
