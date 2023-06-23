import datetime as dt

import pydantic as pd


class SessionUpdateSerializer(pd.BaseModel):
    id: str | None = None
    useragent: str | None = None
    ip: str | None = None
    is_active: bool | None = None


class SessionCreateSerializer(SessionUpdateSerializer):
    user_id: str
    useragent: str
    ip: str


class SessionReadSerializer(SessionCreateSerializer):
    id: str
    updated_at: dt.datetime | None = None
    created_at: dt.datetime

    class Config:
        orm_mode = True


class PaginatedSessionsSerializer(pd.BaseModel):
    sessions: list[SessionReadSerializer]
    total_count: int


class SessionReadUserSerializer(SessionReadSerializer):
    user: 'UserReadSerializer' = None

    class Config:
        orm_mode = True


class SessionFromRequestSchema(pd.BaseModel):
    useragent: str
    ip: str


class SessionCachedSchema(pd.BaseModel):
    id: str
    user_id: str
    useragent: str
    ip: str


from db.serializers.user import UserReadSerializer

SessionReadUserSerializer.update_forward_refs()
