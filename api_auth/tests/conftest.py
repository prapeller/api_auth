from db import init_models

init_models()
pytest_plugins = (
    'tests.functional.plugins.aiohttp_plugin',
    'tests.functional.plugins.redis_cache_plugin',
)
