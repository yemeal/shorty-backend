import math
from uuid import UUID
from typing import Sequence

from src.core.exceptions import DomainErrors
from src.utils import AbstractAsyncRepository, AbstractAsyncUOW
from src.utils import Specification
from src.utils.protocols.user_short_url_query import UserShortUrlQueryPort
from src.models import User, ShortUrl
from src.schemas.pagination_meta import PaginationMeta, PaginationParams


def find_user_by_email(email: str) -> Specification:
    return Specification(
        User.email == email,
        User.is_active == True,
    )


def find_user_by_username(username: str) -> Specification:
    return Specification(
        User.username == username,
        User.is_active == True,
    )


def find_user_by_id(_id: UUID) -> Specification:
    return Specification(
        User.id == _id,
        User.is_active == True,
    )


def find_short_url_by_id_and_user_id(short_url_id: UUID, user_id: UUID) -> Specification:
    return Specification(
        ShortUrl.id == short_url_id,
        ShortUrl.user_id == user_id,
        ShortUrl.is_active == True,
    )


class UserService:
    """Application service for users; short-URL lists go through ``UserShortUrlQueryPort``."""

    def __init__(
        self,
        uow: AbstractAsyncUOW,
        repo: AbstractAsyncRepository[User],
        short_url_repo: AbstractAsyncRepository[ShortUrl],
        user_short_url_query: UserShortUrlQueryPort,
    ) -> None:
        self._uow = uow
        self._repo = repo
        self._short_url_repo = short_url_repo
        self._user_short_url_query = user_short_url_query

    async def get_user_by_email(self, email: str) -> User:
        async with self._uow:
            user = await self._repo.find_one(find_user_by_email(email))
            if not user:
                raise DomainErrors.User.NOT_FOUND_BY_EMAIL(email=email)
            return user

    async def get_user_by_id(self, user_id: UUID) -> User:
        async with self._uow:
            user = await self._repo.find_one(find_user_by_id(user_id))
            if not user:
                raise DomainErrors.User.NOT_FOUND_BY_ID(user_id=user_id)
            return user

    async def get_user_by_username(self, username: str) -> User:
        async with self._uow:
            user = await self._repo.find_one(
                find_user_by_username(username)
            )
            if not user:
                raise DomainErrors.User.NOT_FOUND_BY_USERNAME(username=username)
            return user

    async def check_email_exists(self, email: str) -> bool:
        try:
            await self.get_user_by_email(email)
        except DomainErrors.User.NotFoundByEmailError:
            return False
        return True

    async def check_username_exists(self, username: str) -> bool:
        try:
            await self.get_user_by_username(username)
        except DomainErrors.User.NotFoundByUsernameError:
            return False
        return True

    async def add_new_user(self, new_user: User) -> User:
        try:
            async with self._uow:
                user = await self._repo.add(new_user)
        except DomainErrors.Persistence.IntegrityViolationError:
            if await self.check_email_exists(new_user.email):
                raise DomainErrors.User.EMAIL_ALREADY_EXISTS(email=new_user.email)

            if await self.check_username_exists(new_user.username):
                raise DomainErrors.User.USERNAME_ALREADY_EXISTS(username=new_user.username)

            raise

        return user

    async def delete_short_url_by_id(self, short_url_id: UUID, user_id: UUID) -> ShortUrl:
        async with self._uow:
            deleted_rows = await self._short_url_repo.delete(
                specification=find_short_url_by_id_and_user_id(short_url_id, user_id)
            )
            if not deleted_rows:
                raise DomainErrors.ShortUrl.NOT_FOUND_FOR_OWNER(
                    short_url_id=short_url_id,
                    user_id=user_id,
                )
            return deleted_rows[0]

    async def get_paginated_short_urls_by_user_id(
        self,
        user_id: UUID,
        *,
        pagination_params: PaginationParams,
    ) -> tuple[Sequence[ShortUrl], PaginationMeta]:
        """Return one page of the user's short URLs and pagination metadata.

        Delegates filtering, sorting, and counting to :class:`UserShortUrlQueryPort`;
        ``pagination_params`` is the single API/application input for page, size,
        sort, and search.
        """
        page = pagination_params.page
        page_size = pagination_params.page_size
        async with self._uow:
            items, total = await self._user_short_url_query.list_for_owner(
                user_id,
                page=page,
                page_size=page_size,
                sort_by=pagination_params.sort_by,
                sort_order=pagination_params.sort_order,
                search_query=pagination_params.q,
            )
            total_pages = math.ceil(total / page_size) if total else 0
            meta = PaginationMeta(
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                total_items=total,
                sort_by=pagination_params.sort_by,
                sort_order=pagination_params.sort_order,
                has_next_page=page * page_size < total,
                has_previous_page=page > 1,
                q=pagination_params.q,
            )
            return items, meta
