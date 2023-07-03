import datetime as dt
import typing

import pydantic as pd
from pydantic.main import object_setattr

from core.enums import TokenTypesEnum, PermissionsNamesEnum, OAuthTypesEnum
from core.security import get_token_data


class TokenCreateSchema(pd.BaseModel):
    type: TokenTypesEnum

    sub: str  # user.id
    email: pd.EmailStr  # user.email
    permissions: list[PermissionsNamesEnum] = []  # user.permissions_names

    session_id: str  # session.id
    ip: str  # sesion.ip
    useragent: str  # session.useragent

    exp: dt.datetime  # expiration time

    oauth_type: OAuthTypesEnum
    oauth_token: str


class TokenReadSchema(TokenCreateSchema):

    @classmethod
    def from_jwt(cls, encoded_jwt: str) -> typing.Union['TokenReadSchema', None]:
        m = cls.__new__(cls)
        decoded_jwt: dict | None = get_token_data(encoded_jwt)
        if decoded_jwt is None:
            return None
        object_setattr(m, '__dict__', decoded_jwt)
        object_setattr(m, '__fields_set__', cls.__fields_set__)
        m._init_private_attributes()
        return m


class TokenPairEncodedSerializer(pd.BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
