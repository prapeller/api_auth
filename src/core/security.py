import logging
from functools import wraps

import jwt

from core.config import settings
from core.enums import PermissionsNamesEnum
from core.exceptions import UnauthorizedException

logger = logging.getLogger(__name__)


def get_token_data(encoded_jwt: str) -> dict:
    try:
        return jwt.decode(encoded_jwt, settings.AUTH_SECRET, algorithms=settings.TOKEN_ENCODE_ALGORITHM)
    except jwt.ExpiredSignatureError:  # Token has expired
        raise UnauthorizedException
    except jwt.InvalidTokenError:  # Invalid token
        raise UnauthorizedException


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
