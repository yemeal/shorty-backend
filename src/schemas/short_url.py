from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, AnyUrl, ConfigDict, field_validator
from uuid import UUID
import re

from src.core.config import RESERVED_SLUGS
from src.core.exceptions import SlugAlreadyExistsException
from src.schemas.pagination_meta import PaginationMeta


class ShortUrlCreate(BaseModel):
    long_url: Annotated[
        AnyUrl,
        Field(description="Long URL", max_length=20000),
    ]
    slug: Annotated[
        str | None,
        Field(
            default=None,
            description="Custom slug for this long URL",
            min_length=6,
            max_length=30,
            pattern=r"^[a-zA-Zа-яА-ЯёЁ0-9_-]+$",
            examples=["null", "my-blog", "мой-блог"],
        ),
    ]

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if value.lower() in RESERVED_SLUGS:
            raise SlugAlreadyExistsException(
                f"Slug '{value}' is reserved by system"
            )

        if not re.search(r"[a-zA-Zа-яА-ЯёЁ0-9]", value):
            raise ValueError(
                "Slug must contain at least one letter or number"
            )

        return value


class ShortUrl(BaseModel):
    id: Annotated[
        UUID,
        Field(description="Unique short url identifier"),
    ]

    slug: Annotated[
        str,
        Field(description="Short URL slug"),
    ]
    long_url: Annotated[
        str,
        Field(description="Long URL for this short URL"),
    ]

    created_at: Annotated[
        datetime,
        Field(description="Creation date"),
    ]
    updated_at: Annotated[
        datetime | None,
        Field(description="Last update date"),
    ]

    usage_count: Annotated[
        int,
        Field(description="Total usage count"),
    ]
    is_active: Annotated[
        bool,
        Field(description="Is this long url active? (soft-deleted)"),
    ]

    model_config = ConfigDict(from_attributes=True)


class ShortUrlResponse(BaseModel):
    slug: Annotated[
        str,
        Field(..., description="Short URL slug"),
    ]
    long_url: Annotated[
        str,
        Field(..., description="Long URL for this short URL"),
    ]

    model_config = ConfigDict(from_attributes=True)


class ShortUrlListPage(BaseModel):
    items: list[ShortUrl]
    meta: PaginationMeta
