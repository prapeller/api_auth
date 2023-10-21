import fastapi as fa
from fastapi.security import OAuth2PasswordBearer, OAuth2
from redis.asyncio import Redis

from core.exceptions import UnauthorizedException
from db import SessionLocalAsync
from db.models.user import UserModel
from db.repository import SqlAlchemyRepositoryAsync
from db.serializers.session import SessionFromRequestSchema
from db.serializers.token import TokenReadSchema
from services.auth_manager import AuthManager
from services.cache import RedisCache

redis: Redis | None = None


async def redis_dependency() -> Redis:
    return redis


async def sql_alchemy_repo_dependency(
) -> SqlAlchemyRepositoryAsync:
    async with SessionLocalAsync() as session:
        repo = SqlAlchemyRepositoryAsync(session)
        yield repo


async def redis_cache_dependency(
        redis: Redis = fa.Depends(redis_dependency),
) -> RedisCache:
    return RedisCache(redis)


async def auth_manager_dependency(
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sql_alchemy_repo_dependency),
        redis_cache: RedisCache = fa.Depends(redis_cache_dependency)
) -> AuthManager:
    return AuthManager(repo, redis_cache)


async def pagination_params_dependency(
        offset: int | None = None,
        limit: int | None = None,
):
    return {
        'offset': offset,
        'limit': limit,
    }


oauth2_scheme_local = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

oauth2_scheme_providers = OAuth2(
    flows={
        'login_with_google': {
            'authorizationUrl': '/api/v1/auth/login-oauth/google',
            'tokenUrl': 'https://oauth2.googleapis.com/token',
            'scopes': {
                'openid': 'OpenID scope for authentication',
                'email': 'Email scope for accessing user email',
                'profile': 'Profile scope for accessing user profile information',
            },
        },
        'login_with_yandex': {
            'authorizationUrl': '/api/v1/auth/login-oauth/yandex',
            'tokenUrl': 'https://oauth.yandex.com/token',
        },
    },
)


async def get_current_user_dependency(access_token: str = fa.Depends(oauth2_scheme_local),
                                      repo: SqlAlchemyRepositoryAsync = fa.Depends(sql_alchemy_repo_dependency)):
    access_token_schema = TokenReadSchema.from_jwt(access_token)
    if access_token_schema is None:
        raise UnauthorizedException
    current_user = await repo.get(UserModel, uuid=access_token_schema.sub)
    if current_user is None:
        raise UnauthorizedException
    return current_user


async def verified_token_schema_dependency(request: fa.Request,
                                           access_token: str = fa.Depends(oauth2_scheme_local),
                                           _: str = fa.Depends(oauth2_scheme_providers),
                                           auth_manager: AuthManager = fa.Depends(auth_manager_dependency),
                                           ):
    session_from_request = SessionFromRequestSchema(
        useragent=request.headers.get("user-agent"),
        ip=request.headers.get('X-Forwarded-For'),
    )
    token_schema = await auth_manager.get_verified_token_schema(access_token, session_from_request)
    if token_schema is None:
        raise UnauthorizedException
    return token_schema
