import fastapi as fa
import httpx
from core.config import settings
from core.enums import OAuthTypesEnum
from core.exceptions import BadRequestException

redirect_uri_google = f'http://{settings.API_AUTH_HOST}:{settings.API_AUTH_PORT}/api/v1/auth/oauth-redirect/google'
redirect_uri_yandex = f'http://{settings.API_AUTH_HOST}:{settings.API_AUTH_PORT}/api/v1/auth/oauth-redirect/yandex'


async def get_redirect_uri_with_state(oauth_type: OAuthTypesEnum, stored_state):
    if oauth_type == OAuthTypesEnum.google:
        return f'https://accounts.google.com/o/oauth2/v2/auth?response_type=code&' \
               f'client_id={settings.GOOGLE_CLIENT_ID}&' \
               f'redirect_uri={redirect_uri_google}&' \
               f'scope=openid+email+profile&' \
               f'state={stored_state}'
    elif oauth_type == OAuthTypesEnum.yandex:
        return f'https://oauth.yandex.com/authorize?response_type=code&' \
               f'client_id={settings.YANDEX_CLIENT_ID}&' \
               f'redirect_uri={redirect_uri_yandex}&' \
               f'state={stored_state}'


async def get_oauth_token(request, stored_state, oauth_type: OAuthTypesEnum):
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    if state != stored_state:
        return {'message': 'State mismatch. Authentication failed.'}

    if oauth_type == OAuthTypesEnum.google:
        token_uri = 'https://oauth2.googleapis.com/token'
        token_params = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri_google,
            'grant_type': 'authorization_code'
        }
    elif oauth_type == OAuthTypesEnum.yandex:
        token_uri = 'https://oauth.yandex.com/token'
        token_params = {
            'code': code,
            'client_id': settings.YANDEX_CLIENT_ID,
            'client_secret': settings.YANDEX_CLIENT_SECRET,
            'redirect_uri': redirect_uri_yandex,
            'grant_type': 'authorization_code'
        }
    else:
        raise ValueError('unsupported oauth_type')

    async with httpx.AsyncClient() as client:
        response = await client.post(token_uri, data=token_params)

    if response.status_code == fa.status.HTTP_200_OK:
        token_data = response.json()
        oauth_token = token_data.get('access_token')
        return oauth_token
    else:
        return {'message': 'Token exchange failed.'}


async def get_user_info_oauth(encoded_jwt: str, oauth_type: OAuthTypesEnum) -> dict | None:
    if oauth_type == OAuthTypesEnum.google:
        user_info_uri = 'https://www.googleapis.com/oauth2/v1/userinfo'
    elif oauth_type == OAuthTypesEnum.yandex:
        user_info_uri = 'https://login.yandex.ru/info'
    headers = {'Authorization': f'Bearer {encoded_jwt}'}

    async with httpx.AsyncClient() as client:
        response = await client.get(user_info_uri, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        return user_info

    else:
        return None


async def get_user_data(user_info: dict, oauth_type: OAuthTypesEnum) -> tuple[str, str, str]:
    user_social_uuid = user_info['uuid']

    if oauth_type == OAuthTypesEnum.google:
        user_name = user_info['name']
        user_email = user_info['email']
    elif oauth_type == OAuthTypesEnum.yandex:
        user_name = f'{user_info["first_name"]} {user_info["last_name"]}'
        user_email = user_info['default_email']
    else:
        raise BadRequestException('invalid oauth type')
    return user_email, user_name, user_social_uuid
