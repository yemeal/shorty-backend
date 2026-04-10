from typing import AsyncGenerator
from uuid import UUID

from dishka import Provider, Scope, provide
from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from src.core.config import DATABASE_URL
from src.core.password_hasher import PasslibPasswordHasher
from src.core.http_exceptions import HTTPErrors
from src.models import ShortUrl, User
from src.services.auth_service import AuthService
from src.services.token_service import JWTTokenService
from src.services.url_service import UrlService
from src.services.user_service import UserService
from src.utils.protocols import UrlServiceProtocol
from src.utils import (
    AsyncUOW,
    AbstractAsyncUOW,
    PasswordHasherProtocol,
    TokenServiceProtocol,
    UserServiceProtocol,
    AuthServiceProtocol,
)
from src.utils import SQLAlchemyAsyncRepository, AbstractAsyncRepository
from src.core.exceptions import (
    TokenNoSubException, 
    UserWithIdNotFoundException, 
    TokenException,
    TokenExpiredException,
    InvalidTokenTypeException,
)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_engine(self) -> AsyncEngine:
        return create_async_engine(
            url=DATABASE_URL,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "command_timeout": 60,
            },
        )

    @provide(scope=Scope.APP)
    def provide_sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker() as session:
            yield session


class UserProvider(Provider):
    async def _get_curr_user(
        self,
        request: Request,
        token_service: TokenServiceProtocol,
        user_service: UserServiceProtocol,
    ) -> User:
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPErrors.Auth.NOT_AUTHENTICATED()

        try:
            payload = token_service.decode_token(
                access_token,
                token_type="access",
            )
            sub = payload.get("sub")
            user_id = UUID(str(sub))
        except TokenNoSubException:
            raise HTTPErrors.Auth.TOKEN_SUBJECT_MISSING()
        except InvalidTokenTypeException:
            raise HTTPErrors.Auth.INVALID_TOKEN_TYPE()
        except TokenExpiredException:
            raise HTTPErrors.Auth.TOKEN_EXPIRED()
        except TokenException:
            raise HTTPErrors.Auth.COULD_NOT_VALIDATE_CREDENTIALS()

        try:
            return await user_service.get_user_by_id(user_id)
        except UserWithIdNotFoundException:
            raise HTTPErrors.Auth.USER_NOT_FOUND()
        except Exception:
            raise HTTPErrors.Server.INTERNAL_ERROR()

    @provide(scope=Scope.REQUEST)
    async def provide_current_user_optional(
        self,
        request: Request,
        token_service: TokenServiceProtocol,
        user_service: UserServiceProtocol,
    ) -> User | None:
        try:
            return await self._get_curr_user(
                request,
                token_service,
                user_service,
            )
        except Exception:
            return None

    @provide(scope=Scope.REQUEST)
    async def provide_current_user_required(
        self,
        request: Request,
        token_service: TokenServiceProtocol,
        user_service: UserServiceProtocol,
    ) -> User:
        curr_user = await self._get_curr_user(
            request,
            token_service,
            user_service,
        ) 
        return curr_user

class ServicesProvider(Provider):

    @provide(scope=Scope.APP)
    def provide_password_hasher(self) -> PasswordHasherProtocol:
        return PasslibPasswordHasher()

    @provide(scope=Scope.APP)
    def provide_token_service(self) -> TokenServiceProtocol:
        return JWTTokenService()

    @provide(scope=Scope.REQUEST)
    def provide_uow(
        self,
        session: AsyncSession,
    ) -> AbstractAsyncUOW:
        return AsyncUOW[AsyncSession](session)

    @provide(scope=Scope.REQUEST)
    def provide_url_repo(
        self,
        session: AsyncSession,
    ) -> AbstractAsyncRepository[ShortUrl]:
        return SQLAlchemyAsyncRepository[ShortUrl](session, ShortUrl)  # type: ignore[arg-type]

    @provide(scope=Scope.REQUEST)
    def provide_url_service(
        self,
        uow: AbstractAsyncUOW,
        repo: AbstractAsyncRepository[ShortUrl],
    ) -> UrlServiceProtocol:
        return UrlService(uow=uow, repo=repo)

    @provide(scope=Scope.REQUEST)
    def provide_user_repo(
        self,
        session: AsyncSession,
    ) -> AbstractAsyncRepository[User]:
        return SQLAlchemyAsyncRepository[User](session, User)  # type: ignore[arg-type]

    @provide(scope=Scope.REQUEST)
    def provide_user_service(
        self,
        uow: AbstractAsyncUOW,
        repo: AbstractAsyncRepository[User],
    ) -> UserServiceProtocol:
        return UserService(uow=uow, repo=repo)

    @provide(scope=Scope.REQUEST)
    def provide_auth_service(
        self,
        uow: AbstractAsyncUOW,
        repo: AbstractAsyncRepository[User],
        user_service: UserServiceProtocol,
        token_service: TokenServiceProtocol,
        password_hasher: PasswordHasherProtocol,
    ) -> AuthServiceProtocol:
        return AuthService(
            uow=uow,
            repo=repo,
            user_service=user_service,
            token_service=token_service,
            password_hasher=password_hasher,
        )
