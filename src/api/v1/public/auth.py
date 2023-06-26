from typing import Annotated

import fastapi as fa
from fastapi.security import OAuth2PasswordRequestForm

from core.dependencies import auth_manager_dependency, sql_alchemy_repo_dependency
from core.enums import ResponseDetailEnum, RolesNamesEnum
from db.models.role import RoleModel
from db.repository import SqlAlchemyRepository
from db.serializers.session import SessionFromRequestSchema
from db.serializers.token import TokenPairEncodedSerializer
from db.serializers.user import UserLoginSchema, UserCreateSerializer, UserReadSerializer
from services.auth_manager import AuthManager

router = fa.APIRouter()


@router.post('/register',
             response_model=UserReadSerializer,
             responses={
                 fa.status.HTTP_422_UNPROCESSABLE_ENTITY: {'detail': ResponseDetailEnum.invalid_credentials}
             })
async def auth_register(
        user_ser: UserCreateSerializer,
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),

):
    user = await auth_manager.register(user_ser)
    return user


@router.post("/login",
             response_model=TokenPairEncodedSerializer,
             responses={
                 fa.status.HTTP_401_UNAUTHORIZED: {'detail': ResponseDetailEnum.unauthorized}
             })
async def auth_login(
        form_data: Annotated[OAuth2PasswordRequestForm, fa.Depends()],
        request: fa.Request,
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
):
    user_login_schema = UserLoginSchema(email=form_data.username, password=form_data.password)
    session_schema = SessionFromRequestSchema(useragent=request.headers.get("user-agent"), ip=request.client.host)
    return await auth_manager.login(user_login_schema, session_schema)


@router.post("/refresh-access-token",
             response_model=TokenPairEncodedSerializer,
             responses={
                 fa.status.HTTP_401_UNAUTHORIZED: {'detail': ResponseDetailEnum.unauthorized},
             })
async def auth_refresh_access_token(
        request: fa.Request,
        refresh_token: str = fa.Body(...),
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
):
    session_from_request = SessionFromRequestSchema(useragent=request.headers.get("user-agent"), ip=request.client.host)
    await auth_manager.verify_token(refresh_token, session_from_request)
    return await auth_manager.refresh(refresh_token)
