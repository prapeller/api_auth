import datetime as dt
import uuid
from pathlib import Path

import jwt
import pydantic as pd

from core import config
from core.config import settings
from core.enums import TokenTypesEnum, PermissionsNamesEnum, OAuthTypesEnum
from core.logger_config import setup_logger
from db.models.user import UserModel
from db.serializers.token import TokenPairEncodedSerializer, TokenCreateSchema, TokenReadSchema

SERVICE_DIR = Path(__file__).resolve().parent
SERVICE_NAME = SERVICE_DIR.stem

logger = setup_logger(SERVICE_NAME, SERVICE_DIR)


async def create_temporary_register_token(user: UserModel) -> str:
    token_schema = TokenCreateSchema(
        type=TokenTypesEnum.register,
        sub=user.uuid,
        email=user.email,
        jti=str(uuid.uuid4()),
        exp=dt.datetime.utcnow() + dt.timedelta(minutes=config.TEMPORARY_REGISTER_TOKEN_EXP_MIN),
    )
    token_schema_encoded = jwt.encode(token_schema.dict(), settings.AUTH_SECRET,
                                      algorithm=config.TOKEN_ENCODE_ALGORITHM)
    return token_schema_encoded


async def create_token(
        token_type: TokenTypesEnum,
        user_uuid: str,
        email: pd.EmailStr,
        permissions: list[PermissionsNamesEnum],
        session_uuid: str,
        ip: str,
        useragent: str,
        oauth_type: OAuthTypesEnum,
        oauth_token: str
) -> str:
    jti = str(uuid.uuid4())
    if token_type == TokenTypesEnum.access:
        exp = dt.datetime.utcnow() + dt.timedelta(minutes=config.ACCESS_TOKEN_EXP_MIN)
    else:
        exp = dt.datetime.utcnow() + dt.timedelta(minutes=config.REFRESH_TOKEN_EXP_MIN)

    token_schema = TokenCreateSchema(
        type=token_type,
        sub=user_uuid,
        email=email,
        permissions=permissions,
        session_uuid=session_uuid,
        ip=ip,
        useragent=useragent,
        oauth_type=oauth_type,
        oauth_token=oauth_token,
        jti=jti,
        exp=exp,
    )
    return jwt.encode(token_schema.dict(), settings.AUTH_SECRET, algorithm=config.TOKEN_ENCODE_ALGORITHM)


async def create_token_pair(
        user_uuid: str,
        email: pd.EmailStr,
        permissions: list[PermissionsNamesEnum],
        session_uuid: str,
        ip: str,
        useragent: str,
        oauth_type: OAuthTypesEnum = OAuthTypesEnum.local,
        oauth_token='',
) -> TokenPairEncodedSerializer:
    access_token = await create_token(token_type=TokenTypesEnum.access,
                                      user_uuid=user_uuid,
                                      email=email,
                                      permissions=permissions,
                                      session_uuid=session_uuid,
                                      ip=ip,
                                      useragent=useragent,
                                      oauth_type=oauth_type,
                                      oauth_token=oauth_token)
    refresh_token = await create_token(token_type=TokenTypesEnum.refresh,
                                       user_uuid=user_uuid,
                                       email=email,
                                       permissions=permissions,
                                       session_uuid=session_uuid,
                                       ip=ip,
                                       useragent=useragent,
                                       oauth_type=oauth_type,
                                       oauth_token=oauth_token)
    token_pair = TokenPairEncodedSerializer(access_token=access_token, refresh_token=refresh_token)
    logger.info(f'create_token_pair: created {token_pair=:}')
    return token_pair
