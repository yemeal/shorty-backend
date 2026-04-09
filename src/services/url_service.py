from abc import ABC, abstractmethod

from src.core.exceptions import (
    ShortUrlGenerationException,
    LongUrlNotFoundException,
    SlugAlreadyExistsException,
)
from src.models import ShortUrl
from src.utils import (
    generate_random_slug,
    AbstractAsyncRepository,
    AbstractAsyncUOW,
    retry_instancemethod,
    Specification,
)

# TODO Сделать домены, не зависящие от реализации, чтобы можно было подкидывать их как аннотации


def find_by_slug(slug: str) -> Specification[ShortUrl]:
    return Specification[ShortUrl](
        ShortUrl.slug == slug, ShortUrl.is_active == True
    )


class AbstractUrlService(ABC):
    @abstractmethod
    async def create_random_short_url(self, url: str) -> ShortUrl: ...

    @abstractmethod
    async def create_custom_short_url(
        self, url: str, slug: str
    ) -> ShortUrl: ...

    @abstractmethod
    async def get_original_url(self, slug: str) -> ShortUrl: ...


class UrlService(AbstractUrlService):
    def __init__(
        self,
        uow: AbstractAsyncUOW,
        repo: AbstractAsyncRepository[ShortUrl],
        max_retries: int = 5,
    ) -> None:
        self._uow = uow
        self._repo = repo
        self.max_retries = max_retries

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int) -> None:
        if value < 1:
            raise ValueError("Max retries must be at least 1")

        self._max_retries = value

    async def _save_to_db(self, url: str, slug: str) -> ShortUrl:
        short_url = ShortUrl(
            slug=slug,
            long_url=url,
        )
        try:
            async with self._uow:
                return await self._repo.add(short_url)
        except Exception as e:
            raise ShortUrlGenerationException(e)

    @retry_instancemethod
    async def create_random_short_url(self, url: str) -> ShortUrl:
        """
        1. Gets URL
        2. Generates slug for URL
        3. Adds URL and slug to database
        4. Returns the short URL
        """
        slug = generate_random_slug()
        return await self._save_to_db(url, slug)

    async def create_custom_short_url(
        self, url: str, slug: str
    ) -> ShortUrl:
        """
        1. Gets URL and user_slug
        2. Adds URL and slug to database
        3. Returns the short URL
        """
        try:
            return await self._save_to_db(url, slug)
        except ShortUrlGenerationException:
            raise SlugAlreadyExistsException(
                f"Slug '{slug}' is already in use."
            )

    async def get_original_url(self, slug: str) -> ShortUrl:
        """
        1. Finds original URL by slug
        2. Increments usage count
        3. Commits changes
        4. Returns the original URL
        """
        async with self._uow:
            result = await self._repo.find(find_by_slug(slug))

            if not result:
                raise LongUrlNotFoundException()

            # [0] -> .first()
            result[0].usage_count += 1
            return await self._repo.update(result[0])
