from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from src.core.config import DATABASE_URL
from src.core.password_hasher import PasslibPasswordHasher
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


class ServicesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_current_user(self) -> User | None:
        # TODO Replace with real auth-based user resolution later.
        return None

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

    @provide(scope=Scope.APP)
    def provide_password_hasher(self) -> PasswordHasherProtocol:
        return PasslibPasswordHasher()

    @provide(scope=Scope.APP)
    def provide_token_service(self) -> TokenServiceProtocol:
        return JWTTokenService()

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
