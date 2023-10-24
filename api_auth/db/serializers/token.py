import datetime as dt
import typing

import pydantic as pd
from pydantic.main import object_setattr

from core.enums import TokenTypesEnum, PermissionsNamesEnum, OAuthTypesEnum
from core.security import get_token_data


class TokenCreateSchema(pd.BaseModel):
    type: TokenTypesEnum

    sub: str  # user.uuid
    email: pd.EmailStr  # user.email
    permissions: list[PermissionsNamesEnum] = []  # user.permissions_names

    session_uuid: str | None = None  # session.id
    ip: str | None = None  # sesion.ip
    useragent: str | None = None  # session.useragent

    exp: dt.datetime  # expiration time

    oauth_type: OAuthTypesEnum = OAuthTypesEnum.local
    oauth_token: str | None = None


class TokenReadSchema(TokenCreateSchema):

    @classmethod
    def from_jwt(cls, encoded_jwt: str) -> typing.Union['TokenReadSchema', None]:
        m = cls.__new__(cls)
        decoded_jwt: dict | None = get_token_data(encoded_jwt)
        if decoded_jwt is None:
            return None
        decoded_jwt['exp'] = dt.datetime.fromtimestamp(decoded_jwt['exp'])
        object_setattr(m, '__dict__', decoded_jwt)
        object_setattr(m, '__fields_set__', cls.__fields_set__)
        m._init_private_attributes()
        return m


class TokenPairEncodedSerializer(pd.BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
