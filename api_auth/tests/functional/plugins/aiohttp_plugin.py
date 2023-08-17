import json

import aiohttp
import pytest_asyncio

from core.enums import MethodsEnum


@pytest_asyncio.fixture
async def body_status():
    async def inner(url: str, method: MethodsEnum = MethodsEnum.get, params: dict = None, data: dict = None,
                    headers=None):

        if headers is None:
            headers = {
                'X-Request-Id': 'test',
                'Content-Type': 'application/json',
            }
            data = json.dumps(data)

        async with aiohttp.ClientSession() as session:
            if method == MethodsEnum.get:
                async with session.get(url, headers=headers, params=params) as response:
                    body = await response.json()
                    status = response.status
                    return body, status
            elif method == MethodsEnum.post:
                async with session.post(url, headers=headers, data=data) as response:
                    body = await response.json()
                    status = response.status
                    return body, status

    return inner
