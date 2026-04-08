from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from src.core.config import DATABASE_URL
from src.models import ShortUrl
from src.services.url_service import UrlService
from src.utils import AsyncUOW, AbstractAsyncUOW
from src.utils import SQLAlchemyAsyncRepository, AbstractAsyncRepository

# TODO Абстракция провайдера


class SQLAlchemyDatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_engine(self) -> AsyncEngine:
        return create_async_engine(
            url=DATABASE_URL,
            pool_size=20,
            max_overflow=30,
        )

    @provide(scope=Scope.APP)
    def provide_sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def provide_uow(self, session: AsyncSession) -> AbstractAsyncUOW:
        return AsyncUOW[AsyncSession](session)

    @provide(scope=Scope.REQUEST)
    def provide_url_repo(
        self, session: AsyncSession
    ) -> AbstractAsyncRepository:
        return SQLAlchemyAsyncRepository[ShortUrl](session, ShortUrl)  # type: ignore[arg-type]

    @provide(scope=Scope.REQUEST)
    def provide_url_service(
        self,
        uow: AbstractAsyncUOW,
        repo: AbstractAsyncRepository[ShortUrl],
    ) -> UrlService:
        return UrlService(uow=uow, repo=repo)
