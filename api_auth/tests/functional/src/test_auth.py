from http import HTTPStatus

import pytest

from core.enums import RolesNamesEnum, MethodsEnum
from db import SessionLocalAsync
from db.models.session import SessionModel
from db.repository import SqlAlchemyRepositoryAsync
from db.serializers.token import TokenReadSchema
from services.cache.cache import RedisCache
from tests.functional.settings import test_settings
from tests.functional.src.helpers_users import user_data, create_test_registered_user, delete_user_by_email, \
    get_json_headers, get_login_headers, get_login_form_data

pytestmark = pytest.mark.asyncio

AUTH_URL = f'http://{test_settings.API_AUTH_HOST}:{test_settings.API_AUTH_PORT}/api/v1/auth'

REGISTER_URL = f'{AUTH_URL}/register'
LOGIN_URL = f'{AUTH_URL}/login'
LOGOUT_URL = f'{AUTH_URL}/logout'
REFRESH_URL = f'{AUTH_URL}/refresh-access-token'


async def test_post_api_v1_auth_register(body_status):
    """Test that route will return:
     - status 200
     - 'registered' in body.roles_names
     """
    await delete_user_by_email(email=user_data['email'])

    body, status = await body_status(REGISTER_URL, method=MethodsEnum.post, data=user_data)

    try:
        assert status == HTTPStatus.OK
        assert RolesNamesEnum.registered in body['roles_names']
    finally:
        await delete_user_by_email(email=user_data['email'])


async def test_post_api_v1_auth_login(body_status, redis_cache: RedisCache):
    """Test that route will return:
     - status 200
     - encoded access_token in body.access_token
     - user.email can be accessed in from encoded access_token
     - session was created in db
     - session was created in cache and encoded refresh_token can be accessed by session_id in access_token
     """
    await create_test_registered_user(user_data)
    try:
        headers = await get_login_headers()
        form_data = await get_login_form_data(user_data)
        body, status = await body_status(LOGIN_URL, method=MethodsEnum.post, data=form_data, headers=headers)
        access_token_schema = TokenReadSchema.from_jwt(body['access_token'])
        session_id = access_token_schema.session_id
        async with SqlAlchemyRepositoryAsync(SessionLocalAsync()) as repo:
            session_db = await repo.get(SessionModel, id=session_id)
        refresh_token_cached = await redis_cache.get(session_id)

        assert status == HTTPStatus.OK
        assert access_token_schema.email == user_data['email']
        assert isinstance(body['access_token'], str)
        assert session_db is not None
        assert refresh_token_cached is not None

    finally:
        await delete_user_by_email(email=user_data['email'])


async def test_post_api_v1_auth_logout_authorized(body_status, redis_cache: RedisCache):
    """Test that route will return:
     - status 200 if authorized user is being logged out
     - session was deactivated in db
     - session was removed from cache
     """
    # login
    await create_test_registered_user(user_data)
    try:
        headers = await get_login_headers()
        form_data = await get_login_form_data(user_data)
        body, status = await body_status(LOGIN_URL, method=MethodsEnum.post, data=form_data, headers=headers)
        access_token = body['access_token']
        access_token_schema = TokenReadSchema.from_jwt(access_token)
        session_id = access_token_schema.session_id
        # logout
        auth_headers = await get_json_headers()
        auth_headers.update({'Authorization': f'Bearer {access_token}'})
        body, status = await body_status(LOGOUT_URL, method=MethodsEnum.post, headers=auth_headers)
        async with SqlAlchemyRepositoryAsync(SessionLocalAsync()) as repo:
            session_db = await repo.get(SessionModel, id=session_id)
        refresh_token_cached = await redis_cache.get(session_id)

        assert status == HTTPStatus.OK
        assert session_db.is_active is False
        assert refresh_token_cached is None

    finally:
        await delete_user_by_email(email=user_data['email'])


async def test_post_api_v1_auth_logout_unauthorized(body_status, redis_cache: RedisCache):
    """Test that route will return:
     - status 401 if unauthorized user is being logged out
     """
    await create_test_registered_user(user_data)
    try:
        access_token = 'invalid_access_token'
        auth_headers = await get_json_headers()
        auth_headers.update({'Authorization': f'Bearer {access_token}'})
        body, status = await body_status(LOGOUT_URL, method=MethodsEnum.post, headers=auth_headers)

        assert status == HTTPStatus.UNAUTHORIZED
    finally:
        await delete_user_by_email(email=user_data['email'])


async def test_post_api_v1_auth_refresh_access_token_authorized(body_status, redis_cache: RedisCache):
    """Test that route will return:
     - status 200 if authorized user is being logged out
     - new access_token differs from old access_token
     - session in db still exists and active
     - session in cache still exists and can be accessed by session_id in new access_token
     - new refresh_token in cache differs from old refresh_token
     """
    await create_test_registered_user(user_data)
    try:
        # login
        headers = await get_login_headers()
        form_data = await get_login_form_data(user_data)
        login_body, login_status = await body_status(LOGIN_URL, method=MethodsEnum.post, data=form_data,
                                                     headers=headers)
        old_access_token = login_body['access_token']
        old_refresh_token = login_body['refresh_token']
        old_access_token_schema = TokenReadSchema.from_jwt(old_access_token)
        old_session_id = old_access_token_schema.session_id
        old_refresh_token_cached = await redis_cache.get(old_session_id)
        from time import sleep
        sleep(2)
        # refresh
        refresh_body, refresh_status = await body_status(REFRESH_URL, method=MethodsEnum.post, data=old_refresh_token)
        new_access_token = refresh_body['access_token']
        new_access_token_schema = TokenReadSchema.from_jwt(new_access_token)
        new_session_id = new_access_token_schema.session_id
        async with SqlAlchemyRepositoryAsync(SessionLocalAsync()) as repo:
            session_db = await repo.get(SessionModel, id=new_session_id)
        new_refresh_token_cached = await redis_cache.get(new_session_id)

        assert refresh_status == HTTPStatus.OK
        assert old_access_token != new_access_token
        assert session_db is not None and session_db.is_active is True
        assert new_refresh_token_cached is not None
        assert old_refresh_token_cached != new_refresh_token_cached
    finally:
        await delete_user_by_email(email=user_data['email'])
