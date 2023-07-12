import datetime as dt

import pydantic as pd

from core.enums import PermissionsNamesEnum, RolesNamesEnum
from db import SessionLocalAsync
from db.models.user import UserModel
from db.repository import SqlAlchemyRepositoryAsync
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

    @pd.validator('email')
    async def validate_unique_email(cls, email):
        """checks if user with the same email as user_ser.email already exists"""
        with SqlAlchemyRepositoryAsync(SessionLocalAsync()) as repo:
            user_with_the_same_email = await repo.get(UserModel, email=email)
            if user_with_the_same_email is not None:
                raise ValueError('User with the same email already exists')
        return email


class UserCreateSerializer(UserUpdateSerializer):
    email: pd.EmailStr
    password: str

    async def create(self, repo):
        hashed_password = get_password_hash(self.password)
        self.password = hashed_password
        user = await repo.create(UserModel, self)
        return user


class UserReadSerializer(pd.BaseModel):
    id: str
    updated_at: dt.datetime | None = None
    created_at: dt.datetime

    roles_ids: list[str] = []
    roles_names: list['RolesNamesEnum'] = []
    permissions_ids: list[str] = []
    permissions_names: list['PermissionsNamesEnum'] = []
    active_sessions_ids: list[str] = []

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
