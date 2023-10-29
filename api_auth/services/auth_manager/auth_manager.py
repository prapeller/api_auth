import datetime as dt
from pathlib import Path

import fastapi as fa
import httpx

from core import config
from core.config import settings
from core.enums import TokenTypesEnum, RolesNamesEnum, OAuthTypesEnum
from core.exceptions import InvalidCredentialsException, UnauthorizedException, UserWasNotRegisteredException
from core.logger_config import setup_logger
from db.models.role import RoleModel
from db.models.session import SessionModel
from db.models.user import UserModel
from db.repository import SqlAlchemyRepositoryAsync
from db.serializers.session import (
    SessionReadUserSerializer,
    SessionCreateSerializer,
    SessionFromRequestSchema,
    SessionUpdateSerializer
)
from db.serializers.token import TokenPairEncodedSerializer, TokenReadSchema
from db.serializers.user import UserLoginSchema, UserCreateSerializer
from services.cache.cache import RedisCache
from services.hasher import password_is_verified
from services.jwt_manager.jwt_manager import create_token_pair, create_temporary_register_token
from services.oauth import get_user_info_oauth

SERVICE_DIR = Path(__file__).resolve().parent
SERVICE_NAME = SERVICE_DIR.stem

logger = setup_logger(SERVICE_NAME, SERVICE_DIR)


