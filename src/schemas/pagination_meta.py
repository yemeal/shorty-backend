"""
Pagination and sort for list endpoints (for example GET /me/short_urls).

The client gets page size, totals, and the same sort/search fields it sent where we echo them.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated

from src.core.sort_options import ShortUrlSortBy, SortOrder


class PaginationParams(BaseModel):
    """Query string for a list (use as ``Annotated[PaginationParams, Query()]`` in FastAPI)."""

    page: Annotated[
        int,
        Field(default=1, ge=1, description="Page number, starts at 1"),
    ]
    page_size: Annotated[
        int,
        Field(default=5, ge=1, le=20, description="How many rows per page (1 to 20)"),
    ]
    sort_by: Annotated[
        ShortUrlSortBy,
        Field(default="created_at", description="Sort field: created_at or usage_count"),
    ]
    sort_order: Annotated[
        SortOrder,
        Field(default="desc", description="Sort direction: asc or desc"),
    ]
    q: Annotated[
        str | None,
        Field(default=None, description="Search text inside slug or long URL"),
    ]


class PaginationMeta(BaseModel):
    """Extra numbers for a list response (goes next to ``items``)."""

    page: Annotated[int, Field(..., description="Current page (starts at 1)")]
    page_size: Annotated[int, Field(..., description="Page size you asked for")]
    total_pages: Annotated[
        int,
        Field(
            ...,
            description="Total pages (round up total_items / page_size; 0 if no rows)",
        ),
    ]
    total_items: Annotated[int, Field(..., description="How many rows match the filter (all pages)")]
    sort_by: Annotated[ShortUrlSortBy, Field(description="Sort field we used")]
    sort_order: Annotated[SortOrder, Field(description="Sort direction we used")]
    has_next_page: Annotated[bool, Field(default=False, description="True if there is a next page")]
    has_previous_page: Annotated[bool, Field(default=False, description="True if page is greater than 1")]
    q: Annotated[
        str | None,
        Field(default=None, description="Same search string you sent, or null"),
    ]

    model_config = ConfigDict(from_attributes=True)
