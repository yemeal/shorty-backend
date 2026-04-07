from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from src.core.config import DATABASE_URL

async_engine: AsyncEngine = create_async_engine(
    url=DATABASE_URL,
    pool_size=20,
    max_overflow=30,
)

new_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