class AuthManager():
    """
    - login, logout, refresh,
    - verify access_token user by data from request,
    """

    def __init__(self, repo: SqlAlchemyRepositoryAsync, cache: RedisCache):
        self.repo = repo
        self.cache = cache

    async def _create_session(
            self,
            user: UserModel,
            session_schema: SessionFromRequestSchema,
            oauth_type=OAuthTypesEnum.local,
            oauth_token=''
    ) -> TokenPairEncodedSerializer:
        """
        create session in db
        create token pair based on user and session data
        set refresh token to cache
        return token pair
        """
        session_create_ser = SessionCreateSerializer(user_uuid=user.uuid,
                                                     useragent=session_schema.useragent,
                                                     ip=session_schema.ip,
                                                     )
        session_db: SessionModel = await self.repo.create(SessionModel, session_create_ser)
        session_ser = SessionReadUserSerializer.from_orm(session_db)

        token_pair = await create_token_pair(
            user_uuid=session_ser.user.uuid,
            email=session_ser.user.email,
            permissions=session_ser.user.permissions_names,
            session_uuid=session_ser.uuid,
            ip=session_ser.ip,
            useragent=session_ser.useragent,
            oauth_type=oauth_type,
            oauth_token=oauth_token
        )

        # cache session refresh token
        await self.cache.set(session_ser.uuid,
                             token_pair.refresh_token,
                             ex=dt.timedelta(minutes=config.REFRESH_TOKEN_EXP_MIN))

        return token_pair

    async def _deactivate_session_from_request(self, session_schema: SessionFromRequestSchema):
        """
        get session_db from db
        if session_db:
            -deactivate session_db

            get session_cached from cache with session_db.uuid
            if session_cached:
                -deactivate session_cached
        """
        session_db = await self.repo.get(SessionModel, ip=session_schema.ip, useragent=session_schema.useragent,
                                         is_active=True)
        if session_db:
            session_db = await self.repo.update(session_db, {'is_active': False})
            # logger.info(f'_deactivate_session_from_request: updated {session_db=:}')

            session_cached = await self.cache.get(session_db.uuid)
            if session_cached:
                await self.cache.delete(session_db.uuid)
                logger.info('_deactivate_session_from_request: deleted from cache')

    async def get_verified_token_schema(
            self,
            token: str,
            session_from_request: SessionFromRequestSchema) -> TokenReadSchema | None:
        """
        return provided token schema or
        return None
            -if local service cant decode token
            -if oauth-provider service cant validate token nested inside schema
            -if token session data doesn't match to session_from_request data
            -if there is no refresh_token cached
            -if token_provided is refresh_token - and token_provided != refresh_token cached
        """
        token_schema = TokenReadSchema.from_jwt(token)
        if token_schema is None:
            return None

        if token_schema.oauth_type != OAuthTypesEnum.local:
            token = token_schema.oauth_token
            token_info = await get_user_info_oauth(token_schema.oauth_token, oauth_type=token_schema.oauth_type)
            if token_info is None:
                return None

        if session_from_request.ip != token_schema.ip or \
                session_from_request.useragent != token_schema.useragent:
            logger.error(f'verify_token: {session_from_request=:} doesnt match {token_schema=:}')
            return None

        refresh_token_cached = await self.cache.get(token_schema.session_uuid)
        if refresh_token_cached is None:
            logger.error(f'verify_token: theres no refresh_token by {token_schema.session_uuid=:}')
            return None

        if token_schema.type == TokenTypesEnum.refresh:
            if refresh_token_cached.decode('utf-8') != token:
                return None

        return token_schema

    async def login(self,
                    user_login_schema: UserLoginSchema,
                    session_schema: SessionFromRequestSchema,
                    oauth_type: OAuthTypesEnum = OAuthTypesEnum.local,
                    oauth_token='',
                    ) -> TokenPairEncodedSerializer:
        """
        authenticate user with user_login_serializer data
        deactivate user active session with session_ser data if such already exists
        create new user active session with session_ser data
        """
        user = await self.repo.get(UserModel, email=user_login_schema.email)
        if user is None:
            raise UnauthorizedException

        if oauth_type == OAuthTypesEnum.local:
            if not password_is_verified(user_login_schema.password, user.password):
                logger.info(f"login: can't authenticate {user_login_schema.email=:}")
                raise InvalidCredentialsException

        await self._deactivate_session_from_request(session_schema)

        token_pair = await self._create_session(user=user,
                                                session_schema=session_schema,
                                                oauth_type=oauth_type,
                                                oauth_token=oauth_token,
                                                )
        logger.info(f'login: created {token_pair=:}')

        return token_pair

    async def logout(self, access_token_schema: TokenReadSchema):
        """
        from token get session_uuid
        if session exists in db - deactivate it
        delete session from cache
        """
        session_uuid = access_token_schema.session_uuid
        session_db = await self.repo.get(SessionModel, uuid=session_uuid, is_active=True)
        if session_db:
            await self.repo.update(session_db, SessionUpdateSerializer(is_active=False))
            logger.info(f'logout: updated {session_db=:}')

        await self.cache.delete(session_uuid)
        logger.info(f'logout: deleted from cache by {session_uuid=:}')

    async def logout_all(self, access_token_schema: TokenReadSchema):
        """
        from token get user and all its active sessions
        for every session:
            deactivate in db
            delete session from cache
        """
        user: UserModel = await self.repo.get(UserModel, uuid=access_token_schema.sub)
        for session in user.active_sessions:
            await self.repo.update(session, {'is_active': False})
            await self.cache.delete(session.uuid)
        logger.info(f'logout_all: for {user=:} deactivated all sessions db, deleted all sessions cached')

    async def refresh(self, refresh_token: str) -> TokenPairEncodedSerializer:
        """
        - create new token pair from old refresh_token data
        - update refresh token in cache
        """
        refresh_token_schema = TokenReadSchema.from_jwt(refresh_token)
        token_pair = await create_token_pair(user_uuid=refresh_token_schema.sub,
                                             email=refresh_token_schema.email,
                                             permissions=refresh_token_schema.permissions,
                                             session_uuid=refresh_token_schema.session_uuid,
                                             ip=refresh_token_schema.ip,
                                             useragent=refresh_token_schema.useragent,
                                             oauth_type=refresh_token_schema.oauth_type,
                                             oauth_token=refresh_token_schema.oauth_token,
                                             )
        await self.cache.set(refresh_token_schema.session_uuid,
                             token_pair.refresh_token,
                             ex=dt.timedelta(minutes=config.REFRESH_TOKEN_EXP_MIN))
        return token_pair

    @staticmethod
    async def send_service_request_post(url, url_postfix, headers, body, user):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=body)
                if response.status_code == fa.status.HTTP_200_OK:
                    logger.debug(f'request sent {url_postfix} for {user}')
                else:
                    logger.error(f"request failed {url_postfix} for {user}: {response.status_code}, {response.text}")
                return response
            except (httpx.RequestError, httpx.HTTPError) as e:
                logger.error(f"request failed {url_postfix} for {user}: {e}")
                raise

    async def create_and_send_notify_temporary_register_token(self, user: UserModel):
        temporary_token = await create_temporary_register_token(user)
        headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
                   'Service-Name': settings.PROJECT_NAME}
        user_confirmation_link = (
            f"http://localhost:{settings.API_AUTH_PORT}/api/v1/auth/confirm-email/{temporary_token}"
            if config.DEBUG else f"https://cinema.online/confirm-email/{temporary_token}"
        )
        body = {
            'email_to': user.email,
            'msg_text': f"Hello, {user.name}, welcome and thank you for registration at 'cinema.online'."
                        f"Here is your link to confirm your email: {user_confirmation_link}"
        }
        url_postfix = 'api/v1/services-notifications/send-email'
        url = f"{config.API_NOTIFICATIONS_HTTP_PREFIX}/{url_postfix}"
        return await self.send_service_request_post(url, url_postfix, headers, body, user)

    async def send_duplicate_user_request_to_notifications_service(self, user: UserModel):
        headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
                   'Service-Name': settings.PROJECT_NAME}
        body = {'user_uuid': user.uuid,
                'user_email': user.email}
        url_postfix = 'api/v1/services-users/duplicate-user'
        url = f"{config.API_NOTIFICATIONS_HTTP_PREFIX}/{url_postfix}"
        return await self.send_service_request_post(url, url_postfix, headers, body, user)

    async def register(self, user_ser: UserCreateSerializer):
        try:
            # async with self.repo.session.begin():
            user: UserModel = await self.repo.create_user(user_ser)
            registered_role = await self.repo.get(RoleModel, name=RolesNamesEnum.registered)
            user.roles.append(registered_role)
            await self.repo.session.commit()
            await self.repo.session.refresh(user)
            resp = await self.send_duplicate_user_request_to_notifications_service(user)
            if resp.status_code != fa.status.HTTP_200_OK:
                raise UserWasNotRegisteredException
            resp = await self.create_and_send_notify_temporary_register_token(user)
            if resp.status_code != fa.status.HTTP_200_OK:
                raise UserWasNotRegisteredException
            logger.debug(f'creation and registration completed: {user=:}')
            return user
        except Exception as e:
            await self.repo.session.rollback()
            logger.debug(f'creation and registration failed: {user_ser=:}, {e}')
            raise

    async def confirm_email(self, register_token):
        token_schema = TokenReadSchema.from_jwt(register_token)
        user = await self.repo.get(UserModel, email=token_schema.email)
        if dt.datetime.utcnow() <= token_schema.exp:
            user = await self.repo.update(user, {'is_active': True})
            return user
        await self.send_duplicate_user_request_to_notifications_service(user)
        await self.create_and_send_notify_temporary_register_token(user)
        raise UnauthorizedException("can't confirm this email, token expired, new token was sent to your email")
