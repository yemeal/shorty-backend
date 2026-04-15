from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, AnyUrl, ConfigDict, field_validator
from uuid import UUID
import re

from src.core.config import RESERVED_SLUGS
from src.core.exceptions import DomainErrors
from src.schemas.pagination_meta import PaginationMeta


class ShortUrlCreate(BaseModel):
    long_url: Annotated[
        AnyUrl,
        Field(description="The real URL you want to shorten", max_length=20000),
    ]
    slug: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional custom slug (6-30 chars, letters/numbers/Cyrillic, _ and -). If you skip it, we pick a random slug.",
            min_length=6,
            max_length=30,
            pattern=r"^[a-zA-Zа-яА-ЯёЁ0-9_-]+$",
            examples=["my-blog", "мой-блог"],
        ),
    ]

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if value.lower() in RESERVED_SLUGS:
            raise DomainErrors.ShortUrl.SLUG_RESERVED(
                slug=value,
                note="matches RESERVED_SLUGS",
            )

        if not re.search(r"[a-zA-Zа-яА-ЯёЁ0-9]", value):
            raise ValueError(
                "Slug must contain at least one letter or number"
            )

        return value


class ShortUrl(BaseModel):
    id: Annotated[
        UUID,
        Field(description="Row id for this short link"),
    ]

    slug: Annotated[
        str,
        Field(description="Short part in yoursite/{slug}"),
    ]
    long_url: Annotated[
        str,
        Field(description="Target URL after redirect"),
    ]

    created_at: Annotated[
        datetime,
        Field(description="When the row was created"),
    ]
    updated_at: Annotated[
        datetime | None,
        Field(description="Last change time, or null if never updated"),
    ]

    usage_count: Annotated[
        int,
        Field(description="How many times someone opened the short link"),
    ]
    is_active: Annotated[
        bool,
        Field(description="False if soft-deleted"),
    ]

    model_config = ConfigDict(from_attributes=True)


class ShortUrlResponse(BaseModel):
    slug: Annotated[
        str,
        Field(..., description="Short slug"),
    ]
    long_url: Annotated[
        str,
        Field(..., description="Target URL"),
    ]

    model_config = ConfigDict(from_attributes=True)


class ShortUrlListPage(BaseModel):
    """One page from GET /me/short_urls."""

    items: Annotated[list[ShortUrl], Field(description="Short links on this page")]
    meta: Annotated[PaginationMeta, Field(description="Pagination and sort info")]
