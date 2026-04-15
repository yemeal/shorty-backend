"""
Port for listing one user's short URLs with page, search, and sort.

Small on purpose: one job, one method. Callers do not depend on SQLAlchemy.

Concrete class lives in the database layer (SQLAlchemy adapter).
"""

from typing import Protocol, Sequence
from uuid import UUID

from src.core.sort_options import ShortUrlSortBy, SortOrder
from src.models import ShortUrl


class UserShortUrlQueryPort(Protocol):
    """Read ``ShortUrl`` rows for one owner (``user_id``) with paging."""

    async def list_for_owner(
        self,
        owner_id: UUID,
        *,
        page: int,
        page_size: int,
        sort_by: ShortUrlSortBy,
        sort_order: SortOrder,
        search_query: str | None,
    ) -> tuple[Sequence[ShortUrl], int]:
        """Returns (rows for this page, total row count with the same filters).

        The count must match the list filters (owner, active, optional search)
        and must not apply ``LIMIT`` / ``OFFSET``. Used to build page metadata.
        """
        ...
