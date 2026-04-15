from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, Literal
from src.utils.emoji_validator import SingleEmoji

class UserProfileResponse(BaseModel):
    """What you get from GET /me/profile (or inside the user object)."""
    emoji_avatar: Annotated[
        str,
        Field(..., description="Avatar as one emoji"),
    ]
    ui_theme: Annotated[
        Literal["light", "dark", "system"],
        Field(..., description="light, dark, or system"),
    ]
    ui_language: Annotated[
        Literal["en", "ru"],
        Field(..., description="en or ru"),
    ]
    bio: Annotated[
        str | None,
        Field(..., description="Short about text, or null"),
    ]
    timezone: Annotated[
        str | None,
        Field(..., description="IANA timezone string, or null"),
    ]

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    """Body for PATCH /me/profile; send only fields you want to change."""
    emoji_avatar: Annotated[
        SingleEmoji | None,
        Field(
            default=None,
            max_length=50,
            description="New avatar emoji",
        ),
    ]
    ui_theme: Annotated[
        Literal["light", "dark", "system"] | None,
        Field(
            default=None,
            description="New theme: light, dark, or system",
        ),
    ]
    ui_language: Annotated[
        Literal["en", "ru"] | None,
        Field(
            default=None,
            description="New language: en or ru",
        ),
    ]
    bio: Annotated[
        str | None,
        Field(
            default=None,
            max_length=255,
            description="New bio text, up to 255 characters",
        ),
    ]
    timezone: Annotated[
        str | None,
        Field(
            default=None,
            max_length=50,
            description="New IANA timezone, up to 50 characters",
        ),
    ]
