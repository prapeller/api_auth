import datetime as dt
import logging
import uuid

import jwt
import pydantic as pd

from core.config import settings
from core.enums import TokenTypesEnum, PermissionsNamesEnum, OAuthTypesEnum
from db.serializers.token import TokenPairEncodedSerializer, TokenCreateSchema

logger = logging.getLogger(__name__)


def create_token(
        token_type: TokenTypesEnum,
        user_id: str,
        email: pd.EmailStr,
        permissions: list[PermissionsNamesEnum],
        session_id: str,
        ip: str,
        useragent: str,
        oauth_type: OAuthTypesEnum,
        oauth_token: str
) -> str:
    jti = str(uuid.uuid4())
    if token_type == TokenTypesEnum.access:
        exp = dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXP_MIN)
    else:
        exp = dt.datetime.utcnow() + dt.timedelta(minutes=settings.REFRESH_TOKEN_EXP_MIN)

    token_schema = TokenCreateSchema(
        type=token_type,
        sub=user_id,
        email=email,
        permissions=permissions,
        session_id=session_id,
        ip=ip,
        useragent=useragent,
        oauth_type=oauth_type,
        oauth_token=oauth_token,
        jti=jti,
        exp=exp,
    )
    return jwt.encode(token_schema.dict(), settings.AUTH_SECRET, algorithm=settings.TOKEN_ENCODE_ALGORITHM)


def create_token_pair(
        user_id: str,
        email: pd.EmailStr,
        permissions: list[PermissionsNamesEnum],
        session_id: str,
        ip: str,
        useragent: str,
        oauth_type: OAuthTypesEnum = OAuthTypesEnum.local,
        oauth_token='',
) -> TokenPairEncodedSerializer:
    access_token = create_token(token_type=TokenTypesEnum.access,
                                user_id=user_id,
                                email=email,
                                permissions=permissions,
                                session_id=session_id,
                                ip=ip,
                                useragent=useragent,
                                oauth_type=oauth_type,
                                oauth_token=oauth_token)
    refresh_token = create_token(token_type=TokenTypesEnum.refresh,
                                 user_id=user_id,
                                 email=email,
                                 permissions=permissions,
                                 session_id=session_id,
                                 ip=ip,
                                 useragent=useragent,
                                 oauth_type=oauth_type,
                                 oauth_token=oauth_token)
    token_pair = TokenPairEncodedSerializer(access_token=access_token, refresh_token=refresh_token)
    logger.info(f'jwt_manager.create_token_pair: created {token_pair=:}')
    return token_pair
