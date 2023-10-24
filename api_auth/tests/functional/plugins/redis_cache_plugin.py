import pytest_asyncio
from redis.asyncio import Redis

from services.cache.cache import RedisCache
from tests.functional.settings import test_settings


@pytest_asyncio.fixture
async def redis_cache():
    return RedisCache(redis=Redis(host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT))
