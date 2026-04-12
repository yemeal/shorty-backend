"""
SQLAlchemy implementation of UserShortUrlQueryPort.


- Restrict every row to ShortUrl.user_id == owner_id and active records.
- Optional case-insensitive substring match on slug or long_url (ILIKE), 
same filters for COUNT(*) and the page query.
- Sort by a whitelisted column + asc/desc, then by id in the same direction 
so ordering is stable when created_at or usage_count ties.

- Cross-user or admin listing (different port / query).
- Full-text or trigram search (can be swapped inside this adapter later).

1. Add the value to ShortUrlSortBy in src.core.sort_options.
2. Map it in _SORT_COLUMNS below. Do not accept arbitrary strings from the
   client; only the Literal / OpenAPI enum values reach this layer.
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
    """Executes owner-scoped list + count using the request AsyncSession."""

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
