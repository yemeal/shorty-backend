from sqlalchemy import select

from src.core.exceptions import (
    ShortUrlGenerationException,
    LongUrlNotFoundException,
)
from src.models import ShortUrl
from src.utils import generate_random_slug

# TODO db as Repository, чтобы сервис не имел представления о конкретной
#  реализации сессий, а этим занимался паттерн репозиторий
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


class UrlService:
    @staticmethod
    async def create_short_url(
        url: str,
        db: AsyncSession,
        retries: int = 5,
    ) -> ShortUrl:
        # Принимает юрл
        # Генерит для него слаг
        # Асинхронно обращается к db чтобы он связал юрл и слаг
        # Репозиторий вызывает исключение, если такой слаг уже существует,
        #   мы ретраим 5 раз и если 5 раз подряд у нас вылетает ошибка, то пробрасываем ошибку о том,
        #   что мы совсем тупые, и чтобы конечный пользователь либо повторил, либо выбросил 500 ошибку сервера
        # Если все успешно и слаг добавлен в бд, то возвращаем его.
        for _ in range(retries):
            try:
                short_url = ShortUrl(
                    short_url=generate_random_slug(),
                    long_url=url,
                )
                db.add(short_url)
                await db.commit()
                break
            except IntegrityError:
                await db.rollback()
        else:
            raise ShortUrlGenerationException

        return short_url

    @staticmethod
    async def get_long_url_by_short_url(
        short_url: str,
        db: AsyncSession,
    ) -> ShortUrl:
        query = select(ShortUrl).where(ShortUrl.short_url == short_url)
        result: ShortUrl | None = await db.scalar(query)
        if result is None:
            raise LongUrlNotFoundException()
        result.usage_count += 1
        await db.commit()
        return result
