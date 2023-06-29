import fastapi as fa

from core.dependencies import (
    get_current_user_dependency,
    sql_alchemy_repo_dependency,
    verified_access_token_dependency,
    pagination_params_dependency
)
from core.enums import SessionOrderByEnum, OrderEnum
from db.models.session import SessionModel
from db.models.user import UserModel
from db.repository import SqlAlchemyRepository
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
        repo: SqlAlchemyRepository = fa.Depends(sql_alchemy_repo_dependency),
        order_by: SessionOrderByEnum = SessionOrderByEnum.created_at,
        order: OrderEnum = OrderEnum.desc,
        pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    session_query = repo.session.query(SessionModel).filter(SessionModel.user == current_user)
    total_sessions = session_query.count()
    paginated_sessions = repo.get_paginated_query(SessionModel, session_query, order_by, order, pagination_params).all()

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
        repo: SqlAlchemyRepository = fa.Depends(sql_alchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency)
):
    user = repo.update(current_user, user_ser)
    return user


@router.put("/update-password",
            response_model=UserReadSerializer)
async def me_update_password(
        user_ser: UserUpdatePasswordSerializer,
        repo: SqlAlchemyRepository = fa.Depends(sql_alchemy_repo_dependency),
        access_token: str = fa.Depends(verified_access_token_dependency),
):
    token_schema = TokenReadSchema.from_jwt(access_token)
    user = user_ser.update_password(repo, token_schema.sub)
    return user
