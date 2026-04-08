from src.core.exceptions import (
    ShortUrlGenerationException,
    LongUrlNotFoundException,
)
from src.models import ShortUrl
from src.utils import (
    generate_random_slug,
    AbstractAsyncRepository,
    AbstractAsyncUOW,
    retry_instancemethod,
    Specification,
)

# TODO db as Repository, чтобы сервис не имел представления о конкретной
#  реализации сессий, а этим занимался паттерн репозиторий

# TODO Сделать домены, не зависящие от реализации, чтобы можно было подкидывать их как аннотации

# TODO URLService Abstraction


def find_by_slug(slug: str) -> Specification[ShortUrl]:
    return Specification[ShortUrl](
        ShortUrl.short_url == slug, ShortUrl.is_active == True
    )


class UrlService:

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

    @retry_instancemethod
    async def create_short_url(self, url: str) -> ShortUrl:
        """
        1. Gets URL
        2. Generates slug for URL
        3. Adds URL and slug to database
        4. Commits the transaction
        5. Returns the short URL
        """
        slug = generate_random_slug()
        short_url = ShortUrl(
            short_url=slug,
            long_url=url,
        )

        async with self._uow:
            try:
                return await self._repo.add(short_url)
            except Exception as e:
                raise ShortUrlGenerationException(e)

    async def get_original_url(self, slug: str) -> ShortUrl:
        """
        1. Finds original URL by slug
        2. Increments usage count
        3. Commits changes
        4. Returns the original URL
        """
        async with self._uow:
            result = await self._repo.find(find_by_slug(slug))

            if result is None:
                raise LongUrlNotFoundException()

            result[0].usage_count += 1
            return await self._repo.update(result[0])
