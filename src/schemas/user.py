from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from uuid import UUID

from src.schemas.user_profile import UserProfileResponse
from src.utils.emoji_validator import SingleEmoji


class UserCreate(BaseModel):
    """
    Body for POST /auth/register.
    Only for sign-up; later you change profile with PATCH /me/profile or PATCH /me.
    """
    username: Annotated[
        str,
        Field(
            ...,
            description="Login name, up to 20 characters",
            max_length=20,
        ),
    ]
    password: Annotated[
        str,
        Field(
            ...,
            description="Password, 8 to 100 characters (we store a hash)",
            min_length=8,
            max_length=100,
        ),
    ]
    email: Annotated[
        EmailStr,
        Field(
            ...,
            description="Email you log in with, up to 255 characters",
            max_length=255,
        ),
    ]
    emoji_avatar: Annotated[
        SingleEmoji,
        Field(
            default="⚡️",
            max_length=50,
            description="One emoji for the avatar (server checks it is really one emoji)",
        ),
    ]
    timezone: Annotated[
        str | None,
        Field(
            default=None,
            max_length=50,
            description="IANA zone from the client, for example Europe/Warsaw; null if you do not know",
        ),
    ]


class UserResponse(BaseModel):
    id: Annotated[
        UUID,
        Field(..., description="User id (UUID)"),
    ]

    username: Annotated[
        str,
        Field(..., description="Login name"),
    ]
    email: Annotated[
        str | None,
        Field(
            default=None,
            description="Email on file",
        ),
    ]

    is_active: Annotated[
        bool,
        Field(
            ...,
            description="False if the account is disabled",
        ),
    ]
    telegram_id: Annotated[
        int | None,
        Field(
            default=None,
            description="Telegram id if the account is linked",
        ),
    ]

    profile: Annotated[
        UserProfileResponse,
        Field(
            ...,
            description="Profile row (emoji, theme, language, bio, timezone)",
        ),
    ]

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Body for PATCH /me (only fields you want to change)."""
    username: Annotated[
        str | None,
        Field(
            default=None,
            description="New login name, up to 20 characters",
            max_length=20,
        ),
    ]
    email: Annotated[
        EmailStr | None,
        Field(
            default=None,
            description="New email, up to 255 characters",
            max_length=255,
        ),
    ]
