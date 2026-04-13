from src.core.exceptions import DomainErrors
from src.models import ShortUrl, User
from src.utils import (
    generate_random_slug,
    AbstractAsyncRepository,
    AbstractAsyncUOW,
    retry_instancemethod,
    Specification,
)

# TODO Сделать домены, не зависящие от реализации, чтобы можно было подкидывать их как аннотации


def find_by_slug(slug: str) -> Specification:
    return Specification(
        ShortUrl.slug == slug, ShortUrl.is_active == True
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

    async def _save_to_db(
        self, url: str, slug: str, user: User | None
    ) -> ShortUrl:
        short_url = ShortUrl(
            slug=slug,
            long_url=url,
            user_id=user.id if user else None,
        )
        try:
            async with self._uow:
                return await self._repo.add(short_url)
        except DomainErrors.Persistence.IntegrityViolationError:
            raise
        except Exception as e:
            raise DomainErrors.ShortUrl.GENERATION_FAILED(
                slug=slug,
                cause=e,
            ) from e

    @retry_instancemethod
    async def create_random_short_url(
        self,
        url: str,
        user: User | None = None,
    ) -> ShortUrl:
        """
        1. Gets URL
        2. Generates slug for URL
        3. Adds URL and slug to database
        4. Returns the short URL
        """
        slug = generate_random_slug()
        return await self._save_to_db(url, slug, user)

    async def create_custom_short_url(
        self,
        url: str,
        slug: str,
        user: User | None = None,
    ) -> ShortUrl:
        """
        1. Gets URL and user_slug
        2. Adds URL and slug to database
        3. Returns the short URL
        """
        try:
            return await self._save_to_db(url, slug, user)
        except DomainErrors.Persistence.IntegrityViolationError:
            raise DomainErrors.ShortUrl.SLUG_TAKEN(
                slug=slug,
                message=f"Slug '{slug}' is already in use.",
            ) from None

    async def get_original_url(self, slug: str) -> ShortUrl:
        """
        1. Finds original URL by slug
        2. Increments usage count
        3. Commits changes
        4. Returns the original URL
        """
        async with self._uow:
            short_url = await self._repo.find_one(find_by_slug(slug))

            if not short_url:
                raise DomainErrors.ShortUrl.BY_SLUG_NOT_FOUND(slug=slug)

            short_url.usage_count += 1

            # TODO Short URL visit
            if short_url.user_id is not None:
                pass

            return await self._repo.update(short_url)
