"""
Port: read current user's short URLs with pagination, text search, and sort.

This is intentionally narrow (not a generic repository): one use case,
one method, so callers do not depend on SQLAlchemy or table layout.

Implementations live in the infrastructure layer (e.g. SQLAlchemy adapter).
"""

from typing import Protocol, Sequence
from uuid import UUID

from src.core.sort_options import ShortUrlSortBy, SortOrder
from src.models import ShortUrl


class UserShortUrlQueryPort(Protocol):
    """Load paginated ShortUrl rows scoped to a single owner (user_id)."""

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
        """Return (items_on_this_page, total_matching_filters).

        ``total_matching_filters`` must use the same predicates as the list
        query (owner, active flag, optional search), but without ``LIMIT`` /
        ``OFFSET``. The application layer uses it for page metadata.
        """
        ...
