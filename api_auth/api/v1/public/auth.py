import secrets
from copy import copy
from typing import Annotated

import fastapi as fa
from core.dependencies import auth_manager_dependency, sql_alchemy_repo_dependency
from core.enums import ResponseDetailEnum, OAuthTypesEnum
from core.exceptions import UnauthorizedException
from core.security import generate_password
from db.models.social_account import SocialAccountModel
from db.models.user import UserModel
from db.repository import SqlAlchemyRepositoryAsync
from db.serializers.session import SessionFromRequestSchema
from db.serializers.social_account import SocialAccountCreateSerializer
from db.serializers.token import TokenPairEncodedSerializer, TokenReadSchema
from db.serializers.user import UserLoginSchema, UserCreateSerializer, UserReadSerializer, UserLoginOAuthSchema
from services.auth_manager.auth_manager import AuthManager
from services.oauth import get_oauth_token, get_user_info_oauth, get_redirect_uri_with_state, get_user_data

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


@router.post('/login',
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
    session_from_request = SessionFromRequestSchema(
        useragent=request.headers.get("user-agent"),
        ip=request.headers.get('X-Forwarded-For'),
    )
    token_pair_encoded_ser = await auth_manager.login(user_login_schema, session_from_request)
    return token_pair_encoded_ser


@router.post('/refresh-access-token',
             response_model=TokenPairEncodedSerializer,
             responses={
                 fa.status.HTTP_401_UNAUTHORIZED: {'detail': ResponseDetailEnum.unauthorized},
             })
async def auth_refresh_access_token(
        request: fa.Request,
        refresh_token: str = fa.Body(...),
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
):
    session_from_request = SessionFromRequestSchema(
        useragent=request.headers.get("user-agent"),
        ip=request.headers.get('X-Forwarded-For'),
    )
    token_schema = await auth_manager.get_verified_token_schema(refresh_token, session_from_request)
    if token_schema is None:
        raise UnauthorizedException
    token_pair_encoded_ser = await auth_manager.refresh(refresh_token)
    return token_pair_encoded_ser


@router.post('/verify-access-token',
             response_model=TokenReadSchema,
             responses={
                 fa.status.HTTP_200_OK: {'detail': ResponseDetailEnum.ok},
                 fa.status.HTTP_401_UNAUTHORIZED: {'detail': ResponseDetailEnum.unauthorized},
             })
async def auth_verify_access_token(
        ip: str = fa.Body(...),
        useragent: str = fa.Body(...),
        access_token: str = fa.Body(...),
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
):
    session_from_request = SessionFromRequestSchema(
        useragent=useragent,
        ip=ip
    )
    token_schema = await auth_manager.get_verified_token_schema(access_token, session_from_request)
    if token_schema is None:
        raise UnauthorizedException
    return token_schema


# Store the state value in session memory
stored_state = None


@router.get('/login-oauth/{oauth_type}')
async def login_oauth(
        oauth_type: OAuthTypesEnum
):
    global stored_state
    stored_state = secrets.token_urlsafe(16)
    redirect_uri_with_state = await get_redirect_uri_with_state(oauth_type, stored_state)
    return fa.responses.RedirectResponse(redirect_uri_with_state)


@router.get('/oauth-redirect/{oauth_type}')
async def oauth_redirect(
        oauth_type: OAuthTypesEnum,
        request: fa.Request,
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sql_alchemy_repo_dependency),
):
    global stored_state
    oauth_token = await get_oauth_token(request, copy(stored_state), oauth_type=oauth_type)
    user_info = await get_user_info_oauth(oauth_token, oauth_type=oauth_type)
    user_email, user_name, social_id = await get_user_data(user_info, oauth_type=oauth_type)

    social_account = await repo.get(SocialAccountModel, social_id=social_id, social_name=oauth_type)
    if social_account is None:
        user = await repo.get(UserModel, email=user_email)
        if user is None:
            user_ser = UserCreateSerializer(email=user_email, name=user_name, password=generate_password())
            user = await auth_manager.register(user_ser)
            social_account_ser = SocialAccountCreateSerializer(user_uuid=user.uuid,
                                                               social_name=oauth_type,
                                                               social_id=social_id)
            await repo.create(SocialAccountModel, social_account_ser)
    session_from_request = SessionFromRequestSchema(
        useragent=request.headers.get("user-agent"),
        ip=request.headers.get('X-Forwarded-For'),
    )
    token_pair = await auth_manager.login(UserLoginOAuthSchema(email=user_email),
                                          session_from_request,
                                          oauth_type=oauth_type,
                                          oauth_token=oauth_token)
    return token_pair
