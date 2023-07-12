import logging
import secrets
import string
from functools import wraps

import jwt
from core.config import settings
from core.enums import PermissionsNamesEnum
from core.exceptions import UnauthorizedException

logger = logging.getLogger(__name__)


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


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
            access_token_schema = kwargs.get('access_token_schema')
            if access_token_schema:
                token_permissions = access_token_schema.permissions
                for permission in required:
                    if permission not in token_permissions:
                        logger.error(f'required {permission=:} not in {token_permissions=:}')
                        raise UnauthorizedException

            return await func(*args, **kwargs)

        return wrapper

    return decorator
