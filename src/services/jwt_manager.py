import datetime as dt
import logging
import uuid

import jwt
import pydantic as pd

from core.config import settings
from core.enums import TokenTypesEnum, PermissionsNamesEnum
from db.serializers.token import TokenPairEncodedSerializer, TokenCreateSchema

logger = logging.getLogger(__name__)


def create_token(token_schema: TokenCreateSchema) -> str:
    token_data = token_schema.dict()
    token_data.update({'jti': str(uuid.uuid4())})
    return jwt.encode(token_data, settings.AUTH_SECRET, algorithm=settings.TOKEN_ENCODE_ALGORITHM)


def create_access_token(user_id: str, email: pd.EmailStr, permissions: list[PermissionsNamesEnum],
                        session_id: str, ip: str, useragent: str) -> str:
    token_schema = TokenCreateSchema(
        type=TokenTypesEnum.access,
        sub=user_id,
        email=email,
        permissions=permissions,
        session_id=session_id,
        ip=ip,
        useragent=useragent,
        exp=dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXP_MIN)
    )
    return create_token(token_schema)


def create_refresh_token(user_id: str, email: pd.EmailStr, permissions: list[PermissionsNamesEnum],
                         session_id: str, ip: str, useragent: str) -> str:
    token_schema = TokenCreateSchema(
        type=TokenTypesEnum.refresh,
        sub=user_id,
        email=email,
        permissions=permissions,
        session_id=session_id,
        ip=ip,
        useragent=useragent,
        exp=dt.datetime.utcnow() + dt.timedelta(minutes=settings.REFRESH_TOKEN_EXP_MIN)
    )
    return create_token(token_schema)


def create_token_pair(user_id: str, email: pd.EmailStr, permissions: list[PermissionsNamesEnum],
                      session_id: str, ip: str, useragent: str) -> TokenPairEncodedSerializer:
    access_token = create_access_token(user_id, email, permissions,
                                       session_id, ip, useragent)
    refresh_token = create_refresh_token(user_id, email, permissions,
                                         session_id, ip, useragent)
    token_pair = TokenPairEncodedSerializer(access_token=access_token, refresh_token=refresh_token)
    logger.info(f'jwt_manager.create_token_pair: created {token_pair=:}')
    return token_pair
