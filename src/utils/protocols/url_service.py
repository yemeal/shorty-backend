from typing import Protocol

from src.models import User, ShortUrl

class UrlServiceProtocol(Protocol):
    async def create_random_short_url(
        self,
        url: str,
        user: User | None = None,
    ) -> ShortUrl: ...

    async def create_custom_short_url(
        self,
        url: str,
        slug: str,
        user: User | None = None,
    ) -> ShortUrl: ...

    async def get_original_url(
        self,
        slug: str,
    ) -> ShortUrl: ...
