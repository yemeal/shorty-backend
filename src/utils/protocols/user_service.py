from typing import Protocol, Sequence
from uuid import UUID

from src.models import User, ShortUrl
from src.schemas.pagination_meta import PaginationMeta, PaginationParams


class UserServiceProtocol(Protocol):
    async def get_user_by_id(self, user_id: UUID) -> User: ...

    async def get_user_by_email(self, email: str) -> User: ...

    async def check_email_exists(self, email: str) -> bool: ...

    async def check_username_exists(self, username: str) -> bool: ...

    async def add_new_user(self, new_user: User) -> User: ...

    async def get_paginated_short_urls_by_user_id(
        self,
        user_id: UUID,
        *,
        pagination_params: PaginationParams,
    ) -> tuple[Sequence[ShortUrl], PaginationMeta]: ...
