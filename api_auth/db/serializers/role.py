import datetime as dt

import pydantic as pd

from core.enums import PermissionsNamesEnum


class RoleUpdateSerializer(pd.BaseModel):
    permissions_uuids: list[str] = []

    class Config:
        orm_mode = True


class RoleCreateSerializer(RoleUpdateSerializer):
    name: str


class RoleReadSerializer(RoleCreateSerializer):
    uuid: str
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    permissions_uuids: list[str] = []
    permissions_names: list[PermissionsNamesEnum] = []

    class Config:
        orm_mode = True


class RoleReadUsersSerializer(RoleReadSerializer):
    users: list['UserReadSerializer'] = []

    class Config:
        orm_mode = True


class RoleReadPermissionsSerializer(RoleReadSerializer):
    permissions: list['PermissionReadSerializer'] = []

    class Config:
        orm_mode = True


from db.serializers.user import UserReadSerializer
from db.serializers.permission import PermissionReadSerializer

UserReadSerializer.update_forward_refs()
PermissionReadSerializer.update_forward_refs()
