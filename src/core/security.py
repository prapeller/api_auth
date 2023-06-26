import logging
import secrets
import string
from functools import wraps

import jwt
import requests
from authlib.integrations.starlette_client import OAuth

from core.config import settings
from core.enums import PermissionsNamesEnum
from core.exceptions import UnauthorizedException

logger = logging.getLogger(__name__)

oauth = OAuth()

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'})


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def get_user_info_google(encoded_jwt_google: str) -> dict | None:
    user_info_endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {"Authorization": f"Bearer {encoded_jwt_google}"}
    user_info_response = requests.get(user_info_endpoint, headers=headers)
    if user_info_response.status_code == 200:
        user_info = user_info_response.json()
        return user_info
    else:
        return None


def get_token_data(encoded_jwt_local: str) -> dict | None:
    try:
        return jwt.decode(encoded_jwt_local, settings.AUTH_SECRET, algorithms=settings.TOKEN_ENCODE_ALGORITHM)
    except jwt.ExpiredSignatureError:  # Token has expired
        return None
    except jwt.InvalidTokenError:  # Invalid token
        return None


def permissions(required: list[PermissionsNamesEnum]):
    # decorator for route, that denies access if token has not all specified permissions
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            access_token: str = kwargs.get('access_token')
            if access_token:
                token_permissions = get_token_data(access_token).get('permissions')
                for permission in required:
                    if permission not in token_permissions:
                        logger.error(f'required {permission=:} not in {token_permissions=:}')
                        raise UnauthorizedException

            return await func(*args, **kwargs)

        return wrapper

    return decorator
