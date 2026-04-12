"""
Pagination and sort metadata for list responses.

Used by GET /me/short_urls so the client can render pages without guessing
totals. Values echo the request where applicable (sort_by, sort_order, q).
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated

from src.core.sort_options import ShortUrlSortBy, SortOrder


class PaginationParams(BaseModel):
    """List query parameters (FastAPI: ``Annotated[PaginationParams, Query()]``)."""

    page: Annotated[
        int,
        Field(default=1, ge=1, description="1-based page index"),
    ]
    page_size: Annotated[
        int, 
        Field(default=5, ge=1, le=20, description="Items per page (min 1, max 20)"),
    ]
    sort_by: Annotated[
        ShortUrlSortBy,
        Field(default="created_at", description="created_at | usage_count"),
    ]
    sort_order: Annotated[
        SortOrder,
        Field(default="desc", description="asc | desc"),
    ]
    q: Annotated[
        str | None,
        Field(default=None, description="Substring search on slug or long_url"),
    ]


class PaginationMeta(BaseModel):
    """Server-computed list metadata returned with ``items``."""

    page: Annotated[int, Field(..., description="Current 1-based page")]
    page_size: Annotated[int, Field(..., description="Requested page size")]
    total_pages: Annotated[int, Field(..., description="Ceil(total_items / page_size); 0 if empty")]
    total_items: Annotated[int, Field(..., description="Rows matching filters (all pages)")]
    sort_by: Annotated[ShortUrlSortBy, Field(description="Applied sort field")]
    sort_order: Annotated[SortOrder, Field(description="Applied sort direction")]
    has_next_page: Annotated[bool, Field(default=False, description="More items after this page")]
    has_previous_page: Annotated[bool, Field(default=False, description="Page > 1")]
    q: Annotated[
        str | None,
        Field(default=None, description="Search string echoed from request"),
    ]

    model_config = ConfigDict(from_attributes=True)
