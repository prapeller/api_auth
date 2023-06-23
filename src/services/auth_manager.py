import datetime as dt
import logging

from core.config import settings
from core.enums import TokenTypesEnum
from core.exceptions import InvalidCredentialsException, UnauthorizedException
from db.models.session import SessionModel
from db.models.user import UserModel
from db.repository import SqlAlchemyRepository
from db.serializers.session import (
    SessionReadUserSerializer,
    SessionCreateSerializer,
    SessionFromRequestSchema
)
from db.serializers.token import TokenPairEncodedSerializer, TokenReadSchema
from db.serializers.user import UserLoginSchema
from services.cache import RedisCache
from services.hasher import password_is_verified
from services.jwt_manager import create_token_pair

logger = logging.getLogger(__name__)


class AuthManager():
    """
    - login, logout, refresh,
    - verify access_token user by data from request,
    """

    def __init__(self, repo: SqlAlchemyRepository, cache: RedisCache):
        self.repo = repo
        self.cache = cache

    async def _create_session(self,
                              user: UserModel,
                              session_schema: SessionFromRequestSchema) -> TokenPairEncodedSerializer:
        """
        create session in db
        create token pair based on user and session data
        set refresh token to cache
        return token pair
        """
        session_create_ser = SessionCreateSerializer(user_id=user.id,
                                                     useragent=session_schema.useragent,
                                                     ip=session_schema.ip,
                                                     )
        session_db: SessionModel = self.repo.create(SessionModel, session_create_ser)
        session_ser = SessionReadUserSerializer.from_orm(session_db)

        token_pair = create_token_pair(session_ser.user.id,
                                       session_ser.user.email,
                                       session_ser.user.permissions_names,
                                       session_ser.id,
                                       session_ser.ip,
                                       session_ser.useragent)

        # cache session refresh token
        await self.cache.set(session_ser.id,
                             token_pair.refresh_token,
                             ex=dt.timedelta(minutes=settings.REFRESH_TOKEN_EXP_MIN))

        return token_pair

    async def _deactivate_session_from_request(self, session_schema: SessionFromRequestSchema):
        """
        get session_db from db
        if session_db:
            -deactivate session_db

            get session_cached from cache with session_db.id
            if session_cached:
                -deactivate session_cached
        """
        session_db = self.repo.get(SessionModel, ip=session_schema.ip, useragent=session_schema.useragent,
                                   is_active=True)
        if session_db:
            session_db = self.repo.update(session_db, {'is_active': False})
            logger.info(f'auth_manager._deactivate_session_from_request: udpated {session_db=:}')

            session_cached = await self.cache.get(session_db.id)
            if session_cached:
                await self.cache.delete(session_db.id)
                logger.info('auth_manager._deactivate_session_from_request: deleted from cache')

    async def verify_token(self,
                           token: str,
                           session_from_request: SessionFromRequestSchema) -> None:
        """
        raise unauthorized exception
            -if token session data doesn't match to session_from_request data
            -if there is no refresh_token cached
            -if token_provided is refresh_token - and token_provided != refresh_token cached
        """
        token_schema = TokenReadSchema.from_jwt(token)
        if session_from_request.ip != token_schema.ip or \
                session_from_request.useragent != token_schema.useragent:
            logger.error(f'auth_manager.verify_token: {session_from_request=:} doesnt match {token_schema=:}')
            raise UnauthorizedException

        refresh_token_cached = await self.cache.get(token_schema.session_id)
        if refresh_token_cached is None:
            logger.error(f'auth_manager.verify_token: theres no refresh_token by {token_schema.session_id=:}')
            raise UnauthorizedException

        if token_schema.type == TokenTypesEnum.refresh:
            if refresh_token_cached.decode('utf-8') != token:
                raise UnauthorizedException

    async def login(self,
                    user_login_schema: UserLoginSchema,
                    session_schema: SessionFromRequestSchema,
                    ) -> TokenPairEncodedSerializer:
        """
        authenticate user with user_login_serializer data
        deactivate user active session with session_ser data if such already exists
        create new user active session with session_ser data
        """
        user = self.repo.get(UserModel, email=user_login_schema.email)
        if user is None or not password_is_verified(user_login_schema.password, user.password):
            logger.info(f"auth_manager.login: can't authenticate {user_login_schema.email=:}")
            raise InvalidCredentialsException

        await self._deactivate_session_from_request(session_schema)
        logger.info(f'auth_manager.login: deactivated {session_schema=:}')

        token_pair = await self._create_session(user, session_schema)
        logger.info(f'auth_manager.login: created {token_pair=:}')

        return token_pair

    async def logout(self, access_token: str):
        """
        from token get session_id
        if session exists in db - deactivate it
        delete session from cache
        """
        access_token_schema = TokenReadSchema.from_jwt(access_token)
        session_id = access_token_schema.session_id
        session_db = self.repo.get(SessionModel, id=session_id, is_active=True)
        if session_db:
            self.repo.update(session_db, {'is_active': False})
            logger.info(f'auth_manager.logout: updated {session_db=:}')

        await self.cache.delete(session_id)
        logger.info(f'auth_manager.logout: deleted from cache by {session_id=:}')

    async def logout_all(self, access_token: str):
        """
        from token get user and all its active sessions
        for every session:
            deactivate in db
            delete session from cache
        """
        access_token_schema = TokenReadSchema.from_jwt(access_token)
        user: UserModel = self.repo.get(UserModel, id=access_token_schema.sub)
        for session in user.active_sessions:
            self.repo.update(session, {'is_active': False})
            await self.cache.delete(session.id)
        logger.info(f'auth_manager.logout_all: for {user=:} deleted all sessions')

    async def refresh(self, refresh_token: str) -> TokenPairEncodedSerializer:
        """
        - create new token pair from old refresh_token data
        - update refresh token in cache
        """
        refresh_token_schema = TokenReadSchema.from_jwt(refresh_token)
        token_pair = create_token_pair(user_id=refresh_token_schema.sub,
                                       email=refresh_token_schema.email,
                                       permissions=refresh_token_schema.permissions,
                                       session_id=refresh_token_schema.session_id,
                                       ip=refresh_token_schema.ip,
                                       useragent=refresh_token_schema.useragent,
                                       )
        await self.cache.set(refresh_token_schema.session_id,
                             token_pair.refresh_token,
                             ex=dt.timedelta(minutes=settings.REFRESH_TOKEN_EXP_MIN))
        return token_pair
