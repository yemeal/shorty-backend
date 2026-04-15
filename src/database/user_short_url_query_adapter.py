"""
SQLAlchemy version of ``UserShortUrlQueryPort``.

Rules:
- Only rows for this owner, only active links.
- Optional search: case-insensitive substring on slug or long URL (ILIKE).
  The same filters drive both COUNT(*) and the page query.
- Sort uses a fixed column list plus asc or desc, then ``id`` in the same
  direction so ties on date or usage do not jump around.

Not here: listing other users (different port). Heavier search can replace
ILIKE inside this class later.

To add a new sort field:
1. Put it in ``ShortUrlSortBy`` in ``src.core.sort_options``.
2. Map it in ``_SORT_COLUMNS``. The API must only send enum values, not raw
   strings from the client.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from src.core.sort_options import ShortUrlSortBy, SortOrder
from src.models import ShortUrl
from src.utils.protocols.user_short_url_query import UserShortUrlQueryPort

# Whitelist: API sort_by -> ORM column; keeps sorting data-driven.
_SORT_COLUMNS: dict[ShortUrlSortBy, ColumnElement] = {
    "created_at": ShortUrl.created_at,
    "usage_count": ShortUrl.usage_count,
}


class SqlAlchemyUserShortUrlQuery(UserShortUrlQueryPort):
    """Runs the list and count queries on the request-scoped AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base_filters(
        self,
        owner_id: UUID,
        search_query: str | None,
    ) -> list[ColumnElement]:
        filters = [
            ShortUrl.user_id == owner_id,
            ShortUrl.is_active == True,
        ]
        q = (search_query or "").strip()
        if q:
            pattern = f"%{q}%"
            filters.append(
                or_(
                    ShortUrl.slug.ilike(pattern),
                    ShortUrl.long_url.ilike(pattern),
                )
            )
        return filters

    def _order_clauses(
        self,
        sort_by: ShortUrlSortBy,
        sort_order: SortOrder,
    ) -> tuple[ColumnElement, ColumnElement]:
        column = _SORT_COLUMNS[sort_by]
        id_column = ShortUrl.id
        if sort_order == "desc":
            return (desc(column), desc(id_column))
        return (asc(column), asc(id_column))

    async def list_for_owner(
        self,
        owner_id: UUID,
        *,
        page: int,
        page_size: int,
        sort_by: ShortUrlSortBy,
        sort_order: SortOrder,
        search_query: str | None,
    ) -> tuple[list[ShortUrl], int]:
        filters = self._base_filters(owner_id, search_query)
        order = self._order_clauses(sort_by, sort_order)
        offset = (page - 1) * page_size

        count_stmt = select(func.count()).select_from(ShortUrl).where(*filters)
        total = int((await self._session.execute(count_stmt)).scalar_one())

        list_stmt = (
            select(ShortUrl)
            .where(*filters)
            .order_by(*order)
            .limit(page_size)
            .offset(offset)
        )
        rows = list((await self._session.execute(list_stmt)).scalars().all())
        return rows, total
