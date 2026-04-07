from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, AnyUrl, ConfigDict
from uuid import UUID


class ShortUrlCreate(BaseModel):
    long_url: Annotated[
        AnyUrl,
        Field(description="Long URL", max_length=20000),
    ]


class ShortUrl(BaseModel):
    id: Annotated[
        UUID,
        Field(description="Unique short url identifier"),
    ]

    short_url: Annotated[
        str,
        Field(description="Short (hashed) URL)"),
    ]
    long_url: Annotated[
        str,
        Field(description="Long URL for this hashed URL"),
    ]

    created_at: Annotated[
        datetime,
        Field(description="Creation date"),
    ]
    updated_at: Annotated[
        datetime,
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
    short_url: Annotated[
        str,
        Field(description="Short (hashed) URL"),
    ]
    long_url: Annotated[
        str,
        Field(description="Long URL for this hashed URL"),
    ]

    model_config = ConfigDict(from_attributes=True)