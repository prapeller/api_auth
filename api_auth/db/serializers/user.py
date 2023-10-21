import datetime as dt

import pydantic as pd

from core.enums import PermissionsNamesEnum, RolesNamesEnum
from db.models.user import UserModel
from services.hasher import get_password_hash


class UserUpdatePasswordSerializer(pd.BaseModel):
    password: str

    async def update_password(self, repo, user_id):
        user = await repo.get(UserModel, id=user_id)

        hashed_password = get_password_hash(self.password)
        self.password = hashed_password
        user = await repo.update(user, self)
        return user


class UserUpdateSerializer(pd.BaseModel):
    email: pd.EmailStr | None = None
    name: str | None = None
    is_active: bool | None = None


class UserCreateSerializer(UserUpdateSerializer):
    email: pd.EmailStr
    password: str


class UserReadSerializer(pd.BaseModel):
    id: int
    uuid: str
    updated_at: dt.datetime | None = None
    created_at: dt.datetime

    roles_uuids: list[str] = []
    roles_names: list['RolesNamesEnum'] = []
    permissions_uuids: list[str] = []
    permissions_names: list['PermissionsNamesEnum'] = []
    active_sessions_uuids: list[str] = []

    email: pd.EmailStr
    name: str
    is_active: bool

    class Config:
        orm_mode = True


class UserReadRolesSerializer(UserReadSerializer):
    roles: list['RoleReadSerializer'] = []

    class Config:
        orm_mode = True


class UserReadSessionsSerializer(UserReadSerializer):
    sessions: list['SessionReadSerializer'] = []

    class Config:
        orm_mode = True


class UserLoginSchema(pd.BaseModel):
    email: pd.EmailStr
    password: str


class UserLoginOAuthSchema(UserLoginSchema):
    password: str | None = None


from db.serializers.role import RoleReadSerializer
from db.serializers.session import SessionReadSerializer

RoleReadSerializer.update_forward_refs()
SessionReadSerializer.update_forward_refs()
