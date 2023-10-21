import datetime as dt

import pydantic as pd

from core.enums import PermissionsNamesEnum


class PermissionUpdateSerializer(pd.BaseModel):
    name: PermissionsNamesEnum | None = None


class PermissionCreateSerializer(PermissionUpdateSerializer):
    name: PermissionsNamesEnum


class PermissionReadSerializer(PermissionCreateSerializer):
    uuid: str
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    class Config:
        orm_mode = True
