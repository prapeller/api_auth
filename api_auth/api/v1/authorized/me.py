import fastapi as fa
import sqlalchemy as sa

from core.dependencies import (
    get_current_user_dependency,
    sql_alchemy_repo_dependency,
    verified_token_schema_dependency,
    pagination_params_dependency
)
from core.enums import SessionOrderByEnum, OrderEnum
from db.models.session import SessionModel
from db.models.user import UserModel
from db.repository import SqlAlchemyRepositoryAsync
from db.serializers.permission import PermissionReadSerializer
from db.serializers.session import SessionReadSerializer, PaginatedSessionsSerializer
from db.serializers.token import TokenReadSchema
from db.serializers.user import UserUpdateSerializer, UserUpdatePasswordSerializer, UserReadSerializer

router = fa.APIRouter()


@router.get("/sessions-active",
            response_model=list[SessionReadSerializer])
async def me_login_history(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    return current_user.active_sessions


@router.get("/",
            response_model=UserReadSerializer)
async def me(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    return current_user


@router.get("/sessions",
            response_model=PaginatedSessionsSerializer)
async def me_sessions(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sql_alchemy_repo_dependency),
        order_by: SessionOrderByEnum = SessionOrderByEnum.created_at,
        order: OrderEnum = OrderEnum.desc,
        pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    sessions_select = sa.select(SessionModel).where(SessionModel.user_uuid == current_user.uuid)
    count_statement = sa.select(sa.func.count()).select_from(sessions_select.alias())
    total_sessions = (await repo.session.execute(count_statement)).scalar_one()
    paginated_sessions_select = await repo.get_paginated_select(SessionModel, sessions_select, order_by, order,
                                                                pagination_params)
    paginated_sessions = (await repo.session.execute(paginated_sessions_select)).scalars().all()

    return PaginatedSessionsSerializer(sessions=paginated_sessions, total_count=total_sessions)


@router.get("/permissions",
            response_model=list[PermissionReadSerializer],
            )
async def me_permissions(
        current_user: UserModel = fa.Depends(get_current_user_dependency)
):
    return current_user.permissions


@router.put("/update-credentials",
            response_model=UserReadSerializer)
async def me_update_credentials(
        user_ser: UserUpdateSerializer,
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sql_alchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency)
):
    user = await repo.update(current_user, user_ser)
    return user


@router.put("/update-password",
            response_model=UserReadSerializer)
async def me_update_password(
        user_ser: UserUpdatePasswordSerializer,
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sql_alchemy_repo_dependency),
        access_token_schema: TokenReadSchema = fa.Depends(verified_token_schema_dependency),
):
    user = await user_ser.update_password(repo, access_token_schema.sub)
    return user
