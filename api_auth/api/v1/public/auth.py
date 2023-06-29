import secrets
from typing import Annotated

import fastapi as fa
import requests
from fastapi.security import OAuth2PasswordRequestForm

from core.config import settings
from core.dependencies import auth_manager_dependency, sql_alchemy_repo_dependency
from core.enums import ResponseDetailEnum, OAuthTypesEnum
from core.security import generate_password, get_user_info_oauth
from db.repository import SqlAlchemyRepository
from db.serializers.session import SessionFromRequestSchema
from db.serializers.token import TokenPairEncodedSerializer
from db.serializers.user import UserLoginSchema, UserCreateSerializer, UserReadSerializer, UserLoginOAuthSchema
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
    session_schema = SessionFromRequestSchema(useragent=request.headers.get('user-agent'), ip=request.client.host)
    return await auth_manager.login(user_login_schema, session_schema)


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
    session_from_request = SessionFromRequestSchema(useragent=request.headers.get('user-agent'), ip=request.client.host)
    await auth_manager.verify_token(refresh_token, session_from_request)
    return await auth_manager.refresh(refresh_token)


# Store the state value in memory for demonstration purposes
stored_state = None
redirect_uri_google = f'http://{settings.API_HOST}:{settings.API_PORT}/api/v1/auth/login-with-google-redirect'
redirect_uri_yandex = f'http://{settings.API_HOST}:{settings.API_PORT}/api/v1/auth/login-with-yandex-redirect'


@router.get('/login-with-google')
async def login_with_google():
    state = secrets.token_urlsafe(16)
    global stored_state
    stored_state = state
    return fa.responses.RedirectResponse(
        f'https://accounts.google.com/o/oauth2/v2/auth?'
        f'response_type=code&'
        f'client_id={settings.GOOGLE_CLIENT_ID}&'
        f'redirect_uri={redirect_uri_google}&'
        f'scope=openid+email+profile&'
        f'state={state}')


@router.get('/login-with-google-redirect')
async def login_with_google_redirect(
        request: fa.Request,
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
        repo: SqlAlchemyRepository = fa.Depends(sql_alchemy_repo_dependency),
):
    global stored_state
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    if state != stored_state:
        return {'message': 'State mismatch. Authentication failed.'}

    token_params = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': redirect_uri_google,
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=token_params)

    if response.status_code == 200:
        token_data = response.json()
        access_token_google = token_data.get('access_token')

        user_info = get_user_info_oauth(access_token_google, oauth_type=OAuthTypesEnum.google)
        user_email = user_info['email']
        user_social_id_google = user_info['id']
        user = repo.get_user_social(email=user_email, social_id_google=user_social_id_google)
        if user is None:
            user_ser = UserCreateSerializer(email=user_email, name=user_info['name'], password=generate_password(),
                                            social_id_google=user_social_id_google)
            await auth_manager.register(user_ser)
        session_schema = SessionFromRequestSchema(useragent=request.headers.get('user-agent'), ip=request.client.host)
        return await auth_manager.login(UserLoginOAuthSchema(email=user_email),
                                        session_schema,
                                        oauth_type=OAuthTypesEnum.google,
                                        oauth_token=access_token_google)

    else:
        return {'message': 'Token exchange failed.'}


@router.get('/login-with-yandex')
async def login_with_yandex():
    state = secrets.token_urlsafe(16)
    global stored_state
    stored_state = state
    return fa.responses.RedirectResponse(
        f'https://oauth.yandex.com/authorize?'
        f'response_type=code&'
        f'client_id={settings.YANDEX_CLIENT_ID}&'
        f'redirect_uri={redirect_uri_yandex}&'
        f'state={state}')


@router.get('/login-with-yandex-redirect')
async def login_with_yandex_redirect(
        request: fa.Request,
        auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
        repo: SqlAlchemyRepository = fa.Depends(sql_alchemy_repo_dependency),
):
    global stored_state
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    if state != stored_state:
        return {'message': 'State mismatch. Authentication failed.'}

    token_params = {
        'code': code,
        'client_id': settings.YANDEX_CLIENT_ID,
        'client_secret': settings.YANDEX_CLIENT_SECRET,
        'redirect_uri': redirect_uri_yandex,
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://oauth.yandex.com/token', data=token_params)

    if response.status_code == 200:
        token_data = response.json()
        access_token_yandex = token_data.get('access_token')

        # Fetch user information using the Yandex API
        user_info = get_user_info_oauth(access_token_yandex, oauth_type=OAuthTypesEnum.yandex)
        user_email = user_info['default_email']
        user_social_id = user_info['id']
        user_name = f'{user_info["first_name"]} {user_info["last_name"]}'

        # Check if the user exists in the repository
        user = repo.get_user_social(email=user_email, social_id_yandex=user_social_id)
        if user is None:
            # Register the user if they don't exist
            user_ser = UserCreateSerializer(email=user_email,
                                            name=user_name,
                                            password=generate_password(),
                                            social_id_yandex=user_social_id)
            await auth_manager.register(user_ser)

        # Perform login with Yandex OAuth
        session_schema = SessionFromRequestSchema(useragent=request.headers.get('user-agent'), ip=request.client.host)
        return await auth_manager.login(UserLoginOAuthSchema(email=user_email),
                                        session_schema,
                                        oauth_type=OAuthTypesEnum.yandex,
                                        oauth_token=access_token_yandex)
    else:
        return {'message': 'Token exchange failed.'}
